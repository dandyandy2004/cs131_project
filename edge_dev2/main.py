import os
import cv2
from datetime import datetime
from dotenv import load_dotenv

from cam import open_camera, read_frame, release_camera
from detect import load_model, detect_persons, identify_faces, classify, annotate_frame
from blacklist import load_blacklist
from send import upload_snapshot

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "snapshots")
INFER_EVERY = int(os.getenv("INFER_EVERY", "3"))


def save_snapshot(frame, label):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SNAPSHOT_DIR, f"{label}_{ts}.jpg")
    cv2.imwrite(path, frame)
    return path


def _summarize(detections):
    if not detections:
        return 0.0, None
    best_conf = max(d["conf"] for d in detections)
    known = [d["identity"] for d in detections if d["identity"]]
    return best_conf, known[0] if known else None


def run(window_title="Edge Dev 3 - Person Detection"):
    camera_index = int(os.getenv("CAMERA_INDEX", "0"))

    model = load_model()
    load_blacklist()
    stream = open_camera(camera_index)
    cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)

    prev_person = False
    detections = []
    status, color, person_now = "GREEN - clear", (0, 255, 0), False
    frame_count = 0

    try:
        while True:
            frame = read_frame(stream)
            if frame is None:
                continue
            frame_count += 1

            if frame_count % INFER_EVERY == 0:
                detections = detect_persons(model, frame)
                identify_faces(frame, detections)
                status, color, person_now = classify(detections)

                if person_now != prev_person:
                    label = "enter" if person_now else "leave"
                    path = save_snapshot(frame, label)
                    best_conf, matched_identity = _summarize(detections)
                    print(f"[main] {label.upper()} event -> {path}  identity={matched_identity}")
                    try:
                        upload_snapshot(
                            path,
                            label=label,
                            confidence=best_conf,
                            matched_identity=matched_identity,
                        )
                    except Exception as e:
                        print(f"[main] upload failed: {e}")
                    prev_person = person_now

            annotated = annotate_frame(frame.copy(), detections, status, color)
            cv2.imshow(window_title, annotated)
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                break
    finally:
        release_camera(stream)


if __name__ == "__main__":
    run()
