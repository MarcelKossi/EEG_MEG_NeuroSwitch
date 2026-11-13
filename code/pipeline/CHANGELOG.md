# Pipeline changelog

## v1.2: 13 Nov 2026 (current)

**Correction** (`classical_models.py`)
- In the inner leave-one-run-out loop that produces the held-out predictions for the switch gates, features were indexed with positions relative to the training subset while the label vector was the training subset. Features and labels therefore did not correspond.
- Fixed: `fit_predict(feats[m][tr], y[tr], itr, ite)`.
- **Affected:** the classical switch results (confidence, learned gate, subject-level), so results produced with v1.0/v1.1 must be recomputed.
- **Not affected:** the EEG, MAG, GRAD, MEG, early-fusion and late-fusion results, and `deep_models.py`.

**Additions**
- `common.corrupt()` and the options `--corrupt eeg|meg|both`, `--corrupt-rate`, `--corrupt-gain`, `--corrupt-seed` in `classical_models.py`, `deep_models.py` and `cross_subject.py` (robustness experiment, hypothesis H3). The corruption settings and the number of corrupted trials are saved in each result file.
- `cross_subject.py`: leave-one-subject-out validation with per-subject feature standardisation, and gates trained on grouped out-of-fold predictions.
- `LearnedGate.scores()`: returns the predicted correctness of each expert, for the gate analyses.

## v1.1: 13 Nov 2026

`preprocess.py`

1. **Fixed head-frame origin (0, 0, 0.04) m.** It is used for `find_bad_channels_maxwell`, `maxwell_filter` and the EEG `interpolate_bads`.
   - *Why:* the automatic sphere fit put the head centre 37 mm too far forward ("(X, Y) fit (3.3, 36.9) more than 20 mm from head frame origin"), which can degrade SSS at the back of the head.
2. **Robust EEG bad-channel detection.** Amplitude is now 1.4826 × the median absolute deviation instead of the standard deviation.
   - *Why:* blinks inflated the variance of the frontal electrodes, so six frontal channels (EEG002 and EEG004–008) were interpolated in sub-01.
   - *After the fix:* EEG002, EEG004 and EEG070 are interpolated.

Check which version is on the server:

```bash
grep -c "origin=(0.0, 0.0, 0.04)" preprocess.py        # 3  (v1.1 or later)
grep -c "robust to blinks" preprocess.py               # 1  (v1.1 or later)
grep -c "feats\[m\]\[tr\]" classical_models.py        # 1  (v1.2)
ls cross_subject.py                                    # present in v1.2
```

## v1.0: 9 Nov 2026

First version:
- preprocessing (SSS, EEG interpolation and average reference, 0.1–40 Hz, 200 Hz, per-modality ICA, epochs, rejection);
- classical LDA models with a lossless PCA rotation for speed;
- EEGNet deep models;
- aggregation (Wilcoxon + Holm, chance-level oracle).

Validated on a mock BIDS dataset derived from the MNE sample recording, and on synthetic data of the real size.
