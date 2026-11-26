# Research journal

Project: adaptive EEG/MEG modality switching on simultaneous M/EEG (ds000117).
Kossi Tamplare, GD Goenka University. Supervisor: Dr Rajat Sharma (Head of Department).

Entries are chronological. Each one records what was done, problems and how they were resolved, results, and decisions.

---

## 2 Nov 2026: Framing the question; feasibility study

**Work**
- Defined the question: can a decoder learn when to rely on EEG, on MEG, or on both, and does this beat EEG-only, MEG-only, early fusion and late fusion?
- Reviewed simultaneous M/EEG decoding studies:
  - Corsi et al. 2019: fusion best (AUC 0.66 vs 0.58–0.61);
  - Reichert et al. 2017: MEG more accurate, but EEG transferred better across subjects;
  - Waldert et al. 2007: fusion added nothing.
- Surveyed open datasets with truly simultaneous recordings:
  - selected **ds000117** (Wakeman & Henson) as the main dataset;
  - kept Cogitate MEG-EEG (2026) as a candidate for generalisation.
- Feasibility study before committing compute time:
  - simulation on the MNE `sample` head model with real recorded MEG/EEG noise;
  - 16 simulated subjects;
  - four scenarios: clean, low signal, 20% and 40% corrupted trials.

**Results** (details in `docs/02_feasibility_study.md`)
- **vs single modalities:** the learned switch beat EEG-only by +6.8 to +12.3 points and MEG-only by +2.6 to +6.8 points (Wilcoxon p < 0.05 in all scenarios).
- **vs late fusion:** it beat late fusion by +1.5 to +2.5 points (significant in 3 of 4 scenarios).
- **vs early fusion:** no significant difference (−0.2 to +2.8 points).
- **Oracle:** the oracle's headroom was almost exactly the value expected if EEG and MEG errors were independent (90.9% vs 92.0%). Errors are complementary but largely unpredictable.

**Decision**
- The paper should not promise that switching beats early fusion.
- Main expected contributions: **robustness to a corrupted modality** and **interpretability of the switch's choices**.
- The oracle will always be reported together with its chance level.

---

## 5 Nov 2026: Computing environment

**Work**
- Set up the GPU server: 2 × NVIDIA L40S, driver 550 / CUDA 12.4.
- Created an isolated Python environment:
  - PyTorch 2.14.1 built for CUDA 12.6 (GPU access confirmed);
  - MNE 1.13.2, mne-bids, scikit-learn, braindecode.
  - The PyTorch build is pinned with a constraint file, so other packages cannot replace it with a CPU build.

**Problems**
- **Storage:** the default user storage on the server could not hold a dataset of this size. I set up a dedicated working directory (`$WORK`) and redirected all caches there.
- **Dataset layout:** in ds000117 v2.0.0 the MaxFilter calibration and cross-talk files are stored per subject, and the `derivatives/meg_derivatives` folder of earlier versions no longer exists. The download now targets `sub-XX/ses-meg` only.

---

## 9 Nov 2026: Analysis pipeline v1.0; progress presentation

**Work**
- Verified the dataset against its own metadata:
  - ~83 GB of MEG/EEG;
  - 14,157 trials (882–889 per subject);
  - EOG and ECG channels correctly typed in v2.0.0;
  - **no bad channels marked**, so they are detected automatically.
- Wrote the analysis pipeline:
  - preprocessing (SSS, EEG interpolation and average reference, 0.1–40 Hz, 200 Hz, **separate ICA for EEG and MEG**, epochs −0.2 to 0.8 s);
  - classical experts (shrinkage LDA);
  - deep experts (EEGNet);
  - switching models;
  - group statistics (Wilcoxon with Holm correction, chance-level oracle).
- Validated the pipeline on a mock BIDS dataset derived from the MNE sample recording, and on synthetic data of the real size.
- Presented the progress to my supervisor (`presentations/`).

