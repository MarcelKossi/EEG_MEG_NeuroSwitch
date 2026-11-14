# Real data: classical models, 16 subjects (14 Nov 2026)

**Pipeline:** v1.2 (`code/pipeline/CHANGELOG.md`).
**Method:** shrinkage-LDA experts on 50-ms window means (0–800 ms), within-subject leave-one-run-out cross-validation (6 folds), gates trained on inner held-out predictions only.
**Raw files:** `results/server_sync/2026-11-14_1441/` (one JSON per subject and task, preprocessing logs, aggregate tables).
**Metric:** balanced accuracy (%), mean ± SD across the 16 subjects. Statistics are paired two-sided Wilcoxon signed-rank tests with Holm correction across the four comparisons of each switch.

## 1. Preprocessing

| | Value |
|---|---|
| Trials kept | **13,537 / 14,157 (4.4 % rejected)**; 806–879 per subject, except sub-16 |
| Sub-16 | 669 / 885 kept (24.4 % rejected; no bad channels detected), *under investigation* |
| EEG channels interpolated | 0–4 per subject; EEG002/EEG004 in 4 subjects (01, 05, 08, 14) |
| MEG channels reconstructed by SSS | 0–3 per subject, except sub-03 (12 sensors MEG22xx, run 6 only) |
| ICA components removed | MEG 2–6, EEG 2–7 per subject |
| Runtime | 6.6–8.8 min per subject |

## 2. Faces vs scrambled

| Model | Balanced accuracy | Min–max |
|---|---|---|
| EEG | 71.2 ± 5.6 | 60.8–81.4 |
| MAG | 78.3 ± 4.6 | 70.0–88.9 |
| GRAD | 80.7 ± 5.0 | 71.8–91.0 |
| MEG | 80.5 ± 4.7 | 72.1–90.3 |
| Early fusion | 87.4 ± 4.4 | 76.4–95.3 |
| Late fusion | 82.1 ± 4.3 | 73.3–89.3 |
| Switch: confidence | 84.3 ± 4.2 | 75.7–90.5 |
| **Switch: learned gate** | **87.7 ± 4.4** | 76.6–94.6 |
| Switch: subject-level | 87.4 ± 4.4 | 76.4–95.3 |
| *Oracle EEG/MEG (upper bound)* | *93.7 ± 2.1* | |
| *Oracle 3-way (upper bound)* | *96.8 ± 1.6* | |

**Learned gate minus each baseline** (points; wins over 16 subjects; Holm-corrected p):

| | vs EEG | vs MEG | vs early fusion | vs late fusion |
|---|---|---|---|---|
| Learned gate | +16.5 (16/16, p = 0.0001) | +7.2 (16/16, p = 0.0001) | +0.3 (9/16, p = 0.50) | +5.6 (16/16, p = 0.0001) |
| Confidence switch | +13.1 (16/16, p = 0.0001) | +3.8 (13/16, p = 0.0006) | **−3.1** (2/16, p = 0.0006) | +2.2 (16/16, p = 0.0001) |

**Other indicators**
- Oracle EEG/MEG accuracy: 94.3 %, vs 94.8 % expected if EEG and MEG errors were independent.
- Gate choices: EEG 14 %, MEG 19 %, fused 67 %. The subject-level switch chose the fused expert in all 96 folds.
- Trials correct with EEG only: 13.0 %; with MEG only: 21.7 %. EEG outperformed MEG in 1/16 subjects.

## 3. Famous vs unfamiliar

| Model | Balanced accuracy | Min–max |
|---|---|---|
| EEG | 53.2 ± 3.5 | 48.2–60.3 |
| MAG | 54.1 ± 3.6 | 48.2–59.3 |
| GRAD | 56.3 ± 3.5 | 50.1–60.6 |
| MEG | 56.1 ± 3.5 | 49.9–60.6 |
| **Early fusion** | **57.4 ± 2.8** | 50.2–61.3 |
| Late fusion | 56.2 ± 4.3 | 49.6–62.8 |
| Switch: confidence | 56.7 ± 4.0 | 49.5–63.5 |
| Switch: learned gate | 57.0 ± 2.9 | 51.4–61.2 |
| Switch: subject-level | 57.1 ± 3.2 | 49.9–61.1 |
| *Oracle EEG/MEG (upper bound)* | *78.4 ± 2.7* | |
| *Oracle 3-way (upper bound)* | *82.5 ± 2.2* | |

**Learned gate minus each baseline:**

