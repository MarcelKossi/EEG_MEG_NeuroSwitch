#!/usr/bin/env python
"""Deep (GPU) models: EEGNet experts for EEG, MEG and early fusion (EEG+MEG),
late fusion, three switching models and the oracle - per subject,
leave-one-run-out cross-validation (same folds and metrics as classical_models.py).

Expert = EEGNet (Lawhern et al., 2018), identical architecture for every modality;
only the number of input channels changes (EEG 70, MEG 306, fused 376).
Each channel is z-scored with statistics of the training runs only
(this also puts magnetometers, gradiometers and EEG on the same scale).

Inside each outer fold (test = one run):
  - 4 training runs  -> fit the experts
  - 1 validation run -> early stopping + training the switch gates
  - test run         -> all reported numbers (never seen before)

Usage (inside the virtual environment, one GPU):
  export CUDA_VISIBLE_DEVICES=0
  python deep_models.py --deriv $WORK/derivatives --out $WORK/results/deep --subjects 1 --quick
        # smoke test: 1 fold, 3 epochs, ~1 min, saves nothing
  python deep_models.py --deriv $WORK/derivatives --out $WORK/results/deep \
                        --task faces_vs_scrambled --subjects 1-16
        # resumable: subjects already saved are skipped, so it can be split over several sessions
Then: python aggregate.py --results $WORK/results/deep
"""
import argparse
import copy
import os
import time

import numpy as np
import torch
import torch.nn as nn

import common as C


