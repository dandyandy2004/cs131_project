# How to Run the Local Dashboard

A Streamlit dashboard for testing the system **without Firebase**. The edge
device writes events to a local SQLite file; the dashboard polls that file
and shows the latest snapshot, GREEN/RED alert status, and a recent-event
table.

---

## 1. One-time setup

Install deps (from repo root):

```bash
pip install -r requirements.txt
```

Make sure `edge_dev3/.env` exists (copy from `.env.example` if not) and set:

```ini
LOCAL_MODE=1
DEVICE_ID=edge_dev3
CAMERA_INDEX=0
```

`FIREBASE_*` variables can stay blank in local mode.

---

## 2. Run the edge device (terminal 1)

```bash
cd edge_dev3
python main.py
```

The webcam window opens. On each GREEN↔RED transition the event is written
to `local_data/events.db` and the JPEG stays in `edge_dev3/snapshots/`.

---

## 3. Run the dashboard (terminal 2)

```bash
streamlit run dashboard/app.py
```

Streamlit will open `http://localhost:8501` in your browser. The page
auto-refreshes every 2 seconds (toggle off in the sidebar if you want).

What you see:
- **🟢 GREEN / 🔴 RED** banner — RED if any `enter` event in the last 30s.
- Latest snapshot image + confidence / distance / bbox height.
- Recent events table.

---

## 4. Switch back to Firebase

Set `LOCAL_MODE=0` in `edge_dev3/.env` (or remove the line). Edge writes
will go to Cloud Storage + Firestore again, and the dashboard will report
the SQLite file as empty (which is expected).

---

## Notes

- `local_data/` is gitignored.
- The dashboard never writes to the DB — it's read-only.
- To wipe local history: stop the edge process and delete `local_data/events.db`.
