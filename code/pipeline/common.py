"""Shared code for the classical and deep pipelines.

Everything that decides the *comparison* lives here so both pipelines are
judged identically: data loading, tasks, cross-validation by run, label-free
trial-quality features, the switching gates, late fusion, the oracle and the
metrics.

Models compared (per subject, same trials, same folds):
  EEG, MAG, GRAD, MEG            single-modality experts
  Early fusion                   one model on EEG+MEG channels together (= "fused" expert)
  Late fusion                    EEG and MEG experts trained separately, log-odds summed
  Switch: confidence             per trial, use the most confident expert (EEG / MEG / fused)
  Switch: learned gate           per trial, a small gate predicts which expert will be right
                                 (trained only on held-out predictions of the training runs)
  Switch: subject-level          per subject, use the expert that was best on held-out training runs
  Oracle EEG/MEG, Oracle 3-way   correct if ANY expert is correct -> upper bound only, NOT a result
"""
import glob
import json
import os

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

TASKS = ("faces_vs_scrambled", "famous_vs_unfamiliar")
EXPERTS = ("eeg", "meg", "fused")          # experts the switch chooses between
EXTRA = ("mag", "grad")                    # extra single-modality baselines (not switched)
MODEL_ORDER = ["EEG", "MAG", "GRAD", "MEG", "Early fusion", "Late fusion",
               "Switch: confidence", "Switch: learned gate", "Switch: subject-level",
               "Oracle EEG/MEG", "Oracle 3-way"]


# ----------------------------------------------------------------------------- data
def parse_subjects(text):
    out = []
    for part in str(text).split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def select_files(deriv_root, subjects=None):
    files = subject_files(deriv_root)
    if subjects:
        wanted = {f"sub-{s:02d}" for s in parse_subjects(subjects)}
        files = [f for f in files if os.path.basename(os.path.dirname(f)) in wanted]
    return files


def subject_files(deriv_root):
    return sorted(glob.glob(os.path.join(os.path.expanduser(deriv_root), "sub-*", "sub-*_data.npz")))


def load_subject(path, task):
    d = np.load(path)
    cond = d["condition"]
    if task == "faces_vs_scrambled":
        keep = np.ones(len(cond), bool)
        y = (cond != "scrambled").astype(int)          # 1 = face (famous or unfamiliar)
    elif task == "famous_vs_unfamiliar":
        keep = cond != "scrambled"
        y = (cond == "famous").astype(int)
    else:
        raise ValueError(task)
    types = d["ch_types"]
    return dict(X=d["X"][keep], y=y[keep], run=d["run"][keep], types=types,
                times=d["times"], sfreq=float(d["sfreq"]), subject=int(d["subject"]))


def modality_mask(types, modality):
    return {"eeg": types == "eeg", "mag": types == "mag", "grad": types == "grad",
            "meg": np.isin(types, ["mag", "grad"]),
            "fused": np.isin(types, ["eeg", "mag", "grad"])}[modality]


def run_folds(run):
    """Outer CV: leave one run out (6 folds). Trials of one run never split."""
    for r in np.unique(run):
        yield r, np.where(run != r)[0], np.where(run == r)[0]


# ----------------------------------------------------------------- quality features
def quality_features(X, types, times):
    """Label-free, per-trial signal-quality features (usable at test time).

    For EEG, MAG and GRAD separately: log median baseline std across channels and
    log max peak-to-peak across channels. 6 features per trial.
    """
    base = times < 0
    feats = []
    for t in ("eeg", "mag", "grad"):
        Xm = X[:, types == t]
        if Xm.shape[1] == 0:
            feats += [np.zeros(len(X)), np.zeros(len(X))]
            continue
        feats.append(np.log(np.median(Xm[:, :, base].std(-1), axis=1) + 1e-30))
        feats.append(np.log(np.ptp(Xm, axis=-1).max(axis=1) + 1e-30))
    return np.stack(feats, 1)


# ------------------------------------------------------------ robustness experiment
def corrupt(X, types, times, target="none", rate=0.0, gain=5.0, seed=0):
    """Simulated modality failure (robustness experiment).

    For each corrupted modality ("eeg", "meg" or "both"), an independent random
    `rate` fraction of trials receives a large, slowly varying artifact on all of that
    modality's channels: amplitude = `gain` x the channel's median trial std, random
    spatial pattern, random-walk time course. The same trials are corrupted for every
    model, so comparisons stay paired. Returns (X_corrupted, hit) with hit (n, 2) = EEG/MEG.
    """
    hit = np.zeros((len(X), 2), bool)
    if target == "none" or rate <= 0:
        return X, hit
    rng = np.random.default_rng(seed)
    X = X.copy()
    targets = ["eeg", "meg"] if target == "both" else [target]
    for j, mod in enumerate(("eeg", "meg")):
        if mod not in targets:
            continue
        bad = np.where(rng.random(len(X)) < rate)[0]
        hit[bad, j] = True
        for t in (["eeg"] if mod == "eeg" else ["mag", "grad"]):
            ch = np.where(types == t)[0]
            if len(ch) == 0 or len(bad) == 0:
                continue
            sd = np.median(X[:, ch].std(-1), axis=0)                      # (n_ch,)
            w = np.cumsum(rng.standard_normal((len(bad), len(times))), axis=1)
            w = (w - w.mean(1, keepdims=True)) / (w.std(1, keepdims=True) + 1e-12)
            spat = rng.standard_normal((len(bad), len(ch)))
            X[np.ix_(bad, ch)] += (gain * sd[None, :, None] * spat[:, :, None] * w[:, None, :]).astype(X.dtype)
    return X, hit


