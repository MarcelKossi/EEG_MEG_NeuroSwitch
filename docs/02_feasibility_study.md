# 02: Feasibility study (2 Nov 2026)

**Goal:** before spending server time, check whether a switching model *can* beat EEG-only, MEG-only and fusion, and whether EEG and MEG make **complementary** errors.

**Code:** `code/feasibility_simulation/sim_switch.py` (simulation and models) and `analyze.py` (statistics).
**Raw results:** `results/feasibility_simulation/raw/` (`res_<scenario>.json`, `log_<scenario>.txt`).

> These are **simulated** data on a real head model, **not real recordings**. Always label them as such.

## 1. Design

| Element | Choice |
|---|---|
| Head model | Real simultaneous MEG+EEG forward model of the MNE `sample` subject: BEM, 305 MEG + 59 EEG channels, 7,928 cortical sources with fixed orientation, EEG average reference |
| Noise | **Real recorded joint MEG/EEG noise covariance**, including real cross-modality noise correlation; temporally coloured (AR 0.85) |
| Subjects | 16 simulated subjects × 300 trials (150 per class) |
| Signal | For each subject, a class-discriminative cortical patch (8 mm radius) at a **random location**, hence random orientation and depth. A Gaussian evoked response peaks at 170 ms, with trial-to-trial amplitude and latency jitter. Three extra non-discriminative evoked patches appear in both classes. |
| Source strength | 150 nAm (calibrated so that accuracies fall in a realistic 55–95% range) |
| Scenarios | **clean**; **low signal** (80 nAm); **20%** and **40% bad trials** (independent modality-specific artifacts with 6× amplitude, random-walk time course) |
| Features | Mean amplitude in 8 windows of 50 ms (0–400 ms) per channel |
| Classifier (all experts) | StandardScaler → PCA (40 components for EEG and MEG, 80 for fused) → shrinkage LDA |
| Validation | 5-fold stratified CV per subject. The gate is trained on **inner** out-of-fold predictions, so test labels are never used. |
| Models | EEG, MEG, early fusion, late fusion (summed log-odds), switch by confidence, switch by learned gate (confidences + baseline log-power per modality), subject-level switch, oracle (EEG/MEG and 3-way) |
| Statistics | Paired Wilcoxon signed-rank tests across the 16 subjects |

## 2. Results: mean accuracy % ± SD (16 subjects)

| Model | Clean | Low signal | 20% bad trials | 40% bad trials |
|---|---|---|---|---|
| EEG only | 71.2 ± 11.0 | 62.5 ± 7.9 | 69.7 ± 11.6 | 68.2 ± 11.6 |
| MEG only | 74.0 ± 13.3 | 64.6 ± 13.0 | 73.7 ± 13.0 | 77.9 ± 12.5 |
| Early fusion | 80.6 ± 9.9 | 69.5 ± 13.7 | 77.7 ± 10.8 | 79.7 ± 12.3 |
| Late fusion | 78.6 ± 10.5 | 67.8 ± 12.4 | 77.9 ± 9.9 | 78.3 ± 11.0 |
| Switch: confidence | 79.9 ± 10.1 | 68.9 ± 12.8 | 79.2 ± 9.4 | 79.5 ± 11.3 |
| **Switch: learned gate** | **80.8 ± 9.8** | **69.3 ± 12.9** | **80.5 ± 9.6** | **80.5 ± 12.2** |
| Best single modality per subject (picked with hindsight) | 79.0 | 66.5 | 78.6 | 79.1 |
| Oracle EEG/MEG (upper bound only) | 90.9 ± 5.3 | 85.1 ± 6.7 | 91.2 ± 5.2 | 91.6 ± 5.4 |
| Oracle 3-way (upper bound only) | 93.2 ± 4.2 | 88.4 ± 5.8 | 93.9 ± 3.8 | 93.8 ± 4.1 |
| *Chance-level oracle* 1 − (1 − acc_EEG)(1 − acc_MEG) | *92.0* | *85.8* | *91.7* | *92.1* |

### Learned gate vs each baseline (mean difference in points, Wilcoxon p)

| Comparison | Clean | Low signal | 20% bad | 40% bad |
|---|---|---|---|---|
| vs EEG | +9.5 (p = 0.0007) | +6.8 (p = 0.003) | +10.8 (p = 0.003) | +12.3 (p = 0.0009) |
| vs MEG | +6.8 (p = 0.008) | +4.7 (p = 0.001) | +6.8 (p = 0.0006) | +2.6 (p = 0.033) |
| vs early fusion | +0.2 (p = 0.88) | −0.2 (p = 0.27) | +2.8 (p = 0.13) | +0.8 (p = 0.49) |
| vs late fusion | +2.2 (p = 0.002) | +1.5 (p = 0.13) | +2.5 (p = 0.0007) | +2.2 (p = 0.017) |

### Other indicators

| Indicator | Clean | Low signal | 20% bad | 40% bad |
|---|---|---|---|---|
| Subjects where EEG > MEG | 7/16 | 5/16 | 5/16 | 2/16 |
| Trials only EEG correct | 17.0% | 20.5% | 17.5% | 13.6% |
| Trials only MEG correct | 19.7% | 22.7% | 21.5% | 23.4% |
| Gate choices EEG / MEG / fused | 25 / 24 / 52% | 24 / 27 / 49% | 29 / 25 / 46% | 20 / 34 / 46% |

## 3. Head-model physics check

| Source orientation | N sources | MEG has the better whitened signal |
|---|---|---|
| Tangential (radiality < 0.3) | 2,926 | 66% |
| Intermediate (0.3–0.7) | 2,994 | 54% |
| Radial (> 0.7) | 2,008 | **20%** |

- Correlation of radiality with log(MEG/EEG signal): ρ = −0.39.
- Correlation of depth with log(MEG/EEG signal): **ρ = −0.56** (deeper favours EEG).
- At the **subject level**, with 16 subjects, the MEG–EEG accuracy difference did **not** significantly follow patch radiality or depth (|ρ| ≤ 0.16). The "why" analysis will need source-level work, not only sensor-level accuracy.

## 4. Lessons

1. **H1 supported:** the switch beats EEG-only (+6.8 to +12.3 points) and MEG-only (+2.6 to +6.8) in every scenario.
2. **H2 mostly supported:** the switch beats late fusion by +1.5 to +2.5 points, significant in 3 of 4 scenarios.
3. **No win over early fusion:** −0.2 to +2.8 points, never significant. Early fusion can already weigh both modalities.
4. **The oracle is misleading.** Its ~10-point lead is almost exactly what two classifiers with **independent** errors would reach by luck (90.9% observed vs 92.0% expected). EEG and MEG errors are different but mostly **unpredictable**, so a realistic gate cannot exploit them. The oracle must always be reported next to its chance level.
5. **Robustness is the most promising angle.** The gate's margin over late fusion and MEG is largest with corrupted trials.

**Decision:** frame the paper around **robust adaptive fusion** and **interpretability**, and treat "beats early fusion" as an open question for real data.

## 5. Limitations

- One head model (one anatomy), so between-subject anatomical variability is only approximated by moving the source.
- Simplified artifact model; real blinks, muscle and head movement are more structured. That could help or hurt the gate.
- Linear classifiers only. A deep gate could extract more, although lesson 4 limits how much is available.
