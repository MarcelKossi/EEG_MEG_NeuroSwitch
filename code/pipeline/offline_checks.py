#!/usr/bin/env python
"""Checks computed from saved results only (no data, no GPU).

1. Sensitivity: repeat the group comparisons after excluding subjects
   (e.g. sub-16, whose rejection rate was 24.4 %).
2. Above-chance test: is each model better than 50 % balanced accuracy
   across subjects? (one-sided Wilcoxon signed-rank test, Holm-corrected
   across models)

Usage:
  python offline_checks.py --results <dir with classical/, deep/, robust_*/> --exclude 16
  python offline_checks.py --results <dir> --chance-task famous_vs_unfamiliar --chance-results classical
"""
import argparse
import glob
import json
import os

import numpy as np
from scipy.stats import wilcoxon

MODELS = ["EEG", "MAG", "GRAD", "MEG", "Early fusion", "Late fusion",
          "Switch: confidence", "Switch: learned gate", "Switch: subject-level"]
COMPARE_TO = ["EEG", "MEG", "Early fusion", "Late fusion"]
SWITCHES = ["Switch: confidence", "Switch: learned gate", "Switch: subject-level"]


def load(task_dir, exclude=()):
    rows = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(task_dir, "sub-*.json")))]
    return [r for r in rows if r["subject"] not in exclude]


def holm(ps):
    ps = np.asarray(ps, float)
    order = np.argsort(ps)
    out = np.empty(len(ps))
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, ps[i] * (len(ps) - rank)))
        out[i] = running
    return out


def compare(rows, metric="balanced_accuracy"):
    """Same tests as aggregate.py: each switch vs four baselines, Holm within each switch."""
    A = {m: np.array([r["metrics"][m][metric] for r in rows]) for m in MODELS
         if all(m in r["metrics"] for r in rows)}
    n = len(rows)
    lines = [f"Subjects: {n}", "", "| Model | Mean (%) | SD |", "|---|---|---|"]
    for m in A:
        lines.append(f"| {m} | {A[m].mean() * 100:.1f} | {A[m].std() * 100:.1f} |")
    lines += ["", "| Switch | vs | Mean diff | Wins | p | p (Holm) |", "|---|---|---|---|---|---|"]
    for s in SWITCHES:
        if s not in A:
            continue
        refs = [r for r in COMPARE_TO if r in A]
        diffs = [(A[s] - A[r]) * 100 for r in refs]
        # identical scores in every subject: no test possible, report p = 1
        ps = [wilcoxon(A[s], A[r]).pvalue if np.any(d != 0) else 1.0 for r, d in zip(refs, diffs)]
        for r, d, p, ph in zip(refs, diffs, ps, holm(ps)):
            note = " (identical)" if not np.any(d != 0) else ""
            lines.append(f"| {s} | {r} | {d.mean():+.2f}{note} | {(d > 0).sum()}/{n} | {p:.4f} | {ph:.4f} |")
    return "\n".join(lines)


def above_chance(rows, metric="balanced_accuracy"):
    """One-sided Wilcoxon signed-rank test of (score - 0.5) > 0 across subjects."""
    models = [m for m in MODELS if all(m in r["metrics"] for r in rows)]
    n = len(rows)
    stats = []
    for m in models:
        v = np.array([r["metrics"][m][metric] for r in rows])
        p = wilcoxon(v - 0.5, alternative="greater").pvalue
        stats.append((m, v, p))
    ph = holm([s[2] for s in stats])
    lines = [f"Subjects: {n}", "",
             "| Model | Mean (%) | SD | Subjects > 50 % | p (one-sided) | p (Holm) |",
             "|---|---|---|---|---|---|"]
    for (m, v, p), h in zip(stats, ph):
        lines.append(f"| {m} | {v.mean() * 100:.1f} | {v.std() * 100:.1f} | {(v > 0.5).sum()}/{n} | {p:.4f} | {h:.4f} |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--exclude", default="", help="comma-separated subject numbers, e.g. 16")
    ap.add_argument("--chance-task", default="famous_vs_unfamiliar")
    ap.add_argument("--chance-results", default="classical")
    args = ap.parse_args()
    exclude = {int(s) for s in args.exclude.split(",") if s}

    if exclude:
        print(f"# Sensitivity analysis: subjects excluded {sorted(exclude)}\n")
        for exp in sorted(os.listdir(args.results)):
            for task_dir in sorted(glob.glob(os.path.join(args.results, exp, "*"))):
                if not os.path.isdir(task_dir):
                    continue
                rows = load(task_dir, exclude)
                if rows:
                    print(f"## {exp} / {os.path.basename(task_dir)}\n\n{compare(rows)}\n")

    task_dir = os.path.join(args.results, args.chance_results, args.chance_task)
    print(f"# Above-chance test: {args.chance_results} / {args.chance_task}\n")
    print(above_chance(load(task_dir)) + "\n")


if __name__ == "__main__":
    main()
