# EEG / MEG / Fusion / Switching pipeline (ds000117)

| File | What it does | Needs |
|---|---|---|
| `preprocess.py` | Filtering, cleaning (SSS, bad channels, ICA), cutting trials, saving | CPU |
| `classical_models.py` | Shrinkage-LDA: EEG, MAG, GRAD, MEG, early fusion, late fusion, 3 switches, oracle | CPU, minutes |
| `deep_models.py` | EEGNet: same comparison with deep experts | GPU (or `--device cpu`, slower) |
| `cross_subject.py` | Leave-one-subject-out version of the classical comparison | CPU |
| `aggregate.py` | Group table, Wilcoxon tests, chance-level oracle, gate choices → Markdown | CPU |
| `offline_checks.py` | Checks computed from saved results only: repeat the group tests without some subjects (`--exclude`), and test whether each model is above chance | CPU, seconds |
| `common.py` | Shared rules: folds, gates, late fusion, oracle, corruption, metrics (used by all model scripts) | — |

Data: OpenNeuro **ds000117 v2.0.0**, 16 subjects, 6 runs each, about 885 trials per subject.
Raw MEG/EEG is about **5.2 GB per subject, 83 GB in total**.

---

## 0. Deploy the code on the server

From a lab computer (PowerShell), copy `code/pipeline` to the server:

```powershell
powershell -ExecutionPolicy Bypass -File code\tools\push_code_to_server.ps1
```

The working directory on the server (`$WORK`) holds the Python environment, the data and the results. It is defined in `env.sh`; see `docs/05_server_guide.md`.

**Every new login** starts with:

```bash
source $WORK/$USER/eegmeg/env.sh && cd $WORK/eegmeg_pipeline && source ../.venv/bin/activate
```

## 1. Download the data (inside tmux)

```bash
tmux new -s dl
source $WORK/$USER/eegmeg/env.sh && cd $WORK && source .venv/bin/activate
df -h $WORK                            # $WORK is on the /var partition: need > 90 GB free
openneuro-py download --dataset ds000117 --target-dir $WORK/data/ds000117 --include sub-01/ses-meg
du -sh $WORK/data/ds000117                # about 5.2 GB
```

If subject 1 looks right, download the other 15 (about 78 GB). This can run unattended, overnight if allowed:

```bash
for s in $(seq -w 2 16); do
  openneuro-py download --dataset ds000117 --target-dir $WORK/data/ds000117 --include sub-$s/ses-meg
done
```

- **Leave tmux:** Ctrl+B, then D.
- **Come back:** `tmux attach -t dl`.
- **If a download stops:** rerun the same command. Finished files are skipped.

## 2. Preprocess

**Quick test.** Subject 1, first 2 minutes of each run (a few minutes):

```bash
python preprocess.py --bids-root $WORK/data/ds000117 --out $WORK/derivatives_test --subjects 1 --crop 120
```

Check that the last line says `status: ok`, then open `$WORK/derivatives_test/sub-01/sub-01_log.json`:

- **EEG bad channels:** normally 0–6. More than 10 means something is wrong; tell me.
- **ICA:** usually 1–4 components removed for each of `ica_meg` and `ica_eeg`.
- **Trial drop rate:** normally under 15%.

**Full run.** 16 subjects, 8 at a time (each uses about 4–8 GB RAM and 4 cores):

```bash
python preprocess.py --bids-root $WORK/data/ds000117 --out $WORK/derivatives --subjects 1-16 --n-jobs 8 2>&1 | tee preprocess.log
```

Output is about 0.6 GB per subject, in `$WORK/derivatives/sub-XX/`. A subject that is already done is skipped; add `--overwrite` to redo it.

## 3. Classical models (CPU, about 2–5 min per subject per task)

```bash
python classical_models.py --deriv $WORK/derivatives --out $WORK/results/classical --task faces_vs_scrambled --n-jobs 16
python classical_models.py --deriv $WORK/derivatives --out $WORK/results/classical --task famous_vs_unfamiliar --n-jobs 16
python aggregate.py --results $WORK/results/classical
```

