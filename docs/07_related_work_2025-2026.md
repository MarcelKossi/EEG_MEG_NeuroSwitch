# 07: Related work 2025–2026 and positioning

_Literature search of 14 Nov 2026. It covers simultaneous or joint EEG+MEG decoding, studies using the Wakeman–Henson face data, and adaptive or quality-aware multimodal gating._

## 1. Recent studies

| Study | Data | Task | How EEG and MEG are combined | Main result | Relation to this work |
|---|---|---|---|---|---|
| **Messuti, Scarpetta, Sorrentino & Corsi (2026)**, *FUSE*, bioRxiv | Own dataset: **simultaneous** 74-ch EEG + Elekta TRIUX MEG, 20 subjects, source space (68 ROIs) | Motor-imagery BCI (2 classes) | Self-supervised encoder with a shared EEG–MEG latent space; linear SVM | Accuracy: fused **0.780**, EEG 0.768, MEG 0.688. Fused > MEG (p < 0.001); **fused vs EEG not significant (p = 0.14)**. MEG better than EEG in some subjects. | Same pattern as ours: fusion ≥ the best single modality, the gain over it is not significant, and the better modality varies across subjects. The **opposite modality wins** (EEG for motor imagery, MEG for faces), which supports a task-dependent choice. FUSE has no switching, no late-fusion baseline and no robustness test. |
| **Xiao et al. (2025)**, *BrainOmni*, NeurIPS 2025 (arXiv 2505.18185) | 1,997 h EEG + 656 h MEG pretraining; downstream EEG, MEG and EMEG datasets | Foundation model, 9 tasks | Sensor-aware tokenizer; joint EEG+MEG pretraining | Joint pretraining beat single-modality pretraining on every ablation dataset. SomatoMotor balanced accuracy: EMEG **0.863** vs EEG 0.783 vs MEG 0.838. | Shows a benefit of joint EEG+MEG input at large scale. It **does not use ds000117**, and it has no per-trial modality selection or robustness analysis. |
| **Li & Wang (2026)**, EEG-to-MEG generative framework, arXiv 2602.06990 | Two paired EEG–MEG datasets on Elekta (somatomotor; a famous/unfamiliar/scrambled face set) + 5 EEG datasets | Classification with EEG plus **synthesised** MEG | Pretrained EEG encoder → diffusion model that generates MEG; SVM on EEG + MEG | EEG + synthetic MEG beat EEG alone (median accuracy +10.7 % somatomotor, +4.8 % faces; 3-class face F1 0.390 → 0.438). Real MEG is still slightly better. | Confirms that MEG adds information to EEG for face stimuli. The 3-class task is not comparable with our binary tasks. **To verify:** which face dataset they used (the paper names it "NOD-MEG"). |
| **Huang, Cho, Gohil, Parker Jones & Woolrich (2025)**, *MEG-GPT*, arXiv 2510.18080 | **Wakeman–Henson** (19 subjects, **MEG only**) | 4 classes (famous, unfamiliar, scrambled, button press) | — | Group-level logistic regression: within subject 0.54 → **0.59** with MEG-GPT features; new subject 0.41 → 0.51 (chance 0.25). | Uses the same recordings but **MEG only**, with 4 classes and group-level training. The numbers cannot be compared with ours. Useful for showing that the dataset is a current benchmark. |
| **TNSRE (2025)**, "Enhanced Spatial Division Multiple Access BCI Performance via Incorporating MEG With EEG", doi:10.1109/TNSRE.2025.3550653 | Combined EEG + MEG | Visual BCI (SDMA) | — | Adding MEG to EEG improved BCI performance (from the title). **Details to verify** in the full text, which was not accessible. | Another 2025 study showing an EEG + MEG gain. |
| **Sun & Sheng (2026)**, *QA-MoE*, IJCAI 2026 | Clinical (ADNI, MIMIC-IV) | Clinical prediction | Mixture of experts with an **evidential quality score per modality**; unreliable modalities filtered before routing | Better than strong multimodal baselines under **noisy and missing modalities** (exact numbers not on the abstract page). | **Closest method** to our learned gate, which also uses per-trial signal-quality features, but outside neuroimaging. Supports the robustness framing (H3). |
| **Cogitate Consortium (2026)**, open multi-center MEG-EEG dataset, *Scientific Data* | Simultaneous MEG + EEG, several sites | Conscious visual perception | — | Dataset paper | **Best candidate for a second dataset** (multi-site, larger N), to test generalisation. |
| THINGS benchmark (bioRxiv, 2026), fMRI vs MEG vs EEG | THINGS-MEG (4 subjects) and THINGS-EEG (46 subjects), **different participants** | Object decoding | Separately compared | MEG ≫ single-subject EEG (53.0 % vs 8.8 % top-1); group-averaged EEG approaches MEG. | MEG carries more single-trial visual information than EEG, which is consistent with our MEG > EEG for faces. The recordings are not simultaneous. |

