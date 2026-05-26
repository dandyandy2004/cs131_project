# How to Run the Fog Layer

The fog layer subscribes to the Firestore `events` collection in real time,
prints each new event as JSON, and computes an aggregate GREEN/RED alert
status based on recent events from any edge device.

---

## 1. Prerequisites

- Python 3.9+
- A Firebase project with the `events` Firestore collection already being
  written by at least one edge device (see `HOW_TO_RUN_edge_dev3.md`)
- A service account JSON key with **Cloud Datastore User** role (the same
  key used by the edge devices works fine)

---

## 2. Install dependencies

From the repo root:

```bash
pip install -r requirements.txt
```

---

## 3. Set up credentials

1. Save the Firebase service account JSON key as:

   ```
   fog/firebase_credentials.json
   ```

2. Copy the env template and fill it in:

   ```bash
   cp fog/.env.example fog/.env
   ```

   Edit `fog/.env`:

   ```ini
   FIREBASE_CREDENTIALS=firebase_credentials.json
   FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   ```

> ⚠ `.env` and `firebase_credentials.json` are gitignored — do **not** commit them.

---

## 4. Run it

```bash
cd fog
python main.py
```

Expected output: a one-line `[fog] listening for events…` startup line,
then, on each new event document, a pretty-printed JSON block followed by
an aggregate alert line:

```
{
  "device_id": "edge_dev3",
  "label": "enter",
  "timestamp": "2026-05-26T18:01:33.412+00:00",
  "image_url": "https://storage.googleapis.com/your-project.appspot.com/snapshots/enter_20260526_180133.jpg",
  "confidence": 0.93,
  "bbox_height_px": 412,
  "distance_estimate_m": 2.5
}
[fog] alert status: RED
```

The alert logic: **RED** if any device emitted an `enter` event within
the last 30 seconds, otherwise **GREEN**.

Press `Ctrl+C` to stop.
