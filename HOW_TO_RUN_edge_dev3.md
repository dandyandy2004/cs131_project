# How to Run `edge_dev3`

`edge_dev3` is a webcam-based person-detection edge node. It runs YOLOv8
locally, watches for a person entering or leaving the frame, and on each
transition it uploads a snapshot to Firebase Cloud Storage **and** writes
an event document to Firestore (collection `events`).

---

## 1. Prerequisites

- Python 3.9+
- A working webcam
- A Firebase project (or existing Google Cloud project linked to Firebase)
- A service account JSON key with appropriate roles

---

## 2. Install dependencies

From the repo root:

```bash
pip install -r requirements.txt
```

The first run of YOLO will auto-download `yolov8n.pt` (~6 MB) if it isn't
already in the project root.

---

## 3. Set up Firebase

1. Go to the [Firebase Console](https://console.firebase.google.com/) and
   **create a project** (or select an existing Google Cloud project).
2. In the console, enable **Cloud Storage** and **Cloud Firestore**.
3. In the Google Cloud Console (IAM & Admin → Service Accounts), create a
   service account with these roles:
   - **Firebase Admin**
   - **Cloud Datastore User**
   - **Storage Object Admin**
4. Generate a **JSON key** for that service account and save it as:

   ```
   edge_dev3/firebase_credentials.json
   ```

5. Copy the env template and fill it in:

   ```bash
   cp edge_dev3/.env.example edge_dev3/.env
   ```

   Edit `edge_dev3/.env`:

   ```ini
   FIREBASE_CREDENTIALS=firebase_credentials.json
   FIREBASE_STORAGE_BUCKET=your-project.appspot.com
   DEVICE_ID=edge_dev3
   CAMERA_INDEX=0
   ```

> ⚠ Both `.env` and `firebase_credentials.json` are already in `.gitignore` —
> do **not** commit them.

---

## 4. Run it

```bash
cd edge_dev3
python main.py
```

You'll see a webcam window titled **"Edge Dev 3 - Person Detection"**.
- **GREEN** banner: no person detected
- **RED** banner: at least one person detected
- Each bounding box is labeled with the estimated distance in meters (e.g.
  `1.8m`) and the confidence score.

Press `q` or `Esc` to quit.

---

## 5. Snapshot behavior

- A snapshot is taken **only on a state transition**:
  - GREEN → RED  ⇒ saved as `enter_<timestamp>.jpg`
  - RED → GREEN  ⇒ saved as `leave_<timestamp>.jpg`
- Snapshots are saved locally to `edge_dev3/snapshots/` **and** uploaded to
  Firebase Cloud Storage at `snapshots/<label>_<timestamp>.jpg`.
- A Firestore document is written to the `events` collection with:
  `device_id`, `label`, `timestamp` (server time), `image_url`,
  `confidence`, `bbox_height_px`, `distance_estimate_m`.
- **No upload cap** — every transition uploads.

---

## 6. Troubleshooting

| Problem | Likely fix |
|---|---|
| `Unable to open camera at index 0` | Try `CAMERA_INDEX=1` in `.env`, or close other apps using the webcam |
| `FileNotFoundError: firebase_credentials.json` | The JSON key isn't where `send.py` expects — check `FIREBASE_CREDENTIALS` in `.env` |
| `FIREBASE_STORAGE_BUCKET is not set` | Add `FIREBASE_STORAGE_BUCKET=<your-bucket>` to `.env` |
| `google.auth.exceptions.RefreshError` / `invalid_grant` | Service account key is corrupted or its project is disabled — re-download the JSON key |
| `403 PERMISSION_DENIED` on Firestore | Service account lacks **Cloud Datastore User** role |
| `403` on Cloud Storage upload | Service account lacks **Storage Object Admin** role, or the bucket name in `FIREBASE_STORAGE_BUCKET` is wrong |
| `The default Firebase app already exists` | `firebase_admin.initialize_app` was called twice — should not happen with the current code; restart the process |
| Upload silently skipped | Check console — uploads are wrapped in try/except so detection keeps running |
