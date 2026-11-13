import json, os, sys, numpy as np
from scipy.stats import wilcoxon, spearmanr

for sc in ["clean", "lowsnr", "art20", "art40"]:
    R = json.load(open(os.path.join(sys.argv[1] if len(sys.argv) > 1 else ".", f"res_{sc}.json")))
    keys = list(R[0]["acc"])
    A = {k: np.array([r["acc"][k] for r in R]) for k in keys}
    print(f"\n=== {sc} (n={len(R)}) ===")
    for k in keys:
        print(f"{k:32s} {A[k].mean()*100:5.1f} ± {A[k].std()*100:4.1f}")
    best_single = np.maximum(A["EEG"], A["MEG"])
    print("per-subject best single (oracle pick) %.1f" % (best_single.mean() * 100))
    print("subjects where EEG>MEG:", int((A["EEG"] > A["MEG"]).sum()), "/", len(R))
    for sw in ["Switch: confidence", "Switch: learned gate", "Switch: subject-level"]:
        for ref in ["EEG", "MEG", "Early fusion", "Late fusion"]:
            d = A[sw] - A[ref]
            p = wilcoxon(A[sw], A[ref]).pvalue if np.any(d != 0) else 1.0
            print(f"  {sw:22s} - {ref:12s}: {d.mean()*100:+5.1f} pts  p={p:.3g}")
    rad = np.array([r["meta"]["radiality"] for r in R])
    dep = np.array([r["meta"]["depth"] for r in R])
    diff = A["MEG"] - A["EEG"]
    print("Spearman(radiality, MEG-EEG acc) r=%.2f p=%.3g" % spearmanr(rad, diff))
    print("Spearman(depth, MEG-EEG acc)     r=%.2f p=%.3g" % spearmanr(dep, diff))
    oe = np.mean([r["meta"]["only_eeg"] for r in R]); om = np.mean([r["meta"]["only_meg"] for r in R])
    print("trials only EEG correct %.1f%%, only MEG correct %.1f%%" % (oe * 100, om * 100))
    ch = np.sum([r["meta"]["choice"] for r in R], 0)
    print("gate choices EEG/MEG/fused:", (ch / ch.sum()).round(2))
