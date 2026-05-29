import os
from datetime import datetime

from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore, storage

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "firebase_credentials.json")
FIREBASE_STORAGE_BUCKET = os.getenv("FIREBASE_STORAGE_BUCKET")


def _init_firebase():
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


def upload_snapshot(
    local_path,
    label="event",
    confidence=0.0,
    matched_identity=None,
):
    """Upload snapshot to Firebase Cloud Storage and log event in Firestore."""
    _init_firebase()

    device_id = os.getenv("DEVICE_ID", "edge_dev1")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob_path = f"snapshots/{label}_{ts}.jpg"

    bucket = storage.bucket()
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(local_path, content_type="image/jpeg")
    blob.make_public()
    image_url = blob.public_url

    db = firestore.client()
    db.collection("events").add({
        "device_id": device_id,
        "label": label,
        "timestamp": firestore.SERVER_TIMESTAMP,
        "image_url": image_url,
        "confidence": float(confidence),
        "identity": matched_identity,
    })

    print(f"[send] {device_id} {label} identity={matched_identity} -> {image_url}")
    return {"image_url": image_url}
