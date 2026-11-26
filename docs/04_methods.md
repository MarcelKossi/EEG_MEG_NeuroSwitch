# 04: Materials and Methods

_Draft of the Methods section of the paper, 18 Nov 2026, updated 26 Nov 2026. It describes exactly what `code/pipeline/` v1.2 does. Author–year citations; the format will be adapted once the journal is chosen._

---

## 2.1 Overview

We compared seven ways of decoding single trials from simultaneous EEG and MEG, on the same trials, folds and participants:
- three single-modality decoders (EEG, MEG, and for reference magnetometers and gradiometers alone);
- two fixed fusion schemes (early and late fusion);
- three switching models, which select one of three experts (EEG, MEG, fused) on every trial or for every participant.

The comparison was run with two types of expert, a regularised linear classifier and a compact convolutional network, on two decoding problems. A robustness experiment then corrupted one modality on a subset of trials.

```
 raw MEG + EEG (ds000117, 16 participants, 6 runs)
        │
        ▼
 preprocessing per modality: SSS (MEG) · bad electrodes + average reference (EEG)
 · 0.1–40 Hz · 200 Hz · separate ICA for MEG and EEG · epochs −0.2 to 0.8 s
 · joint rejection (a trial is kept or dropped for both modalities)
        │
        ├── optional: corrupt EEG or MEG on 20 % / 40 % of trials (robustness experiment)
        ▼
 three experts trained on the same trials:   EEG (70 ch)   MEG (306 ch)   fused (376 ch)
 (shrinkage LDA on window means, or EEGNet)       │             │              │
        ├────────────────────────────────────────┴──────┬──────┴──────────────┘
        ▼                                                ▼
 fixed combinations                              switching models
 · early fusion = fused expert                   · confidence: most confident expert
 · late fusion = sum of EEG and MEG log-odds     · learned gate: predicted correctness from
                                                   confidences + 6 signal-quality features
                                                 · subject level: best expert on held-out data
        │                                                │
        └──────────────► balanced accuracy on the left-out run ◄──┘
                         paired Wilcoxon tests across participants, Holm correction
```

## 2.2 Dataset

We used the multi-subject, multi-modal face-processing dataset of Wakeman and Henson (2015), OpenNeuro accession ds000117, version 2.0.0.

**Participants and task.**
- Sixteen healthy adults viewed photographs of famous faces, unfamiliar faces and scrambled faces in six runs.
- Participants judged the symmetry of each image with a key press. The responses were not used here.

**Recordings.**
- MEG was recorded with an Elekta Neuromag VectorView system: 102 magnetometers and 204 planar gradiometers.
- EEG was recorded simultaneously from 70 scalp electrodes.
- Two EOG channels and one ECG channel were recorded alongside.
- All channels were sampled at 1,100 Hz.

**Data preparation.**
- We downloaded the MEG sessions of all 16 participants, together with their fine-calibration and cross-talk files.
- Events were read from the BIDS `events.tsv` files: trigger codes 5–7 for famous faces, 13–15 for unfamiliar faces and 17–19 for scrambled faces.
- The dataset marks no bad channels, so bad channels were detected automatically (Section 2.3).
- The 16 participants presented 14,157 trials in total (882–889 per participant).

## 2.3 Preprocessing

Preprocessing used MNE-Python (Gramfort et al., 2013). Each run was processed separately up to the ICA step.

**MEG.**
- Flat and noisy MEG channels were detected per run with the Maxwell-filter-based detector of MNE.
- Signal-space separation (SSS; Taulu and Kajola, 2005) was then applied with the participant's fine-calibration and cross-talk files, and bad channels were reconstructed.
- We used a fixed expansion origin of (0, 0, 40) mm in head coordinates. The sphere fitted to the digitised head points lay about 37 mm anterior to the head-frame origin, probably because of points on the nose.
- All runs were transformed to the head position of the first run, so a given MEG channel carries the same spatial meaning in every run.
- Temporal SSS and movement compensation were not applied.

**Filtering and resampling.** All channels were band-pass filtered between 0.1 and 40 Hz (zero-phase FIR filter, MNE defaults) and resampled to 200 Hz.

**EEG.**
- Bad electrodes were detected per run from a robust amplitude measure. An electrode was marked bad when the robust z-score (median and MAD across electrodes) of its log median absolute deviation exceeded 5 in absolute value, or when its amplitude was below 10⁻³ of the median.
- This criterion is insensitive to brief blinks, which would otherwise flag frontal electrodes.
- The union of bad electrodes across the six runs was interpolated with spherical splines in every run.
- The EEG was then re-referenced to the common average.