| | vs EEG | vs MEG | vs early fusion | vs late fusion |
|---|---|---|---|---|
| Learned gate | +3.9 (14/16, p = 0.002) | +0.9 (11/16, p = 0.13) | −0.3 (5/16, p = 0.43) | +0.9 (12/16, p = 0.21) |

**Other indicators**
- Oracle EEG/MEG accuracy: 78.4 %, vs 79.4 % expected under independence.
- Gate choices: EEG 24 %, MEG 33 %, fused 43 %.
- EEG outperformed MEG in 4/16 subjects; sub-13's subject-level switch chose EEG in 5/6 folds.

## 4. Per-subject balanced accuracy

| Subject | Faces: EEG | MEG | Early | Late | Gate | Famous: EEG | MEG | Early | Late | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 61.3 | 80.7 | 87.9 | 76.7 | 85.9 | 48.2 | 55.6 | 58.1 | 53.5 | 57.8 |
| 02 | 70.7 | 74.9 | 80.4 | 80.0 | 82.9 | 53.0 | 60.6 | 60.6 | 61.3 | 59.3 |
| 03 | 66.1 | 72.1 | 76.4 | 73.3 | 76.6 | 52.4 | 49.9 | 50.2 | 49.9 | 51.4 |
| 04 | 76.1 | 81.9 | 87.1 | 86.5 | 87.4 | 55.3 | 57.8 | 55.8 | 58.4 | 59.3 |
| 05 | 75.4 | 84.8 | 90.5 | 86.9 | 92.1 | 50.9 | 50.6 | 58.8 | 53.0 | 55.9 |
| 06 | 71.1 | 76.3 | 84.8 | 80.7 | 84.5 | 55.1 | 58.2 | 58.8 | 57.4 | 59.6 |
| 07 | 78.2 | 77.4 | 89.3 | 85.1 | 90.4 | 54.5 | 57.7 | 56.7 | 56.0 | 56.5 |
| 08 | 66.9 | 81.2 | 88.5 | 79.0 | 88.6 | 48.4 | 53.7 | 54.9 | 52.5 | 53.9 |
| 09 | 73.5 | 79.8 | 88.7 | 84.1 | 90.5 | 49.3 | 52.8 | 56.1 | 49.6 | 52.3 |
| 10 | 60.8 | 79.7 | 84.9 | 77.6 | 83.4 | 49.3 | 52.7 | 55.5 | 49.7 | 53.4 |
| 11 | 68.8 | 74.9 | 85.2 | 78.6 | 85.0 | 54.1 | 53.9 | 57.2 | 55.4 | 56.1 |
| 12 | 72.9 | 83.4 | 88.9 | 85.3 | 90.2 | 50.4 | 60.4 | 60.2 | 60.0 | 59.3 |
| 13 | 75.0 | 80.2 | 87.5 | 82.8 | 87.2 | 60.3 | 54.5 | 54.0 | 57.6 | 58.0 |
| 14 | 67.2 | 81.9 | 91.4 | 81.1 | 91.1 | 56.4 | 59.8 | 58.8 | 60.9 | 61.2 |
| 15 | 74.2 | 90.3 | 95.3 | 87.0 | 94.6 | 54.3 | 59.1 | 61.3 | 60.6 | 59.2 |
| 16 | 81.4 | 88.4 | 91.9 | 89.3 | 92.4 | 58.9 | 60.3 | 60.7 | 62.8 | 59.4 |

## 5. Interpretation (classical models, within subject)

1. **Single modalities.** MEG decodes better than EEG in both tasks (faces: 80.5 vs 71.2). Gradiometers alone match the full MEG array, so the magnetometers add no information here.
2. **H1 is supported against EEG in both tasks.** Against MEG, it is supported for faces vs scrambled (+7.2, 16/16 subjects) but not for famous vs unfamiliar (+0.9, n.s.).
3. **H2 is supported for faces vs scrambled.** Late fusion, which weighs a weak EEG equally, falls 5.6 points below the learned gate. For famous vs unfamiliar the difference is not significant.
4. **No gain over early fusion** in either task (+0.3 and −0.3, n.s.), which reproduces the feasibility study. On clean data, a regularised linear model fed with all channels already exploits both modalities. A confidence-based switch is even worse than early fusion (−3.1).
5. **No predictable complementarity.** In both tasks, the oracle's headroom is what independent errors would produce by chance (gap of 0.5 and 1.0 points).
6. **Metric caveat.** ROC-AUC is not comparable between switches and single models, because a switch's score mixes the probability scales of different experts. Balanced accuracy is therefore the primary metric.

**Next:** robustness experiment (H3), in which EEG or MEG is corrupted on 20 % or 40 % of trials.
