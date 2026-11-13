# 05: Computing environment and reproducibility

## Hardware

| Item | Value |
|---|---|
| Server | GPU server (lab server), Ubuntu |
| CPU / RAM | 128 cores / 503 GB |
| GPU | 2 × NVIDIA L40S (46 GB); one GPU used per job |
| Driver / CUDA | 550.163.01 / 12.4 |

## Software

Python 3.12.3 in an isolated virtual environment (versions in `requirements.txt`):

| Package | Version |
|---|---|
| MNE-Python | 1.13.2 |
| mne-bids | 0.20.0 |
| NumPy | 2.5.4 |
| scikit-learn | 1.9.1 |
| pandas | 3.1.1 |
| PyTorch | 2.14.1 (CUDA 12.6 build) |
| braindecode | 2.0.0 |
| openneuro-py | 2026.9.1 |

PyTorch is installed first from the CUDA 12.6 index and then pinned with a constraint file. Without the pin, installing other packages can silently replace the GPU build with a CPU one:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install torch==2.14.1 --index-url https://download.pytorch.org/whl/cu126
pip freeze | grep -i "^torch" > constraints.txt
pip install -r requirements.txt -c constraints.txt
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"   # 2.14.1+cu126 True
```

## Data and storage

| Item | Size |
|---|---|
| Raw data: `sub-XX/ses-meg` only, 16 subjects | ~83 GB |
| Preprocessed output | ~0.55 GB per subject |
| Results | a few MB |

Raw and preprocessed data are **not** versioned (see `.gitignore`). They can be regenerated from OpenNeuro ds000117 v2.0.0 with the commands in `code/pipeline/README.md`.

On the lab server, the working directory is `$WORK/<user>/eegmeg` (separate 246 GB partition). Unused files there may be removed automatically after about 30 days, so result files are copied back to this repository after each session (`code/tools/sync_from_server.ps1`).

## Reproducibility measures

- **Pinned software** (`requirements.txt`) and a versioned pipeline (`code/pipeline/CHANGELOG.md`).
- **Fixed random seeds:** ICA 97; deep models `--seed 42`, plus subject, fold and expert offsets.
- **A JSON log per subject** for preprocessing (bad channels, ICA components removed, trials kept) and **a JSON file per subject × task** for results (all metrics, gate choices, fold details, hyperparameters).
- **Deterministic folds:** leave-one-run-out within subject, leave-one-subject-out across subjects.

## Measured runtimes (lab server)

| Step | Time |
|---|---|
| Preprocessing, one subject (6 runs) | 7.5 min (1 subject per process; 8 processes in parallel) |
| Classical models, one subject × one task | a few minutes on 4 cores |
| EEGNet smoke test (1 fold, 3 epochs) | 0.1 min on one L40S |
