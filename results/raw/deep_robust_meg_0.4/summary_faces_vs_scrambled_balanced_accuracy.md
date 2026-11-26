## faces_vs_scrambled

Subjects: 16  |  metric: balanced_accuracy  |  method: deep-EEGNet

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 81.3 | 3.8 | 72.6 | 86.5 |
| MEG | 72.6 | 7.1 | 61.5 | 84.0 |
| Early fusion | 77.0 | 6.2 | 68.5 | 88.3 |
| Late fusion | 84.3 | 4.5 | 74.7 | 91.2 |
| Switch: confidence | 84.2 | 4.5 | 75.0 | 90.3 |
| Switch: learned gate | 84.0 | 4.7 | 74.5 | 90.2 |
| Switch: subject-level | 81.3 | 4.5 | 72.5 | 86.9 |
| Oracle EEG/MEG (upper bound, not a result) | 94.0 | 2.2 | 89.2 | 97.3 |
| Oracle 3-way (upper bound, not a result) | 96.0 | 1.7 | 92.4 | 98.5 |

Oracle EEG/MEG accuracy 94.3% vs 95.1% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +2.86 | 15/16 | 0.0002 | 0.0004 |
| Switch: confidence | MEG | +11.57 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | Early fusion | +7.19 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | Late fusion | -0.09 | 8/16 | 0.6322 | 0.6322 |
| Switch: learned gate | EEG | +2.75 | 12/16 | 0.0017 | 0.0034 |
| Switch: learned gate | MEG | +11.45 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | Early fusion | +7.07 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | Late fusion | -0.21 | 6/16 | 0.4332 | 0.4332 |
| Switch: subject-level | EEG | -0.04 | 5/16 | 0.7897 | 0.7897 |
| Switch: subject-level | MEG | +8.67 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | Early fusion | +4.28 | 12/16 | 0.0076 | 0.0153 |
| Switch: subject-level | Late fusion | -3.00 | 1/16 | 0.0001 | 0.0003 |

Learned gate choices (share of test trials): eeg 54%, meg 22%, fused 24%
Trials only EEG correct: 21.4%  |  only MEG correct: 12.0%
Subjects where EEG beats MEG: 15/16

Per subject (balanced_accuracy, %):

| Subject | EEG | MEG | Early fusion | Late fusion | Switch: learned gate |
|---|---|---|---|---|---|
| sub-01 | 80.4 | 77.1 | 78.2 | 85.6 | 84.9 |
| sub-02 | 76.1 | 66.1 | 68.7 | 78.1 | 76.1 |
| sub-03 | 75.5 | 68.6 | 71.4 | 76.6 | 76.3 |
| sub-04 | 85.3 | 65.8 | 75.5 | 85.6 | 87.3 |
| sub-05 | 82.2 | 81.5 | 88.3 | 89.9 | 90.2 |
| sub-06 | 84.4 | 61.5 | 73.4 | 83.7 | 84.2 |
| sub-07 | 85.0 | 69.0 | 72.4 | 86.0 | 84.1 |
| sub-08 | 79.1 | 74.6 | 79.2 | 83.1 | 83.3 |
| sub-09 | 80.8 | 62.7 | 68.7 | 80.6 | 80.5 |
| sub-10 | 72.6 | 66.4 | 68.5 | 74.7 | 74.5 |
| sub-11 | 82.7 | 70.7 | 75.3 | 85.1 | 85.0 |
| sub-12 | 81.2 | 78.6 | 80.4 | 85.5 | 85.6 |
| sub-13 | 86.5 | 72.6 | 77.3 | 87.3 | 87.8 |
| sub-14 | 80.3 | 80.6 | 85.1 | 86.9 | 86.9 |
| sub-15 | 84.6 | 84.0 | 86.5 | 91.2 | 90.1 |
| sub-16 | 84.1 | 81.6 | 82.8 | 88.3 | 88.1 |
