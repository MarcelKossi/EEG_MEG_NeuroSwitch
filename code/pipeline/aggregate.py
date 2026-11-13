#!/usr/bin/env python
"""Group results across subjects: mean +- SD, paired Wilcoxon tests and the
chance-level oracle. Writes a Markdown table you can paste into the paper/slides.

Usage:
  python aggregate.py --results $WORK/results/classical
  python aggregate.py --results $WORK/results/deep --metric auc
"""
import argparse
import glob
import json
import os

import numpy as np
from scipy.stats import wilcoxon

import common as C

COMPARE_TO = ["EEG", "MEG", "Early fusion", "Late fusion"]
SWITCHES = ["Switch: confidence", "Switch: learned gate", "Switch: subject-level"]


def load(task_dir):
    rows = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(task_dir, "sub-*.json")))]
    return rows


def summarize(rows, metric):
    lines = []
    models = [m for m in C.MODEL_ORDER if all(m in r["metrics"] for r in rows)]
    A = {m: np.array([r["metrics"][m].get(metric, np.nan) for r in rows]) for m in models}
    acc = {m: np.array([r["metrics"][m]["accuracy"] for r in rows]) for m in models}
    n = len(rows)
    lines.append(f"Subjects: {n}  |  metric: {metric}  |  method: {rows[0].get('method')}\n")
    lines.append(f"| Model | Mean {metric} (%) | SD | Min | Max |")
    lines.append("|---|---|---|---|---|")
    for m in models:
        v = A[m] * 100
        if np.all(np.isnan(v)):
            continue
        tag = " (upper bound, not a result)" if m.startswith("Oracle") else ""
        lines.append(f"| {m}{tag} | {np.nanmean(v):.1f} | {np.nanstd(v):.1f} | {np.nanmin(v):.1f} | {np.nanmax(v):.1f} |")
    if "EEG" in acc and "MEG" in acc and "Oracle EEG/MEG" in acc:
        chance = 1 - (1 - acc["EEG"]) * (1 - acc["MEG"])
        lines.append(f"\nOracle EEG/MEG accuracy {acc['Oracle EEG/MEG'].mean() * 100:.1f}% vs "
                     f"{chance.mean() * 100:.1f}% expected if EEG and MEG errors were independent "
                     "(the gap between the two = predictable complementarity).")
    lines.append("\n**Paired Wilcoxon signed-rank tests across subjects** "
                 f"(difference in {metric}, percentage points; Holm-corrected p within each switch)\n")
    lines.append("| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |")
    lines.append("|---|---|---|---|---|---|")
    for s in SWITCHES:
        if s not in A:
            continue
        ps, rws = [], []
        for ref in COMPARE_TO:
            if ref not in A:
                continue
            d = (A[s] - A[ref]) * 100
            p = wilcoxon(A[s], A[ref]).pvalue if n >= 5 and np.any(d != 0) else np.nan
            ps.append(p)
            rws.append((ref, d))
        order = np.argsort(np.nan_to_num(ps, nan=1.0))
        holm = np.full(len(ps), np.nan)
        running = 0.0
        for rank, i in enumerate(order):
            if np.isnan(ps[i]):
                continue
            running = max(running, min(1.0, ps[i] * (len(ps) - rank)))
            holm[i] = running
        for (ref, d), p, ph in zip(rws, ps, holm):
            lines.append(f"| {s} | {ref} | {d.mean():+.2f} | {(d > 0).sum()}/{n} | {p:.4f} | {ph:.4f} |")
    share = np.mean([[r["gate_learned_share"][e] for e in C.EXPERTS] for r in rows], 0)
    lines.append("\nLearned gate choices (share of test trials): " +
                 ", ".join(f"{e} {v * 100:.0f}%" for e, v in zip(C.EXPERTS, share)))
    oe = np.mean([r["only_eeg_correct"] for r in rows]) * 100
    om = np.mean([r["only_meg_correct"] for r in rows]) * 100
    lines.append(f"Trials only EEG correct: {oe:.1f}%  |  only MEG correct: {om:.1f}%")
    better = sum(r["metrics"]["EEG"][metric] > r["metrics"]["MEG"][metric] for r in rows)
    lines.append(f"Subjects where EEG beats MEG: {better}/{n}")
    lines.append("\nPer subject (" + metric + ", %):\n")
    head = ["Subject"] + [m for m in ("EEG", "MEG", "Early fusion", "Late fusion", "Switch: learned gate") if m in A]
    lines.append("| " + " | ".join(head) + " |")
    lines.append("|" + "---|" * len(head))
    for i, r in enumerate(rows):
        lines.append(f"| sub-{r['subject']:02d} | " + " | ".join(f"{A[m][i] * 100:.1f}" for m in head[1:]) + " |")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="e.g. $WORK/results/classical")
    ap.add_argument("--metric", default="balanced_accuracy", choices=["balanced_accuracy", "accuracy", "auc"])
    args = ap.parse_args()
    for task in C.TASKS:
        task_dir = os.path.join(args.results, task)
        rows = load(task_dir)
        if not rows:
            continue
        text = f"## {task}\n\n" + summarize(rows, args.metric)
        print(text + "\n")
        with open(os.path.join(args.results, f"summary_{task}_{args.metric}.md"), "w") as f:
            f.write(text + "\n")


if __name__ == "__main__":
    main()
