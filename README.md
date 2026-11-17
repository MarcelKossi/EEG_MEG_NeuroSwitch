# When to trust EEG, MEG, or both? Adaptive modality switching for simultaneous M/EEG decoding

**Kossi Tamplare**, GD Goenka University  
Supervisor: **Dr Rajat Sharma**, Head of Department, GD Goenka University  
Joint paper in preparation.

_Status: experiments completed (14 November 2026); manuscript in preparation._

---

## Why this research

EEG and MEG are two windows on the same brain activity. EEG measures electric potentials on the scalp; MEG measures the magnetic fields just outside the head. Recorded together, they see the same neurons through different physics:

- **MEG** is almost blind to currents that point straight towards the scalp (radial sources), but it sees the others sharply, because the skull does not distort magnetic fields.
- **EEG** sees every orientation, including deeper sources, but the skull blurs it and it picks up more noise from electrodes, eye movements and muscles.

So which signal should a brain decoder use? Published studies on simultaneous recordings disagree:
- MEG wins in some tasks (Reichert et al., 2017);
- combining both wins in others (Corsi et al., 2019);
- sometimes combining adds nothing (Waldert et al., 2007; Messuti et al., 2026).

What these studies share is that they compare **fixed** recipes: EEG alone, MEG alone, or one way of fusing them, chosen in advance and applied to every trial and every person.

This project asks a different question: **can a decoder learn, trial by trial, when to rely on EEG, on MEG, or on both, and does that make it more accurate or more robust?** The question matters in practice. Signal quality changes from one trial to the next (a blink, a loose electrode, a head movement), and the "right" fusion recipe is rarely known in advance.

## The idea

```
               ┌─ EEG expert ───┐
single trial ─>├─ MEG expert ───┤──> switch picks one expert for this trial ──> decision
               └─ fused expert ─┘          ▲
                        how confident each expert is + how clean each signal looks
```

Three "experts" are trained on the same trials: one on EEG, one on MEG, and one on both together. A **switch** then decides, for each trial, which expert to trust.

The switch is compared with the two classic recipes:
- **Early fusion:** one model receives all EEG and MEG channels at once.
- **Late fusion:** separate EEG and MEG models, whose outputs are added together.

## What was done

1. **Feasibility study.** Before using real data, the idea was tested in a simulation built on a real head model and real recorded noise. It suggested that a switch should beat single modalities and late fusion, but probably not early fusion on clean data. The project was framed accordingly.
2. **Data.** I used OpenNeuro **ds000117** (Wakeman & Henson, 2015): 16 participants viewing famous, unfamiliar and scrambled faces, with **306 MEG and 70 EEG channels recorded simultaneously**. After cleaning, 13,537 of 14,157 trials were kept.
3. **Fair preprocessing.** EEG and MEG were cleaned **separately**, so the EEG-only model never receives information that leaked from MEG, and vice versa. The same trials were used for every model.
4. **Benchmark with a classical decoder** (regularised linear classifier) on two problems:
   - **faces vs scrambled images:** a strong brain response;
   - **famous vs unfamiliar faces:** a subtle one.
5. **Benchmark with a deep decoder** (EEGNet) on faces vs scrambled, to see whether the conclusions depend on the type of classifier.
6. **Robustness test.** One modality (EEG or MEG) was deliberately corrupted on 20 % or 40 % of the trials, to see which strategy copes with a degraded signal.

Every comparison is paired, using the same trials, folds and participants, and is tested across the 16 participants. The switch is always trained without access to the test data.

## What we found

**1. MEG decodes faces better than EEG, and combining both is better still.**

Faces vs scrambled, balanced accuracy (%), mean over 16 participants:

| Method | Classical decoder | Deep decoder (EEGNet) |
|---|---|---|
| EEG alone | 71.2 | 81.3 |
| MEG alone | 80.5 | 88.3 |
| Early fusion | **87.4** | 89.1 |
| Late fusion | 82.1 | **91.5** |
| Switch, learned | **87.7** | 90.8 |
| Switch, confidence-based | 84.3 | **91.8** |

**2. The best fixed recipe depends on the decoder, and the switch adapts.**
- With the classical decoder, early fusion is clearly better than late fusion. With EEGNet it is the reverse.
- A researcher who picks one recipe in advance can therefore lose 2–5 points.
- The switches stay close to whichever recipe is best:
  - classical decoder: learned switch level with early fusion;
  - EEGNet: confidence switch level with late fusion; the learned switch is 0.6 point below it, but 1.7 points above early fusion.

**3. When one signal degrades, the learned switch beats every fixed recipe.**

| Condition | Early fusion | Late fusion | Learned switch |
|---|---|---|---|
| Clean data | 87.4 | 82.1 | **87.7** |
| EEG corrupted (20 % / 40 % of trials) | 83.5 / 84.0 | 77.5 / 73.3 | **86.0 / 85.8** |
| MEG corrupted (20 % / 40 % of trials) | 83.9 / 81.2 | 79.1 / 76.7 | **85.2 / 83.5** |

