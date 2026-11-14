## faces_vs_scrambled

Subjects: 16  |  metric: balanced_accuracy  |  method: classical-LDA

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 68.5 | 4.4 | 60.0 | 75.4 |
| MAG | 78.3 | 4.6 | 70.0 | 88.9 |
| GRAD | 80.7 | 5.0 | 71.8 | 91.0 |
| MEG | 80.5 | 4.7 | 72.1 | 90.3 |
| Early fusion | 83.5 | 4.8 | 72.5 | 92.2 |
| Late fusion | 77.5 | 3.7 | 68.8 | 83.0 |
| Switch: confidence | 79.7 | 3.5 | 71.0 | 85.3 |
| Switch: learned gate | 86.0 | 4.3 | 76.9 | 93.7 |
| Switch: subject-level | 83.2 | 5.0 | 71.5 | 91.9 |
| Oracle EEG/MEG (upper bound, not a result) | 93.4 | 2.0 | 88.6 | 97.0 |
| Oracle 3-way (upper bound, not a result) | 96.5 | 1.5 | 92.4 | 99.1 |

Oracle EEG/MEG accuracy 94.1% vs 94.3% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +11.21 | 16/16 | 0.0000 | 0.0001 |
| Switch: confidence | MEG | -0.78 | 6/16 | 0.4332 | 0.4332 |
| Switch: confidence | Early fusion | -3.82 | 1/16 | 0.0001 | 0.0002 |
| Switch: confidence | Late fusion | +2.21 | 15/16 | 0.0001 | 0.0002 |
| Switch: learned gate | EEG | +17.45 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | MEG | +5.46 | 16/16 | 0.0000 | 0.0001 |
| Switch: learned gate | Early fusion | +2.43 | 15/16 | 0.0001 | 0.0001 |
| Switch: learned gate | Late fusion | +8.45 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | EEG | +14.68 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | MEG | +2.69 | 15/16 | 0.0001 | 0.0001 |
| Switch: subject-level | Early fusion | -0.34 | 1/16 | 0.0109 | 0.0109 |
| Switch: subject-level | Late fusion | +5.68 | 16/16 | 0.0000 | 0.0001 |

Learned gate choices (share of test trials): eeg 14%, meg 31%, fused 55%
Trials only EEG correct: 12.7%  |  only MEG correct: 24.2%
Subjects where EEG beats MEG: 0/16

Per subject (balanced_accuracy, %):

| Subject | EEG | MEG | Early fusion | Late fusion | Switch: learned gate |
|---|---|---|---|---|---|
| sub-01 | 60.0 | 80.7 | 83.0 | 73.7 | 83.3 |
| sub-02 | 67.1 | 74.9 | 77.9 | 72.8 | 79.5 |
| sub-03 | 61.5 | 72.1 | 72.5 | 68.8 | 76.9 |
| sub-04 | 71.0 | 81.9 | 85.0 | 81.7 | 87.5 |
| sub-05 | 71.0 | 84.8 | 88.6 | 81.3 | 91.5 |
| sub-06 | 71.0 | 76.3 | 78.9 | 78.7 | 83.5 |
| sub-07 | 71.1 | 77.4 | 81.4 | 78.1 | 86.4 |
| sub-08 | 66.4 | 81.2 | 85.2 | 76.8 | 87.4 |
| sub-09 | 69.2 | 79.8 | 84.4 | 76.7 | 86.4 |
| sub-10 | 64.9 | 79.7 | 81.5 | 75.5 | 83.2 |
| sub-11 | 71.3 | 74.9 | 80.5 | 77.8 | 82.3 |
| sub-12 | 73.3 | 83.4 | 84.8 | 82.5 | 88.7 |
| sub-13 | 74.0 | 80.2 | 83.1 | 78.6 | 86.8 |
| sub-14 | 62.6 | 81.9 | 86.7 | 74.4 | 86.6 |
| sub-15 | 66.4 | 90.3 | 92.2 | 79.6 | 93.7 |
| sub-16 | 75.4 | 88.4 | 90.8 | 83.0 | 91.6 |
