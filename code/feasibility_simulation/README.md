# Feasibility simulation code (2 Nov 2026)

| File | Role |
|---|---|
| `sim_switch.py` | Simulates 16 subjects on the real MNE `sample` head model and noise covariance, trains EEG / MEG / fused experts (PCA + shrinkage LDA), late fusion, switches and oracle, with 5-fold CV. Writes `res_<scenario>.json`. |
| `analyze.py` | Group statistics (mean ± SD, Wilcoxon), physics correlations, gate choices. |

## How it was run

The simulation needs MNE-Python and the MNE testing data (`MEG/sample`: forward model, noise covariance, raw file).

```bash
export MNE_SAMPLE_DIR=/path/to/mne-testing-data/MEG/sample/
export SIM_OUT_DIR=results/feasibility_simulation/raw
python sim_switch.py clean  16 150e-9 0      # scenario name, n subjects, source strength (A·m), artifact rate
python sim_switch.py lowsnr 16 80e-9  0
python sim_switch.py art20  16 150e-9 0.2
python sim_switch.py art40  16 150e-9 0.4
python analyze.py $SIM_OUT_DIR
```

Results: `results/feasibility_simulation/`. Report: `docs/02_feasibility_study.md`.
