## faces_vs_scrambled

Subjects: 11  |  metric: balanced_accuracy  |  method: classical-LDA

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 69.9 | 5.5 | 60.8 | 78.2 |
| MAG | 76.4 | 3.5 | 70.0 | 82.7 |
| GRAD | 78.7 | 3.9 | 71.8 | 85.1 |
| MEG | 78.5 | 3.6 | 72.1 | 84.8 |
| Early fusion | 85.8 | 4.0 | 76.4 | 90.5 |
| Late fusion | 80.8 | 4.2 | 73.3 | 86.9 |
| Switch: confidence | 82.9 | 4.0 | 75.7 | 89.1 |
| Switch: learned gate | 86.1 | 4.2 | 76.6 | 92.1 |
| Switch: subject-level | 85.8 | 4.0 | 76.4 | 90.5 |
| Oracle EEG/MEG (upper bound, not a result) | 93.0 | 1.9 | 88.9 | 96.5 |
| Oracle 3-way (upper bound, not a result) | 96.3 | 1.6 | 91.9 | 98.5 |

Oracle EEG/MEG accuracy 93.7% vs 94.1% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +12.98 | 11/11 | 0.0010 | 0.0039 |
| Switch: confidence | MEG | +4.35 | 9/11 | 0.0068 | 0.0137 |
| Switch: confidence | Early fusion | -2.90 | 2/11 | 0.0068 | 0.0137 |
| Switch: confidence | Late fusion | +2.10 | 11/11 | 0.0010 | 0.0039 |
| Switch: learned gate | EEG | +16.25 | 11/11 | 0.0010 | 0.0039 |
| Switch: learned gate | MEG | +7.61 | 11/11 | 0.0010 | 0.0039 |
| Switch: learned gate | Early fusion | +0.36 | 7/11 | 0.4131 | 0.4131 |
| Switch: learned gate | Late fusion | +5.36 | 11/11 | 0.0010 | 0.0039 |
| Switch: subject-level | EEG | +15.89 | 11/11 | 0.0010 | 0.0039 |
| Switch: subject-level | MEG | +7.26 | 11/11 | 0.0010 | 0.0039 |
| Switch: subject-level | Early fusion | +0.00 | 0/11 | nan | nan |
| Switch: subject-level | Late fusion | +5.00 | 11/11 | 0.0010 | 0.0039 |

Learned gate choices (share of test trials): eeg 16%, meg 20%, fused 64%
Trials only EEG correct: 14.2%  |  only MEG correct: 22.3%
Subjects where EEG beats MEG: 1/11

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
