## faces_vs_scrambled

Subjects: 16  |  metric: balanced_accuracy  |  method: classical-LDA

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 71.2 | 5.6 | 60.8 | 81.4 |
| MAG | 73.4 | 4.2 | 66.3 | 79.7 |
| GRAD | 77.2 | 4.5 | 70.2 | 85.6 |
| MEG | 77.1 | 4.4 | 70.1 | 85.1 |
| Early fusion | 83.9 | 4.3 | 73.1 | 91.7 |
| Late fusion | 79.1 | 4.6 | 71.9 | 87.7 |
| Switch: confidence | 81.4 | 4.5 | 73.4 | 88.9 |
| Switch: learned gate | 85.2 | 4.3 | 75.4 | 91.9 |
| Switch: subject-level | 83.8 | 4.4 | 72.3 | 91.7 |
| Oracle EEG/MEG (upper bound, not a result) | 92.4 | 2.4 | 88.7 | 96.7 |
| Oracle 3-way (upper bound, not a result) | 96.1 | 1.6 | 93.0 | 98.8 |

Oracle EEG/MEG accuracy 93.0% vs 93.8% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +10.21 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | MEG | +4.30 | 14/16 | 0.0002 | 0.0003 |
| Switch: confidence | Early fusion | -2.43 | 2/16 | 0.0003 | 0.0003 |
| Switch: confidence | Late fusion | +2.29 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | EEG | +14.00 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | MEG | +8.10 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | Early fusion | +1.36 | 14/16 | 0.0003 | 0.0003 |
| Switch: learned gate | Late fusion | +6.08 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | EEG | +12.59 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | MEG | +6.69 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | Early fusion | -0.05 | 0/16 | 0.3173 | 0.3173 |
| Switch: subject-level | Late fusion | +4.68 | 15/16 | 0.0001 | 0.0001 |

Learned gate choices (share of test trials): eeg 19%, meg 19%, fused 62%
Trials only EEG correct: 15.1%  |  only MEG correct: 20.5%
Subjects where EEG beats MEG: 1/16

Per subject (balanced_accuracy, %):

| Subject | EEG | MEG | Early fusion | Late fusion | Switch: learned gate |
|---|---|---|---|---|---|
| sub-01 | 61.3 | 76.2 | 83.2 | 72.1 | 83.1 |
| sub-02 | 70.7 | 72.3 | 79.0 | 78.0 | 80.6 |
| sub-03 | 66.1 | 71.6 | 73.1 | 72.6 | 75.4 |
| sub-04 | 76.1 | 77.7 | 82.8 | 80.2 | 85.0 |
| sub-05 | 75.4 | 83.3 | 87.8 | 85.6 | 89.5 |
| sub-06 | 71.1 | 72.5 | 83.8 | 76.5 | 85.1 |
| sub-07 | 78.2 | 73.9 | 87.0 | 83.0 | 89.6 |
| sub-08 | 66.9 | 78.5 | 85.7 | 78.6 | 85.4 |
| sub-09 | 73.5 | 78.1 | 83.4 | 80.6 | 84.5 |
| sub-10 | 60.8 | 75.8 | 79.2 | 71.9 | 79.5 |
| sub-11 | 68.8 | 70.1 | 80.6 | 75.1 | 81.9 |
| sub-12 | 72.9 | 79.9 | 84.9 | 81.0 | 86.8 |
| sub-13 | 75.0 | 78.0 | 85.2 | 82.4 | 86.3 |
| sub-14 | 67.2 | 76.6 | 85.7 | 77.2 | 87.7 |
| sub-15 | 74.2 | 85.1 | 91.7 | 83.9 | 91.9 |
| sub-16 | 81.4 | 84.5 | 88.8 | 87.7 | 91.1 |
