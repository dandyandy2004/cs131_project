import os
import cv2
from datetime import datetime

from cam import open_camera, read_frame, release_camera
from detect import load_model, detect_persons, classify, annotate_frame
from send import upload_snapshot

WINDOW_TITLE = "Edge Dev 3 - Person Detection"
SNAPSHOT_DIR = "snapshots"
MAX_SNAPSHOTS = 2   # hard cap: at most 2 uploads per program run (1 enter + 1 leave)


def save_snapshot(frame, label):
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(SNAPSHOT_DIR, f"{label}_{ts}.jpg")
    cv2.imwrite(path, frame)
    return path


def run():
    model = load_model()
    cap = open_camera(0)
    cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_AUTOSIZE)

    prev_person = False       # was a person in the previous frame?
    snapshots_taken = 0       # total enter+leave events captured

    try:
        while True:
            frame = read_frame(cap)
            if frame is None:
                print("Could not read frame")
                continue

            boxes = detect_persons(model, frame)
            status, color, person_now = classify(boxes)
            annotated = annotate_frame(frame.copy(), boxes, status, color)

            # --- transition detection ---
            if person_now != prev_person and snapshots_taken < MAX_SNAPSHOTS:
                label = "enter" if person_now else "leave"
                path = save_snapshot(frame, label)
                print(f"[main] {label.upper()} event -> {path}")
                try:
                    upload_snapshot(path, label=label)
                except Exception as e:
                    print(f"[main] upload failed: {e}")
                snapshots_taken += 1

            prev_person = person_now

            cv2.imshow(WINDOW_TITLE, annotated)
            key = cv2.waitKey(10) & 0xFF
            if key == 27 or key == ord("q"):
                break
    finally:
        release_camera(cap)


if __name__ == "__main__":
    run()
