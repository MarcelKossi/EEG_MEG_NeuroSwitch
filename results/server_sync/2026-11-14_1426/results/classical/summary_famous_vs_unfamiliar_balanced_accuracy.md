## famous_vs_unfamiliar

Subjects: 11  |  metric: balanced_accuracy  |  method: classical-LDA

| Model | Mean balanced_accuracy (%) | SD | Min | Max |
|---|---|---|---|---|
| EEG | 51.9 | 2.6 | 48.2 | 55.3 |
| MAG | 53.3 | 3.5 | 48.2 | 59.1 |
| GRAD | 55.2 | 3.4 | 50.1 | 60.6 |
| MEG | 54.9 | 3.2 | 49.9 | 60.6 |
| Early fusion | 56.6 | 2.6 | 50.2 | 60.6 |
| Late fusion | 54.2 | 3.7 | 49.6 | 61.3 |
| Switch: confidence | 55.1 | 3.5 | 49.5 | 61.4 |
| Switch: learned gate | 56.0 | 2.8 | 51.4 | 59.6 |
| Switch: subject-level | 55.7 | 2.9 | 49.9 | 60.6 |
| Oracle EEG/MEG (upper bound, not a result) | 77.5 | 2.8 | 74.0 | 82.2 |
| Oracle 3-way (upper bound, not a result) | 81.8 | 2.2 | 77.7 | 86.4 |

Oracle EEG/MEG accuracy 77.5% vs 78.2% expected if EEG and MEG errors were independent (the gap between the two = predictable complementarity).

**Paired Wilcoxon signed-rank tests across subjects** (difference in balanced_accuracy, percentage points; Holm-corrected p within each switch)

| Switch | vs | Mean diff | Wins/Subjects | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +3.19 | 10/11 | 0.0098 | 0.0391 |
| Switch: confidence | MEG | +0.19 | 5/11 | 0.9658 | 0.9658 |
| Switch: confidence | Early fusion | -1.54 | 3/11 | 0.1230 | 0.2461 |
| Switch: confidence | Late fusion | +0.82 | 8/11 | 0.0137 | 0.0410 |
| Switch: learned gate | EEG | +4.10 | 10/11 | 0.0020 | 0.0078 |
| Switch: learned gate | MEG | +1.09 | 8/11 | 0.0537 | 0.1074 |
| Switch: learned gate | Early fusion | -0.64 | 3/11 | 0.2402 | 0.2402 |
| Switch: learned gate | Late fusion | +1.73 | 10/11 | 0.0137 | 0.0410 |
| Switch: subject-level | EEG | +3.88 | 10/11 | 0.0068 | 0.0273 |
| Switch: subject-level | MEG | +0.87 | 5/11 | 0.6250 | 0.6250 |
| Switch: subject-level | Early fusion | -0.86 | 1/11 | 0.0195 | 0.0586 |
| Switch: subject-level | Late fusion | +1.51 | 7/11 | 0.2402 | 0.4805 |

Learned gate choices (share of test trials): eeg 23%, meg 33%, fused 44%
Trials only EEG correct: 22.7%  |  only MEG correct: 25.7%
Subjects where EEG beats MEG: 3/11

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
