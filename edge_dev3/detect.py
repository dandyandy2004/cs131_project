import cv2
from ultralytics import YOLO

MODEL_PATH = "yolov8n.pt"
PERSON_CLASS = 0

# Monocular distance estimation constants.
# FOCAL_LENGTH_PX is a placeholder; calibrate with a known-distance reference shot.
FOCAL_LENGTH_PX = 600.0
KNOWN_PERSON_HEIGHT_M = 1.70


def load_model(path=MODEL_PATH):
    return YOLO(path)


def estimate_distance(bbox_height_px):
    if bbox_height_px <= 0:
        return 0.0
    return (KNOWN_PERSON_HEIGHT_M * FOCAL_LENGTH_PX) / float(bbox_height_px)


def detect_persons(model, frame):
    results = model(frame, classes=[PERSON_CLASS], verbose=False)
    raw_boxes = results[0].boxes
    detections = []
    for box in raw_boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        h = int(y2 - y1)
        detections.append({
            "xyxy": [x1, y1, x2, y2],
            "conf": conf,
            "bbox_height_px": h,
            "distance_m": estimate_distance(h),
        })
    return detections


def classify(detections):
    if len(detections) > 0:
        return "RED - person detected", (0, 0, 255), True
    return "GREEN - clear", (0, 255, 0), False


def annotate_frame(frame, detections, status, status_color):
    for det in detections:
        x1, y1, x2, y2 = det["xyxy"]
        conf = det["conf"]
        dist = det["distance_m"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), status_color, 2)
        cv2.putText(
            frame,
            f"{dist:.1f}m",
            (x1, y1 - 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"person {conf:.0%}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            status_color,
            2,
        )
    cv2.putText(
        frame,
        status,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        status_color,
        2,
    )
    return frame