**Artifact correction.**
- Independent component analysis (FastICA) was fitted separately for MEG (40 components) and for EEG (30 components). Each fit used the concatenation of the six runs, high-pass filtered at 1 Hz.
- Ocular components were identified by correlation with the EOG channels, and cardiac components by cross-trial phase statistics with the ECG channel (Dammers et al., 2008). At most four components were removed per artifact type and modality.
- **The two decompositions were kept separate on purpose.** A component estimated jointly from EEG and MEG and then removed would carry information from one modality into the other, and the EEG-only and MEG-only decoders would no longer be strictly unimodal.

**Epoching and rejection.**
- Epochs were extracted from −0.2 to 0.8 s around image onset and baseline-corrected on −0.2 to 0 s.
- An epoch was rejected when its peak-to-peak amplitude exceeded 4,000 fT/cm on any gradiometer, 4,000 fT on any magnetometer or 150 µV on any EEG electrode.
- **A rejected epoch was removed for both modalities.** All models were therefore trained and tested on identical trials.

**Outcome.**
- 13,537 of the 14,157 trials were kept (4.4 % rejected).
- One participant (sub-16) lost 24.4 % of its trials, with no bad channel detected. We therefore repeated all comparisons without this participant (Section 2.10).
- Bad channels found:
  - in one participant (sub-03), SSS reconstructed a block of 12 MEG channels in the last run only;
  - electrodes EEG002 and EEG004 were interpolated in four participants.

Each participant's data were stored as an array of trials × 376 channels (70 EEG, 102 magnetometers, 204 gradiometers) × 201 samples, with condition and run labels.

## 2.4 Decoding problems

- **Faces vs scrambled.** Famous and unfamiliar faces (class 1) against scrambled faces (class 0). This problem has a strong evoked response and a class ratio of about 2:1.
- **Famous vs unfamiliar.** Scrambled trials were excluded. The two classes are balanced, and the neural difference is small.

## 2.5 Experts

Five experts were trained in every fold. They share one architecture and one training procedure and differ only in their input channels:

| Expert | Channels |
|---|---|
| EEG | 70 EEG |
| MAG | 102 magnetometers |
| GRAD | 204 gradiometers |
| MEG | 306 MEG |
| Fused | 376 (EEG + MEG) |

The switching models choose between the EEG, MEG and fused experts. MAG and GRAD are reported as additional single-modality baselines.

### 2.5.1 Classical experts

**Features.**
- For every channel, the mean amplitude was computed in 16 consecutive windows of 50 ms from 0 to 800 ms after image onset.
- This gives 16 × n_channels features per trial: 1,120 for EEG, 4,896 for MEG and 6,016 for the fused expert.

**Classifier.**
- Features were standardised.
- They were then rotated by a principal component analysis that kept all components. The rotation is lossless; it projects the data onto the subspace spanned by the training trials and only speeds up the next step.
- Classification used linear discriminant analysis with Ledoit–Wolf shrinkage of the covariance (Ledoit and Wolf, 2004; Blankertz et al., 2011) and equal class priors.

### 2.5.2 Deep experts

**Architecture.** We used EEGNet-8,2 (Lawhern et al., 2018), which has three parts:
- 8 temporal filters of 64 samples (320 ms);
- 2 depthwise spatial filters per temporal filter, spanning all input channels;
- a separable convolution with 16 filters of 16 samples, followed by average pooling (factors 4 and 8), dropout of 0.5, and a linear output layer with two classes.

The same architecture was used for every expert; only the number of input channels changed.

**Input.** The full epoch (−0.2 to 0.8 s, 201 samples) was given to the network. Each channel was z-scored with the mean and standard deviation of the training trials only. This also put EEG, magnetometers and gradiometers on a common scale.

**Training.**
- Optimiser: AdamW (Loshchilov and Hutter, 2019), learning rate 10⁻³, weight decay 10⁻³, batch size 64.
- Loss: cross-entropy, with class weights inversely proportional to class frequency.
- Training ran for at most 200 epochs. Early stopping used the validation loss (patience 25 epochs), and the weights with the lowest validation loss were kept.
- Random seeds were fixed per participant, fold and expert.
- Each expert was trained on one NVIDIA L40S GPU.

## 2.6 Fixed fusion schemes

**Early fusion.** The fused expert, which receives all 376 channels in a single model.

