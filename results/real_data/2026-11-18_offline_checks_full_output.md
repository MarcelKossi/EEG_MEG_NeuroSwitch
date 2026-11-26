# Full output of offline_checks.py (18 Nov 2026)

Command (run on the result files of 14 Nov, now in `results/raw/`): `python offline_checks.py --results results/raw --exclude 16`

Interpretation: `2026-11-18_offline_checks.md`.

## Sensitivity analysis: subjects excluded [16]

### classical / faces_vs_scrambled

Subjects: 15

| Model | Mean (%) | SD |
|---|---|---|
| EEG | 70.5 | 5.1 |
| MAG | 77.9 | 4.5 |
| GRAD | 80.1 | 4.6 |
| MEG | 80.0 | 4.4 |
| Early fusion | 87.1 | 4.4 |
| Late fusion | 81.7 | 4.0 |
| Switch: confidence | 83.9 | 4.0 |
| Switch: learned gate | 87.4 | 4.4 |
| Switch: subject-level | 87.1 | 4.4 |

| Switch | vs | Mean diff | Wins | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +13.37 | 15/15 | 0.0001 | 0.0002 |
| Switch: confidence | MEG | +3.95 | 12/15 | 0.0012 | 0.0012 |
| Switch: confidence | Early fusion | -3.20 | 2/15 | 0.0006 | 0.0012 |
| Switch: confidence | Late fusion | +2.26 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | EEG | +16.83 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | MEG | +7.41 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | Early fusion | +0.26 | 8/15 | 0.6387 | 0.6387 |
| Switch: learned gate | Late fusion | +5.72 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | EEG | +16.57 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | MEG | +7.14 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | Early fusion | +0.00 (identical) | 0/15 | 1.0000 | 1.0000 |
| Switch: subject-level | Late fusion | +5.46 | 15/15 | 0.0001 | 0.0002 |

### classical / famous_vs_unfamiliar

Subjects: 15

| Model | Mean (%) | SD |
|---|---|---|
| EEG | 52.8 | 3.3 |
| MAG | 54.0 | 3.6 |
| GRAD | 56.1 | 3.5 |
| MEG | 55.8 | 3.4 |
| Early fusion | 57.1 | 2.8 |
| Late fusion | 55.7 | 4.0 |
| Switch: confidence | 56.3 | 3.7 |
| Switch: learned gate | 56.9 | 2.9 |
| Switch: subject-level | 57.1 | 3.3 |

| Switch | vs | Mean diff | Wins | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +3.50 | 13/15 | 0.0034 | 0.0134 |
| Switch: confidence | MEG | +0.47 | 7/15 | 0.5995 | 0.6056 |
| Switch: confidence | Early fusion | -0.83 | 6/15 | 0.3028 | 0.6056 |
| Switch: confidence | Late fusion | +0.58 | 10/15 | 0.0480 | 0.1440 |
| Switch: learned gate | EEG | +4.09 | 13/15 | 0.0006 | 0.0024 |
| Switch: learned gate | MEG | +1.06 | 11/15 | 0.0256 | 0.0767 |
| Switch: learned gate | Early fusion | -0.24 | 5/15 | 0.5614 | 0.5614 |
| Switch: learned gate | Late fusion | +1.17 | 12/15 | 0.0302 | 0.0767 |
| Switch: subject-level | EEG | +4.28 | 14/15 | 0.0006 | 0.0024 |
| Switch: subject-level | MEG | +1.24 | 9/15 | 0.1401 | 0.3210 |
| Switch: subject-level | Early fusion | -0.06 | 4/15 | 0.3454 | 0.3454 |
| Switch: subject-level | Late fusion | +1.35 | 10/15 | 0.1070 | 0.3210 |

### deep / faces_vs_scrambled

Subjects: 15

| Model | Mean (%) | SD |
|---|---|---|
| EEG | 81.1 | 3.8 |
| MEG | 87.8 | 4.1 |
| Early fusion | 88.7 | 4.4 |
| Late fusion | 91.1 | 3.3 |
| Switch: confidence | 91.4 | 3.3 |
| Switch: learned gate | 90.5 | 3.8 |
| Switch: subject-level | 88.9 | 4.1 |