**Design decisions**
- **Leave-one-run-out cross-validation**, so neighbouring trials are never split between training and testing.
- **Gates trained only on held-out predictions** from the training runs.
- **Balanced accuracy** as the primary metric, because of the 2:1 ratio of faces to scrambled trials.

---

## 13 Nov 2026: First real-data session (subject 01)

**Work**
- Deployed the pipeline on the server.
- Started the download of all 16 subjects (sub-01 complete; sub-02 to sub-16 in progress).
- Preprocessing test on subject 01 (120 s per run): pipeline completed, 168/184 trials kept.
- **Full preprocessing of subject 01:**
  - 879/887 trials kept (0.9% rejected): 292 famous, 293 unfamiliar, 294 scrambled;
  - 70 EEG, 102 magnetometer and 204 gradiometer channels;
  - 7.5 min.
- Classical models on subject 01, and a GPU smoke test of the EEGNet pipeline on the L40S (passed).

**Problems and fixes (pipeline v1.1)**
1. **SSS origin.** The sphere fitted to the digitised head points sat 37 mm anterior to the head-frame origin, probably because of nose points. This risks a poor SSS reconstruction over posterior sensors, where face-related activity is expected. I switched to a fixed origin of (0, 0, 40) mm for bad-channel detection, Maxwell filtering and EEG interpolation.
2. **EEG bad-channel detection was biased by blinks.** Six frontal electrodes were flagged because blinks inflate their variance, and interpolating them would have penalised EEG in the comparison. Detection now uses a robust amplitude measure (median absolute deviation), and ICA removes the blinks. Only EEG002, EEG004 (flagged in most runs) and EEG070 (one run) remain interpolated.
3. **Storage.** The working directory has enough free space for the full dataset and derivatives (~55 GB margin), but nothing else should be stored there.

**Preliminary result, subject 01** (single subject; not interpreted)
- Balanced accuracy, faces vs scrambled: EEG 61.3%, MEG 80.7%, **early fusion 87.9%**, late fusion 76.7%.
- Famous vs unfamiliar: EEG 48.2% (chance level), MEG 55.6%, early fusion 58.1%, late fusion 53.5%.
- Late fusion fell below MEG alone. This is consistent with the concern that equal weighting is hurt by a weak modality, to be checked across subjects.

---

## 13 Nov 2026 (evening): Pipeline v1.2

**Error found and corrected**
- **Indexing error in `classical_models.py`.** In the inner cross-validation that trains the switch gates, features were indexed over all trials while labels were indexed over training trials only, so features and labels did not correspond.
- **Consequence:** the switch results for subject 01 (confidence, learned gate and subject-level) are **invalid** and will be recomputed.
- **Not affected:** the EEG, MEG, early-fusion and late-fusion results, and the deep-learning pipeline, which uses a separate validation run.
- **After the fix:** on synthetic data, the learned gate moved from consistently below early fusion to level with it or slightly above.

**Additions**
- **Robustness experiment** (`--corrupt eeg|meg|both`, `--corrupt-rate`, `--corrupt-gain`):
  - large, slowly varying artifacts are added to one modality on a random subset of trials;
  - the same trials are corrupted for every model, so comparisons stay paired.
- **Cross-subject validation** (`cross_subject.py`):
  - leave-one-subject-out with per-subject feature standardisation;
  - gates trained on grouped out-of-fold predictions from the training subjects.

**Next session**
1. Deploy v1.2 on the server.
2. Re-run the classical models for subject 01.
3. Preprocess the remaining subjects once the download is complete.
4. Run the classical models on 16 subjects, then the group statistics.
5. Time one full deep-learning subject.

---

## 14 Nov 2026: Full dataset, classical models on 16 subjects

**Work**
- Deployed pipeline v1.2 on the server.
- Completed the download (16 subjects, ~83 GB).
- Preprocessed all 16 subjects: **13,537 of 14,157 trials kept** (4.4 % rejected), 6.6–8.8 min per subject.
- Ran the classical models for both tasks on all 16 subjects, and recomputed subject 01 with v1.2.

