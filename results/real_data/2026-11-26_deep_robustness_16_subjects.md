# Real data: robustness with EEGNet experts, 16 subjects (26 Nov 2026)

**Pipeline:** v1.2 (`deep_models.py`, unchanged). **Task:** faces vs scrambled. **Metric:** balanced accuracy (%), mean ± SD across 16 subjects (SD with ddof = 0, as in `aggregate.py`).
**Statistics:** paired two-sided Wilcoxon signed-rank tests across subjects, Holm correction across the four comparisons of each switch (`aggregate.py`).
**Raw files:** `results/server_sync/2026-11-26_1616/results/deep_robust_eeg_0.4/` and `.../deep_robust_meg_0.4/` (16 JSON files each, plus `summary_faces_vs_scrambled_balanced_accuracy.md`).
**Clean-data reference:** EEGNet results of 14 Nov (`2026-11-14_deep_and_robustness_16_subjects.md`, section 1). LDA robustness: same report, section 2.
**Runs:** 20, 23, 25 and 26 Nov 2026, on the lab server (2 × NVIDIA L40S).

## 1. Setup

- **Same corruption as the LDA robustness experiment:** 40 % of trials, artifact amplitude 5 × channel SD, random spatial pattern and random-walk time course, generator seeded with 0 + subject number.
  - The number of corrupted trials is identical to the LDA runs in every subject: 5,429 of 13,537 trials (40.1 %) in each condition.
  - The corruption applies to training, validation and test trials alike.
- **Two conditions:** EEG corrupted on 40 % of trials; MEG (magnetometers and gradiometers) corrupted on 40 % of trials.
- **Everything else as on clean data:** same folds (leave one run out; 4 training runs, 1 validation run, 1 test run), same EEGNet-8,2 experts and training settings, same switches. The learned gate is trained on the validation run, with quality features computed from the corrupted data.
- **All three experts are retrained in each condition**, including the expert of the intact modality (see section 6).
- **Running time:** 6.6–12.9 min per subject with MEG corrupted and 10.0–28.4 min with EEG corrupted, against 2.5–4.2 min for the clean run of 14 Nov. The GPUs were shared with other processes during some of the robustness runs.

## 2. Accuracy by condition

| Model | Clean | EEG corrupted (40 %) | MEG corrupted (40 %) |
|---|---|---|---|
| EEG | 81.3 ± 3.8 | 63.2 ± 4.5 | 81.3 ± 3.8 |
| MEG | 88.3 ± 4.3 | 88.4 ± 4.2 | 72.6 ± 7.1 |
| Early fusion | 89.1 ± 4.6 | 86.7 ± 4.8 | 77.0 ± 6.2 |
| Late fusion | **91.5 ± 3.5** | 88.5 ± 4.3 | **84.3 ± 4.5** |
| Switch: confidence | **91.8 ± 3.5** | **88.8 ± 4.3** | 84.2 ± 4.5 |
| Switch: learned gate | 90.8 ± 4.0 | 88.3 ± 4.5 | 84.0 ± 4.7 |
| Switch: subject-level | 89.3 ± 4.3 | 88.0 ± 4.3 | 81.3 ± 4.5 |
| *Oracle EEG/MEG (upper bound)* | *96.7 ± 1.8* | *95.2 ± 1.9* | *94.0 ± 2.2* |
| *Oracle 3-way (upper bound)* | *97.6 ± 1.6* | *96.6 ± 1.4* | *96.0 ± 1.7* |

**Change from clean data** (difference of the group means, points):

| Model | EEG corrupted | MEG corrupted |
|---|---|---|
| EEG | −18.1 | 0.0 |
| MEG | +0.1 | −15.7 |
| Early fusion | −2.5 | −12.2 |
| Late fusion | −2.9 | −7.2 |
| Switch: confidence | −3.0 | −7.6 |
| Switch: learned gate | −2.5 | −6.8 |
| Switch: subject-level | −1.3 | −8.1 |

## 3. Switches against the fixed strategies

**Switch minus baseline** (points; wins over 16 subjects; Holm-corrected p):

*EEG corrupted on 40 % of trials*