The learned switch beats early fusion in all four corrupted conditions, in 14–15 of 16 participants. It also visibly **moves away from the damaged signal**: when EEG is corrupted, it hands more trials to the MEG expert, and when MEG is corrupted, it hands more to the EEG expert.

**4. There is no hidden "perfect switch" on clean data.** EEG and MEG often make mistakes on different trials. That leaves room, in theory, for a perfect switch that would always pick the right expert. But the size of that room is what chance alone would produce, so the errors cannot be predicted from the signals. This explains why no switch can do much better than the best fusion on clean data.

**5. Subtle distinctions remain hard.** Famous vs unfamiliar faces is decoded only slightly above chance (53–57 %) by every method.

### Hypotheses: outcome

| | Hypothesis | Outcome |
|---|---|---|
| H1 | The switch beats EEG alone and MEG alone | **Supported** against EEG (both problems) and against MEG (faces vs scrambled, both decoders). For famous vs unfamiliar, the gain over MEG is not significant. |
| H2 | It beats late fusion | **Supported with the classical decoder** (+5.6 points, 16/16 participants). **Not with EEGNet**, where late fusion is the best fixed recipe. |
| H3 | It is as accurate as early fusion and more robust | **Supported.** Level on clean data; better with a corrupted modality (+1.4 to +2.4 points). |
| H4 | Its choices are interpretable | **Partly supported.** It follows signal quality. A source-level explanation is left for future work. |

## What it means

**No single way of combining EEG and MEG is best in every situation.** A learned switch is a safe default:
- it stays close to the best fixed recipe whatever the decoder;
- it is the only method that keeps its accuracy when one of the two signals degrades.

The gains on clean data are small. The main value of switching is **robustness**, not a higher peak accuracy.

## Limitations

- **One dataset:** a single site, a single visual task, 16 participants.
- **Synthetic corruption:** the robustness test uses artificial artifacts, not real sensor failures.
- **Partial deep benchmark:** the deep decoder was evaluated on one problem only.
- **Within-person decoding only:** models were trained and tested within each participant.

## Next steps

- Test generalisation on a second simultaneous M/EEG dataset (for example the multi-site Cogitate dataset, 2026).
- Use real sensor failures instead of synthetic corruption.
- Decode across participants.
- Relate the switch's choices to where the brain activity comes from (source-level analysis).

## Repository guide

| Folder | Content |
|---|---|
| `docs/` | Research background, feasibility study, dataset, methods, computing environment, roadmap, related work 2025–2026 |
| `code/pipeline/` | Analysis code: preprocessing, classical and deep models, statistics. Commands are in its README. |
| `results/` | Feasibility results, result reports on the real data, and the raw result files |
| `journal/` | Research log: what was done, problems met, decisions |
| `presentations/` | Progress presentation |

The data are public (OpenNeuro ds000117) and are not stored in this repository.

## References

- BrainOmni: a brain foundation model for unified EEG and MEG signals (2025). *NeurIPS 2025*; arXiv:2505.18185.
- Corsi, M.-C. et al. (2019). Integrating EEG and MEG signals to improve motor imagery classification in brain–computer interface. *Int. J. Neural Systems*, 29(1), 1850014.
- Lawhern, V. J. et al. (2018). EEGNet: a compact convolutional neural network for EEG-based brain–computer interfaces. *J. Neural Eng.*, 15, 056013.
- Messuti, Scarpetta, Sorrentino & Corsi (2026). FUSE: fusing EEG–MEG in a shared embedding via self-supervised learning for BCI. *bioRxiv*.
- Reichert, C. et al. (2017). A comparative study on the detection of covert attention in event-related EEG and MEG signals to control a BCI. *Front. Neurosci.*, 11, 575.
- Wakeman, D. G. & Henson, R. N. (2015). A multi-subject, multi-modal human neuroimaging dataset. *Scientific Data*, 2, 150001.
- Waldert, S. et al. (2007). Decoding performance for hand movements: EEG vs. MEG. *Proc. IEEE EMBS*.

Full discussion of recent work: `docs/07_related_work_2025-2026.md`.

## Acknowledgements

I thank Dr Rajat Sharma for supervising this work. The data were obtained from the OpenNeuro database (accession number ds000117), collected by Wakeman and Henson with support from the UK Medical Research Council and Elekta Ltd. The analyses rely on MNE-Python, scikit-learn and PyTorch.

**Use of AI tools.** Parts of the code, the literature search, the feasibility simulation and the drafting of the documentation were developed with the assistance of an AI model (Claude, Anthropic). All experiments on the real dataset were run by me on the lab server. I checked and validated the code and the results, and I take full responsibility for them and their interpretation.
