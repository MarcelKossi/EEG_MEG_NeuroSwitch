#!/usr/bin/env python
"""Classical (CPU) models: EEG, MAG, GRAD, MEG, early fusion, late fusion,
three switching models and the oracle - per subject, leave-one-run-out CV.

Expert = shrinkage LDA on time-window means (16 windows of 50 ms, 0-0.8 s)
of the chosen channels, with equal class priors (lossless PCA rotation first, for speed). Same model for every modality,
so differences come from the data, not from the classifier.

The switch gates are trained on *inner* leave-one-run-out predictions of the
training runs only - the test run's labels are never used to choose an expert.

Robustness experiment: add e.g. --corrupt eeg --corrupt-rate 0.2 (use a separate --out folder).

Usage:
  python classical_models.py --deriv $WORK/derivatives --out $WORK/results/classical \
                             --task faces_vs_scrambled --n-jobs 16
  python classical_models.py ... --task famous_vs_unfamiliar
Runs on CPU only (no GPU needed). Then: python aggregate.py --results $WORK/results/classical
"""
import argparse
import os
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import numpy as np  # noqa: E402
from sklearn.decomposition import PCA  # noqa: E402
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA  # noqa: E402
from sklearn.pipeline import make_pipeline  # noqa: E402
from sklearn.preprocessing import StandardScaler  # noqa: E402

import common as C  # noqa: E402

WIN = 0.05
T_START, T_END = 0.0, 0.8


def window_features(X, times):
    starts = np.arange(T_START, T_END - 1e-9, WIN)
    F = [X[:, :, (times >= a) & (times < a + WIN)].mean(-1) for a in starts]
    return np.concatenate(F, axis=1).astype(np.float64)


def make_model():
    # PCA keeps ALL components (n_components=None -> min(n_trials, n_features)): it only
    # rotates the data into the subspace spanned by the training trials, which makes the
    # shrinkage-LDA ~50x faster with (almost) no change to the classifier.
    return make_pipeline(StandardScaler(), PCA(n_components=None, svd_solver="full"),
                         LDA(solver="lsqr", shrinkage="auto", priors=[0.5, 0.5]))


def fit_predict(F, y, tr, te):
    m = make_model().fit(F[tr], y[tr])
    return m.predict_proba(F[te])[:, 1]


def run_subject(path, task, out_dir, overwrite=False, corruption=None):
    d = C.load_subject(path, task)
    sub = d["subject"]
    out_path = os.path.join(out_dir, task, f"sub-{sub:02d}.json")
    if os.path.exists(out_path) and not overwrite:
        print(f"sub-{sub:02d} {task}: exists, skipping", flush=True)
        return out_path
    t0 = time.time()
    X, y, run, types, times = d["X"], d["y"], d["run"], d["types"], d["times"]
    corruption = corruption or {"target": "none", "rate": 0.0, "gain": 5.0, "seed": 0}
    X, hit = C.corrupt(X, types, times, corruption["target"], corruption["rate"],
                       corruption["gain"], corruption["seed"] + sub)
    feats = {m: window_features(X[:, C.modality_mask(types, m)], times)
             for m in C.EXPERTS + C.EXTRA}
    Q = C.quality_features(X, types, times)

    n = len(y)
    scores = {k: np.zeros(n) for k in C.MODEL_ORDER if not k.startswith("Oracle")}
    correct = {k: np.zeros(n, bool) for k in C.MODEL_ORDER}
    choices = {"confidence": np.zeros(n, int), "learned": np.zeros(n, int)}
    subj_choices = []
    for r, tr, te in C.run_folds(run):
        P_te = np.stack([fit_predict(feats[m], y, tr, te) for m in C.EXPERTS], 1)
        P_ex = {m: fit_predict(feats[m], y, tr, te) for m in C.EXTRA}
        # inner leave-one-run-out on training runs -> held-out predictions for the gates
        P_in = np.zeros((len(tr), 3))
        for _, itr, ite in C.run_folds(run[tr]):
            for k, m in enumerate(C.EXPERTS):
                P_in[ite, k] = fit_predict(feats[m][tr], y[tr], itr, ite) if len(np.unique(y[tr][itr])) == 2 else 0.5
        gate = C.LearnedGate().fit(P_in, Q[tr], y[tr])
        sc = C.best_expert(P_in, y[tr])
        subj_choices.append(C.EXPERTS[sc])
        out, corr, ch = C.evaluate_fold(P_te, P_ex, y[te], Q[te], gate, sc)
        for k, v in out.items():
            if v is not None:
                scores[k][te] = v
        for k, v in corr.items():
            correct[k][te] = v
        for k, v in ch.items():
            choices[k][te] = v
        print(f"sub-{sub:02d} {task} fold run-{r}: "
              f"EEG {corr['EEG'].mean():.3f} MEG {corr['MEG'].mean():.3f} "
              f"fused {corr['Early fusion'].mean():.3f} gate {corr['Switch: learned gate'].mean():.3f}",
              flush=True)

    meta = {"subject": sub, "task": task, "method": "classical-LDA", "n_trials": int(n),
            "corruption": {**corruption, "eeg_trials_hit": int(hit[:, 0].sum()),
                           "meg_trials_hit": int(hit[:, 1].sum())},
            "class_counts": {"0": int((y == 0).sum()), "1": int((y == 1).sum())},
            "subject_level_choice_per_fold": subj_choices,
            "minutes": round((time.time() - t0) / 60, 2)}
    res = C.summarize_subject(y, scores, correct, choices, meta)
    C.save_json(res, out_path)
    b = res["metrics"]
    print(f"sub-{sub:02d} {task} DONE  balanced acc: " + ", ".join(
        f"{k} {b[k]['balanced_accuracy']:.3f}" for k in ("EEG", "MEG", "Early fusion", "Late fusion",
                                                        "Switch: learned gate")), flush=True)
    return out_path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deriv", required=True, help="output folder of preprocess.py")
    ap.add_argument("--out", required=True, help="results folder")
    ap.add_argument("--task", default="faces_vs_scrambled", choices=C.TASKS)
    ap.add_argument("--subjects", default=None, help="e.g. 1-4 (default: all found)")
    ap.add_argument("--n-jobs", type=int, default=1, help="subjects in parallel")
    ap.add_argument("--overwrite", action="store_true")
    C.add_corruption_args(ap)
    args = ap.parse_args()
    corruption = {"target": args.corrupt, "rate": args.corrupt_rate,
                  "gain": args.corrupt_gain, "seed": args.corrupt_seed}

    files = C.select_files(args.deriv, args.subjects)
    if not files:
        raise SystemExit(f"No sub-*/sub-*_data.npz found in {args.deriv}")
    print(f"{len(files)} subjects, task {args.task}", flush=True)
    if args.n_jobs > 1:
        from joblib import Parallel, delayed
        Parallel(n_jobs=args.n_jobs)(delayed(run_subject)(f, args.task, args.out, args.overwrite, corruption) for f in files)
    else:
        for f in files:
            run_subject(f, args.task, args.out, args.overwrite, corruption)


if __name__ == "__main__":
    main()