**Results** (`results/real_data/2026-11-14_classical_16_subjects.md`)
- **Faces vs scrambled.** The learned gate reached 87.7 %, against EEG 71.2 %, MEG 80.5 %, late fusion 82.1 % and early fusion 87.4 %. It beat EEG, MEG and late fusion in all 16 subjects (Holm p = 0.0001), and was level with early fusion (+0.3, p = 0.50).
- **Famous vs unfamiliar.** All models are close to chance (EEG 53.2 %, MEG 56.1 %, early fusion 57.4 %, learned gate 57.0 %). The gate beat EEG only (+3.9, p = 0.002).
- **Oracle.** In both tasks the oracle matched the value expected from independent errors, as in the feasibility study.
- **Gradiometers.** Gradiometers alone matched the full MEG array.

**Problems and observations**
- **The server is available only during daily sessions.** Long jobs must finish within a session, and results are synced to the PC before the end of each session.
- **Sub-16:** 24.4 % of trials rejected, with no bad channels detected. To be investigated: which sensor type triggers the rejections.
- **Sub-03:** a block of 12 MEG sensors (MEG22xx) was flagged in run 6 only and reconstructed by SSS.
- **Metric.** ROC-AUC is not comparable between switching models and single models. Balanced accuracy stays the primary metric.

**Decision**
- The results confirm the framing chosen after the feasibility study: the switch matches, but does not beat, early fusion on clean data.
- The remaining necessary experiment is the **robustness test** (H3).

**Afternoon: deep models and robustness** (`results/real_data/2026-11-14_deep_and_robustness_16_subjects.md`)
- **EEGNet, faces vs scrambled, 16 subjects:** EEG 81.3 %, MEG 88.3 %, early fusion 89.1 %, **late fusion 91.5 %**, confidence switch 91.8 %, learned gate 90.8 %.
  - With EEGNet the ranking of the fixed fusions is reversed compared with LDA: late fusion now beats early fusion.
  - The switches stay level with the best scheme in both cases (LDA: early fusion; EEGNet: late fusion).
- **Robustness (LDA), one modality corrupted on 20 % or 40 % of trials:**
  - The learned gate beat every fixed strategy, including early fusion (+1.4 to +2.4 points, 14–15/16 subjects, Holm p ≤ 0.0003), and it re-routed trials away from the corrupted modality.
  - **H3 is supported.**
- **Related work 2025–2026** reviewed (`docs/07_related_work_2025-2026.md`). FUSE (2026) also finds that EEG+MEG fusion does not significantly beat the best single modality. No recent study evaluates per-trial modality selection or robustness for simultaneous EEG/MEG.
- **Decision:** the experiments needed for the paper are complete. Writing starts next.

---

## 18 Nov 2026: Supervisor feedback; offline checks; Methods; literature search

**Supervisor feedback**
- The README was out of date and gave the impression that the results were not conclusive. It was rewritten as an explanatory overview of the project and its results.
- The supervisor asked for a deep literature review and for the methodology to be written before the paper draft.

**Offline checks** (`code/pipeline/offline_checks.py`, computed from the result files of 14 Nov; `results/real_data/2026-11-18_offline_checks.md`)
- **Without sub-16** (24.4 % of trials rejected), every conclusion holds on 15 subjects:
  - learned gate level with early fusion on clean data (+0.3, 8/15, p = 0.64);
  - learned gate better than early fusion in the four corrupted conditions (+1.3 to +2.5, 13–14/15, Holm p ≤ 0.0006);
  - with EEGNet, learned gate +1.8 over early fusion and −0.7 below late fusion, as with 16 subjects.
- **Famous vs unfamiliar:** every LDA model is above chance across subjects (one-sided Wilcoxon against 50 %, Holm p ≤ 0.003). EEG is the weakest (53.2 %, 12/16 subjects above 50 %).

