## faces_vs_scrambled

Subjects: 16  |  metric: balanced_accuracy  |  method: classical-LDA

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 71.2 | 5.6 | 60.8 | 81.4 |
| MAG | 68.4 | 4.2 | 61.2 | 77.8 |
| GRAD | 73.8 | 4.0 | 66.4 | 81.5 |
| MEG | 73.9 | 4.0 | 67.7 | 81.4 |
| Early fusion | 81.2 | 4.5 | 72.2 | 88.0 |
| Late fusion | 76.7 | 4.2 | 69.5 | 85.6 |
| Switch: confidence | 78.9 | 4.0 | 70.6 | 85.9 |
| Switch: learned gate | 83.5 | 4.1 | 74.9 | 89.3 |
| Switch: subject-level | 80.9 | 4.4 | 72.2 | 88.0 |
| Oracle EEG/MEG (upper bound, not a result) | 91.7 | 2.6 | 88.0 | 96.7 |
| Oracle 3-way (upper bound, not a result) | 95.4 | 1.8 | 92.5 | 98.1 |

Oracle EEG/MEG accuracy 92.4% vs 93.0% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +7.72 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | MEG | +5.00 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | Early fusion | -2.22 | 2/16 | 0.0042 | 0.0042 |
| Switch: confidence | Late fusion | +2.27 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | EEG | +12.23 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | MEG | +9.51 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | Early fusion | +2.29 | 15/16 | 0.0001 | 0.0001 |
| Switch: learned gate | Late fusion | +6.78 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | EEG | +9.71 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | MEG | +6.99 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | Early fusion | -0.23 | 0/16 | 0.1088 | 0.1088 |
| Switch: subject-level | Late fusion | +4.26 | 14/16 | 0.0002 | 0.0004 |

Learned gate choices (share of test trials): eeg 25%, meg 16%, fused 59%
Trials only EEG correct: 17.5%  |  only MEG correct: 19.9%
Subjects where EEG beats MEG: 7/16

Per subject (balanced_accuracy, %):

| Subject | EEG | MEG | Early fusion | Late fusion | Switch: learned gate |
|---|---|---|---|---|---|
| sub-01 | 61.3 | 74.7 | 80.2 | 73.2 | 80.3 |
| sub-02 | 70.7 | 70.4 | 72.3 | 74.2 | 77.8 |
| sub-03 | 66.1 | 68.2 | 72.2 | 69.5 | 74.9 |
| sub-04 | 76.1 | 73.6 | 81.3 | 78.1 | 84.0 |
| sub-05 | 75.4 | 77.1 | 85.5 | 81.4 | 87.6 |
| sub-06 | 71.1 | 69.2 | 82.6 | 75.7 | 82.6 |
| sub-07 | 78.2 | 73.2 | 84.6 | 78.7 | 87.7 |
| sub-08 | 66.9 | 75.5 | 82.0 | 74.7 | 82.0 |
| sub-09 | 73.5 | 73.1 | 79.6 | 76.4 | 85.1 |
| sub-10 | 60.8 | 71.9 | 76.8 | 71.1 | 78.1 |
| sub-11 | 68.8 | 67.7 | 78.0 | 73.0 | 79.9 |
| sub-12 | 72.9 | 78.7 | 85.0 | 80.1 | 86.4 |
| sub-13 | 75.0 | 71.8 | 80.7 | 77.0 | 85.5 |
| sub-14 | 67.2 | 75.4 | 83.9 | 75.5 | 85.7 |
| sub-15 | 74.2 | 81.1 | 88.0 | 82.6 | 89.3 |
| sub-16 | 81.4 | 81.4 | 85.9 | 85.6 | 88.2 |
