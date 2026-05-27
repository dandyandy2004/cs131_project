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
    bbox_height_px=0,
    distance_estimate_ft=0.0,
):
    """Upload a snapshot to Firebase Cloud Storage and log an event in Firestore."""
    _init_firebase()

    device_id = os.getenv("DEVICE_ID", "edge_dev3")
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

from google.cloud import storage

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")


def upload_snapshot(local_path, label="event"):
    if not BUCKET_NAME:
        raise RuntimeError("GCS_BUCKET_NAME is not set — check edge_dev3/.env")

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    filename = f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    blob = bucket.blob(filename)

    blob.upload_from_filename(local_path)


    image_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    print("User can view image here:", image_url)   
    return filename

