# 06: Roadmap, decisions, risks

_Updated 25 Nov 2026. One experiment is being completed (EEGNet robustness, 3 EEG subjects left); the manuscript is in preparation._

## 1. Experiments: status

| # | Experiment | Status | Results |
|---|---|---|---|
| 1 | Feasibility simulation (head model, 16 simulated subjects) | Done (2 Nov) | `results/feasibility_simulation/` |
| 2 | Download and preprocessing of ds000117 (16 subjects; 13,537 / 14,157 trials kept) | Done (13–14 Nov) | `results/server_sync/2026-11-14_1441/preprocessing_logs/` |
| 3 | Classical (LDA) benchmark, 2 tasks × 16 subjects | Done (14 Nov) | `results/real_data/2026-11-14_classical_16_subjects.md` |
| 4 | Deep (EEGNet) benchmark, faces vs scrambled × 16 subjects | Done (14 Nov) | `results/real_data/2026-11-14_deep_and_robustness_16_subjects.md` |
| 5 | Robustness: EEG or MEG corrupted on 20 % / 40 % of trials (LDA, faces vs scrambled) | Done (14 Nov) | same report as 4 |
| 6 | Related work 2025–2026 | Done (14 Nov) | `docs/07_related_work_2025-2026.md` |
| 7 | Offline checks: all comparisons without sub-16; above-chance test for famous vs unfamiliar | Done (18 Nov) | `results/real_data/2026-11-18_offline_checks.md` |
| 8 | Robustness with EEGNet experts: EEG or MEG corrupted on 40 % of trials, faces vs scrambled | In progress (20, 23 and 25 Nov): MEG 16/16, EEG 13/16 subjects | `results/server_sync/2026-11-25_1621/` (raw files; report after completion) |

## 2. Out of scope for this paper (future work)

These were decided against to keep the experiments strictly to what the paper needs (14 Nov):

- **Cross-subject validation** (`cross_subject.py`): the code is written but has not been run.
- **EEGNet on famous vs unfamiliar**: on this task all classical methods are above chance, but only by 3–7 points.
- **Source-level interpretability** (MRI-based orientation and depth of the generators).
- **Second dataset** (Cogitate MEG-EEG, 2026) for generalisation.
- **Real sensor failures** instead of synthetic corruption.

## 3. Next steps

| # | Step | Status |
|---|---|---|
| 1 | Decide the target venue and format of the paper | After the literature review |
| 2 | Paper outline, to be validated by the supervisor | To do |
| 3 | Figures: main accuracy figure (LDA vs EEGNet), robustness figure, gate-choice figure | To do |
| 4 | Writing: Methods (full draft: `docs/04_methods.md`, 18 Nov), Results, Discussion, Introduction | Methods drafted |
| 5 | Sensitivity check without sub-16 | Done (18 Nov): no conclusion changes |
| 6 | Deep literature review: candidate list under review, then `docs/08_literature_review.md` | In progress |
| 7 | Name of the method ("NeuroSwitch" proposed; the name is already used by commercial products outside research) | To decide |

## 4. Points to report in the paper

- **Sub-16:** 24.4 % of trials rejected, with no bad channels detected.
- **Sub-03:** 12 MEG sensors reconstructed by SSS in run 6.
- **Metric:** ROC-AUC is not comparable between switches and single models, because a switch mixes the probability scales of different experts. Balanced accuracy is therefore the primary metric.
- **Deep learned gate:** it is trained on a single validation run (about 145 trials), which probably explains why it falls below the confidence switch.
- **Pipeline correction v1.2:** an indexing error in the inner cross-validation was found and corrected before the group analysis. All reported switch results use v1.2.

## 5. Risks

| Risk | Mitigation |
|---|---|
| Reviewers ask for generalisation beyond one dataset | State it as a limitation; name Cogitate as the next dataset |
| Reviewers question synthetic corruption | Describe the corruption model precisely; propose real sensor failures as future work |
| Raw server files deleted (`$WORK`, ~30 days) | All result files are already synced to this repository; the raw data can be re-downloaded from OpenNeuro |
