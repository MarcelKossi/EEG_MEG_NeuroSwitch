## faces_vs_scrambled

Subjects: 16  |  metric: balanced_accuracy  |  method: deep-EEGNet

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 63.2 | 4.5 | 54.9 | 73.9 |
| MEG | 88.4 | 4.2 | 79.6 | 95.2 |
| Early fusion | 86.7 | 4.8 | 78.1 | 94.6 |
| Late fusion | 88.5 | 4.3 | 80.7 | 95.1 |
| Switch: confidence | 88.8 | 4.3 | 80.1 | 95.4 |
| Switch: learned gate | 88.3 | 4.5 | 80.1 | 95.1 |
| Switch: subject-level | 88.0 | 4.3 | 79.1 | 94.9 |
| Oracle EEG/MEG (upper bound, not a result) | 95.2 | 1.9 | 91.3 | 98.4 |
| Oracle 3-way (upper bound, not a result) | 96.6 | 1.4 | 93.3 | 99.2 |

Oracle EEG/MEG accuracy 95.4% vs 95.9% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +25.62 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | MEG | +0.35 | 10/16 | 0.1754 | 0.3507 |
| Switch: confidence | Early fusion | +2.12 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | Late fusion | +0.26 | 9/16 | 0.2744 | 0.3507 |
| Switch: learned gate | EEG | +25.17 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | MEG | -0.10 | 8/16 | 0.7436 | 1.0000 |
| Switch: learned gate | Early fusion | +1.66 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | Late fusion | -0.19 | 7/16 | 0.5619 | 1.0000 |
| Switch: subject-level | EEG | +24.81 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | MEG | -0.45 | 4/16 | 0.0609 | 0.0609 |
| Switch: subject-level | Early fusion | +1.31 | 14/16 | 0.0027 | 0.0081 |
| Switch: subject-level | Late fusion | -0.55 | 3/16 | 0.0076 | 0.0153 |

Learned gate choices (share of test trials): eeg 6%, meg 58%, fused 36%
Trials only EEG correct: 6.6%  |  only MEG correct: 31.3%
Subjects where EEG beats MEG: 0/16

Per subject (balanced_accuracy, %):

| Subject | EEG | MEG | Early fusion | Late fusion | Switch: learned gate |
|---|---|---|---|---|---|
| sub-01 | 54.9 | 87.0 | 85.5 | 86.5 | 87.1 |
| sub-02 | 59.5 | 83.5 | 80.0 | 83.6 | 80.7 |
| sub-03 | 61.2 | 79.6 | 78.1 | 80.7 | 80.1 |
| sub-04 | 63.3 | 87.7 | 86.4 | 89.1 | 88.3 |
| sub-05 | 70.0 | 92.7 | 93.8 | 94.5 | 94.9 |
| sub-06 | 66.2 | 85.4 | 85.2 | 85.9 | 85.5 |
| sub-07 | 58.8 | 86.8 | 85.9 | 86.4 | 86.4 |
| sub-08 | 65.5 | 91.0 | 88.3 | 89.9 | 89.4 |
| sub-09 | 57.3 | 88.1 | 86.6 | 86.9 | 88.3 |
| sub-10 | 61.7 | 86.3 | 80.4 | 85.2 | 85.3 |
| sub-11 | 64.2 | 84.8 | 82.8 | 85.5 | 86.6 |
| sub-12 | 62.2 | 93.3 | 89.4 | 93.7 | 92.7 |
| sub-13 | 64.8 | 87.1 | 84.9 | 85.7 | 86.2 |
| sub-14 | 62.5 | 92.2 | 90.8 | 92.6 | 91.7 |
| sub-15 | 73.9 | 94.2 | 94.6 | 95.1 | 94.7 |
| sub-16 | 64.5 | 95.2 | 93.9 | 94.8 | 95.1 |