| Switch | vs | Mean diff | Wins | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +10.27 | 15/15 | 0.0001 | 0.0002 |
| Switch: confidence | MEG | +3.54 | 15/15 | 0.0001 | 0.0002 |
| Switch: confidence | Early fusion | +2.71 | 15/15 | 0.0001 | 0.0002 |
| Switch: confidence | Late fusion | +0.27 | 10/15 | 0.1354 | 0.1354 |
| Switch: learned gate | EEG | +9.33 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | MEG | +2.60 | 14/15 | 0.0002 | 0.0004 |
| Switch: learned gate | Early fusion | +1.77 | 14/15 | 0.0001 | 0.0004 |
| Switch: learned gate | Late fusion | -0.66 | 3/15 | 0.0157 | 0.0157 |
| Switch: subject-level | EEG | +7.75 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | MEG | +1.02 | 12/15 | 0.0026 | 0.0052 |
| Switch: subject-level | Early fusion | +0.19 | 9/15 | 0.3109 | 0.3109 |
| Switch: subject-level | Late fusion | -2.24 | 0/15 | 0.0001 | 0.0002 |

### robust_eeg_0.2 / faces_vs_scrambled

Subjects: 15

| Model | Mean (%) | SD |
|---|---|---|
| EEG | 68.0 | 4.2 |
| MAG | 77.9 | 4.5 |
| GRAD | 80.1 | 4.6 |
| MEG | 80.0 | 4.4 |
| Early fusion | 83.0 | 4.5 |
| Late fusion | 77.1 | 3.6 |
| Switch: confidence | 79.3 | 3.2 |
| Switch: learned gate | 85.6 | 4.2 |
| Switch: subject-level | 82.7 | 4.7 |

| Switch | vs | Mean diff | Wins | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +11.30 | 15/15 | 0.0001 | 0.0002 |
| Switch: confidence | MEG | -0.63 | 6/15 | 0.5995 | 0.5995 |
| Switch: confidence | Early fusion | -3.70 | 1/15 | 0.0002 | 0.0004 |
| Switch: confidence | Late fusion | +2.21 | 14/15 | 0.0001 | 0.0004 |
| Switch: learned gate | EEG | +17.53 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | MEG | +5.61 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | Early fusion | +2.53 | 14/15 | 0.0001 | 0.0002 |
| Switch: learned gate | Late fusion | +8.44 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | EEG | +14.63 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | MEG | +2.70 | 14/15 | 0.0001 | 0.0002 |
| Switch: subject-level | Early fusion | -0.37 | 0/15 | 0.0117 | 0.0117 |
| Switch: subject-level | Late fusion | +5.54 | 15/15 | 0.0001 | 0.0002 |

### robust_eeg_0.4 / faces_vs_scrambled

Subjects: 15

| Model | Mean (%) | SD |
|---|---|---|
| EEG | 65.5 | 3.2 |
| MAG | 77.9 | 4.5 |
| GRAD | 80.1 | 4.6 |
| MEG | 80.0 | 4.4 |
| Early fusion | 83.6 | 4.3 |
| Late fusion | 73.1 | 3.4 |
| Switch: confidence | 74.5 | 3.5 |
| Switch: learned gate | 85.5 | 3.9 |
| Switch: subject-level | 83.2 | 4.4 |

| Switch | vs | Mean diff | Wins | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +9.01 | 15/15 | 0.0001 | 0.0002 |
| Switch: confidence | MEG | -5.44 | 0/15 | 0.0001 | 0.0002 |
| Switch: confidence | Early fusion | -9.04 | 0/15 | 0.0001 | 0.0002 |
| Switch: confidence | Late fusion | +1.42 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | EEG | +19.95 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | MEG | +5.50 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | Early fusion | +1.90 | 14/15 | 0.0002 | 0.0002 |
| Switch: learned gate | Late fusion | +12.36 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | EEG | +17.70 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | MEG | +3.25 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | Early fusion | -0.35 | 1/15 | 0.0109 | 0.0109 |
| Switch: subject-level | Late fusion | +10.11 | 15/15 | 0.0001 | 0.0002 |

### robust_meg_0.2 / faces_vs_scrambled