**Late fusion.** The EEG and MEG experts were trained separately, and their outputs were combined by summing their log-odds:

  p_late = σ( logit(p_EEG) + logit(p_MEG) ),

where p is the predicted probability of class 1 and σ the logistic function. This is the product-of-experts rule for two experts with independent errors. It weights each modality by its confidence on the trial.

## 2.7 Switching models

Each switching model selects one expert among {EEG, MEG, fused} and outputs that expert's prediction. All three were fitted without access to the test run.

**Confidence switch.** For each trial, it uses the expert whose output is furthest from 0.5, that is, argmax_k |p_k − 0.5|.

**Learned gate.**
- For each expert k, a logistic regression (L2 penalty, C = 1, after standardisation) was trained to predict whether expert k classifies the trial correctly.
- Its nine inputs are known at test time without labels:
  - (i) the confidences of the three experts, 2|p_k − 0.5|;
  - (ii) six signal-quality features, two per sensor type (EEG, magnetometers, gradiometers): the logarithm of the median baseline standard deviation across channels, and the logarithm of the largest peak-to-peak amplitude across channels.
- On a test trial, the gate uses the expert with the highest predicted probability of being correct.
- If an expert was correct on all, or none, of the gate's training trials, its probability was set to that constant.
- Ties were broken in favour of the fused expert, then MEG.

**Subject-level switch.** For each participant and fold, it uses the expert with the highest balanced accuracy on held-out training data, for all test trials.

**Oracle (upper bound only).**
- A trial counts as correct if either the EEG or the MEG expert classifies it correctly. A three-expert version is reported as well.
- The oracle is not a usable model. We report it next to the accuracy two experts would reach by chance if their errors were independent, 1 − (1 − acc_EEG)(1 − acc_MEG).
- When the observed oracle does not exceed this value, the two modalities make different errors, but those errors cannot be predicted from the signals.

## 2.8 Validation

All analyses were within participant. Data from one participant were never used to train or test a model for another.

**Outer loop.**
- Leave-one-run-out cross-validation gave six folds per participant. Each run was the test set once.
- Trials from the same run, which share slow drifts and head position, were never split between training and test.

**Training data for the switches.** The switching models must learn from predictions that resemble test predictions, that is, predictions on data the experts were not trained on.

**Classical pipeline.**
- Within each outer fold, a second leave-one-run-out loop over the five training runs produced held-out predictions for every training trial.
- The learned gate and the subject-level choice were fitted on these predictions.
- The experts used on the test run were refitted on all five training runs.

**Deep pipeline.**
- Within each outer fold, four of the five training runs trained the experts.
- The fifth run, a different one in each fold, served for early stopping and to fit the learned gate and the subject-level choice (about 145 trials).
- An inner loop as in the classical pipeline would have multiplied the training time by six.

## 2.9 Robustness experiment

To test whether the switching models cope with a degraded modality, we simulated a failure of one modality on a random subset of trials.

**Corruption model.**
- A random fraction ρ of trials was corrupted, with ρ = 0.2 or 0.4.
- On each corrupted trial, every channel of the target modality received a slowly varying artifact:
  - a Gaussian random walk over the 201 samples, standardised to zero mean and unit variance;
  - multiplied by a random spatial weight for each channel;
  - scaled to five times that channel's median within-trial standard deviation.
- For MEG, both magnetometers and gradiometers were corrupted.
- The random generator was seeded per participant, so every model saw exactly the same corrupted trials.

**What changes and what does not.**
- The corruption was applied after preprocessing, to training and test trials alike. This mimics a recording in which a sensor array is intermittently compromised.
- Nothing else in the pipeline was changed. In particular, the quality features of the learned gate were computed from the corrupted data, exactly as they would be in practice.

**Conditions.**
- With the classical experts (faces vs scrambled), we ran four conditions: EEG or MEG corrupted on 20 % or 40 % of trials.
- With the deep experts (faces vs scrambled), we ran the two 40 % conditions: EEG or MEG corrupted on 40 % of trials.
- In every condition, the three experts were retrained, including the expert of the intact modality. The same trials were corrupted with both types of expert.

## 2.10 Metrics and statistical analysis

**Metrics.**
- The primary metric was balanced accuracy, the mean of the two class-wise recalls, computed over all test trials of a participant. It is insensitive to the 2:1 class ratio of faces vs scrambled.
- We also report:
  - accuracy;
  - the share of test trials assigned to each expert by the learned gate;
  - the proportion of trials classified correctly by EEG only or by MEG only.
