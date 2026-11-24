# Real data: offline checks (18 Nov 2026)

Both checks were computed from the result files already saved on 14 Nov (`results/server_sync/2026-11-14_1600/results/`). No data or GPU were needed.
**Script:** `code/pipeline/offline_checks.py`. **Metric:** balanced accuracy (%).
**Full output:** `results/real_data/2026-11-18_offline_checks_full_output.md`.

## 1. Sensitivity analysis without sub-16

**Why:** sub-16 lost 24.4 % of its trials at rejection (669 of 885 kept). No bad channels were detected, so the rejections come from amplitude thresholds alone.

**Method:** the paired comparisons of the 14 Nov reports were repeated on the remaining 15 subjects, with the same tests. These are two-sided Wilcoxon signed-rank tests, Holm-corrected across the four baselines of each switch.

**Learned gate vs each baseline, 15 subjects** (mean difference in points; wins; Holm p):

| Experiment | vs early fusion | vs late fusion | vs MEG | vs EEG |
|---|---|---|---|---|
| LDA, faces vs scrambled | +0.3 (8/15, 0.64) | +5.7 (15/15, 0.0002) | +7.4 (15/15, 0.0002) | +16.8 (15/15, 0.0002) |
| LDA, famous vs unfamiliar | −0.2 (5/15, 0.56) | +1.2 (12/15, 0.077) | +1.1 (11/15, 0.077) | +4.1 (13/15, 0.0024) |
| EEGNet, faces vs scrambled | +1.8 (14/15, 0.0004) | −0.7 (3/15, 0.016) | +2.6 (14/15, 0.0004) | +9.3 (15/15, 0.0002) |
| LDA, EEG corrupted 20 % | **+2.5** (14/15, 0.0002) | +8.4 (15/15, 0.0002) | +5.6 (15/15, 0.0002) | +17.5 (15/15, 0.0002) |
| LDA, EEG corrupted 40 % | **+1.9** (14/15, 0.0002) | +12.4 (15/15, 0.0002) | +5.5 (15/15, 0.0002) | +20.0 (15/15, 0.0002) |
| LDA, MEG corrupted 20 % | **+1.3** (13/15, 0.0006) | +6.3 (15/15, 0.0002) | +8.2 (15/15, 0.0002) | +14.3 (15/15, 0.0002) |
| LDA, MEG corrupted 40 % | **+2.3** (14/15, 0.0002) | +7.1 (15/15, 0.0002) | +9.7 (15/15, 0.0002) | +12.6 (15/15, 0.0002) |

**EEGNet, confidence switch vs late fusion:** +0.3 (10/15, p = 0.14), unchanged in direction and significance.

**Effect of sub-16 on its own:**
- Its learned-gate advantage over early fusion goes in the same direction as the group in every condition: +0.5 on clean data, +0.8 for EEG 20 % and 40 %, and +2.3 for MEG 20 % and 40 %.
- Excluding it lowers the group means by 0.2 to 0.7 point, because sub-16 is one of the best-decoded participants.

**Conclusion:** no conclusion of the 14 Nov reports depends on sub-16. The 16-subject analysis stays the main analysis, and this check is reported as a sensitivity analysis.

## 2. Famous vs unfamiliar: above chance?

**Method:** a one-sided Wilcoxon signed-rank test of balanced accuracy against 50 % across the 16 subjects, Holm-corrected across the nine models (LDA).

| Model | Mean | Subjects > 50 % | p (Holm) |
|---|---|---|---|
| EEG | 53.2 | 12/16 | 0.0026 |
| MAG | 54.1 | 14/16 | 0.0010 |
| GRAD | 56.3 | 16/16 | 0.0001 |
| MEG | 56.1 | 15/16 | 0.0002 |
| Early fusion | 57.4 | 16/16 | 0.0001 |
| Late fusion | 56.2 | 13/16 | 0.0006 |
| Switch: confidence | 56.7 | 15/16 | 0.0002 |
| Switch: learned gate | 57.0 | 16/16 | 0.0001 |
| Switch: subject-level | 57.1 | 15/16 | 0.0002 |

**Conclusion:**
- Every model decodes famous vs unfamiliar faces above chance at the group level, EEG included.
- The effect is small (3–7 points above chance), so this task is reported as a hard, low-signal condition, not as a failure.

**Caveat:** a group-level test on accuracies shows that the effect is present in at least part of the population; it does not show that it is present in every subject (Allefeld et al., 2016). Per-subject permutation tests would need new runs on the server and are not needed for the claims of the paper.
