"""Feasibility (headroom) analysis for EEG/MEG modality switching.

Physics-grounded simulation: real simultaneous MEG+EEG forward model (MNE 'sample'
subject, BEM, 305 MEG + 59 EEG) and the real joint MEG/EEG noise covariance
(includes real cross-modality noise correlation). Each simulated subject gets a
different discriminative cortical patch (random location -> random orientation /
depth), which is what physically decides whether EEG or MEG sees it better.

Compared per subject (5-fold CV, ~300 trials):
  EEG-only, MEG-only, early fusion (concat), late fusion (avg log-prob),
  switch-confidence (pick most confident expert), switch-learned (gate trained on
  inner out-of-fold predictions + test-time quality features), subject-level
  switch (pick expert by inner-CV accuracy), oracle switch (upper bound).
"""
import os, sys, json, warnings
import numpy as np
import mne
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

warnings.filterwarnings("ignore")
mne.set_log_level("ERROR")
# Folder MEG/sample of the MNE testing data (forward model, noise covariance, raw file)
D = os.environ.get("MNE_SAMPLE_DIR", os.path.expanduser("~/mne-testing-data/MEG/sample/"))
OUT = os.environ.get("SIM_OUT_DIR", ".")
SF = 100.0
T = np.arange(-0.2, 0.5, 1 / SF)          # epoch times
WIN = [(t, t + 0.05) for t in np.arange(0.0, 0.40, 0.05)]  # 8 feature windows

# ---------------- head model & noise ----------------
fwd = mne.read_forward_solution(D + "sample_audvis_trunc-meg-eeg-oct-6-fwd.fif")
fwd = mne.convert_forward_solution(fwd, surf_ori=True, force_fixed=True, use_cps=True)
info = fwd["info"]
good = [i for i, c in enumerate(info["ch_names"]) if c not in info["bads"]]
ch = [info["ch_names"][i] for i in good]
G = fwd["sol"]["data"][good]                       # (n_ch, n_src) fixed normal
eeg_idx = np.array([i for i, c in enumerate(ch) if c.startswith("EEG")])
meg_idx = np.array([i for i, c in enumerate(ch) if c.startswith("MEG")])
# EEG average reference (applied to leadfield and noise alike)
Ravg = np.eye(len(ch))
Ravg[np.ix_(eeg_idx, eeg_idx)] -= 1.0 / len(eeg_idx)
G = Ravg @ G
cov = mne.read_cov(D + "sample_audvis-cov.fif")
cidx = [cov.ch_names.index(c) for c in ch]
C = cov.data[np.ix_(cidx, cidx)]
C = Ravg @ C @ Ravg.T
w, V = np.linalg.eigh(C)
w = np.clip(w, 0, None)
Lc = V * np.sqrt(w)                                 # C = Lc Lc^T

rr = fwd["source_rr"]; nn = fwd["source_nn"]
raw = mne.io.read_raw_fif(D + "sample_audvis_trunc_raw.fif")
_, origin, _ = mne.bem.fit_sphere_to_headshape(raw.info, units="m")
vec = rr - origin
dist = np.linalg.norm(vec, axis=1)
radiality = np.abs(np.sum(nn * vec / dist[:, None], axis=1))   # 1 = radial
depth = dist.max() - dist


def patch(center, radius=0.008):
    return np.where(np.linalg.norm(rr - rr[center], axis=1) < radius)[0]


def waveform(lat, width, n_trials, rng, jitter=0.02):
    lats = lat + rng.normal(0, jitter, n_trials)
    return np.exp(-0.5 * ((T[None, :] - lats[:, None]) / width) ** 2)


def colored_noise(n_trials, rng, ar=0.85):
    z = rng.standard_normal((n_trials, len(ch), len(T)))
    out = np.empty_like(z)
    out[..., 0] = z[..., 0]
    for t in range(1, len(T)):
        out[..., t] = ar * out[..., t - 1] + np.sqrt(1 - ar ** 2) * z[..., t]
    return np.einsum("ck,nkt->nct", Lc, out)