Older references used in the paper: Corsi et al. 2019 (fusion AUC 0.66 vs 0.58–0.61), Reichert et al. 2017 (MEG more accurate, EEG transfers better), Waldert et al. 2007 (fusion adds nothing).

## 2. What these studies show (2025–2026)

1. **Fusion usually matches or slightly exceeds the best single modality, but the gain over it is often not significant.** This holds in FUSE 2026 (EEG+MEG vs EEG: p = 0.14) and in our classical results (switch or early fusion vs early fusion: n.s.).
2. **Which modality is better depends on the task:** EEG for motor imagery (FUSE), MEG for visual object and face decoding (THINGS benchmark, Li & Wang, our results). It also varies across subjects within a task (FUSE; in our data EEG > MEG in 1/16 subjects for faces and 4/16 for famous vs unfamiliar).
3. **The field has moved to large pretrained models** (BrainOmni, MEG-GPT) and generative cross-modal models (Li & Wang). None of them selects a modality per trial or tests robustness to a corrupted modality.
4. **Quality-aware gating is an active topic in multimodal machine learning** (QA-MoE 2026; confidence-guided MoE gates, 2025), but it has not been applied to simultaneous EEG/MEG.

## 3. Positioning of this work

| Aspect | Recent studies | This work |
|---|---|---|
| Baselines | Usually EEG, MEG and one fusion scheme | EEG, MAG, GRAD, MEG, **early and late fusion**, 3 switching models, oracle; same classifier for all |
| Leakage control | Rarely reported in detail | Modality-isolated preprocessing (separate SSS, interpolation, referencing and ICA); leave-one-run-out; gates trained only on held-out training data |
| Per-trial modality selection | Not studied | Learned gate using expert confidences and signal quality |
| Oracle analysis | Not reported | Oracle reported **with its chance level**: the apparent complementarity of EEG and MEG errors matches what independent errors produce |
| Robustness to a corrupted modality | Not studied in M/EEG (QA-MoE: clinical data) | Controlled corruption of EEG or MEG (in progress) |
| Classifier dependence | — | LDA vs EEGNet on the same splits (in progress: on sub-01, EEGNet raised EEG from 61 % to 80 % and reversed the early- vs late-fusion ranking) |

**Honest claim:**
- We do **not** claim state-of-the-art decoding accuracy. No recent study reports the same tasks with the same protocol, and studies on the same recordings use different class definitions (MEG-GPT: 4 classes, MEG only).
- The contribution is a **controlled, leakage-free comparison of how to combine simultaneous EEG and MEG**, a learned switch that matches the best fusion and beats single modalities and late fusion, and an analysis of **when** adaptive selection can help (robustness) and when it cannot (clean data, unpredictable errors).

## Sources

- [FUSE: FUsing EEG–MEG in a Shared Embedding via self-supervised learning for BCI (bioRxiv 2026)](https://www.biorxiv.org/content/10.64898/2026.09.09.750152v1)
- [BrainOmni: A Brain Foundation Model for Unified EEG and MEG Signals (arXiv 2505.18185)](https://arxiv.org/pdf/2505.18185)
- [A Pre-trained EEG-to-MEG Generative Framework for Enhancing BCI Decoding (arXiv 2602.06990)](https://arxiv.org/pdf/2602.06990)
- [MEG-GPT: A transformer-based foundation model for magnetoencephalography data (arXiv 2510.18080)](https://arxiv.org/html/2510.18080v1)
- [Enhanced Spatial Division Multiple Access BCI Performance via Incorporating MEG With EEG (TNSRE 2025)](https://doi.org/10.1109/tnsre.2025.3550653)
- [QA-MoE: Quality-Aware and Stable Multimodal Mixture-of-Experts (IJCAI 2026)](https://ijcai.org/proceedings/2026/766)
- [Rethinking Gating Mechanism in Sparse MoE: Confidence-Guided Gate (arXiv 2505.19525)](https://arxiv.org/pdf/2505.19525)
- [An open multi-center MEG-EEG dataset for studying conscious visual perception (Scientific Data 2026)](https://www.nature.com/articles/s41597-026-07350-9)
- [A Quantitative Benchmark of Visual Information in Human Brain Recordings Across fMRI, MEG, and EEG (bioRxiv 2026)](https://www.biorxiv.org/content/10.64898/2026.01.11.698841v1.full)
- [Multisubject, multimodal face processing, ds000117 v2.0.0 (OpenNeuro)](https://openneuro.org/datasets/ds000117/versions/2.0.0)