The tables are saved as `$WORK/results/classical/summary_<task>_balanced_accuracy.md`.

## 4. Deep models (GPU)

```bash
export CUDA_VISIBLE_DEVICES=0             # check nvidia-smi first: use a free GPU
python deep_models.py --deriv $WORK/derivatives --out $WORK/results/deep --subjects 1 --quick
```

The quick test trains 1 fold for 3 epochs and saves nothing. If it prints `Quick test OK`, launch the full run inside tmux:

```bash
python deep_models.py --deriv $WORK/derivatives --out $WORK/results/deep --task faces_vs_scrambled --subjects 1-16 2>&1 | tee deep_faces.log
python deep_models.py --deriv $WORK/derivatives --out $WORK/results/deep --task famous_vs_unfamiliar --subjects 1-16 2>&1 | tee deep_famous.log
python aggregate.py --results $WORK/results/deep
```

- **Resumable:** finished subjects are skipped, so the work can be split over several 4-hour sessions.
- **Add `--with-mag-grad`** to also train separate magnetometer and gradiometer experts (+40% time).

## 5. Cross-subject validation (CPU, ~15–30 min per task with `--n-jobs 16`)

```bash
python cross_subject.py --deriv $WORK/derivatives --out $WORK/results/cross_subject --task faces_vs_scrambled --n-jobs 16
python cross_subject.py --deriv $WORK/derivatives --out $WORK/results/cross_subject --task famous_vs_unfamiliar --n-jobs 16
python aggregate.py --results $WORK/results/cross_subject
```

## 6. Robustness experiment (corrupted modality)

Add `--corrupt eeg|meg|both --corrupt-rate 0.2` (or `0.4`) to `classical_models.py`, `cross_subject.py` or `deep_models.py`. Always write to a **separate** results folder:

```bash
for m in eeg meg both; do for r in 0.2 0.4; do
  python classical_models.py --deriv $WORK/derivatives --out $WORK/results/robust_${m}_${r} \
         --task faces_vs_scrambled --corrupt $m --corrupt-rate $r --n-jobs 16
  python aggregate.py --results $WORK/results/robust_${m}_${r}
done; done
```

## 7. Bring the results home

The `summary_*.md` files and `results/*/*/sub-XX.json` are small. Copy them to your laptop with `scp`, or email them to yourself.

---

## Rules

- **Disk:** everything stays in `$WORK/$USER/eegmeg`, on the `/var` partition (246 GB, shared with the system). Check it with `df -h $WORK` (not `df -h /`) and never let it fill up.
- **Back-ups:** `$WORK` may be cleaned of files unused for about 30 days. Keep the scripts and the `results/` folder copied elsewhere too.
- **GPUs:** one GPU only (`CUDA_VISIBLE_DEVICES=0` or `1`, whichever `nvidia-smi` shows free).
- **SLURM:** if jobs must go through the scheduler, wrap these commands in an `sbatch` script.

## Design choices (for the Methods section)

- **Modality isolation:** SSS uses only MEG. EEG interpolation and average reference use only EEG. ICA is fitted separately for EEG and for MEG. So the EEG-only model never receives MEG information, and vice versa.
- **Paired trials:** a trial rejected in either modality is removed for all models.
- **Cross-validation:** leave-one-run-out (6 folds), so trials from the same run are never split between training and testing.
- **Gates:**
  - Classical: the gates learn only from inner leave-one-run-out predictions on training runs.
  - Deep: one training run is held out for early stopping and gate training.
  - In both, the test run's labels are never used to pick an expert.
- **Same classifier for every modality** (shrinkage LDA, or EEGNet), with equal class priors or class-weighted loss. Balanced accuracy is the main metric, because faces outnumber scrambled trials 2:1.
- **Oracle:** reported only as an upper bound, next to the chance level `1 − (1 − acc_EEG)(1 − acc_MEG)`.
