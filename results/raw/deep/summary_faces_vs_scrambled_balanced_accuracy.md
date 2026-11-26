## faces_vs_scrambled

Subjects: 16  |  metric: balanced_accuracy  |  method: deep-EEGNet

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 81.3 | 3.8 | 72.6 | 86.5 |
| MEG | 88.3 | 4.3 | 79.6 | 95.5 |
| Early fusion | 89.1 | 4.6 | 79.5 | 96.0 |
| Late fusion | 91.5 | 3.5 | 84.0 | 96.6 |
| Switch: confidence | 91.8 | 3.5 | 83.9 | 97.3 |
| Switch: learned gate | 90.8 | 4.0 | 81.7 | 96.5 |
| Switch: subject-level | 89.3 | 4.3 | 80.2 | 96.0 |
| Oracle EEG/MEG (upper bound, not a result) | 96.7 | 1.8 | 93.0 | 99.2 |
| Oracle 3-way (upper bound, not a result) | 97.6 | 1.6 | 94.0 | 99.6 |

Oracle EEG/MEG accuracy 96.9% vs 97.9% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +10.46 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | MEG | +3.44 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | Early fusion | +2.62 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | Late fusion | +0.31 | 11/16 | 0.0833 | 0.0833 |
| Switch: learned gate | EEG | +9.52 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | MEG | +2.50 | 15/16 | 0.0001 | 0.0002 |
| Switch: learned gate | Early fusion | +1.69 | 15/16 | 0.0001 | 0.0002 |
| Switch: learned gate | Late fusion | -0.63 | 3/16 | 0.0125 | 0.0125 |
| Switch: subject-level | EEG | +8.01 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | MEG | +0.99 | 13/16 | 0.0017 | 0.0034 |
| Switch: subject-level | Early fusion | +0.18 | 9/16 | 0.3109 | 0.3109 |
| Switch: subject-level | Late fusion | -2.14 | 0/16 | 0.0000 | 0.0001 |

Learned gate choices (share of test trials): eeg 16%, meg 38%, fused 46%
Trials only EEG correct: 8.2%  |  only MEG correct: 14.7%
Subjects where EEG beats MEG: 0/16

Per subject (balanced_accuracy, %):

| Subject | EEG | MEG | Early fusion | Late fusion | Switch: learned gate |
|---|---|---|---|---|---|
| sub-01 | 80.4 | 86.8 | 88.0 | 91.5 | 91.2 |
| sub-02 | 76.1 | 82.1 | 80.6 | 85.8 | 83.9 |
| sub-03 | 75.5 | 79.6 | 79.5 | 84.0 | 81.7 |
| sub-04 | 85.3 | 87.7 | 90.8 | 92.6 | 92.6 |
| sub-05 | 82.2 | 92.7 | 95.3 | 95.5 | 95.2 |
| sub-06 | 84.4 | 85.4 | 89.5 | 91.3 | 90.3 |
| sub-07 | 85.0 | 86.8 | 87.9 | 91.1 | 90.3 |
| sub-08 | 79.1 | 91.0 | 90.2 | 90.8 | 91.4 |
| sub-09 | 80.8 | 88.1 | 89.8 | 90.9 | 91.0 |
| sub-10 | 72.6 | 86.1 | 85.4 | 87.2 | 85.7 |
| sub-11 | 82.7 | 84.7 | 85.9 | 89.4 | 90.2 |
| sub-12 | 81.2 | 93.3 | 92.1 | 94.4 | 93.6 |
| sub-13 | 86.5 | 87.1 | 87.6 | 92.1 | 90.3 |
| sub-14 | 80.3 | 92.2 | 92.2 | 94.0 | 93.2 |
| sub-15 | 84.6 | 94.2 | 95.5 | 96.2 | 96.1 |
| sub-16 | 84.1 | 95.5 | 96.0 | 96.6 | 96.5 |
