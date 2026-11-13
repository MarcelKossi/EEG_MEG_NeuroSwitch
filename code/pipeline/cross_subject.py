#!/usr/bin/env python
"""Cross-subject validation (leave-one-subject-out) with the classical experts.

Question: does the comparison EEG vs MEG vs fusion vs switching hold when the model
has never seen the test person? (Reichert et al. 2017 found that EEG transferred
across subjects better than MEG.)

For each test subject:
  - experts (EEG, MAG, GRAD, MEG, fused) are trained on all trials of the other subjects;
  - the switch gates and the "subject-level" choice are trained on out-of-fold
    predictions from a 3-fold split of the TRAINING subjects (grouped by subject),
    so the test subject's labels are never used;
  - every feature is z-scored within each subject (label-free per-subject alignment,
    which compensates for differences in head position and signal amplitude).

Same features, classifier, models and metrics as classical_models.py.
"Switch: subject-level" here means: the expert that generalised best to held-out
training subjects (one choice for the whole test subject).

Usage (CPU; ~15-30 min with --n-jobs 16 on the lab server):
  python cross_subject.py --deriv $WORK/derivatives --out $WORK/results/cross_subject \
                          --task faces_vs_scrambled --n-jobs 16
  python aggregate.py --results $WORK/results/cross_subject
"""
import argparse
import os
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np  # noqa: E402
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA  # noqa: E402
from sklearn.model_selection import GroupKFold  # noqa: E402

import common as C  # noqa: E402
from classical_models import window_features  # noqa: E402


def zscore_within(F):
    mu = F.mean(0, keepdims=True)
    sd = F.std(0, keepdims=True) + 1e-12
    return (F - mu) / sd


def make_model():
    # features are already z-scored within subject; n_trials >> n_features here, no PCA needed
    return LDA(solver="lsqr", shrinkage="auto", priors=[0.5, 0.5])


def load_all(files, task, corruption):
    """Features per subject, restricted to the channels common to all subjects."""
    raw = [np.load(f) for f in files]
    common_names = [c for c in raw[0]["ch_names"] if all(c in set(r["ch_names"]) for r in raw[1:])]
    if len(common_names) < len(raw[0]["ch_names"]):
        print(f"Note: {len(raw[0]['ch_names']) - len(common_names)} channels not present in all "
              "subjects were left out", flush=True)
    data = []
    for f, r in zip(files, raw):
        d = C.load_subject(f, task)
        names = list(r["ch_names"])
        idx = np.array([names.index(c) for c in common_names])
        X, types = d["X"][:, idx], d["types"][idx]
        X, hit = C.corrupt(X, types, d["times"], corruption["target"], corruption["rate"],
                           corruption["gain"], corruption["seed"] + d["subject"])
        feats = {m: zscore_within(window_features(X[:, C.modality_mask(types, m)], d["times"]))
                 for m in C.EXPERTS + C.EXTRA}
        Q = zscore_within(C.quality_features(X, types, d["times"]))
        data.append(dict(subject=d["subject"], y=d["y"], feats=feats, Q=Q, hit=hit))
        del X
    return data


def stack(data, idx, key):
    if key in ("y", "Q"):
        return np.concatenate([data[i][key] for i in idx])
    return {m: np.concatenate([data[i]["feats"][m] for i in idx]) for m in C.EXPERTS + C.EXTRA}


def fit_predict(Ftr, ytr, Fte):
    return make_model().fit(Ftr, ytr).predict_proba(Fte)[:, 1]


def run_fold(data, t, task, out_dir, corruption, overwrite):
    sub = data[t]["subject"]
    out_path = os.path.join(out_dir, task, f"sub-{sub:02d}.json")
    if os.path.exists(out_path) and not overwrite:
        print(f"sub-{sub:02d} {task}: exists, skipping", flush=True)
        return
    t0 = time.time()
    tr_idx = [i for i in range(len(data)) if i != t]
    Ftr, ytr, Qtr = stack(data, tr_idx, "feats"), stack(data, tr_idx, "y"), stack(data, tr_idx, "Q")
    groups = np.concatenate([np.full(len(data[i]["y"]), data[i]["subject"]) for i in tr_idx])
    Fte, yte, Qte = data[t]["feats"], data[t]["y"], data[t]["Q"]

    P_te = np.stack([fit_predict(Ftr[m], ytr, Fte[m]) for m in C.EXPERTS], 1)
    P_ex = {m: fit_predict(Ftr[m], ytr, Fte[m]) for m in C.EXTRA}
    # out-of-fold predictions on the training subjects (grouped by subject) for the gates
    P_in = np.zeros((len(ytr), 3))
    for itr, ite in GroupKFold(n_splits=min(3, len(tr_idx))).split(Qtr, ytr, groups):
        for k, m in enumerate(C.EXPERTS):
            P_in[ite, k] = fit_predict(Ftr[m][itr], ytr[itr], Ftr[m][ite])
    gate = C.LearnedGate().fit(P_in, Qtr, ytr)
    sc = C.best_expert(P_in, ytr)

    out, corr, ch = C.evaluate_fold(P_te, P_ex, yte, Qte, gate, sc)
    scores = {k: v for k, v in out.items() if v is not None}
    meta = {"subject": sub, "task": task, "method": "classical-LDA-leave-one-subject-out",
            "n_trials": int(len(yte)), "n_training_subjects": len(tr_idx),
            "class_counts": {"0": int((yte == 0).sum()), "1": int((yte == 1).sum())},
            "subject_level_choice": C.EXPERTS[sc],
            "corruption": {**corruption, "eeg_trials_hit": int(data[t]["hit"][:, 0].sum()),
                           "meg_trials_hit": int(data[t]["hit"][:, 1].sum())},
            "minutes": round((time.time() - t0) / 60, 2)}
    res = C.summarize_subject(yte, scores, corr, ch, meta)
    C.save_json(res, out_path)
    b = res["metrics"]
    print(f"sub-{sub:02d} {task} LOSO DONE balanced acc: " + ", ".join(
        f"{k} {b[k]['balanced_accuracy']:.3f}" for k in ("EEG", "MEG", "Early fusion", "Late fusion",
                                                        "Switch: learned gate")) +
          f" | {meta['minutes']} min", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deriv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--task", default="faces_vs_scrambled", choices=C.TASKS)
    ap.add_argument("--subjects", default=None, help="subjects to include (default: all found)")
    ap.add_argument("--n-jobs", type=int, default=1, help="test subjects processed in parallel")
    ap.add_argument("--overwrite", action="store_true")
    C.add_corruption_args(ap)
    args = ap.parse_args()
    corruption = {"target": args.corrupt, "rate": args.corrupt_rate,
                  "gain": args.corrupt_gain, "seed": args.corrupt_seed}

    files = C.select_files(args.deriv, args.subjects)
    if len(files) < 3:
        raise SystemExit("Leave-one-subject-out needs at least 3 preprocessed subjects.")
    print(f"{len(files)} subjects, task {args.task}: loading features...", flush=True)
    data = load_all(files, args.task, corruption)
    if args.n_jobs > 1:
        from joblib import Parallel, delayed
        Parallel(n_jobs=args.n_jobs)(delayed(run_fold)(data, t, args.task, args.out, corruption, args.overwrite)
                                     for t in range(len(data)))
    else:
        for t in range(len(data)):
            run_fold(data, t, args.task, args.out, corruption, args.overwrite)


if __name__ == "__main__":
    main()
