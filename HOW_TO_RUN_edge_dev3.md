# How to Run `edge_dev3`

`edge_dev3` is the webcam-based person-detection edge node. It runs YOLOv8
locally, watches for a person entering or leaving the frame, and uploads a
snapshot to Google Drive on each transition (capped at 2 uploads per run:
one ENTER, one LEAVE).

---

## 1. Prerequisites

- Python 3.9+
- A working webcam (index 0)
- A Google Cloud project with the **Google Drive API** enabled
- A **service account** + downloaded JSON key
- A Google Drive folder that you have **shared with the service account's email**

---

## 2. Install dependencies

From the repo root:

```bash
pip install ultralytics opencv-python google-api-python-client google-auth python-dotenv
```

The first run of YOLO will auto-download `yolov8n.pt` (~6 MB) if it isn't
already in the project root.

---

## 3. Set up Google credentials

1. In Google Cloud Console, create a **service account** under your project.
2. Generate a **JSON key** for it and save it as:

   ```
   edge_dev3/credentials.json
   ```

3. In Google Drive, create a folder (e.g. `cs131_snapshots`) and **share it
   with the service account's email address** (Editor access).
4. Copy that folder's ID from the URL
   (`https://drive.google.com/drive/folders/<FOLDER_ID>`).
5. Copy the example env file and fill it in:

   ```bash
   cp edge_dev3/.env.example edge_dev3/.env
   ```

   Then edit `edge_dev3/.env`:

   ```ini
   GOOGLE_APPLICATION_CREDENTIALS=credentials.json
   DRIVE_FOLDER_ID=<paste your folder ID here>
   CAMERA_INDEX=0
   MAX_SNAPSHOTS=2
   ```

> ⚠ Both `.env` and `credentials.json` are already in `.gitignore` — do **not** commit them.

---

## 4. Run it

```bash
cd edge_dev3
python main.py
```

You'll see a webcam window labeled **"Edge Dev 3 - Person Detection"**.
- **GREEN** banner: no person detected
- **RED** banner: at least one person detected

Press `q` or `Esc` to quit.

---

## 5. Snapshot behavior

- A snapshot is taken **only on a state transition**:
  - GREEN → RED  ⇒ saved as `enter_<timestamp>.jpg`
  - RED → GREEN  ⇒ saved as `leave_<timestamp>.jpg`
- Snapshots are saved locally to `edge_dev3/snapshots/` **and** uploaded to
  your Google Drive folder.
- Hard limit: **2 uploads per run** (`MAX_SNAPSHOTS = 2` in `main.py`).
  Restart the script to reset the counter.

---

## 6. Troubleshooting

| Problem | Likely fix |
|---|---|
| `Unable to open camera at index 0` | Try `open_camera(1)` in `main.py`, or close other apps using the webcam |
| `FileNotFoundError: credentials.json` | The JSON key isn't where `send.py` expects — check the path |
| `HttpError 404` from Drive | The folder ID is wrong, or you didn't share the folder with the service account email |
| `HttpError 403` from Drive | Drive API not enabled on the project, or the service account lacks access to the folder |
| Upload silently skipped | Check console — uploads are wrapped in try/except so detection keeps running |
