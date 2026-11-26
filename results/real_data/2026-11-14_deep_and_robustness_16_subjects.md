# Real data: deep models and robustness experiment, 16 subjects (14 Nov 2026)

**Pipeline:** v1.2. **Task:** faces vs scrambled. **Metric:** balanced accuracy (%), mean ± SD across 16 subjects.
**Statistics:** paired two-sided Wilcoxon tests, Holm correction across the four comparisons of each switch.
**Raw files:** `results/raw/{deep,robust_eeg_0.2,robust_eeg_0.4,robust_meg_0.2,robust_meg_0.4}/`.
Classical results on clean data: `2026-11-14_classical_16_subjects.md`.

## 1. Deep experts (EEGNet)

**Setup** (`deep_models.py`):
- Same leave-one-run-out folds as the classical models: per fold, 4 training runs, 1 validation run (early stopping and gate training) and 1 test run.
- EEGNet-8,2; AdamW (learning rate 10⁻³, weight decay 10⁻³); batch size 64; at most 200 epochs, patience 25; seed 42.
- One NVIDIA L40S, about 3 min per subject.

| Model | EEGNet | (LDA, for comparison) |
|---|---|---|
| EEG | 81.3 ± 3.8 | 71.2 ± 5.6 |
| MEG | 88.3 ± 4.3 | 80.5 ± 4.7 |
| Early fusion | 89.1 ± 4.6 | **87.4 ± 4.4** |
| Late fusion | **91.5 ± 3.5** | 82.1 ± 4.3 |
| Switch: confidence | **91.8 ± 3.5** | 84.3 ± 4.2 |
| Switch: learned gate | 90.8 ± 4.0 | **87.7 ± 4.4** |
| Switch: subject-level | 89.3 ± 4.3 | 87.4 ± 4.4 |
| *Oracle EEG/MEG (upper bound)* | *96.7 ± 1.8* | *93.7 ± 2.1* |

**EEGNet: switch minus baseline** (points; wins over 16 subjects; Holm-corrected p):

| | vs EEG | vs MEG | vs early fusion | vs late fusion |
|---|---|---|---|---|
| Confidence switch | +10.5 (16/16, 0.0001) | +3.4 (16/16, 0.0001) | **+2.6 (16/16, 0.0001)** | +0.3 (11/16, 0.083) |
| Learned gate | +9.5 (16/16, 0.0001) | +2.5 (15/16, 0.0002) | **+1.7 (15/16, 0.0002)** | −0.6 (3/16, 0.0125) |
| Subject-level | +8.0 (16/16, 0.0001) | +1.0 (13/16, 0.0034) | +0.2 (9/16, 0.31) | −2.1 (0/16, 0.0001) |

**Other indicators (EEGNet)**
- Oracle EEG/MEG accuracy: 96.9 %, vs 97.9 % expected under independent errors.
- Gate choices: EEG 16 %, MEG 38 %, fused 46 %.
- EEG outperformed MEG in 0/16 subjects.

**Per subject (EEGNet):**

| Subject | EEG | MEG | Early fusion | Late fusion | Learned gate |
|---|---|---|---|---|---|
| 01 | 80.4 | 86.8 | 88.0 | 91.5 | 91.2 |
| 02 | 76.1 | 82.1 | 80.6 | 85.8 | 83.9 |
| 03 | 75.5 | 79.6 | 79.5 | 84.0 | 81.7 |
| 04 | 85.3 | 87.7 | 90.8 | 92.6 | 92.6 |
| 05 | 82.2 | 92.7 | 95.3 | 95.5 | 95.2 |
| 06 | 84.4 | 85.4 | 89.5 | 91.3 | 90.3 |
| 07 | 85.0 | 86.8 | 87.9 | 91.1 | 90.3 |
| 08 | 79.1 | 91.0 | 90.2 | 90.8 | 91.4 |
| 09 | 80.8 | 88.1 | 89.8 | 90.9 | 91.0 |
| 10 | 72.6 | 86.1 | 85.4 | 87.2 | 85.7 |
| 11 | 82.7 | 84.7 | 85.9 | 89.4 | 90.2 |
| 12 | 81.2 | 93.3 | 92.1 | 94.4 | 93.6 |
| 13 | 86.5 | 87.1 | 87.6 | 92.1 | 90.3 |
| 14 | 80.3 | 92.2 | 92.2 | 94.0 | 93.2 |
| 15 | 84.6 | 94.2 | 95.5 | 96.2 | 96.1 |
| 16 | 84.1 | 95.5 | 96.0 | 96.6 | 96.5 |