**Methods**
- `docs/04_methods.md` was turned into a full Materials and Methods section:
  - overview diagram;
  - EEGNet architecture;
  - training data of the switches;
  - corruption model;
  - statistics, including the sensitivity and above-chance analyses.

**Literature**
- PubMed and bioRxiv were searched for the review.
- 78 candidate articles, with verified references, were listed for reading (local working file).
- No study was found that selects between EEG and MEG trial by trial.

**Decisions**
- Position to present to the supervisor (not yet confirmed): no second dataset in this paper. The claims are paired, within-dataset comparisons replicated across 16 participants, two decoding problems, two classifiers and several corruption levels; generalisation to other data is stated as a limitation and future work.
- The EEGNet robustness experiment (EEG or MEG corrupted on 40 % of trials) will be run on 19 Nov, so that H3 is tested with both types of expert.
- The name of the method is pending: "NeuroSwitch" is free in the research literature, but it is already used by commercial products.

---

## 20–26 Nov 2026: Robustness experiment with EEGNet experts

**Work**
- Ran the EEGNet robustness experiment on faces vs scrambled: EEG or MEG corrupted on 40 % of trials, 16 subjects per condition, with the same corruption as in the LDA experiment (5,429 of 13,537 trials corrupted in each condition).
- Four lab sessions (20, 23, 25 and 26 Nov); one job per GPU on 25 and 26 Nov. `deep_models.py` resumes from the subjects already saved, so each session continued where the previous one stopped.
- Group statistics with `aggregate.py`; report in `results/real_data/2026-11-26_deep_robustness_16_subjects.md`. Raw files: `results/raw/`.

**Problems**
- **Two jobs per GPU (20 Nov)** lowered the total throughput compared with one job per GPU. Rule adopted: one job per GPU.
- **Running time varied widely**, from 6.6 to 28.4 min per subject, against about 3 min for the clean EEGNet run of 14 Nov. On 26 Nov, other processes occupied both GPUs at 100 %, yet a subject took only 10–13 min. The cause of the slow sessions was not identified.
- **End of the daily session:** a subject interrupted at the end of a session restarts from its first fold at the next session.
- **Logs:** the job logs are written outside the folder copied by the sync script. On 25 and 26 Nov, they were copied into it on the server before the sync (`cp $WORK/deep_robust_*_0.4_*.log $WORK/eegmeg_pipeline/`).

**Results** (balanced accuracy, %, 16 subjects; clean values from 14 Nov)

| Model | Clean | EEG corrupted 40 % | MEG corrupted 40 % |
|---|---|---|---|
| Early fusion | 89.1 | 86.7 | 77.0 |
| Late fusion | 91.5 | 88.5 | 84.3 |
| Switch: confidence | 91.8 | 88.8 | 84.2 |
| Switch: learned gate | 90.8 | 88.3 | 84.0 |

- With EEGNet experts, **late fusion is robust to a corrupted modality.** The switches are level with it (−0.2 to +0.3 point, n.s.) but do not beat it.
- The learned gate beats early fusion in both conditions (+1.7 and +7.1 points, 16/16 subjects, Holm p = 0.0001) and re-routes trials away from the corrupted modality.
- This differs from LDA, where late fusion and the confidence switch collapsed and the learned gate beat every fixed strategy.
- Across both expert types, the learned gate is the only switch that is never significantly below the best fixed strategy in the four 40 % conditions.
- In every condition, the oracle stays below the value expected from independent errors.
- **Reproducibility:** reruns within the same condition gave identical results (sub-08, 23 and 25 Nov). The retrained MEG expert differed slightly from the clean run in 5 of 16 subjects (up to 1.4 points), probably because of non-deterministic GPU arithmetic.

**Decisions and open points**
- The sync folder `2026-11-23_1610` was not kept: its content is included in `2026-11-23_1621`.
- No GPU computation is needed anymore for this paper.
- To decide with the supervisor: how to frame the robustness result now that it depends on the type of expert, before updating the README.
- To decide: running the sensitivity analysis without sub-16 on the two EEGNet robustness conditions (offline).
