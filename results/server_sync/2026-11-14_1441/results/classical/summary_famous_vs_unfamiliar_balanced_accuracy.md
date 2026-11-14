## famous_vs_unfamiliar

Subjects: 16  |  metric: balanced_accuracy  |  method: classical-LDA

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 53.2 | 3.5 | 48.2 | 60.3 |
| MAG | 54.1 | 3.6 | 48.2 | 59.3 |
| GRAD | 56.3 | 3.5 | 50.1 | 60.6 |
| MEG | 56.1 | 3.5 | 49.9 | 60.6 |
| Early fusion | 57.4 | 2.8 | 50.2 | 61.3 |
| Late fusion | 56.2 | 4.3 | 49.6 | 62.8 |
| Switch: confidence | 56.7 | 4.0 | 49.5 | 63.5 |
| Switch: learned gate | 57.0 | 2.9 | 51.4 | 61.2 |
| Switch: subject-level | 57.1 | 3.2 | 49.9 | 61.1 |
| Oracle EEG/MEG (upper bound, not a result) | 78.4 | 2.7 | 74.0 | 82.2 |
| Oracle 3-way (upper bound, not a result) | 82.5 | 2.2 | 77.7 | 86.4 |

Oracle EEG/MEG accuracy 78.4% vs 79.4% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +3.57 | 14/16 | 0.0017 | 0.0067 |
| Switch: confidence | MEG | +0.64 | 8/16 | 0.3755 | 0.7509 |
| Switch: confidence | Early fusion | -0.61 | 7/16 | 0.4637 | 0.7509 |
| Switch: confidence | Late fusion | +0.59 | 11/16 | 0.0309 | 0.0927 |
| Switch: learned gate | EEG | +3.87 | 14/16 | 0.0006 | 0.0023 |
| Switch: learned gate | MEG | +0.94 | 11/16 | 0.0443 | 0.1329 |
| Switch: learned gate | Early fusion | -0.31 | 5/16 | 0.4332 | 0.4332 |
| Switch: learned gate | Late fusion | +0.89 | 12/16 | 0.1046 | 0.2092 |
| Switch: subject-level | EEG | +3.95 | 14/16 | 0.0010 | 0.0040 |
| Switch: subject-level | MEG | +1.02 | 9/16 | 0.3066 | 0.6627 |
| Switch: subject-level | Early fusion | -0.23 | 4/16 | 0.2209 | 0.6627 |
| Switch: subject-level | Late fusion | +0.97 | 10/16 | 0.2522 | 0.6627 |

Learned gate choices (share of test trials): eeg 24%, meg 33%, fused 43%
Trials only EEG correct: 22.3%  |  only MEG correct: 25.3%
Subjects where EEG beats MEG: 4/16

Per subject (balanced_accuracy, %):

| Subject | EEG | MEG | Early fusion | Late fusion | Switch: learned gate |
|---|---|---|---|---|---|
| sub-01 | 48.2 | 55.6 | 58.1 | 53.5 | 57.8 |
| sub-02 | 53.0 | 60.6 | 60.6 | 61.3 | 59.3 |
| sub-03 | 52.4 | 49.9 | 50.2 | 49.9 | 51.4 |
| sub-04 | 55.3 | 57.8 | 55.8 | 58.4 | 59.3 |
| sub-05 | 50.9 | 50.6 | 58.8 | 53.0 | 55.9 |
| sub-06 | 55.1 | 58.2 | 58.8 | 57.4 | 59.6 |
| sub-07 | 54.5 | 57.7 | 56.7 | 56.0 | 56.5 |
| sub-08 | 48.4 | 53.7 | 54.9 | 52.5 | 53.9 |
| sub-09 | 49.3 | 52.8 | 56.1 | 49.6 | 52.3 |
| sub-10 | 49.3 | 52.7 | 55.5 | 49.7 | 53.4 |
| sub-11 | 54.1 | 53.9 | 57.2 | 55.4 | 56.1 |
| sub-12 | 50.4 | 60.4 | 60.2 | 60.0 | 59.3 |
| sub-13 | 60.3 | 54.5 | 54.0 | 57.6 | 58.0 |
| sub-14 | 56.4 | 59.8 | 58.8 | 60.9 | 61.2 |
| sub-15 | 54.3 | 59.1 | 61.3 | 60.6 | 59.2 |
| sub-16 | 58.9 | 60.3 | 60.7 | 62.8 | 59.4 |
