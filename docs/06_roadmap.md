# 06: Roadmap, open decisions, risks

_Updated 13 Nov 2026 (evening)_

## 1. Next steps

| # | Step | Where | Estimate | Status |
|---|---|---|---|---|
| 1 | Download sub-02 … sub-16 (~78 GB) | Server, tmux `dl` | 1–2 h | In progress (13 Nov) |
| 2 | Deploy pipeline v1.2 on the server (`push_code_to_server.ps1`) | Lab PC | 5 min | To do (next session) |
| 3 | Preprocess the 16 subjects (`--n-jobs 8`) | Server, CPU | ~20–30 min | Sub-01 done |
| 3b | Classical models, 2 tasks × 16 subjects, then `aggregate.py`. Sub-01 switch results must be recomputed with v1.2. | Server, CPU | < 30 min | Sub-01 baselines done |
| 4 | Time one full deep subject, then deep models on 16 subjects × 2 tasks | Lab GPU | 1–2 sessions (to confirm) | Smoke test OK |
| 5 | Sync results to the PC; update `results/real_data/` and the journal | PC | 10 min | Each session |
| 6 | **Robustness experiment:** corrupt EEG, MEG or both on 20%/40% of trials (`--corrupt`) | Server | 1 session | Code ready (v1.2) |
| 7 | **Cross-subject experiment:** leave-one-subject-out (`cross_subject.py`) | Server, CPU | ~30 min per task | Code ready (v1.2) |
| 8 | **Interpretability:** gate choices vs signal quality; source orientation and depth per subject (MRI available in ds000117) | Code to add | 2+ sessions | To do |
| 9 | Second dataset (Cogitate MEG-EEG) | Server (space!) | Later | Decision needed |
| 10 | Paper writing: Methods draft ready (`04_methods.md`) | PC | In parallel | Started |

## 2. Decisions waiting for the supervisor or owner

1. **Main claim:** "switching beats fusion", or "robust adaptive fusion plus which modality, for whom and why"? The feasibility study supports the second.
2. **Tasks:** keep both (faces vs scrambled, famous vs unfamiliar) or focus on one?
3. **Second dataset:** Cogitate MEG-EEG, or a motor-imagery BCI dataset (Corsi et al.; the data may need a request to the authors)?
4. **Server:** `/scratch` access; whether long jobs can run overnight; whether SLURM must be used.

## 3. Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `/var/tmp` files deleted after ~30 days without use | Loss of data or results | Sync to PC after every session; raw data can be re-downloaded |
| `/var` partition fills up (shared with the system) | Server problems for everyone | Check `df -h /var/tmp`; no extra datasets; delete raw data after preprocessing if needed |
| Switch does not beat early fusion on real data | Weaker headline claim | Robustness and interpretability framing (already chosen) |
| EEG much weaker than MEG for all subjects | No switching benefit | Report honestly; the robustness test still applies; check EEG preprocessing (bad channels, reference) |
| Limited GPU time (~4 h/day) | Slow deep experiments | Resumable scripts; classical results first; run deep jobs in tmux |
| Code differences between PC and server | Results not reproducible | Edit only `code/pipeline/` on the PC, then `push_code_to_server.ps1`; note versions in `CHANGELOG.md` |
