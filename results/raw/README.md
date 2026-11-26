# Raw result files

Result files produced by `code/pipeline/` v1.2 on the 16 subjects of ds000117. All result reports in `results/real_data/` are computed from these files.

| Folder | Content | Report |
|---|---|---|
| `classical/` | Shrinkage-LDA, both tasks: one JSON per subject and task, plus the group tables (`summary_*.md`) | `2026-11-14_classical_16_subjects.md` |
| `deep/` | EEGNet, faces vs scrambled | `2026-11-14_deep_and_robustness_16_subjects.md` |
| `robust_eeg_0.2/`, `robust_eeg_0.4/`, `robust_meg_0.2/`, `robust_meg_0.4/` | Shrinkage-LDA with EEG or MEG corrupted on 20 % or 40 % of trials | `2026-11-14_deep_and_robustness_16_subjects.md` |
| `deep_robust_eeg_0.4/`, `deep_robust_meg_0.4/` | EEGNet with EEG or MEG corrupted on 40 % of trials | `2026-11-26_deep_robustness_16_subjects.md` |
| `preprocessing/` | One preprocessing log per subject: bad channels, ICA components removed, trials kept, parameters | `2026-11-14_classical_16_subjects.md` |

- Each result folder contains `faces_vs_scrambled/sub-XX.json` (and `famous_vs_unfamiliar/` for `classical/`), and the group table `summary_<task>_balanced_accuracy.md` written by `aggregate.py`.
- In the preprocessing logs, the paths of the MaxFilter calibration and cross-talk files are reduced to their file names.
- The group tables can be recomputed with `python code/pipeline/aggregate.py --results results/raw/<folder>`.