| | vs EEG | vs MEG | vs early fusion | vs late fusion |
|---|---|---|---|---|
| Confidence switch | +25.6 (16/16, 0.0001) | +0.4 (10/16, 0.35) | **+2.1 (16/16, 0.0001)** | +0.3 (9/16, 0.35) |
| Learned gate | +25.2 (16/16, 0.0001) | −0.1 (8/16, 1.0) | **+1.7 (16/16, 0.0001)** | −0.2 (7/16, 1.0) |
| Subject-level | +24.8 (16/16, 0.0001) | −0.5 (4/16, 0.061) | +1.3 (14/16, 0.0081) | −0.5 (3/16, 0.015) |

*MEG corrupted on 40 % of trials*

| | vs EEG | vs MEG | vs early fusion | vs late fusion |
|---|---|---|---|---|
| Confidence switch | +2.9 (15/16, 0.0004) | +11.6 (16/16, 0.0001) | **+7.2 (16/16, 0.0001)** | −0.1 (8/16, 0.63) |
| Learned gate | +2.7 (12/16, 0.0034) | +11.5 (16/16, 0.0001) | **+7.1 (16/16, 0.0001)** | −0.2 (6/16, 0.43) |
| Subject-level | 0.0 (5/16, 0.79) | +8.7 (16/16, 0.0001) | +4.3 (12/16, 0.015) | −3.0 (1/16, 0.0003) |

**Learned gate against the two fixed fusions, all conditions:**

| Condition | vs early fusion | vs late fusion |
|---|---|---|
| Clean | +1.7 (15/16, 0.0002) | −0.6 (3/16, 0.0125) |
| EEG corrupted, 40 % | +1.7 (16/16, 0.0001) | −0.2 (7/16, 1.0) |
| MEG corrupted, 40 % | +7.1 (16/16, 0.0001) | −0.2 (6/16, 0.43) |

## 4. Comparison with the LDA experts (40 % conditions)

Mean balanced accuracy (%). LDA values from the 14 Nov report (section 2) and from `results/server_sync/2026-11-26_1616/results/robust_{eeg,meg}_0.4/`.

| Model | LDA, EEG 40 % | LDA, MEG 40 % | EEGNet, EEG 40 % | EEGNet, MEG 40 % |
|---|---|---|---|---|
| Intact modality alone | 80.5 (MEG) | 71.2 (EEG) | 88.4 (MEG) | 81.3 (EEG) |
| Early fusion | 84.0 | 81.2 | 86.7 | 77.0 |
| Late fusion | 73.3 | 76.7 | **88.5** | **84.3** |
| Switch: confidence | 74.7 | 78.9 | **88.8** | 84.2 |
| Switch: learned gate | **85.8** | **83.5** | 88.3 | 84.0 |

**Learned gate minus the best fixed strategy** (points; wins; Holm p):

| Expert type | EEG corrupted, 40 % | MEG corrupted, 40 % |
|---|---|---|
| LDA (best fixed: early fusion) | +1.8 (15/16, 0.0001) | +2.3 (15/16, 0.0001) |
| EEGNet (best fixed: late fusion) | −0.2 (7/16, 1.0) | −0.2 (6/16, 0.43) |

## 5. Gate choices, complementarity and oracle

**Learned gate choices** (share of test trials, EEG / MEG / fused, %):

| Clean | EEG corrupted | MEG corrupted |
|---|---|---|
| 16 / 38 / 46 | 6 / 58 / 36 | 54 / 22 / 24 |

**Trials classified correctly by one expert only** (%), and subjects in which EEG beats MEG:

| | Clean | EEG corrupted | MEG corrupted |
|---|---|---|---|
| Only EEG correct | 8.2 | 6.6 | 21.4 |
| Only MEG correct | 14.7 | 31.3 | 12.0 |
| EEG better than MEG | 0/16 | 0/16 | 15/16 |

**Oracle EEG/MEG** (accuracy, %), with the value expected if EEG and MEG errors were independent:

| Clean | EEG corrupted | MEG corrupted |
|---|---|---|
| 96.9 vs 97.9 | 95.4 vs 95.9 | 94.3 vs 95.1 |

## 6. Reproducibility of the retrained experts

