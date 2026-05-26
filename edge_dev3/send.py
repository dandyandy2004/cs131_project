import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

LOCAL_MODE = os.getenv("LOCAL_MODE", "0") == "1"
LOCAL_DB_PATH = os.getenv(
    "LOCAL_DB_PATH",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "local_data", "events.db")),
)
FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "firebase_credentials.json")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")


def _init_sqlite():
    os.makedirs(os.path.dirname(LOCAL_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(LOCAL_DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            label TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            image_path TEXT NOT NULL,
            confidence REAL NOT NULL,
            bbox_height_px INTEGER NOT NULL,
            distance_estimate_ft REAL NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def _upload_local(local_path, label, confidence, bbox_height_px, distance_estimate_ft, device_id):
    abs_path = os.path.abspath(local_path)
    ts = datetime.now().isoformat(timespec="seconds")
    conn = _init_sqlite()
    conn.execute(
        "INSERT INTO events "
        "(device_id, label, timestamp, image_path, confidence, bbox_height_px, distance_estimate_ft) "
        "VALUES (?,?,?,?,?,?,?)",
        (
            device_id,
            label,
            ts,
            abs_path,
            float(confidence),
            int(bbox_height_px),
            float(distance_estimate_ft),
        ),
    )
    conn.commit()
    conn.close()
    print(f"[send] LOCAL {device_id} {label} -> {abs_path} (db: {LOCAL_DB_PATH})")
    return {"image_url": abs_path, "doc_ref": None}


def _init_firebase():
    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        return
    if not FIREBASE_STORAGE_BUCKET:
        raise RuntimeError("FIREBASE_STORAGE_BUCKET is not set — check .env")
    if not os.path.exists(FIREBASE_CREDENTIALS):
        raise FileNotFoundError(
            f"Firebase service account file not found: {FIREBASE_CREDENTIALS}"
        )
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred, {"storageBucket": FIREBASE_STORAGE_BUCKET})


def _upload_firebase(local_path, label, confidence, bbox_height_px, distance_estimate_ft, device_id):
    from firebase_admin import firestore, storage

    _init_firebase()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob_path = f"snapshots/{label}_{ts}.jpg"

    bucket = storage.bucket()
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path, content_type="image/jpeg")
    blob.make_public()
    image_url = blob.public_url

    db = firestore.client()
    doc_ref = db.collection("events").add({
        "device_id": device_id,
        "label": label,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "image_url": image_url,
        "confidence": float(confidence),
        "bbox_height_px": int(bbox_height_px),
        "distance_estimate_ft": float(distance_estimate_ft),
    })

    print(f"[send] {device_id} {label} -> {image_url}")
    return {"image_url": image_url, "doc_ref": doc_ref}


def upload_snapshot(
    local_path,
    label="event",
    confidence=0.0,
    bbox_height_px=0,
    distance_estimate_ft=0.0,
):
    """Persist a snapshot + event. Local SQLite if LOCAL_MODE=1, else Firebase."""
    device_id = os.getenv("DEVICE_ID", "edge_dev3")
    if LOCAL_MODE:
        return _upload_local(
            local_path, label, confidence, bbox_height_px, distance_estimate_ft, device_id
        )
    return _upload_firebase(
        local_path, label, confidence, bbox_height_px, distance_estimate_ft, device_id
    )