def add_corruption_args(ap):
    ap.add_argument("--corrupt", default="none", choices=["none", "eeg", "meg", "both"],
                    help="robustness experiment: modality to corrupt")
    ap.add_argument("--corrupt-rate", type=float, default=0.2, help="fraction of trials corrupted")
    ap.add_argument("--corrupt-gain", type=float, default=5.0, help="artifact amplitude (x channel std)")
    ap.add_argument("--corrupt-seed", type=int, default=0)


# ------------------------------------------------------------------------- gates
def _logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p) - np.log(1 - p)


def gate_inputs(P, Q):
    """P: (n, 3) P(class 1) from EEG/MEG/fused experts; Q: quality features."""
    conf = np.abs(P - 0.5) * 2
    return np.concatenate([conf, Q], axis=1)


class LearnedGate:
    """One logistic regression per expert predicting 'this expert is correct'.
    At test time the expert with the highest predicted correctness is used."""

    def fit(self, P, Q, y):
        G = gate_inputs(P, Q)
        correct = (P > 0.5) == y[:, None]
        self.models, self.const = [], []
        for k in range(P.shape[1]):
            c = correct[:, k]
            if c.all() or (~c).all():
                self.models.append(None)
                self.const.append(float(c.mean()))
            else:
                m = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000))
                self.models.append(m.fit(G, c))
                self.const.append(None)
        return self

    def scores(self, P, Q):
        """Predicted probability that each expert is correct, per trial: (n, 3)."""
        G = gate_inputs(P, Q)
        S = np.zeros_like(P)
        for k, m in enumerate(self.models):
            S[:, k] = self.const[k] if m is None else m.predict_proba(G)[:, 1]
        return S

    def choose(self, P, Q):
        S = self.scores(P, Q)
        # ties -> prefer fused (index 2), then MEG, then EEG
        return np.argmax(S + 1e-9 * np.arange(P.shape[1]), axis=1)


def best_expert(P, y):
    """Subject-level switch: expert with best balanced accuracy on held-out training data."""
    scores = [balanced_accuracy_score(y, (P[:, k] > 0.5).astype(int)) for k in range(P.shape[1])]
    return int(np.argmax(np.array(scores) + 1e-9 * np.arange(len(scores))))


# ---------------------------------------------------------------- fold evaluation
def evaluate_fold(P_test, P_extra_test, y_test, Q_test, gate, subj_choice):
    """Returns per-model probability-of-class-1 (or None) and correctness for one fold.

    P_test: (n, 3) for EEG, MEG, fused;  P_extra_test: dict name -> (n,) for MAG/GRAD.
    """
    n = len(y_test)
    idx = np.arange(n)
    out = {}
    out["EEG"] = P_test[:, 0]
    out["MEG"] = P_test[:, 1]
    out["Early fusion"] = P_test[:, 2]
    for k, v in P_extra_test.items():
        out[k.upper()] = v
    out["Late fusion"] = 1 / (1 + np.exp(-(_logit(P_test[:, 0]) + _logit(P_test[:, 1]))))
    ci = np.argmax(np.abs(P_test - 0.5) + 1e-9 * np.arange(3), axis=1)
    out["Switch: confidence"] = P_test[idx, ci]
    gi = gate.choose(P_test, Q_test)
    out["Switch: learned gate"] = P_test[idx, gi]
    out["Switch: subject-level"] = P_test[:, subj_choice]
    correct = {k: (v > 0.5) == y_test for k, v in out.items()}
    corr3 = (P_test > 0.5) == y_test[:, None]
    correct["Oracle EEG/MEG"] = corr3[:, :2].any(1)
    correct["Oracle 3-way"] = corr3.any(1)
    out["Oracle EEG/MEG"] = None
    out["Oracle 3-way"] = None
    return out, correct, {"confidence": ci, "learned": gi}


def summarize_subject(y, scores, correct, choices, meta):
    """scores/correct: dict model -> concatenated arrays over all folds (trial order = y)."""
    res = {"metrics": {}, **meta}
    for name in MODEL_ORDER:
        if name not in correct:
            continue
        c = correct[name]
        pred = np.where(c, y, 1 - y)
        m = {"accuracy": float(c.mean()),
             "balanced_accuracy": float(balanced_accuracy_score(y, pred))}
        s = scores.get(name)
        if s is not None and len(np.unique(y)) == 2:
            m["auc"] = float(roc_auc_score(y, s))
        res["metrics"][name] = m
    e, mg = correct["EEG"], correct["MEG"]
    res["only_eeg_correct"] = float((e & ~mg).mean())
    res["only_meg_correct"] = float((mg & ~e).mean())
    res["both_wrong"] = float((~e & ~mg).mean())
    for gname, ch in choices.items():
        cnt = np.bincount(ch, minlength=3) / len(ch)
        res[f"gate_{gname}_share"] = dict(zip(EXPERTS, [round(float(v), 4) for v in cnt]))
    return res


def save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)
