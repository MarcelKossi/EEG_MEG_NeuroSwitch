# When to trust EEG, MEG, or both: adaptive modality switching for simultaneous M/EEG decoding

**Kossi Tamplare**, GD Goenka University  
Supervisor: **Dr Rajat Sharma**, Head of Department, GD Goenka University  
This repository supports a joint paper currently in preparation.

_Status: active research. Last updated 13 November 2026._

---

## Motivation

EEG and MEG record the same neural currents through different physics. MEG is nearly blind to radially oriented sources but sees tangential ones with little spatial blurring. EEG sees both orientations, but the skull smears it and it is more exposed to electrode and ocular noise. As a result, published comparisons on simultaneously recorded data disagree:
- MEG decodes better in some tasks (Reichert et al., 2017);
- fusion helps in others (Corsi et al., 2019);
- and sometimes fusion adds nothing (Waldert et al., 2007).

These studies compare **fixed** choices. This project asks whether a decoder can **learn when to rely on EEG, on MEG, or on both**, and whether doing so makes decoding more accurate or more robust.

## Research questions and hypotheses

| | Hypothesis | How it is tested |
|---|---|---|
| H1 | A switching model outperforms EEG-only and MEG-only decoding | Paired comparison across 16 subjects |
| H2 | It outperforms late fusion, which weighs a weak modality equally | Same |
| H3 | It is at least as accurate as early fusion and **more robust when one modality is corrupted** | Same, plus controlled corruption of EEG or MEG |
| H4 | The switch's choices are interpretable: they follow trial-level signal quality and, across subjects, source orientation and depth | Gate-choice analysis; source-level analysis (planned) |

A feasibility study on a realistic head model ([docs/02](docs/02_feasibility_study.md)) supported H1 and H2 but showed **no accuracy gain over early fusion on clean data**. The project therefore treats **robustness (H3) and interpretability (H4)** as its main expected contributions, rather than a raw accuracy gain over fusion.

## Data

**OpenNeuro ds000117 v2.0.0** (Wakeman & Henson, 2015; CC0):
- 16 participants viewing famous, unfamiliar and scrambled faces;
- 306-channel MEG and 70-channel EEG recorded **simultaneously**;
- 6 runs per participant, about 885 trials per participant.

Two decoding problems are used: faces vs scrambled (strong, early N170/M170 response) and famous vs unfamiliar (subtle, later). Details: [docs/03](docs/03_dataset_ds000117.md).

## Approach

```
               ┌─ EEG expert ───┐
single trial ─>├─ MEG expert ───┤──> gate selects one expert per trial ──> decision
               └─ fused expert ─┘          ▲
                          expert confidences + label-free signal quality of each modality
```

- **Identical experts.** All experts share one architecture: shrinkage LDA on time-window means, or EEGNet. Only the input channels differ.
- **Modality isolation.** SSS, interpolation, re-referencing and ICA are all computed **separately** for EEG and MEG, so the EEG-only model never receives MEG information.
- **No test leakage.** The gate is trained only on held-out predictions from the training runs or subjects.
- **Honest upper bound.** The oracle switch is reported next to the accuracy expected by chance if EEG and MEG errors were independent.

Full methods: [docs/04_methods.md](docs/04_methods.md).

## Results so far

**Feasibility simulation** (realistic head model and noise, 16 simulated subjects; *not real data*). The learned switch reached:
- 80.8% accuracy, vs 71.2% for EEG, 74.0% for MEG and 78.6% for late fusion;
- **80.6% for early fusion**, i.e. no significant difference.

The oracle's apparent ~10-point headroom matched what independent errors produce by chance (90.9% observed vs 92.0% expected). See [results/feasibility_simulation](results/feasibility_simulation/SUMMARY.md).

**Real data:** the preprocessing has been validated on subject 01 (879/887 trials kept). The group analysis on all 16 subjects is in progress. Preliminary single-subject numbers are in [results/real_data](results/real_data/). They are not interpreted until the full sample is available.

## Repository structure

```
├── README.md
├── requirements.txt              pinned software versions
├── journal/JOURNAL.md            research log: what was done, problems, decisions
├── docs/
│   ├── 01_research_overview.md   question, physics, literature, hypotheses
│   ├── 02_feasibility_study.md   simulation design and results
│   ├── 03_dataset_ds000117.md    verified dataset facts
│   ├── 04_methods.md             methods (draft of the paper's section)
│   ├── 05_server_guide.md        computing environment and reproducibility
│   └── 06_roadmap.md             next steps, open decisions, risks
├── code/
│   ├── pipeline/                 preprocessing, models, statistics (see its README)
│   ├── feasibility_simulation/   simulation study
│   └── tools/                    PowerShell helpers to move code/results to and from the server
├── results/
│   ├── feasibility_simulation/
│   ├── real_data/
│   └── server_sync/              raw result files copied from the server
└── presentations/
```

## Reproducing the analysis

```bash
pip install -r requirements.txt          # PyTorch: install the CUDA build first (see docs/05)
python code/pipeline/preprocess.py       --bids-root <ds000117> --out derivatives --subjects 1-16 --n-jobs 8
python code/pipeline/classical_models.py --deriv derivatives --out results/classical --task faces_vs_scrambled
python code/pipeline/cross_subject.py    --deriv derivatives --out results/cross_subject --task faces_vs_scrambled
python code/pipeline/deep_models.py      --deriv derivatives --out results/deep --task faces_vs_scrambled
python code/pipeline/aggregate.py        --results results/classical
```

All steps, options and runtimes: [code/pipeline/README.md](code/pipeline/README.md).

## References

- Corsi, M.-C. et al. (2019). Integrating EEG and MEG signals to improve motor imagery classification in brain–computer interface. *Int. J. Neural Systems*, 29(1), 1850014.
- Reichert, C. et al. (2017). A comparative study on the detection of covert attention in event-related EEG and MEG signals to control a BCI. *Front. Neurosci.*, 11, 575.
- Waldert, S. et al. (2007). Decoding performance for hand movements: EEG vs. MEG. *Proc. IEEE EMBS*.
- Wakeman, D. G. & Henson, R. N. (2015). A multi-subject, multi-modal human neuroimaging dataset. *Scientific Data*, 2, 150001.
- Lawhern, V. J. et al. (2018). EEGNet. *J. Neural Eng.*, 15, 056013.
- Gramfort, A. et al. (2013). MEG and EEG data analysis with MNE-Python. *Front. Neurosci.*, 7, 267.

## Acknowledgements

I thank Dr Rajat Sharma for supervising this work. The data were obtained from the OpenNeuro database (accession number ds000117), collected by Wakeman and Henson with support from the UK Medical Research Council and Elekta Ltd. The analyses rely on MNE-Python, scikit-learn and PyTorch.

**Use of AI tools.** Parts of the code, the literature search, the feasibility simulation and the drafting of the documentation were developed with the assistance of an AI model (Claude, Anthropic). All experiments on the real dataset were run by me on the lab server. I checked and validated the code and the results, and I take full responsibility for them and their interpretation.
