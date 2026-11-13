# 03: Dataset: OpenNeuro ds000117 v2.0.0

**"Multisubject, multimodal face processing"** (Wakeman, Apšvalka, Henson)
DOI: `10.18112/openneuro.ds000117.v2.0.0` · License: **CC0** · BIDS 1.8.0

These facts were verified from the dataset's own files (`dataset_description.json`, `README`, `CHANGES`, `*_events.tsv`, `*_channels.tsv`, `*_meg.json`) on 9 Nov 2026.

**How to acknowledge** (from the dataset): cite Wakeman & Henson (2015), *Scientific Data* 2:150001 (PubMed 25977808), and add:
*"This data was obtained from the OpenNeuro database. Its accession number is ds000117."*

## 1. Recording

| Item | Value |
|---|---|
| Subjects | 16 (sub-01 … sub-16) |
| System | Elekta Neuromag VectorView: **306 MEG** (102 magnetometers + 204 planar gradiometers) |
| EEG | **70** scalp electrodes recorded **simultaneously** |
| Other channels | **EOG061**, **EOG062** (eye), **ECG063** (heart), EEG064 (misc), trigger channels |
| Sampling rate | 1,100 Hz |
| Power line | 50 Hz |
| Head position | Continuous HPI (coils at 293–328 Hz) |
| Runs | 6 per subject, ~8 min each (run-01 of sub-01: 491 s) |
| MEG calibration files | `sub-XX_ses-meg_acq-calibration_meg.dat` and `sub-XX_ses-meg_acq-crosstalk_meg.fif`, **inside each subject's `ses-meg/meg/` folder** |
| Bad channels | **None marked** in `channels.tsv`, so the pipeline detects them automatically |

Version 2.0.0 (January 2026) labels these channels EOG061/EOG062/ECG063/EEG064 with their correct types (older versions called them EEG061–EEG064). There is **no `derivatives/meg_derivatives` folder** in this version, which is why the first download command failed on 5 Nov.

## 2. Task and events

Participants viewed **famous**, **unfamiliar** and **scrambled** faces, each presented once and repeated either immediately or after a delay. Events come from `*_events.tsv` (`onset` in seconds, `value` = trigger code):

| trial_type | Code | Condition | Repetition |
|---|---|---|---|
| IniFF / ImmFF / DelFF | 5 / 6 / 7 | famous | initial / immediate / delayed |
| IniUF / ImmUF / DelUF | 13 / 14 / 15 | unfamiliar | initial / immediate / delayed |
| IniSF / ImmSF / DelSF | 17 / 18 / 19 | scrambled | initial / immediate / delayed |
| btnL / btnR, etc. | 4096, 8192, … | button presses | ignored |

**Trial counts (all 16 subjects):** 4,716 famous, 4,726 unfamiliar, 4,715 scrambled, **14,157 in total**. That is **882–889 per subject**, about 148 per run.

**Decoding tasks used:**
- **faces_vs_scrambled:** famous + unfamiliar (≈590) vs scrambled (≈295), imbalanced 2:1. Strong early response (N170/M170).
- **famous_vs_unfamiliar:** ≈295 vs ≈295, balanced. Subtle and late, so harder.

## 3. Files and sizes

```
ds000117/
├── dataset_description.json, README, CHANGES, participants.tsv
└── sub-01/ses-meg/meg/
    ├── sub-01_ses-meg_task-facerecognition_run-01_meg.fif      (~820–845 MB each, 6 runs)
    ├── sub-01_ses-meg_task-facerecognition_run-01_events.tsv
    ├── sub-01_ses-meg_task-facerecognition_run-01_channels.tsv
    ├── sub-01_ses-meg_task-facerecognition_run-01_meg.json
    ├── sub-01_ses-meg_acq-calibration_meg.dat
    ├── sub-01_ses-meg_acq-crosstalk_meg.fif                    (also ends in _meg.fif: don't count it as a run!)
    └── sub-01_ses-meg_coordsystem.json
```

| Download | Size |
|---|---|
| One subject (`sub-XX/ses-meg`) | ~4.9–5.2 GB |
| 16 subjects | **~83 GB** |
| Preprocessed output (`sub-XX_data.npz` + `sub-XX_epo.fif`) | ~0.5–0.6 GB per subject, ~9 GB in total |

The dataset also contains fMRI and structural MRI (`ses-mri`). They are **not downloaded**; the pipeline uses only `ses-meg`.

## 4. Download command (server)

```bash
openneuro-py download --dataset ds000117 --target-dir $WORK/data/ds000117 --include sub-01/ses-meg
for s in $(seq -w 2 16); do openneuro-py download --dataset ds000117 --target-dir $WORK/data/ds000117 --include sub-$s/ses-meg; done
```

Rerunning the command skips complete files, which is useful after network errors.

## 5. Observations on real data (sub-01, 13 Nov)

- 879/887 trials kept after cleaning.
- Bad EEG channels detected: EEG002 and EEG004 (most runs) and EEG070 (run 1).
- No bad MEG channels after SSS detection.
- ICA removed 4 MEG and 4 EEG components (eye and heart).
