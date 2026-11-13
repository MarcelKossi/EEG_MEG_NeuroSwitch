# 01: Research overview

## 1. Research question

EEG (electric potentials on the scalp) and MEG (magnetic fields outside the head) can be recorded **simultaneously** from the same brain activity. Published studies disagree on which modality decodes best: sometimes EEG, sometimes MEG, sometimes their combination.

> **Question:** Can a model learn **when** to rely on EEG, on MEG, or on both (per trial or per subject), and does this give better or more robust decoding than:
> 1. EEG alone,
> 2. MEG alone,
> 3. **early fusion** (one model on all EEG+MEG channels), and
> 4. **late fusion** (separate EEG and MEG models whose outputs are combined)?

## 2. Why the better modality changes: physics

| Property | EEG | MEG |
|---|---|---|
| Measures | Volume currents (potentials) | Magnetic field of primary currents |
| Radial sources (perpendicular to the skull, e.g. gyral crowns) | Sees them | **Almost blind** |
| Tangential sources (sulcal walls) | Sees them | Sees them well |
| Deep sources | Relatively better | Field fades quickly with distance |
| Skull and scalp | Blur and attenuate the signal | Almost transparent |
| Typical noise | Electrodes, sweat, muscle, blinks | Environment, head movement, sensor jumps |

**Head-model check** (feasibility study, 7,928 cortical sources of the MNE `sample` subject):
- **Strongly radial sources:** MEG had the better signal in only **20%** of cases.
- **Tangential sources:** MEG had the better signal in **66%** of cases.
- **Orientation overall:** radiality correlated with the MEG/EEG signal ratio at ρ = −0.39.
- **Depth** favoured EEG (ρ = −0.56).

**Consequence:** which modality is better depends on **where** the task-related activity is, on the **subject's cortical folding**, and on the **noise in each trial**. That is the motivation for an adaptive (switching) model.

## 3. Prior work on simultaneous EEG+MEG decoding

| Study | Task, N | Finding |
|---|---|---|
| Corsi et al., *Int. J. Neural Syst.* 29(1), 2019 | Motor imagery BCI, 15 subjects | AUC: EEG 0.58, MEG-mag 0.58, MEG-grad 0.61, **fusion 0.66**. The fusion weighs each classifier by its confidence, so it is effectively a *soft switch* and our strongest baseline. |
| Reichert et al., *Front. Neurosci.* 11:575, 2017 | Covert attention ERP/ERF | **MEG more accurate** within subject; **EEG transferred better across subjects**. |
| Waldert et al., *IEEE EMBS* 2007 | Hand-movement direction | EEG 54%, MEG 57%, **EEG+MEG 57%**: fusion added nothing. |

**Gap:** these studies compare **fixed** choices (EEG, MEG or fusion). None learns, per trial or per subject, *which* source of information to trust, and none tests robustness when one modality is corrupted.

Accuracy numbers from different studies **cannot be compared directly**: the tasks, subjects and preprocessing differ. All baselines are therefore **re-implemented on the same dataset, with the same trial splits** (see `04_methods.md`).

## 4. Hypotheses

- **H1:** The switching model is more accurate than EEG-only and MEG-only.
- **H2:** The switching model is more accurate than late fusion, which weighs a weak modality equally.
- **H3:** The switching model is at least as accurate as early fusion, and **more robust** when one modality is corrupted.
- **H4:** The gate's choices are interpretable: they follow signal quality and, across subjects, the physics (orientation and depth of the generators).

The feasibility study (`02_feasibility_study.md`) supports H1, H2 and H3a, but gives **no evidence that switching beats early fusion on clean data**. The paper should therefore lead with **robustness and interpretability**, not with a raw accuracy win over fusion.

## 5. Expected contributions

1. A **fair, paired benchmark** of EEG, MEG, early fusion and late fusion on the same simultaneous recordings (ds000117), with strict modality isolation and no test leakage.
2. A **gated switching model** (confidence, learned and subject-level gates) with an honest oracle analysis that reports the **chance-level oracle** next to the oracle.
3. A **robustness analysis**: corrupting EEG or MEG on some test trials, to show where adaptive selection beats fixed fusion.
4. An **interpretability analysis**: which modality the gate chooses, for which subjects and trials, and why.

## 6. Datasets

| Dataset | Use | Status |
|---|---|---|
| **OpenNeuro ds000117 v2.0.0** (Wakeman & Henson 2015) | Main dataset | Downloading on the lab server (13 Nov) |
| Cogitate MEG-EEG (Scientific Data, 2026) | Second dataset (generalisation) | Candidate |
| MNE `sample` data | Pipeline tests only | Used |

## 7. References

- Corsi, M.-C. et al. (2019). Integrating EEG and MEG signals to improve motor imagery classification in brain–computer interface. *International Journal of Neural Systems*, 29(1), 1850014.
- Reichert, C. et al. (2017). A comparative study on the detection of covert attention in event-related EEG and MEG signals to control a BCI. *Frontiers in Neuroscience*, 11, 575.
- Waldert, S. et al. (2007). Decoding performance for hand movements: EEG vs. MEG. *Proc. IEEE EMBS*.
- Wakeman, D. G. & Henson, R. N. (2015). A multi-subject, multi-modal human neuroimaging dataset. *Scientific Data*, 2, 150001.
- Henson, R. N. et al. (2019). Multimodal integration of M/EEG and f/MRI data in SPM12. *Frontiers in Neuroscience*, 13, 300.
- Lawhern, V. J. et al. (2018). EEGNet: a compact convolutional neural network for EEG-based brain–computer interfaces. *Journal of Neural Engineering*, 15, 056013.
- Gramfort, A. et al. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience*, 7, 267.