Subjects: 15

| Model | Mean (%) | SD |
|---|---|---|
| EEG | 70.5 | 5.1 |
| MAG | 73.0 | 4.1 |
| GRAD | 76.7 | 4.2 |
| MEG | 76.6 | 4.1 |
| Early fusion | 83.5 | 4.2 |
| Late fusion | 78.6 | 4.2 |
| Switch: confidence | 80.9 | 4.2 |
| Switch: learned gate | 84.8 | 4.1 |
| Switch: subject-level | 83.5 | 4.4 |

| Switch | vs | Mean diff | Wins | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +10.39 | 15/15 | 0.0001 | 0.0002 |
| Switch: confidence | MEG | +4.30 | 13/15 | 0.0003 | 0.0004 |
| Switch: confidence | Early fusion | -2.60 | 1/15 | 0.0002 | 0.0004 |
| Switch: confidence | Late fusion | +2.36 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | EEG | +14.28 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | MEG | +8.20 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | Early fusion | +1.30 | 13/15 | 0.0006 | 0.0006 |
| Switch: learned gate | Late fusion | +6.26 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | EEG | +12.94 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | MEG | +6.85 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | Early fusion | -0.05 | 0/15 | 0.3173 | 0.3173 |
| Switch: subject-level | Late fusion | +4.91 | 14/15 | 0.0001 | 0.0002 |

### robust_meg_0.4 / faces_vs_scrambled

Subjects: 15

| Model | Mean (%) | SD |
|---|---|---|
| EEG | 70.5 | 5.1 |
| MAG | 67.9 | 3.9 |
| GRAD | 73.3 | 3.6 |
| MEG | 73.4 | 3.7 |
| Early fusion | 80.8 | 4.4 |
| Late fusion | 76.1 | 3.6 |
| Switch: confidence | 78.5 | 3.7 |
| Switch: learned gate | 83.1 | 4.1 |
| Switch: subject-level | 80.8 | 4.5 |

| Switch | vs | Mean diff | Wins | p | p (Holm) |
|---|---|---|---|---|---|
| Switch: confidence | EEG | +7.93 | 15/15 | 0.0001 | 0.0002 |
| Switch: confidence | MEG | +5.03 | 15/15 | 0.0001 | 0.0002 |
| Switch: confidence | Early fusion | -2.37 | 1/15 | 0.0054 | 0.0054 |
| Switch: confidence | Late fusion | +2.40 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | EEG | +12.59 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | MEG | +9.69 | 15/15 | 0.0001 | 0.0002 |
| Switch: learned gate | Early fusion | +2.29 | 14/15 | 0.0002 | 0.0002 |
| Switch: learned gate | Late fusion | +7.05 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | EEG | +10.22 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | MEG | +7.32 | 15/15 | 0.0001 | 0.0002 |
| Switch: subject-level | Early fusion | -0.09 | 0/15 | 0.1797 | 0.1797 |
| Switch: subject-level | Late fusion | +4.68 | 14/15 | 0.0001 | 0.0002 |

## Above-chance test: classical / famous_vs_unfamiliar

Subjects: 16

| Model | Mean (%) | SD | Subjects > 50 % | p (one-sided) | p (Holm) |
|---|---|---|---|---|---|
| EEG | 53.2 | 3.5 | 12/16 | 0.0026 | 0.0026 |
| MAG | 54.1 | 3.6 | 14/16 | 0.0005 | 0.0010 |
| GRAD | 56.3 | 3.5 | 16/16 | 0.0000 | 0.0001 |
| MEG | 56.1 | 3.5 | 15/16 | 0.0000 | 0.0002 |
| Early fusion | 57.4 | 2.8 | 16/16 | 0.0000 | 0.0001 |
| Late fusion | 56.2 | 4.3 | 13/16 | 0.0002 | 0.0006 |
| Switch: confidence | 56.7 | 4.0 | 15/16 | 0.0000 | 0.0002 |
| Switch: learned gate | 57.0 | 2.9 | 16/16 | 0.0000 | 0.0001 |
| Switch: subject-level | 57.1 | 3.2 | 15/16 | 0.0000 | 0.0002 |

