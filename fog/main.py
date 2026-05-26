import json
import os
import threading
import time

from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

from receive import watch_events
from decision import apply_alert_logic

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "firebase_credentials.json")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")

_seen_ids = set()
_lock = threading.Lock()


def _init_firebase():
    if firebase_admin._apps:
        return
    if not os.path.exists(FIREBASE_CREDENTIALS):
        raise FileNotFoundError(
            f"Firebase service account file not found: {FIREBASE_CREDENTIALS}"
        )
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    options = {}
    if FIREBASE_STORAGE_BUCKET:
        options["storageBucket"] = FIREBASE_STORAGE_BUCKET
    firebase_admin.initialize_app(cred, options or None)


def _serialize(event):
    out = dict(event)
    ts = out.get("timestamp")
    if ts is not None and hasattr(ts, "isoformat"):
        out["timestamp"] = ts.isoformat()
    return out


def _on_snapshot(col_snapshot, changes, read_time):
    new_events = []
    all_events = []

    with _lock:
        for change in changes:
            doc = change.document
            data = doc.to_dict() or {}
            if change.type.name == "ADDED" and doc.id not in _seen_ids:
                _seen_ids.add(doc.id)
                new_events.append(data)

        for doc in col_snapshot:
            data = doc.to_dict() or {}
            all_events.append(data)

    for ev in new_events:
        print(json.dumps(_serialize(ev), indent=2, default=str))

    status = apply_alert_logic(all_events)
    print(f"[fog] alert status: {status}")


def main():
    _init_firebase()
    watch_events(_on_snapshot)
    print("[fog] listening for events… (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[fog] stopping.")


if __name__ == "__main__":
    main()
