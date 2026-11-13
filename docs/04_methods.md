# 04: Methods (draft for the paper)

This text describes exactly what `code/pipeline/` v1.2 does. Parameters in **bold** are those a reviewer is most likely to ask about.

## 2.1 Data

We used the publicly available simultaneous MEG/EEG recordings of OpenNeuro ds000117 v2.0.0 (Wakeman & Henson, 2015):
- 16 participants viewed famous, unfamiliar and scrambled faces in 6 runs each;
- 306-channel Elekta Neuromag VectorView MEG (102 magnetometers, 204 planar gradiometers) and 70 EEG electrodes, sampled at 1,100 Hz;
- vertical and horizontal EOG, and ECG, recorded alongside.

Events were taken from the BIDS `events.tsv` files (trigger codes 5–7 famous, 13–15 unfamiliar, 17–19 scrambled). Responses were ignored. Latencies are relative to the trigger; a constant stimulus-presentation delay, if any, does not affect decoding.

## 2.2 Preprocessing (`preprocess.py`, MNE-Python 1.13)

Each run was processed separately until ICA.

1. **Channel information** (names, types, bad-channel status) was taken from the BIDS `channels.tsv`.
2. **MEG.**
   - Flat and noisy MEG channels were detected with `find_bad_channels_maxwell`.
   - The data were then cleaned by **Maxwell filtering (SSS)**, using the subject's fine-calibration and cross-talk files and a **fixed expansion origin of (0, 0, 40) mm in head coordinates**. Bad channels were reconstructed.
   - Every run was transformed to the **head position of the first run**, so a given MEG sensor carries the same meaning in all runs.
   - Temporal SSS and movement compensation were not applied.
3. **Filtering and resampling.**
   - All channels were band-pass filtered at **0.1–40 Hz** (zero-phase FIR, MNE defaults).
   - The data were resampled to **200 Hz**; event samples were resampled jointly with the data.
4. **EEG.**
   - Flat or persistently noisy electrodes were detected per run: a robust z-score of the log median-absolute-deviation amplitude, with **|z| > 5**, or an amplitude below 10⁻³ of the median. This measure is insensitive to brief blinks.
   - The **union of bad electrodes across runs** was interpolated with spherical splines in every run, so all runs share the same electrode set.
   - The EEG was then re-referenced to the **common average**.
5. **Artifact correction: ICA, separately per modality.**
   - FastICA was fitted on the 1-Hz high-passed concatenation of all runs: **40 components for MEG and 30 for EEG**, in two independent decompositions.
   - Ocular components were identified by correlation with EOG061/EOG062, and cardiac components by cross-trial phase statistics with ECG063. At most 4 components were removed per artifact type.
   - **ICA was never fitted on EEG and MEG together.** Removing a joint component would mix information from both modalities into the "EEG-only" and "MEG-only" data.
6. **Epoching.**
   - Epochs ran from **−0.2 to 0.8 s** around stimulus onset, with baseline correction (−0.2 to 0 s).
   - Epochs were rejected if the peak-to-peak amplitude exceeded **4,000 fT/cm (gradiometers), 4,000 fT (magnetometers) or 150 µV (EEG)**.
   - A rejected epoch was removed **for all modalities**, so all models are compared on identical trials.

The output per subject is an array of n trials × 376 channels (70 EEG, 102 magnetometers, 204 gradiometers) × 201 samples, with condition, repetition and run labels.

## 2.3 Decoding tasks

- **Faces vs scrambled:** famous and unfamiliar faces vs scrambled faces (about 2:1 imbalance).
- **Famous vs unfamiliar:** scrambled trials excluded (balanced).

## 2.4 Experts

Five single-model "experts" share **one architecture and one training procedure**; only the input channels differ:

| Expert | Channels |
|---|---|
| EEG | 70 |
| MAG | 102 |
| GRAD | 204 |
| MEG | 306 |
| Fused (early fusion) | 376 |

**Classical experts** (`classical_models.py`):
- **Features:** mean amplitude in **16 windows of 50 ms from 0 to 800 ms**, per channel.
- **Classifier:** standardisation, then a lossless PCA rotation (all components kept, for speed), then **shrinkage LDA** (Ledoit–Wolf, equal class priors).

