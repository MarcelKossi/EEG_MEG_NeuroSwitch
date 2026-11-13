# Feasibility simulation: results summary (2 Nov 2026)

**Simulated** data on a real MEG+EEG head model with real noise: 16 subjects × 300 trials, accuracy in %.
Full design and discussion: `docs/02_feasibility_study.md`. Raw per-subject data: `raw/res_<scenario>.json`; console output: `raw/log_<scenario>.txt`.

| Model | Clean | Low signal | 20% bad trials | 40% bad trials |
|---|---|---|---|---|
| EEG only | 71.2 | 62.5 | 69.7 | 68.2 |
| MEG only | 74.0 | 64.6 | 73.7 | 77.9 |
| Early fusion | 80.6 | 69.5 | 77.7 | 79.7 |
| Late fusion | 78.6 | 67.8 | 77.9 | 78.3 |
| Switch: confidence | 79.9 | 68.9 | 79.2 | 79.5 |
| **Switch: learned gate** | **80.8** | **69.3** | **80.5** | **80.5** |
| Oracle EEG/MEG (upper bound) | 90.9 | 85.1 | 91.2 | 91.6 |
| Chance-level oracle (independent errors) | 92.0 | 85.8 | 91.7 | 92.1 |

**Learned gate minus baseline**, in points (Wilcoxon p across 16 subjects):

| Baseline | Clean | Low signal | 20% bad | 40% bad |
|---|---|---|---|---|
| EEG | +9.5 (0.0007) | +6.8 (0.003) | +10.8 (0.003) | +12.3 (0.0009) |
| MEG | +6.8 (0.008) | +4.7 (0.001) | +6.8 (0.0006) | +2.6 (0.033) |
| Early fusion | +0.2 (0.88) | −0.2 (0.27) | +2.8 (0.13) | +0.8 (0.49) |
| Late fusion | +2.2 (0.002) | +1.5 (0.13) | +2.5 (0.0007) | +2.2 (0.017) |

**Bottom line:**
- The switch beats both single modalities and late fusion.
- It **ties with early fusion**.
- The oracle's lead is chance-level.