class EEGNet(nn.Module):
    """EEGNet-8,2 (Lawhern et al. 2018, J. Neural Eng.). Input: (batch, channels, times)."""

    def __init__(self, n_ch, n_times, n_classes=2, F1=8, D=2, F2=16, k1=64, drop=0.5):
        super().__init__()
        self.block1 = nn.Sequential(
            nn.Conv2d(1, F1, (1, k1), padding=(0, k1 // 2), bias=False),       # temporal filters
            nn.BatchNorm2d(F1),
            nn.Conv2d(F1, F1 * D, (n_ch, 1), groups=F1, bias=False),          # spatial filters
            nn.BatchNorm2d(F1 * D), nn.ELU(), nn.AvgPool2d((1, 4)), nn.Dropout(drop))
        self.block2 = nn.Sequential(
            nn.Conv2d(F1 * D, F1 * D, (1, 16), padding=(0, 8), groups=F1 * D, bias=False),
            nn.Conv2d(F1 * D, F2, 1, bias=False),
            nn.BatchNorm2d(F2), nn.ELU(), nn.AvgPool2d((1, 8)), nn.Dropout(drop))
        self.eval()
        with torch.no_grad():
            n_feat = self.block2(self.block1(torch.zeros(1, 1, n_ch, n_times))).numel()
        self.train()
        self.fc = nn.Linear(n_feat, n_classes)

    def forward(self, x):
        x = self.block2(self.block1(x.unsqueeze(1)))
        return self.fc(x.flatten(1))


def zscore_fit(X):
    mu = X.mean(axis=(0, 2), keepdims=True, dtype=np.float64)
    sd = X.std(axis=(0, 2), keepdims=True, dtype=np.float64) + 1e-30
    return mu, sd


def train_expert(Xtr, ytr, Xva, yva, args, device, seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    model = EEGNet(Xtr.shape[1], Xtr.shape[2], drop=args.dropout).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    counts = np.bincount(ytr, minlength=2).astype(np.float64)
    w = torch.tensor(len(ytr) / (2 * np.maximum(counts, 1)), dtype=torch.float32, device=device)
    loss_fn = nn.CrossEntropyLoss(weight=w)                     # balanced classes
    Xt = torch.from_numpy(Xtr).to(device)
    yt = torch.from_numpy(ytr.astype(np.int64)).to(device)
    Xv = torch.from_numpy(Xva).to(device)
    yv = torch.from_numpy(yva.astype(np.int64)).to(device)
    best, best_state, wait, ep = np.inf, None, 0, 0
    g = torch.Generator(device="cpu").manual_seed(seed)
    for ep in range(args.max_epochs):
        model.train()
        perm = torch.randperm(len(yt), generator=g).to(device)
        for i in range(0, len(perm), args.batch_size):
            idx = perm[i:i + args.batch_size]
            if len(idx) < 2:
                continue
            opt.zero_grad(set_to_none=True)
            loss = loss_fn(model(Xt[idx]), yt[idx])
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            vl = loss_fn(model(Xv), yv).item()
        if vl < best - 1e-4:
            best, best_state, wait = vl, copy.deepcopy(model.state_dict()), 0
        else:
            wait += 1
            if wait >= args.patience:
                break
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return model, {"epochs": ep + 1, "best_val_loss": round(float(best), 4)}


@torch.no_grad()
def predict(model, X, device, bs=512):
    out = []
    for i in range(0, len(X), bs):
        xb = torch.from_numpy(X[i:i + bs]).to(device)
        out.append(torch.softmax(model(xb), dim=1)[:, 1].float().cpu().numpy())
    return np.concatenate(out)


def run_subject(path, args, device):
    d = C.load_subject(path, args.task)
    sub = d["subject"]
    out_path = os.path.join(args.out, args.task, f"sub-{sub:02d}.json")
    if os.path.exists(out_path) and not args.overwrite and not args.quick:
        print(f"sub-{sub:02d} {args.task}: exists, skipping", flush=True)
        return
    t0 = time.time()
    X, y, run, types, times = d["X"], d["y"], d["run"], d["types"], d["times"]
    X, hit = C.corrupt(X, types, times, args.corrupt, args.corrupt_rate, args.corrupt_gain,
                       args.corrupt_seed + sub)
    Q = C.quality_features(X, types, times)
    experts = list(C.EXPERTS) + (list(C.EXTRA) if args.with_mag_grad else [])
    masks = {m: C.modality_mask(types, m) for m in experts}

    n = len(y)
    scores = {k: np.zeros(n) for k in C.MODEL_ORDER if not k.startswith("Oracle")}
    correct = {k: np.zeros(n, bool) for k in C.MODEL_ORDER}
    choices = {"confidence": np.zeros(n, int), "learned": np.zeros(n, int)}
    fold_info, subj_choices = [], []
    runs = np.unique(run)
    for fi, (r, tr, te) in enumerate(C.run_folds(run)):
        tr_runs = [x for x in runs if x != r]
        val_run = tr_runs[fi % len(tr_runs)]                   # rotates across folds
        fit = tr[run[tr] != val_run]
        va = tr[run[tr] == val_run]
        P_va = np.zeros((len(va), 3))
        P_te = np.zeros((len(te), 3))
        P_ex = {}
        info = {"test_run": int(r), "val_run": int(val_run)}
        for k, m in enumerate(experts):
            Xm = X[:, masks[m]]
            mu, sd = zscore_fit(Xm[fit])
            Z = ((Xm - mu) / sd).astype(np.float32)
            model, tinfo = train_expert(Z[fit], y[fit], Z[va], y[va], args, device,
                                        seed=args.seed + 1000 * sub + 10 * int(r) + k)
            info[m] = tinfo
            p_te = predict(model, Z[te], device)
            if m in C.EXPERTS:
                P_va[:, k] = predict(model, Z[va], device)
                P_te[:, k] = p_te
            else:
                P_ex[m] = p_te
            del model, Z
            if device.type == "cuda":
                torch.cuda.empty_cache()
        gate = C.LearnedGate().fit(P_va, Q[va], y[va])
        sc = C.best_expert(P_va, y[va])
        subj_choices.append(C.EXPERTS[sc])
        out, corr, ch = C.evaluate_fold(P_te, P_ex, y[te], Q[te], gate, sc)
        print(f"sub-{sub:02d} {args.task} fold run-{r}: "
              f"EEG {corr['EEG'].mean():.3f} MEG {corr['MEG'].mean():.3f} "
              f"fused {corr['Early fusion'].mean():.3f} late {corr['Late fusion'].mean():.3f} "
              f"gate {corr['Switch: learned gate'].mean():.3f} "
              f"| epochs {[info[m]['epochs'] for m in experts]} | {(time.time() - t0) / 60:.1f} min",
              flush=True)
        if args.quick:
            print("Quick test OK (1 fold, nothing saved).", flush=True)
            return
        for k, v in out.items():
            if v is not None:
                scores[k][te] = v
        for k, v in corr.items():
            correct[k][te] = v
        for k, v in ch.items():
            choices[k][te] = v
        fold_info.append(info)

    if not args.with_mag_grad:
        for k in ("MAG", "GRAD"):
            scores.pop(k, None)
            correct.pop(k, None)
    meta = {"subject": sub, "task": args.task, "method": "deep-EEGNet", "n_trials": int(n),
            "corruption": {"target": args.corrupt, "rate": args.corrupt_rate, "gain": args.corrupt_gain,
                           "seed": args.corrupt_seed, "eeg_trials_hit": int(hit[:, 0].sum()),
                           "meg_trials_hit": int(hit[:, 1].sum())},
            "class_counts": {"0": int((y == 0).sum()), "1": int((y == 1).sum())},
            "subject_level_choice_per_fold": subj_choices, "folds": fold_info,
            "hyperparameters": {k: getattr(args, k) for k in
                                ("lr", "weight_decay", "batch_size", "max_epochs", "patience", "dropout", "seed")},
            "minutes": round((time.time() - t0) / 60, 2)}
    res = C.summarize_subject(y, scores, correct, choices, meta)
    C.save_json(res, out_path)
    b = res["metrics"]
    print(f"sub-{sub:02d} {args.task} DONE balanced acc: " + ", ".join(
        f"{k} {b[k]['balanced_accuracy']:.3f}" for k in ("EEG", "MEG", "Early fusion", "Late fusion",
                                                        "Switch: learned gate")), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deriv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--task", default="faces_vs_scrambled", choices=C.TASKS)
    ap.add_argument("--subjects", default=None)
    ap.add_argument("--device", default="cuda", help="cuda or cpu")
    ap.add_argument("--with-mag-grad", action="store_true", help="also train MAG and GRAD experts (+40%% time)")
    ap.add_argument("--quick", action="store_true", help="smoke test: 1 fold, 3 epochs, no saving")
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--weight-decay", type=float, default=1e-3)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--max-epochs", type=int, default=200)
    ap.add_argument("--patience", type=int, default=25)
    ap.add_argument("--dropout", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--overwrite", action="store_true")
    C.add_corruption_args(ap)
    args = ap.parse_args()
    if args.quick:
        args.max_epochs = 3

    if args.device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("CUDA not available. Check: source env.sh and the venv; or use --device cpu")
    device = torch.device(args.device)
    if device.type == "cuda":
        torch.backends.cudnn.benchmark = True
        print(f"GPU: {torch.cuda.get_device_name(0)}  (CUDA_VISIBLE_DEVICES="
              f"{os.environ.get('CUDA_VISIBLE_DEVICES', 'all')})", flush=True)
    files = C.select_files(args.deriv, args.subjects)
    if not files:
        raise SystemExit(f"No sub-*/sub-*_data.npz found in {args.deriv}")
    print(f"{len(files)} subjects, task {args.task}, torch {torch.__version__}", flush=True)
    for f in files:
        run_subject(f, args, device)


if __name__ == "__main__":
    main()
