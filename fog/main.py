import os
import time
import tempfile
from datetime import datetime

import cv2
import numpy as np
import requests
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore, storage

from decision import DeviceTracker
from receive import start_listener

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

try:
    import Jetson.GPIO as GPIO
    _GPIO = True
except ImportError:
    _GPIO = False
    print("[fog] Jetson.GPIO not available — LED output disabled")

RED_PIN   = int(os.getenv("LED_RED_PIN",   "11"))
GREEN_PIN = int(os.getenv("LED_GREEN_PIN", "13"))


def _setup_gpio():
    if not _GPIO:
        return
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(RED_PIN,   GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(GREEN_PIN, GPIO.OUT, initial=GPIO.HIGH)


def _set_led(status):
    if not _GPIO:
        return
    GPIO.output(RED_PIN,   GPIO.HIGH if status == "RED" else GPIO.LOW)
    GPIO.output(GREEN_PIN, GPIO.LOW  if status == "RED" else GPIO.HIGH)


def _init_firebase():
    cred_path = os.getenv("FIREBASE_CREDENTIALS", "firebase_credentials.json")
    bucket    = os.getenv("FIREBASE_STORAGE_BUCKET")
    if not os.path.exists(cred_path):
        raise FileNotFoundError(f"Credentials not found: {cred_path}")
    firebase_admin.initialize_app(
        credentials.Certificate(cred_path),
        {"storageBucket": bucket},
    )


def _download_image(url):
    try:
        resp = requests.get(url, timeout=5)
        arr = np.frombuffer(resp.content, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"[fog] Failed to download {url}: {e}")
        return None


def _stitch_and_upload(snapshot_urls, identity):
    """Download latest snapshot from each device, stitch side-by-side, upload as 360° view."""
    frames = []
    for dev, url in sorted(snapshot_urls.items()):  # sorted so order is deterministic
        img = _download_image(url)
        if img is not None:
            cv2.putText(img, dev, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            frames.append(img)

    if not frames:
        return None

    # Resize all frames to the same height before stitching
    h = min(f.shape[0] for f in frames)
    resized = [cv2.resize(f, (int(f.shape[1] * h / f.shape[0]), h)) for f in frames]
    combined = np.hstack(resized)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            cv2.imwrite(tmp.name, combined)
            tmp_path = tmp.name

        blob = storage.bucket().blob(f"combined/{identity}_{ts}_360view.jpg")
        blob.upload_from_filename(tmp_path, content_type="image/jpeg")
        blob.make_public()
        return blob.public_url
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def run():
    _init_firebase()
    db = firestore.client()
    tracker = DeviceTracker()
    _setup_gpio()

    last_status = [None]
    latest_snapshots = {}  # device_id -> most recent image_url

    def _push_status(status, combined_url=None, identity=None):
        if status == last_status[0] and combined_url is None:
            return
        last_status[0] = status
        _set_led(status)
        doc = {
            "status": status,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "devices": tracker.device_summary(),
        }
        if combined_url:
            doc["combined_image_url"] = combined_url
            doc["identity"] = identity
        db.collection("combined_status").document("current").set(doc)
        print(f"[fog] *** {status} ***  identity={identity}  devices={tracker.device_summary()}")

    def on_event(device_id, label, identity, image_url):
        if image_url:
            latest_snapshots[device_id] = image_url

        tracker.update(device_id, label, identity)
        status = tracker.combined_status()

        combined_url = None
        if status == "RED" and status != last_status[0]:
            # New blacklist hit — stitch 360° view from both devices' latest snapshots
            print(f"[fog] Blacklist hit: {identity} on {device_id} — stitching 360° view")
            combined_url = _stitch_and_upload(latest_snapshots, identity or "unknown")
            if combined_url:
                print(f"[fog] 360° view uploaded: {combined_url}")
                db.collection("combined_alerts").add({
                    "identity": identity,
                    "triggered_by": device_id,
                    "timestamp": firestore.SERVER_TIMESTAMP,
                    "combined_image_url": combined_url,
                    "device_snapshots": dict(latest_snapshots),
                })

        _push_status(status, combined_url, identity)

    print("[fog] Listening for events from all edge devices...")
    unsubscribe = start_listener(db, on_event)

    try:
        while True:
            # Recheck every 10 s so stale devices eventually flip back to GREEN
            _push_status(tracker.combined_status())
            time.sleep(10)
    except KeyboardInterrupt:
        print("[fog] Shutting down")
    finally:
        unsubscribe()
        if _GPIO:
            GPIO.cleanup()


if __name__ == "__main__":
    run()
