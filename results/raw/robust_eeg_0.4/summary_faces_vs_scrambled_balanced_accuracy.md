## faces_vs_scrambled

Subjects: 16  |  metric: balanced_accuracy  |  method: classical-LDA

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 65.5 | 3.1 | 59.7 | 70.9 |
| MAG | 78.3 | 4.6 | 70.0 | 88.9 |
| GRAD | 80.7 | 5.0 | 71.8 | 91.0 |
| MEG | 80.5 | 4.7 | 72.1 | 90.3 |
| Early fusion | 84.0 | 4.5 | 75.8 | 92.4 |
| Late fusion | 73.3 | 3.3 | 65.0 | 79.1 |
| Switch: confidence | 74.7 | 3.4 | 66.1 | 80.2 |
| Switch: learned gate | 85.8 | 4.0 | 78.0 | 93.0 |
| Switch: subject-level | 83.6 | 4.5 | 75.0 | 92.1 |
| Oracle EEG/MEG (upper bound, not a result) | 93.1 | 1.9 | 88.9 | 96.9 |
| Oracle 3-way (upper bound, not a result) | 96.5 | 1.3 | 93.1 | 99.0 |

Oracle EEG/MEG accuracy 93.6% vs 93.7% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +9.17 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | MEG | -5.81 | 0/16 | 0.0000 | 0.0001 |
| Switch: confidence | Early fusion | -9.33 | 0/16 | 0.0000 | 0.0001 |
| Switch: confidence | Late fusion | +1.41 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | EEG | +20.33 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | MEG | +5.35 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | Early fusion | +1.83 | 15/16 | 0.0001 | 0.0001 |
| Switch: learned gate | Late fusion | +12.57 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | EEG | +18.08 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | MEG | +3.10 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | Early fusion | -0.42 | 1/16 | 0.0069 | 0.0069 |
| Switch: subject-level | Late fusion | +10.31 | 16/16 | 0.0000 | 0.0001 |

Learned gate choices (share of test trials): eeg 10%, meg 35%, fused 55%
Trials only EEG correct: 12.3%  |  only MEG correct: 27.1%
Subjects where EEG beats MEG: 0/16

Per subject (balanced_accuracy, %):

| Subject | EEG | MEG | Early fusion | Late fusion | Switch: learned gate |
|---|---|---|---|---|---|
| sub-01 | 61.6 | 80.7 | 84.6 | 71.7 | 84.2 |
| sub-02 | 65.6 | 74.9 | 78.7 | 72.1 | 80.5 |
| sub-03 | 59.7 | 72.1 | 75.8 | 65.0 | 78.0 |
| sub-04 | 69.6 | 81.9 | 83.9 | 75.6 | 88.3 |
| sub-05 | 65.5 | 84.8 | 89.3 | 74.4 | 90.1 |
| sub-06 | 68.0 | 76.3 | 79.4 | 74.7 | 84.5 |
| sub-07 | 69.6 | 77.4 | 83.3 | 74.3 | 85.8 |
| sub-08 | 64.1 | 81.2 | 86.2 | 72.4 | 86.7 |
| sub-09 | 66.1 | 79.8 | 82.0 | 74.5 | 83.9 |
| sub-10 | 61.7 | 79.7 | 81.8 | 69.7 | 83.3 |
| sub-11 | 62.1 | 74.9 | 79.7 | 67.9 | 81.4 |
| sub-12 | 64.2 | 83.4 | 88.5 | 74.5 | 88.7 |
| sub-13 | 70.9 | 80.2 | 81.8 | 76.3 | 84.0 |
| sub-14 | 67.2 | 81.9 | 86.2 | 74.5 | 89.5 |
| sub-15 | 67.0 | 90.3 | 92.4 | 79.1 | 93.0 |
| sub-16 | 65.5 | 88.4 | 90.7 | 75.8 | 91.5 |
