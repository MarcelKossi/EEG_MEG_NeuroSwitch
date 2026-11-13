# Files copied from the server

`code/tools/sync_from_server.ps1` creates one dated folder here per sync, for example `2026-11-13_1745/`:

```
2026-11-13_1745/
├── results/
│   ├── classical/<task>/sub-XX.json   + summary_<task>_balanced_accuracy.md
│   └── deep/<task>/sub-XX.json        + summary_<task>_balanced_accuracy.md
└── preprocessing_logs/
    ├── sub-XX_log.json   (bad channels, ICA components, trials kept, per subject)
    └── *.log             (console output of the runs)
```

Do not edit these files. Write interpretations in `results/real_data/` and in the journal.