**Deep experts** (`deep_models.py`):
- **Model:** **EEGNet-8,2** (Lawhern et al., 2018): temporal kernel 64 samples, dropout 0.5.
- **Input:** epochs z-scored per channel using training-set statistics. This also equalises the units of EEG, magnetometers and gradiometers.
- **Training:** AdamW (learning rate 10⁻³, weight decay 10⁻³), batch size 64, class-weighted cross-entropy, at most 200 epochs, **early stopping** (patience 25) on validation loss.

## 2.5 Fusion and switching models

- **Early fusion:** the fused expert (all 376 channels in one model).
- **Late fusion:** the EEG and MEG experts' log-odds are summed. This is a confidence-weighted combination of the two modalities' outputs.
- **Switch: confidence.** For each trial, the expert among {EEG, MEG, fused} with the highest confidence |p − 0.5| is used.
- **Switch: learned gate.**
  - For each expert, a logistic regression predicts whether that expert will be correct, from (i) the confidences of the three experts and (ii) six label-free signal-quality features: per modality (EEG, MAG, GRAD), the log median baseline standard deviation and the log maximum peak-to-peak amplitude of the trial.
  - The expert with the highest predicted probability of being correct is used.
- **Switch: subject level.** The expert with the best balanced accuracy on held-out training data is used for all test trials of that subject.
- **Oracle** (upper bound only): a trial counts as correct if *any* expert is correct (EEG/MEG, and EEG/MEG/fused). We report it next to the accuracy expected if the experts' errors were independent: 1 − (1 − acc_EEG)(1 − acc_MEG).

## 2.6 Validation

**Within subject.**
- **Leave-one-run-out cross-validation** (6 folds): trials from the same run are never split between training and testing.
- **Gates never see test labels.**
  - In the classical pipeline, the gates and the subject-level choice are trained on **inner** leave-one-run-out predictions within the 5 training runs.
  - In the deep pipeline, 4 runs train the experts. The 5th run (rotating across folds) is used for early stopping and to train the gates. The 6th run is the test run.

**Across subjects** (`cross_subject.py`).
- **Leave-one-subject-out:** the classical experts are trained on all trials of the other 15 subjects.
- **Per-subject alignment:** each feature is z-scored within each subject. This uses no labels and compensates for differences in head position and signal amplitude between subjects.
- **Gates:** the gates and the subject-level choice are trained on out-of-fold predictions from a 3-fold split of the training subjects, grouped by subject.
- **Channels:** only channels present in every subject are used.

## 2.6b Robustness to a corrupted modality

To test H3, one modality (EEG, MEG, or both independently) is corrupted on a random fraction of trials (20% or 40%) before feature extraction:
- **Artifact:** a slowly varying, random-walk time course with a random spatial pattern, added to all channels of that modality.
- **Amplitude:** 5 times each channel's median trial standard deviation.
- **Pairing:** the same trials are corrupted for every model, and the corruption is the same in training and test data.
- All models are then compared exactly as in 2.5–2.7.

## 2.7 Metrics and statistics

- **Primary metric:** balanced accuracy, because of the 2:1 imbalance in faces vs scrambled.
- **Also reported:** accuracy and ROC AUC; the gate's choice frequencies; and the proportion of trials that only EEG or only MEG classified correctly.
- **Statistical test:** each switching model is compared with EEG, MEG, early fusion and late fusion using **paired two-sided Wilcoxon signed-rank tests across the 16 subjects**, with Holm correction across the four comparisons of each switching model.

## 2.8 Software and hardware

| Item | Version or detail |
|---|---|
| Python | 3.12.3 |
| MNE-Python | 1.13.2 |
| mne-bids | 0.20.0 |
| NumPy | 2.5.4 |
| scikit-learn | 1.9.1 |
| PyTorch | 2.14.1 (CUDA 12.6) |
| braindecode | 2.0.0 (installed, not used by the models) |
| pandas | 3.1.1 |
| Server | Dell PowerEdge R760XA, 128 CPU cores, 503 GB RAM, NVIDIA L40S (46 GB) |

## Planned additions (not yet implemented)

- **Interpretability:** relate gate choices to trial-level signal quality and, across subjects, to source orientation and depth (source-level analysis using the participants' MRI).
