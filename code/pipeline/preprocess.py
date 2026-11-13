#!/usr/bin/env python
"""Preprocess OpenNeuro ds000117 (simultaneous MEG + EEG, face processing).

Builds clean single trials for the EEG-only / MEG-only / fusion / switching models.

Per subject (6 runs):
  1. Read the raw FIF runs and apply channel info from the BIDS channels.tsv
     (306 MEG, 70 EEG, EOG061/EOG062, ECG063).
  2. MEG: automatic flat/noisy channel detection, then Maxwell filtering (SSS)
     with the subject's calibration + crosstalk files. All runs are moved to
     the head position of the first run, so MEG sensors mean the same thing
     in every run.
  3. Band-pass 0.1-40 Hz, events from events.tsv, resample to 200 Hz.
  4. EEG: automatic flat/noisy channel detection (union over runs),
     spherical-spline interpolation, average reference.
  5. ICA fitted SEPARATELY on EEG and on MEG (never mixed: an "EEG-only" model
     must not receive information that leaked from MEG channels, and vice versa).
     Ocular (EOG061/062) and cardiac (ECG063) components are removed.
  6. Epochs -0.2 to 0.8 s, baseline -0.2 to 0 s, peak-to-peak rejection.
     A rejected trial is removed for BOTH modalities, so every comparison is
     paired (same trials for EEG, MEG, fusion and switch).
  7. Save  <out>/sub-XX/sub-XX_epo.fif   (MNE epochs, all channels)
           <out>/sub-XX/sub-XX_data.npz  (float32 arrays read by the models)
           <out>/sub-XX/sub-XX_log.json  (what was done: bad channels, ICA, drops)

Usage (on the server, inside the virtual environment):
  python preprocess.py --bids-root $WORK/data/ds000117 --out $WORK/derivatives \
                       --subjects 1 --crop 120          # quick test (2 min/run)
  python preprocess.py --bids-root $WORK/data/ds000117 --out $WORK/derivatives \
                       --subjects 1-16 --n-jobs 8       # full run
"""
import argparse
import csv
import glob
import json
import os
import sys
import time
import traceback

import numpy as np

# keep each worker from grabbing all 128 cores
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import mne  # noqa: E402
from mne.preprocessing import ICA, find_bad_channels_maxwell, maxwell_filter  # noqa: E402

# ----------------------------------------------------------------------------
# Dataset facts (ds000117 v2.0.0, verified from its README / events.tsv / channels.tsv)
# ----------------------------------------------------------------------------
STIM_CODES = {  # trial_type -> (value, condition, repetition)
    "IniFF": (5, "famous", "initial"), "ImmFF": (6, "famous", "immediate"),
    "DelFF": (7, "famous", "delayed"),
    "IniUF": (13, "unfamiliar", "initial"), "ImmUF": (14, "unfamiliar", "immediate"),
    "DelUF": (15, "unfamiliar", "delayed"),
    "IniSF": (17, "scrambled", "initial"), "ImmSF": (18, "scrambled", "immediate"),
    "DelSF": (19, "scrambled", "delayed"),
}
EOG_CHS = ["EOG061", "EOG062"]
ECG_CH = "ECG063"
TSV_TYPES = {"MEGMAG": "mag", "MEGGRADPLANAR": "grad", "EEG": "eeg", "EOG": "eog",
             "ECG": "ecg", "MISC": "misc", "TRIG": "stim"}

DEFAULTS = dict(
    l_freq=0.1, h_freq=40.0, sfreq=200.0,
    tmin=-0.2, tmax=0.8,
    reject=dict(grad=4000e-13, mag=4e-12, eeg=150e-6),
    ica_n_meg=40, ica_n_eeg=30, ica_max_remove=4, seed=97,
    eeg_bad_z=5.0,
)


def log(msg, sub=None):
    tag = f"[sub-{sub:02d}] " if sub is not None else ""
    print(time.strftime("%H:%M:%S"), tag + msg, flush=True)