- ROC AUC is not used to compare switching models with single models. A switch combines probabilities from different experts, whose scales are not calibrated against each other, so its ranking-based AUC is not comparable with that of a single model.

**Paired comparisons.**
- Each switching model was compared with EEG, MEG, early fusion and late fusion.
- The test was a two-sided Wilcoxon signed-rank test on the 16 per-participant balanced accuracies.
- The Holm–Bonferroni correction was applied across the four comparisons of each switching model.
- We report the mean difference, the number of participants in which the switch was better, and the corrected p-value.

**Sensitivity analysis.** All paired comparisons were repeated without sub-16 (Section 2.3).

**Above-chance decoding.**
- For the famous-vs-unfamiliar problem, each model's balanced accuracy was compared with 50 % by a one-sided Wilcoxon signed-rank test across participants, with Holm correction across models.
- Such a group-level test shows that the information is present in at least part of the population, not in every participant (Allefeld et al., 2016).

## 2.11 Preliminary simulation (supplementary material)

Before the analysis of the real data, we ran a simulation to check whether a switching model could plausibly beat single modalities and fixed fusion.

**Design.**
- Head model: the simultaneous MEG and EEG forward model of the MNE `sample` participant (Gramfort et al., 2013).
- Noise: real recorded MEG/EEG noise.
- Signal: for each of 16 simulated participants, a class-dependent cortical source at a random location, and therefore of random depth and orientation.
- Scenarios: clean data, a weaker signal, and 20 % or 40 % of trials with modality-specific artifacts.
- Models: the same set as in Sections 2.5–2.7, with classical experts.

**Results that shaped the real-data analysis.**
- The switching model was level with early fusion on clean data.
- The oracle stayed at the value expected from independent errors.

Full results are given in the supplementary material.

## 2.12 Software, hardware and availability

| Item | Version or detail |
|---|---|
| Python | 3.12.3 |
| MNE-Python | 1.13.2 |
| mne-bids | 0.20.0 |
| NumPy | 2.5.4 |
| SciPy | statistics (Wilcoxon tests) |
| scikit-learn | 1.9.1 |
| PyTorch | 2.14.1 (CUDA 12.6) |
| Hardware | GPU server, 128 CPU cores, 503 GB RAM, 2 × NVIDIA L40S (46 GB) |

**Running times.**
- Preprocessing took 6.6–8.8 min per participant.
- The classical models took about 1 min per participant and problem.
- The deep models took about 3 min per participant on one GPU on clean data, and 6.6–28.4 min per participant in the robustness conditions, which were partly run on GPUs shared with other jobs.

**Availability.** The data are openly available on OpenNeuro (ds000117). The analysis code, the per-participant results and the scripts that produce every table will be released with the paper.

---

### Not part of this paper

- **Cross-subject decoding.** A leave-one-participant-out version of the pipeline (`cross_subject.py`) is implemented but was not run. It is left for future work, together with source-level analyses and a second dataset.

### References cited in this section (to be checked against the final reference list)

- Allefeld, C., Görgen, K., & Haynes, J.-D. (2016). Valid population inference for information-based imaging: from the second-level t-test to prevalence inference. *NeuroImage*, 141, 378–392.
- Blankertz, B., Lemm, S., Treder, M., Haufe, S., & Müller, K.-R. (2011). Single-trial analysis and classification of ERP components: a tutorial. *NeuroImage*, 56(2), 814–825.
- Dammers, J., et al. (2008). Integration of amplitude and phase statistics for complete artifact removal in independent components of neuromagnetic recordings. *IEEE Trans. Biomed. Eng.*, 55(10), 2353–2362.
- Gramfort, A., et al. (2013). MEG and EEG data analysis with MNE-Python. *Front. Neurosci.*, 7, 267.
- Lawhern, V. J., et al. (2018). EEGNet: a compact convolutional neural network for EEG-based brain–computer interfaces. *J. Neural Eng.*, 15, 056013.
- Ledoit, O., & Wolf, M. (2004). A well-conditioned estimator for large-dimensional covariance matrices. *J. Multivariate Anal.*, 88(2), 365–411.
- Loshchilov, I., & Hutter, F. (2019). Decoupled weight decay regularization. *ICLR 2019*.
- Taulu, S., & Kajola, M. (2005). Presentation of electromagnetic multichannel data: the signal space separation method. *J. Appl. Phys.*, 97, 124905.
- Wakeman, D. G., & Henson, R. N. (2015). A multi-subject, multi-modal human neuroimaging dataset. *Sci. Data*, 2, 150001.
