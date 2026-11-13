# Adaptive EEG/MEG Modality Switching for Brain-Signal Decoding

### Progress presentation

**Presenter:** Kossi Tamplare  ·  **Supervisor:** Dr Rajat Sharma, Head of Department  ·  GD Goenka University

---

## 1. Research question

EEG (electrical) and MEG (magnetic) can be recorded **at the same time** from the same brain.
Published studies show that **sometimes EEG decodes better, sometimes MEG does, and sometimes combining them (fusion) is best**.

**Our question:** can a model **automatically switch** between EEG, MEG and fused signals, trial by trial or subject by subject, and be more accurate than:

1. EEG alone
2. MEG alone
3. Early fusion (EEG and MEG channels given to one model)
4. Late fusion (separate EEG and MEG models, outputs combined)

---

## 2. Why the winner changes: physics

- **MEG is almost blind to *radial* sources** (currents pointing straight out toward the scalp). It sees *tangential* sources well.
- **EEG sees both orientations**, but the skull blurs it and electrode noise affects it.
- **Deep sources favour EEG**, because magnetic fields fade faster with distance.

On a real MEG+EEG head model (7,928 cortical sources), we checked this:

- **Strongly radial sources:** MEG had the better signal in only **20%** of cases.
- **Tangential sources:** MEG had the better signal in **66%** of cases.
- **Depth:** deeper sources clearly favoured EEG (rank correlation **−0.56**).

So which modality is better depends on **where the activity is, the subject's anatomy, and the noise on each trial**. That is the motivation for switching.

---

## 3. What earlier studies found (all simultaneous EEG+MEG)

| Study | Task | Result |
|---|---|---|
| Corsi et al., *Int. J. Neural Syst.* 2019 (15 subjects) | Motor imagery (BCI) | AUC: EEG 0.58, MEG-mag 0.58, MEG-grad 0.61, **fusion 0.66** |
| Reichert et al., *Front. Neurosci.* 2017 | Covert attention | **MEG more accurate**, but **EEG transferred better across subjects** |
| Waldert et al., *IEEE EMBS* 2007 | Hand-movement direction | EEG 54%, MEG 57%, EEG+MEG 57%: **fusion added nothing** |

**Gap:** these studies compare fixed choices (EEG, MEG or fusion). None **learns when to switch**. Corsi's confidence-weighted fusion is the closest, and it is our main baseline.

> Numbers from different studies can't be compared directly (different tasks, subjects and data). We therefore **re-implement every baseline on the same dataset, with the same trial splits**.

---

## 4. Dataset selected: OpenNeuro ds000117 (Wakeman & Henson, 2015)

| Item | Value |
|---|---|
| Subjects | 16 healthy adults |
| Recording | Elekta MEG (102 magnetometers + 204 gradiometers) **simultaneously** with 70 EEG electrodes, plus EOG and ECG |
| Sampling rate | 1,100 Hz |
| Task | Famous, unfamiliar and scrambled faces; 6 runs of ~7.5 min |
| Trials | **14,157 in total, about 885 per subject** (~295 per condition) |
| Size | ~5.2 GB per subject, **~83 GB** of raw MEG/EEG |
| Version | v2.0.0 (January 2026): EOG/ECG channels correctly labelled; calibration and crosstalk files included |

**Decoding tasks:**
- **Faces vs scrambled:** strong, early response (N170/M170).
- **Famous vs unfamiliar:** subtle, harder. This is where differences between models should show most.

---

## 5. Proposed model: gated switching between experts

```
          ┌── EEG expert ───┐
trial ───>├── MEG expert ───┤──> GATE picks one expert per trial ──> prediction
          └── Fused expert ─┘          ↑
                         expert confidences + signal-quality of each modality
```

- **Experts:** the **same classifier** for every modality, so differences come from the data:
  - classical: shrinkage LDA;
  - deep: EEGNet.
- **Three switch variants:**
  1. **Confidence switch:** use the most confident expert.
  2. **Learned gate:** a small model predicts which expert will be right, from confidences and per-trial noise levels.
  3. **Subject-level switch:** pick the best expert for each person.
- **Oracle switch** (knows the right answer): reported **only as an upper bound**, together with its chance level.

---

## 6. Feasibility study (done)

Before using real data, we tested the idea in a **simulation built on a real head model and real recorded noise**: 16 simulated subjects × 300 trials, linear classifiers.

| Model | Clean | Low signal | 20% bad trials | 40% bad trials |
|---|---|---|---|---|
| EEG only | 71.2 | 62.5 | 69.7 | 68.2 |
| MEG only | 74.0 | 64.6 | 73.7 | 77.9 |
| Early fusion | 80.6 | 69.5 | 77.7 | 79.7 |
| Late fusion | 78.6 | 67.8 | 77.9 | 78.3 |
| **Switch (learned gate)** | **80.8** | **69.3** | **80.5** | **80.5** |
| Oracle (upper bound only) | 90.9 | 85.1 | 91.2 | 91.6 |

*Accuracy in %. These are simulation results, **not real recordings**.*

---

## 7. What the feasibility study taught us