def parse_subjects(text):
    out = []
    for part in text.split(","):
        if "-" in part:
            a, b = part.split("-")
            out += list(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def read_tsv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def apply_channels_tsv(raw, tsv_path):
    """Set channel names/types/bads from BIDS channels.tsv (robust to old FIF names)."""
    rows = read_tsv(tsv_path)
    names = [r["name"] for r in rows]
    if names != raw.ch_names and len(names) == len(raw.ch_names):
        # Older FIF files may still say EEG061 etc. while the tsv says EOG061.
        raw.rename_channels(dict(zip(raw.ch_names, names)))
    types = {r["name"]: TSV_TYPES[r["type"]] for r in rows
             if r["type"] in TSV_TYPES and r["name"] in raw.ch_names}
    current = dict(zip(raw.ch_names, raw.get_channel_types()))
    change = {k: v for k, v in types.items() if current[k] != v}
    if change:
        raw.set_channel_types(change, on_unit_change="ignore")
    bads = [r["name"] for r in rows if r.get("status", "good") == "bad"]
    raw.info["bads"] = sorted(set(raw.info["bads"]) | set(bads))


def read_events(tsv_path, raw, trigger_delay):
    """Stimulus events (9 codes) from events.tsv -> MNE events + metadata rows."""
    sf = raw.info["sfreq"]
    events, meta = [], []
    for r in read_tsv(tsv_path):
        if r["trial_type"] not in STIM_CODES:
            continue  # button presses etc.
        code, cond, rep = STIM_CODES[r["trial_type"]]
        onset = float(r["onset"]) + trigger_delay
        samp = int(round(onset * sf)) + raw.first_samp
        if samp < raw.first_samp or samp > raw.last_samp:
            continue
        events.append([samp, 0, code])
        meta.append(dict(condition=cond, repetition=rep, trial_type=r["trial_type"],
                         stim_file=r.get("stim_file", "n/a")))
    return np.array(events, int).reshape(-1, 3), meta


def detect_eeg_bads(raw, z_thresh):
    """Flat or persistently noisy EEG channels (robust z of log MAD amplitude; brief blinks do not count)."""
    picks = mne.pick_types(raw.info, eeg=True, exclude=[])
    data = raw.get_data(picks=picks)
    sd = 1.4826 * np.median(np.abs(data - np.median(data, axis=1, keepdims=True)), axis=1)  # robust to blinks
    names = [raw.ch_names[p] for p in picks]
    logsd = np.log(sd + 1e-30)
    med = np.median(logsd)
    mad = np.median(np.abs(logsd - med)) * 1.4826 + 1e-12
    z = (logsd - med) / mad
    bad = [n for n, zz, s in zip(names, z, sd)
           if abs(zz) > z_thresh or s < 1e-3 * np.exp(med)]
    return bad


def run_ica(raws, ch_type, n_comp, max_remove, seed, sub):
    """Fit ICA on one modality only, find EOG/ECG components, apply to all runs."""
    raw_cat = mne.concatenate_raws([r.copy() for r in raws], on_mismatch="warn")
    raw_cat.filter(1.0, None, picks=[ch_type], verbose=False)  # ICA prefers >=1 Hz
    n_ch = len(mne.pick_types(raw_cat.info, meg=ch_type == "meg",
                              eeg=ch_type == "eeg", exclude="bads"))
    n_comp = int(min(n_comp, n_ch - 2))
    ica = ICA(n_components=n_comp, method="fastica", random_state=seed, max_iter="auto")
    ica.fit(raw_cat, picks=ch_type, verbose=False)
    excl, info = [], {"n_components": n_comp}
    eogs = [c for c in EOG_CHS if c in raw_cat.ch_names]
    if eogs:
        try:
            idx, _ = ica.find_bads_eog(raw_cat, ch_name=eogs, verbose=False)
            excl += list(idx)[:max_remove]
            info["eog"] = [int(i) for i in idx]
        except Exception as e:  # noqa: BLE001
            info["eog_error"] = str(e)
    try:
        if ECG_CH in raw_cat.ch_names:
            idx, _ = ica.find_bads_ecg(raw_cat, ch_name=ECG_CH, method="ctps", verbose=False)
        elif ch_type == "meg":
            idx, _ = ica.find_bads_ecg(raw_cat, method="ctps", verbose=False)
        else:
            idx = []
        excl += [i for i in list(idx)[:max_remove] if i not in excl]
        info["ecg"] = [int(i) for i in idx]
    except Exception as e:  # noqa: BLE001
        info["ecg_error"] = str(e)
    ica.exclude = sorted(set(int(i) for i in excl))
    info["excluded"] = ica.exclude
    log(f"ICA {ch_type}: {n_comp} comps, removed {ica.exclude}", sub)
    for r in raws:
        ica.apply(r, verbose=False)
    del raw_cat
    return info


def process_subject(sub, args):
    p = DEFAULTS
    t0 = time.time()
    bids = os.path.expanduser(args.bids_root)
    meg_dir = os.path.join(bids, f"sub-{sub:02d}", "ses-meg", "meg")
    run_files = sorted(glob.glob(os.path.join(meg_dir, f"sub-{sub:02d}_ses-meg_task-facerecognition_run-*_meg.fif")))
    if not run_files:
        raise FileNotFoundError(f"No run files in {meg_dir}")
    out_dir = os.path.join(os.path.expanduser(args.out), f"sub-{sub:02d}")
    os.makedirs(out_dir, exist_ok=True)
    npz_path = os.path.join(out_dir, f"sub-{sub:02d}_data.npz")
    if os.path.exists(npz_path) and not args.overwrite:
        log("already done, skipping (use --overwrite to redo)", sub)
        return {"subject": sub, "status": "skipped"}

    cal = glob.glob(os.path.join(meg_dir, "*acq-calibration_meg.dat"))
    ctc = glob.glob(os.path.join(meg_dir, "*acq-crosstalk_meg.fif"))
    cal = cal[0] if cal else None
    ctc = ctc[0] if ctc else None
    report = {"subject": sub, "runs": [], "calibration": cal, "crosstalk": ctc,
              "params": {k: v for k, v in p.items()}, "crop_s": args.crop}
    if cal is None or ctc is None:
        log("WARNING: calibration/crosstalk file missing -> SSS less precise", sub)

    raws, events_all, meta_all = [], [], []
    destination = None
    for f in run_files:
        run = int(f.split("_run-")[1].split("_")[0])
        log(f"run {run}: reading {os.path.basename(f)}", sub)
        raw = mne.io.read_raw_fif(f, preload=False, verbose=False)
        if args.crop:
            raw.crop(0, min(args.crop, raw.times[-1]))
        raw.load_data(verbose=False)
        tsv = f.replace("_meg.fif", "_channels.tsv")
        if os.path.exists(tsv):
            apply_channels_tsv(raw, tsv)
        raw.del_proj()
        keep = mne.pick_types(raw.info, meg=True, eeg=True, eog=True, ecg=True, exclude=[])
        ev, meta = read_events(f.replace("_meg.fif", "_events.tsv"), raw, args.trigger_delay)
        raw.pick(keep)

        # ---- MEG: bad channels + Maxwell filter (SSS) --------------------------
        noisy, flat = find_bad_channels_maxwell(
            raw, calibration=cal, cross_talk=ctc, origin=(0.0, 0.0, 0.04), coord_frame="head", verbose=False)
        raw.info["bads"] = sorted(set(raw.info["bads"]) | set(noisy) | set(flat))
        meg_bads = [b for b in raw.info["bads"] if b.startswith("MEG")]
        if destination is None:
            destination = raw.info["dev_head_t"]
        raw = maxwell_filter(raw, calibration=cal, cross_talk=ctc, origin=(0.0, 0.0, 0.04), coord_frame="head",
                             destination=destination, verbose=False)

        # ---- filtering, events, resampling ----------------------------------
        raw.filter(p["l_freq"], p["h_freq"], picks=["meg", "eeg", "eog", "ecg"],
                   n_jobs=1, verbose=False)
        raw, ev = raw.resample(p["sfreq"], events=ev, verbose=False)
        eeg_bads = detect_eeg_bads(raw, p["eeg_bad_z"])
        for m in meta:
            m["run"] = run
        raws.append(raw)
        events_all.append(ev)
        meta_all.append(meta)
        report["runs"].append(dict(run=run, n_stim_events=len(ev), meg_bads_sss=meg_bads,
                                   eeg_bads_detected=eeg_bads))
        log(f"run {run}: {len(ev)} stimuli, MEG bads {meg_bads}, EEG bads {eeg_bads}", sub)

    # ---- EEG: same bad set in every run, interpolate, average reference -----
    eeg_bad_union = sorted(set(b for r in report["runs"] for b in r["eeg_bads_detected"])
                           | set(b for raw in raws for b in raw.info["bads"]
                                 if not b.startswith("MEG")))
    report["eeg_bads_interpolated"] = eeg_bad_union
    for i, raw in enumerate(raws):
        raw.info["bads"] = list(eeg_bad_union)
        if eeg_bad_union:
            try:
                raw.interpolate_bads(reset_bads=True, mode="accurate", origin=(0.0, 0.0, 0.04), verbose=False)
            except Exception as e:  # noqa: BLE001  (e.g. missing electrode positions)
                log(f"EEG interpolation failed ({e!r}); dropping {eeg_bad_union}", sub)
                raw.info["bads"] = []
                raw.drop_channels(eeg_bad_union)
                report["eeg_bads_dropped_instead"] = eeg_bad_union
        raw.set_eeg_reference("average", projection=False, verbose=False)

    # ---- ICA, separately per modality ---------------------------------------
    if not args.no_ica:
        report["ica_meg"] = run_ica(raws, "meg", p["ica_n_meg"], p["ica_max_remove"], p["seed"], sub)
        report["ica_eeg"] = run_ica(raws, "eeg", p["ica_n_eeg"], p["ica_max_remove"], p["seed"], sub)

    # ---- epochs ---------------------------------------------------------------
    event_id = {f"{c}/{r}": v for (v, c, r) in STIM_CODES.values()}
    epochs_list = []
    import pandas as pd
    for raw, ev, meta in zip(raws, events_all, meta_all):
        present = {k: v for k, v in event_id.items() if v in set(ev[:, 2])}
        ep = mne.Epochs(raw, ev, event_id=present, tmin=p["tmin"], tmax=p["tmax"],
                        baseline=(None, 0), reject=p["reject"], preload=True,
                        metadata=pd.DataFrame(meta), on_missing="ignore", verbose=False)
        epochs_list.append(ep)
    n_before = sum(len(m) for m in meta_all)
    epochs = mne.concatenate_epochs(epochs_list, on_mismatch="warn", verbose=False)
    n_after = len(epochs)
    report["n_trials_before"] = n_before
    report["n_trials_after"] = n_after
    report["drop_rate"] = round(1 - n_after / max(n_before, 1), 4)
    if report["drop_rate"] > 0.25:
        log(f"WARNING: {report['drop_rate']:.0%} trials rejected - check data / thresholds", sub)

    epochs.save(os.path.join(out_dir, f"sub-{sub:02d}_epo.fif"), overwrite=True, verbose=False)

    picks = mne.pick_types(epochs.info, meg=True, eeg=True, exclude=[])
    X = epochs.get_data(picks=picks).astype(np.float32)
    ch_types = np.array(epochs.get_channel_types(picks=picks))
    md = epochs.metadata
    np.savez(npz_path, X=X, ch_names=np.array([epochs.ch_names[i] for i in picks]),
             ch_types=ch_types, times=epochs.times.astype(np.float32),
             condition=md["condition"].to_numpy(str), repetition=md["repetition"].to_numpy(str),
             run=md["run"].to_numpy(int), sfreq=np.float32(epochs.info["sfreq"]),
             subject=np.int32(sub))
    counts = md["condition"].value_counts().to_dict()
    report["condition_counts"] = {k: int(v) for k, v in counts.items()}
    report["n_channels"] = {t: int((ch_types == t).sum()) for t in ("eeg", "mag", "grad")}
    report["minutes"] = round((time.time() - t0) / 60, 1)
    report["status"] = "ok"
    with open(os.path.join(out_dir, f"sub-{sub:02d}_log.json"), "w") as f:
        json.dump(report, f, indent=2, default=str)
    log(f"done: {n_after}/{n_before} trials kept {report['condition_counts']}, "
        f"channels {report['n_channels']}, {report['minutes']} min", sub)
    return {"subject": sub, "status": "ok", "kept": n_after, "total": n_before}


def safe_process(sub, args):
    try:
        mne.set_log_level("ERROR")
        return process_subject(sub, args)
    except Exception as e:  # noqa: BLE001
        log("FAILED: " + repr(e), sub)
        traceback.print_exc()
        return {"subject": sub, "status": "failed", "error": repr(e)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bids-root", required=True, help="folder that contains sub-01 ... sub-16")
    ap.add_argument("--out", required=True, help="output folder for preprocessed data")
    ap.add_argument("--subjects", default="1-16", help="e.g. 1 or 1-16 or 1,3,5")
    ap.add_argument("--n-jobs", type=int, default=1, help="subjects processed in parallel")
    ap.add_argument("--crop", type=float, default=None, help="seconds per run (quick test)")
    ap.add_argument("--no-ica", action="store_true", help="skip ICA (faster, less clean)")
    ap.add_argument("--trigger-delay", type=float, default=0.0,
                    help="seconds added to event onsets (only shifts the time axis)")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    subs = parse_subjects(args.subjects)
    log(f"MNE {mne.__version__}; subjects {subs}; n_jobs {args.n_jobs}")
    if args.n_jobs > 1 and len(subs) > 1:
        from joblib import Parallel, delayed
        res = Parallel(n_jobs=args.n_jobs)(delayed(safe_process)(s, args) for s in subs)
    else:
        res = [safe_process(s, args) for s in subs]
    print("\nSUMMARY")
    for r in res:
        print(r)
    if any(r["status"] == "failed" for r in res):
        sys.exit(1)


if __name__ == "__main__":
    main()