- The expert of the intact modality receives exactly the same data as on clean data: the corruption function copies the array and modifies only the target channels, and the training seeds depend only on subject, fold and expert.
- **EEG expert with MEG corrupted:** balanced accuracy identical to the clean run in all 16 subjects.
- **MEG expert with EEG corrupted:** identical in 11 of 16 subjects. It differs in five: sub-01 (+0.2 point), sub-02 (+1.4), sub-10 (+0.2), sub-11 (+0.1) and sub-16 (−0.2). Group mean 88.4 instead of 88.3.
  - The best validation losses differ from the clean run by at most 0.0004 for the MEG expert and 0.001 for the EEG expert. Early stopping changed in 2 of the 96 MEG folds (sub-02, test run 6: 46 → 59 epochs; sub-16, test run 1: 46 → 45 epochs).
  - The most likely cause is non-deterministic GPU arithmetic (cuDNN autotuning is enabled; deterministic algorithms are not enforced). This was not tested.
- **Within the same condition, reruns reproduced the results exactly:** the folds of sub-08 (EEG corrupted) computed on 23 and 25 Nov gave identical accuracies and epoch counts.

## 7. Interpretation

1. **With EEGNet experts, late fusion is robust to a corrupted modality, and the switches stay level with it.**
   - Late fusion loses 2.9 points with EEG corrupted and 7.2 with MEG corrupted, about as much as the switches.
   - Neither the confidence switch nor the learned gate differs significantly from late fusion in either condition (−0.2 to +0.3 point).
   - The learned gate's deficit relative to late fusion on clean data (−0.6 point, 3/16 subjects, p = 0.0125) is no longer significant with a corrupted modality (−0.2 point in both conditions).
2. **The switches beat early fusion and the corrupted modality by a wide margin.**
   - Early fusion is the strategy most affected by MEG corruption (−12.2 points). The learned gate exceeds it by +7.1 points in all 16 subjects.
   - With EEG corrupted, no method significantly beats MEG alone (learned gate −0.1, confidence switch +0.4, n.s.).
   - With MEG corrupted, both switches beat EEG alone (learned gate +2.7 points, 12/16 subjects; confidence switch +2.9 points, 15/16).
3. **The result differs from LDA.** With LDA experts, late fusion and the confidence switch collapse under corruption (73.3 and 74.7 % with EEG corrupted), and the learned gate beats every fixed strategy. With EEGNet experts, late fusion does not collapse.
   - The reason was not investigated. One possible explanation is that a corrupted EEGNet expert gives less confident outputs on corrupted trials, so it carries less weight in the sum of log-odds. This has not been tested.
4. **Across both expert types, the learned gate is the only switch that, in each of the four 40 % conditions, is either significantly better than the best fixed strategy or not significantly different from it.**
   - LDA: +1.8 and +2.3 points over early fusion.
   - EEGNet: −0.2 and −0.2 point relative to late fusion (n.s.).
   - The two other switches are significantly below the best fixed strategy in at least one condition: the confidence switch with LDA (−9.3 and −2.2 points relative to early fusion), and the subject-level switch with LDA, EEG corrupted (−0.4, 1/16), and with EEGNet, MEG corrupted (−3.0, 1/16).
   - No fixed strategy is the best one for both expert types (descriptive; the fixed strategies were not tested against each other): with LDA, late fusion is 10.7 and 4.5 points below early fusion (EEG and MEG corrupted); with EEGNet, early fusion is 7.3 points below late fusion when MEG is corrupted.
   - On clean data, the learned gate is level with the best fixed strategy for LDA (+0.3 over early fusion, n.s.) but not for EEGNet (−0.6 below late fusion).
5. **The learned gate re-routes trials away from the corrupted modality**, as with LDA:
   - EEG corrupted: EEG share 16 → 6 %, MEG share 38 → 58 %;
   - MEG corrupted: MEG share 38 → 22 %, EEG share 16 → 54 %.
6. **No predictable complementarity.** In every condition, the oracle stays below the value expected from independent errors.

**Hypothesis H3** (as accurate as early fusion and more robust):
- With LDA, it was supported (14 Nov).
- With EEGNet, the learned gate is more robust than early fusion and the corrupted modality, but not more robust than late fusion, which is the best fixed strategy for this expert type.

## 8. Limitations and checks not yet done

- **Sensitivity analysis without sub-16:** not yet run for these two conditions (`offline_checks.py` was applied to the 14 Nov results only).
- **One corruption level** (40 %) with EEGNet, against two (20 % and 40 %) with LDA.
- **Synthetic artifacts**, as in the LDA experiment.
- **Single validation run** for the deep learned gate (about 145 trials), as on clean data.
