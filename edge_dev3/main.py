import os
import cv2
from datetime import datetime
from dotenv import load_dotenv

from cam import open_camera, read_frame, release_camera
from detect import load_model, detect_persons, classify, annotate_frame
from send import upload_snapshot

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), "snapshots")


def save_snapshot(frame, label):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SNAPSHOT_DIR, f"{label}_{ts}.jpg")
    cv2.imwrite(path, frame)
    return path


def _summarize(detections):
    if not detections:
        return 0.0, 0, 0.0
    best_conf = max(d["conf"] for d in detections)
    largest_bbox_h = max(d["bbox_height_px"] for d in detections)
    positive_distances = [d["distance_m"] for d in detections if d["distance_m"] > 0]
    closest_distance = min(positive_distances) if positive_distances else 0.0
    return best_conf, largest_bbox_h, closest_distance


def run(window_title="Edge Dev 3 - Person Detection"):
    camera_index = int(os.getenv("CAMERA_INDEX", "0"))

    model = load_model()
    cap = open_camera(camera_index)
    cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)

    prev_person = False

    try:
        while True:
            frame = read_frame(cap)
            if frame is None:
                print("Could not read frame")
                continue

            detections = detect_persons(model, frame)
            status, color, person_now = classify(detections)
            annotated = annotate_frame(frame.copy(), detections, status, color)

            if person_now != prev_person:
                label = "enter" if person_now else "leave"
                path = save_snapshot(frame, label)
                best_conf, largest_bbox_h, closest_distance = _summarize(detections)
                print(f"[main] {label.upper()} event -> {path}")
                try:
                    upload_snapshot(
                        path,
                        label=label,
                        confidence=best_conf,
                        bbox_height_px=largest_bbox_h,
                        distance_estimate_m=closest_distance,
                    )
                except Exception as e:
                    print(f"[main] upload failed: {e}")

            prev_person = person_now

            cv2.imshow(window_title, annotated)
            key = cv2.waitKey(10) & 0xFF
            if key == 27 or key == ord("q"):
                break
    finally:
        release_camera(cap)


if __name__ == "__main__":
    run()