def simulate_subject(seed, n_trials=300, q=20e-9, art_rate=0.0, art_gain=6.0):
    rng = np.random.default_rng(seed)
    y = np.repeat([0, 1], n_trials // 2)
    rng.shuffle(y)
    # discriminative patch: anywhere on cortex (random orientation/depth)
    c = rng.integers(G.shape[1])
    P = patch(c)
    topo = G[:, P].sum(1) / len(P)                      # mean-moment patch
    amp = q * np.exp(rng.normal(0, 0.3, n_trials)) * (y == 1)
    X = topo[None, :, None] * (amp[:, None] * waveform(0.17, 0.04, n_trials, rng))[:, None, :]
    # common (non-discriminative) evoked activity: 3 random patches, both classes
    for _ in range(3):
        Pc = patch(rng.integers(G.shape[1]))
        tc = G[:, Pc].sum(1) / len(Pc)
        a = q * np.exp(rng.normal(0, 0.3, n_trials))
        X += tc[None, :, None] * (a[:, None] * waveform(rng.uniform(.08, .3), .05, n_trials, rng))[:, None, :]
    X += colored_noise(n_trials, rng)
    # per-trial modality-specific artifacts (independent across modalities)
    qual = np.zeros((n_trials, 2))
    if art_rate > 0:
        for k, idx in enumerate([eeg_idx, meg_idx]):
            bad = rng.random(n_trials) < art_rate
            for i in np.where(bad)[0]:
                # spatially smooth artifact: random mix of top noise components
                comp = Lc[idx][:, -5:] @ rng.standard_normal(5)
                tw = np.cumsum(rng.standard_normal(len(T)))
                tw = (tw - tw.mean()) / (tw.std() + 1e-12)
                X[i][idx] += art_gain * comp[:, None] * tw[None, :]
            qual[:, k] = bad
    return X, y, dict(radiality=float(radiality[P].mean()), depth=float(depth[P].mean()),
                      art=qual)


def feats(X, idx):
    F = [X[:, idx][:, :, (T >= a) & (T < b)].mean(-1) for a, b in WIN]
    return np.concatenate(F, axis=1)


def qfeat(X):
    """test-time quality features: log baseline power per modality."""
    base = T < 0
    return np.stack([np.log(X[:, eeg_idx][:, :, base].var(-1).mean(1)),
                     np.log(X[:, meg_idx][:, :, base].var(-1).mean(1))], 1)


from sklearn.decomposition import PCA


def model(nc):
    return make_pipeline(StandardScaler(), PCA(nc, random_state=0),
                         LDA(solver="lsqr", shrinkage="auto"))


def expert_probs(Ftr, ytr, Fte):
    out = []
    for F_tr, F_te, nc in zip(Ftr, Fte, (40, 40, 80)):
        m = model(nc).fit(F_tr, ytr)
        out.append(m.predict_proba(F_te)[:, 1])
    return np.stack(out, 1)                              # (n, 3): eeg, meg, fused


def oof_probs(Fs, y, seed):
    P = np.zeros((len(y), 3))
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(Fs[0], y):
        P[te] = expert_probs([F[tr] for F in Fs], y[tr], [F[te] for F in Fs])
    return P


def gate_feats(P, Q):
    conf = np.abs(P - 0.5)
    return np.concatenate([conf, Q, Q[:, :1] - Q[:, 1:]], 1)


def run_subject(seed, **kw):
    X, y, meta = simulate_subject(seed, **kw)
    Fe, Fm = feats(X, eeg_idx), feats(X, meg_idx)
    Fs = [Fe, Fm, np.concatenate([Fe, Fm], 1)]
    Q = qfeat(X)
    pred = {k: np.zeros(len(y)) for k in
            ["EEG", "MEG", "Early fusion", "Late fusion", "Switch: confidence",
             "Switch: learned gate", "Switch: subject-level", "Oracle switch (EEG/MEG)",
             "Oracle switch (EEG/MEG/fused)"]}
    choice = np.zeros(len(y), int)
    for fold, (tr, te) in enumerate(StratifiedKFold(5, shuffle=True, random_state=seed).split(Fe, y)):
        P = expert_probs([F[tr] for F in Fs], y[tr], [F[te] for F in Fs])
        yt = y[te]
        corr = (P > 0.5) == yt[:, None]
        pred["EEG"][te] = corr[:, 0]; pred["MEG"][te] = corr[:, 1]
        pred["Early fusion"][te] = corr[:, 2]
        lp = np.log(np.clip(P[:, :2], 1e-6, 1 - 1e-6)) - np.log(np.clip(1 - P[:, :2], 1e-6, 1))
        pred["Late fusion"][te] = (lp.sum(1) > 0) == yt
        ci = np.argmax(np.abs(P - 0.5), 1)
        pred["Switch: confidence"][te] = corr[np.arange(len(te)), ci]
        # learned gate from inner out-of-fold predictions (no test labels used)
        Pin = oof_probs([F[tr] for F in Fs], y[tr], seed + 1000 + fold)
        cin = (Pin > 0.5) == y[tr][:, None]
        Gtr, Gte = gate_feats(Pin, Q[tr]), gate_feats(P, Q[te])
        sc = np.zeros((len(te), 3))
        for k in range(3):
            if cin[:, k].all() or (~cin[:, k]).all():
                sc[:, k] = cin[:, k].mean()
            else:
                g = make_pipeline(StandardScaler(), LogisticRegression(C=1.0)).fit(Gtr, cin[:, k])
                sc[:, k] = g.predict_proba(Gte)[:, 1]
        gi = np.argmax(sc, 1)
        choice[te] = gi
        pred["Switch: learned gate"][te] = corr[np.arange(len(te)), gi]
        si = np.argmax(cin.mean(0))
        pred["Switch: subject-level"][te] = corr[:, si]
        pred["Oracle switch (EEG/MEG)"][te] = corr[:, :2].any(1)
        pred["Oracle switch (EEG/MEG/fused)"][te] = corr.any(1)
        if fold == 0:
            pass
    accs = {k: float(v.mean()) for k, v in pred.items()}
    e, m = pred["EEG"].astype(bool), pred["MEG"].astype(bool)
    meta.pop("art")
    meta.update(only_eeg=float((e & ~m).mean()), only_meg=float((m & ~e).mean()),
                choice=np.bincount(choice, minlength=3).tolist())
    return accs, meta


if __name__ == "__main__":
    scen = sys.argv[1]; n_sub = int(sys.argv[2]); q = float(sys.argv[3])
    art = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    res = []
    for s in range(n_sub):
        a, m = run_subject(1000 * (sum(map(ord, scen)) % 97) + s, q=q, art_rate=art)
        res.append(dict(acc=a, meta=m))
        print(s, {k: round(v, 3) for k, v in a.items() if "Oracle" not in k}, flush=True)
    json.dump(res, open(os.path.join(OUT, f"res_{scen}.json"), "w"))