1. **Switch vs EEG-only and MEG-only:** clearly better, by **+6.8 to +12.3 points** over EEG and **+2.6 to +6.8** over MEG (Wilcoxon, p < 0.05).
2. **Switch vs late fusion:** better by **+1.5 to +2.5 points** (significant in 3 of 4 scenarios).
3. **Switch vs early fusion:** **no significant difference.** This is an honest limitation.
4. **Most of the oracle's ~10-point lead is chance.** Two independent classifiers at 70–74% would already reach ~92% "oracle" accuracy, so the oracle must always be reported next to this chance level.

**Consequence for the paper's claim:** instead of "switching beats fusion", we target:
- **Robust adaptive fusion:** never worse than the best single modality, better than late fusion, and most useful when one modality is corrupted.
- **Which modality, for whom, and why:** gate choices explained by source orientation and depth.

**Real data (ds000117) is the deciding test.**

---

## 8. Implementation status

**Infrastructure: ready**
- Lab server (Dell PowerEdge R760XA, 2 × NVIDIA L40S 46 GB, 128 cores, 503 GB RAM).
- Python environment: PyTorch 2.14 (CUDA 12.6, GPU confirmed), MNE 1.13, MNE-BIDS, braindecode, scikit-learn.
- Storage: `/home` is full and `/scratch` is not writable for our account, so we work in `/var/tmp` (241 GB free). A `/scratch` folder has been requested from the admin.
- Connection to OpenNeuro tested from the server.

**Code: written and validated on mock and synthetic data**

| Script | Content |
|---|---|
| `preprocess.py` | MEG Maxwell filtering (SSS) with the subject's calibration files; automatic bad-channel detection; EEG interpolation and average reference; 0.1–40 Hz filter; **separate ICA for EEG and MEG** (EOG/ECG removal); trials −0.2 to 0.8 s; artifact rejection |
| `classical_models.py` | EEG, MAG, GRAD, MEG, early fusion, late fusion, 3 switches, oracle (CPU) |
| `deep_models.py` | Same comparison with EEGNet experts (GPU), resumable across 4-hour sessions |
| `aggregate.py` | Group table, paired Wilcoxon tests (Holm-corrected), chance-level oracle, gate choices |

---

## 9. Methodological safeguards (reviewer-proof design)

- **Modality isolation:** ICA, interpolation and referencing are never computed across EEG and MEG together. The "EEG-only" model never receives MEG information.
- **Paired comparison:** the same trials and the same folds for every model.
- **No test leakage:** the gate learns only from held-out *training* runs and never sees test labels.
- **Run-wise cross-validation** (leave-one-run-out), so neighbouring trials are never split between training and testing.
- **Class imbalance:** faces outnumber scrambled trials 2:1, so **balanced accuracy** is the main metric, with AUC also reported.
- **Statistics:** paired Wilcoxon across subjects with Holm correction. The oracle is shown only next to its chance level.

---

## 10. Next steps and timeline

| Step | Where | Estimated time |
|---|---|---|
| 1. Download subject 1, check; then all 16 subjects (83 GB) | Lab server (tmux, can run overnight) | 1 lab session |
| 2. Preprocessing test (1 subject), then all 16 | Lab server, CPU | 1 lab session |
| 3. **First real results:** classical models, both tasks + statistics | CPU (server or laptop) | < 1 hour |
| 4. Deep models (EEGNet experts + gate), both tasks | Lab GPU | 1–2 GPU sessions |
| 5. Robustness test: corrupt EEG or MEG on some test trials | GPU / CPU | 1 session |
| 6. Cross-subject test (leave-one-subject-out) | GPU | 1–2 sessions |
| 7. Second dataset (Cogitate MEG-EEG) for generalization | Server | later |
| 8. Paper writing | — | in parallel |

---

## 11. Points for the supervisor's decision

1. **Main claim of the paper:** "switching beats fusion", or "robust adaptive fusion + which modality, for whom and why"? The feasibility study supports the second.
2. **Tasks:** both faces vs scrambled and famous vs unfamiliar, or one main task?
3. **Second dataset:** Cogitate MEG-EEG (2026), or a motor-imagery BCI dataset (Corsi et al., which may require contacting the authors)?
4. **Server access:** support for the `/scratch` request, and whether long jobs can run overnight.

---

## References

- Corsi, M.-C. et al. (2019). Integrating EEG and MEG signals to improve motor imagery classification in brain–computer interface. *International Journal of Neural Systems*, 29(1), 1850014.
- Reichert, C. et al. (2017). A comparative study on the detection of covert attention in event-related EEG and MEG signals to control a BCI. *Frontiers in Neuroscience*, 11, 575.
- Waldert, S. et al. (2007). Decoding performance for hand movements: EEG vs. MEG. *Proc. IEEE EMBS*.
- Wakeman, D. G. & Henson, R. N. (2015). A multi-subject, multi-modal human neuroimaging dataset. *Scientific Data*, 2, 150001.
- Henson, R. N. et al. (2019). Multimodal integration of M/EEG and f/MRI data in SPM12. *Frontiers in Neuroscience*, 13, 300.
- Lawhern, V. J. et al. (2018). EEGNet: a compact convolutional neural network for EEG-based brain–computer interfaces. *Journal of Neural Engineering*, 15, 056013.
- Gramfort, A. et al. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience*, 7, 267.