## 2. Robustness: one modality corrupted (classical LDA)

**Setup:**
- On 20 % or 40 % of trials (173 and 368 trials for sub-01), a slowly varying artifact (5 × channel SD, random spatial pattern) is added to every EEG channel, or to every MEG channel.
- The corruption applies to training and test trials alike, and the same trials are corrupted for every model.

| Model | Clean | EEG 20 % | EEG 40 % | MEG 20 % | MEG 40 % |
|---|---|---|---|---|---|
| EEG | 71.2 | 68.5 | 65.5 | 71.2 | 71.2 |
| MEG | 80.5 | 80.5 | 80.5 | 77.1 | 73.9 |
| Early fusion | 87.4 | 83.5 | 84.0 | 83.9 | 81.2 |
| Late fusion | 82.1 | 77.5 | 73.3 | 79.1 | 76.7 |
| Switch: confidence | 84.3 | 79.7 | 74.7 | 81.4 | 78.9 |
| **Switch: learned gate** | **87.7** | **86.0** | **85.8** | **85.2** | **83.5** |
| Switch: subject-level | 87.4 | 83.2 | 83.6 | 83.8 | 80.9 |
| *Oracle EEG/MEG* | *93.7* | *93.4* | *93.1* | *92.4* | *91.7* |

**Learned gate minus early fusion** (the strongest fixed baseline on clean data):

| Condition | Difference | Wins | p (Holm) |
|---|---|---|---|
| Clean | +0.3 | 9/16 | 0.50 |
| EEG corrupted, 20 % | **+2.4** | 15/16 | 0.0001 |
| EEG corrupted, 40 % | **+1.8** | 15/16 | 0.0001 |
| MEG corrupted, 20 % | **+1.4** | 14/16 | 0.0003 |
| MEG corrupted, 40 % | **+2.3** | 15/16 | 0.0001 |

The learned gate also beats late fusion by +6.1 to +12.6 points (16/16 subjects in every condition) and MEG by +5.4 to +9.5.

**Gate choices** (share of test trials, EEG / MEG / fused):

| Clean | EEG 20 % | EEG 40 % | MEG 20 % | MEG 40 % |
|---|---|---|---|---|
| 14 / 19 / 67 | 14 / 31 / 55 | 10 / 35 / 55 | 19 / 19 / 62 | 25 / 16 / 59 |

When EEG is corrupted, the gate moves trials towards the MEG expert (MEG share 19 % → 35 %). When MEG is corrupted, it moves them towards EEG (EEG share 14 % → 25 %).

## 3. Interpretation

1. **On clean data, the best fixed combination depends on the classifier.**
   - With LDA, early fusion is best and late fusion lags by 5.3 points.
   - With EEGNet, late fusion is best and early fusion lags by 2.4 points.

   The switches track the best option in both cases:
   - LDA: learned gate 87.7 vs early fusion 87.4 (n.s.);
   - EEGNet: confidence switch 91.8 vs late fusion 91.5 (n.s.); learned gate +1.7 over early fusion and −0.6 below late fusion.

   An adaptive switch therefore removes the need to know in advance which fusion scheme suits a given classifier.
2. **With one modality corrupted, the learned gate beats every fixed strategy, including early fusion** (+1.4 to +2.4 points, 14–15/16 subjects, Holm p ≤ 0.0003). This supports **H3**. Late fusion and the confidence switch degrade the most, because a corrupted expert can still be confidently wrong.
3. **The gate re-routes trials away from the corrupted modality**, which shows that its decisions follow signal quality (H4, first evidence).
4. **No predictable complementarity on clean data.** The oracle stays at the level expected from independent errors, with both classifiers.
5. **EEGNet benefits EEG most** (+10.1 points over LDA) and narrows the EEG–MEG gap from 9.3 to 7.0 points.

**Limitations:**
- The robustness experiment uses synthetic artifacts and LDA experts only.
- The deep models were run on faces vs scrambled only.
- The deep learned gate is trained on a single validation run (about 145 trials), which probably explains why it is below the confidence switch.
