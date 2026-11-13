# Real data: subject 01, preliminary results (13 Nov 2026)

> **Correction (pipeline v1.2, 13 Nov evening):** an indexing error in the inner cross-validation of `classical_models.py` (v1.0/v1.1) made the **switch results below invalid** (confidence, learned gate, subject-level). They are struck through and will be recomputed with v1.2. The EEG, MEG, early-fusion and late-fusion results are not affected. See `code/pipeline/CHANGELOG.md`.

> **One subject only. No conclusion can be drawn.** Group statistics will be computed on the 16 subjects with `aggregate.py`.
> Source: console output on the server (screenshots of 13 Nov). The raw JSON files are on the server in `$WORK/results/classical/<task>/sub-01.json`; copy them here with `code/tools/sync_from_server.ps1`.

## 1. Preprocessing (code v1.1)

| Item | Value |
|---|---|
| Runs | 6 (146, 148, 150, 147, 148, 148 stimuli) |
| MEG bad channels (SSS detection) | none |
| EEG bad channels interpolated | EEG002, EEG004 (most runs), EEG070 (run 1): **3** |
| ICA, MEG | 40 components, removed 4 (ocular + cardiac) |
| ICA, EEG | 30 components, removed 4 (ocular + cardiac) |
| Trials kept | **879 / 887** (0.9% rejected): 292 famous, 293 unfamiliar, 294 scrambled |
| Channels | 70 EEG, 102 magnetometers, 204 gradiometers |
| Duration | 7.5 min |

The v1.0 run of the same subject (before the fixes) interpolated 6 frontal EEG channels and kept 880/887 trials.

## 2. Classical models: balanced accuracy (leave-one-run-out, 6 folds)

| Model | Faces vs scrambled | Famous vs unfamiliar |
|---|---|---|
| EEG | 61.3% | 48.2% |
| MEG | 80.7% | 55.6% |
| **Early fusion** | **87.9%** | **58.1%** |
| Late fusion | 76.7% | 53.5% |
| ~~Switch: learned gate~~ | ~~79.3%~~ (invalid, to recompute) | ~~56.9%~~ (invalid, to recompute) |

**Accuracy per fold, faces vs scrambled:**

| Test run | EEG | MEG | Fused | ~~Learned gate~~ (invalid) |
|---|---|---|---|---|
| 1 | 0.603 | 0.829 | 0.925 | ~~0.705~~ |
| 2 | 0.685 | 0.849 | 0.897 | ~~0.884~~ |
| 3 | 0.644 | 0.799 | 0.859 | ~~0.779~~ |
| 4 | 0.648 | 0.807 | 0.876 | ~~0.807~~ |
| 5 | 0.630 | 0.815 | 0.863 | ~~0.829~~ |
| 6 | 0.646 | 0.782 | 0.871 | ~~0.850~~ |

**Accuracy per fold, famous vs unfamiliar:**

| Test run | EEG | MEG | Fused | ~~Learned gate~~ (invalid) |
|---|---|---|---|---|
| 1 | 0.479 | 0.615 | 0.573 | ~~0.510~~ |
| 2 | 0.551 | 0.561 | 0.612 | ~~0.571~~ |
| 3 | 0.414 | 0.556 | 0.566 | ~~0.556~~ |
| 4 | 0.417 | 0.479 | 0.542 | ~~0.531~~ |
| 5 | 0.490 | 0.551 | 0.582 | ~~0.653~~ |
| 6 | 0.541 | 0.571 | 0.571 | ~~0.612~~ |

These per-fold numbers are plain accuracy, as printed by the script; the table above it is balanced accuracy over all folds.

## 3. Deep model: smoke test only

EEGNet on GPU 0 (L40S), faces vs scrambled, 1 fold (test run 1), 3 epochs:
EEG 0.610, MEG 0.829, fused 0.842, late fusion 0.856, gate 0.815, in 0.1 min.
This only checks that the code runs. With 3 epochs the numbers are not meaningful.

## 4. First observations (to be checked on 16 subjects)

1. **MEG ≫ EEG for this subject.** EEG decodes faces vs scrambled at 61% and famous vs unfamiliar at chance level.
2. **Early fusion is the best model in both tasks**, even with weak EEG. EEG adds information when combined at the channel level.
3. **Late fusion falls below MEG alone** (76.7% vs 80.7%). Summing a weak modality with equal weight hurts. This is the situation adaptive weighting is meant to fix, and it should be tested on all subjects.
4. ~~The learned gate result~~: invalid (v1.1 indexing error), to be recomputed with v1.2.
5. **Points to check if EEG stays weak for most subjects:**
   - the EEG reference and the bad channels;
   - the features (EEG N170 is at occipito-temporal sites; the window-mean features cover it);
   - whether the 0.1 Hz high-pass and baseline are appropriate.
