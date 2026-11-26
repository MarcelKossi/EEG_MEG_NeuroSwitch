## faces_vs_scrambled

Subjects: 16  |  metric: balanced_accuracy  |  method: classical-LDA

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 71.2 | 5.6 | 60.8 | 81.4 |
| MAG | 78.3 | 4.6 | 70.0 | 88.9 |
| GRAD | 80.7 | 5.0 | 71.8 | 91.0 |
| MEG | 80.5 | 4.7 | 72.1 | 90.3 |
| Early fusion | 87.4 | 4.4 | 76.4 | 95.3 |
| Late fusion | 82.1 | 4.3 | 73.3 | 89.3 |
| Switch: confidence | 84.3 | 4.2 | 75.7 | 90.5 |
| Switch: learned gate | 87.7 | 4.4 | 76.6 | 94.6 |
| Switch: subject-level | 87.4 | 4.4 | 76.4 | 95.3 |
| Oracle EEG/MEG (upper bound, not a result) | 93.7 | 2.1 | 88.9 | 97.7 |
| Oracle 3-way (upper bound, not a result) | 96.8 | 1.6 | 91.9 | 99.1 |

Oracle EEG/MEG accuracy 94.3% vs 94.8% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +13.10 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | MEG | +3.83 | 13/16 | 0.0006 | 0.0006 |
| Switch: confidence | Early fusion | -3.09 | 2/16 | 0.0003 | 0.0006 |
| Switch: confidence | Late fusion | +2.19 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | EEG | +16.47 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | MEG | +7.20 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | Early fusion | +0.28 | 9/16 | 0.4954 | 0.4954 |
| Switch: learned gate | Late fusion | +5.56 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | EEG | +16.19 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | MEG | +6.92 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | Early fusion | +0.00 | 0/16 | nan | nan |
| Switch: subject-level | Late fusion | +5.28 | 16/16 | 0.0000 | 0.0001 |

Learned gate choices (share of test trials): eeg 14%, meg 19%, fused 67%
Trials only EEG correct: 13.0%  |  only MEG correct: 21.7%
Subjects where EEG beats MEG: 1/16

Per subject (balanced_accuracy, %):

| Subject | EEG | MEG | Early fusion | Late fusion | Switch: learned gate |
|---|---|---|---|---|---|
| sub-01 | 61.3 | 80.7 | 87.9 | 76.7 | 85.9 |
| sub-02 | 70.7 | 74.9 | 80.4 | 80.0 | 82.9 |
| sub-03 | 66.1 | 72.1 | 76.4 | 73.3 | 76.6 |
| sub-04 | 76.1 | 81.9 | 87.1 | 86.5 | 87.4 |
| sub-05 | 75.4 | 84.8 | 90.5 | 86.9 | 92.1 |
| sub-06 | 71.1 | 76.3 | 84.8 | 80.7 | 84.5 |
| sub-07 | 78.2 | 77.4 | 89.3 | 85.1 | 90.4 |
| sub-08 | 66.9 | 81.2 | 88.5 | 79.0 | 88.6 |
| sub-09 | 73.5 | 79.8 | 88.7 | 84.1 | 90.5 |
| sub-10 | 60.8 | 79.7 | 84.9 | 77.6 | 83.4 |
| sub-11 | 68.8 | 74.9 | 85.2 | 78.6 | 85.0 |
| sub-12 | 72.9 | 83.4 | 88.9 | 85.3 | 90.2 |
| sub-13 | 75.0 | 80.2 | 87.5 | 82.8 | 87.2 |
| sub-14 | 67.2 | 81.9 | 91.4 | 81.1 | 91.1 |
| sub-15 | 74.2 | 90.3 | 95.3 | 87.0 | 94.6 |
| sub-16 | 81.4 | 88.4 | 91.9 | 89.3 | 92.4 |
