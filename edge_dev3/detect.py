import cv2
from ultralytics import YOLO

MODEL_PATH = "yolov8n.pt"
PERSON_CLASS = 0

# Monocular distance estimation. Output is in FEET.
# FOCAL_LENGTH_PX is a placeholder; calibrate with a known-distance reference shot.
FOCAL_LENGTH_PX = 400.0
KNOWN_PERSON_HEIGHT_FT = 5.58  # ≈ 5'7"

# Inference scale — smaller is faster, less accurate at distance.
INFER_IMGSZ = 320


def load_model(path=MODEL_PATH):
    model = YOLO(path)
    model.overrides["verbose"] = False
    return model


def estimate_distance(bbox_height_px):
    if bbox_height_px <= 0:
        return 0.0
    return (KNOWN_PERSON_HEIGHT_FT * FOCAL_LENGTH_PX) / float(bbox_height_px)


def detect_persons(model, frame, imgsz=INFER_IMGSZ):
    """Run YOLO on a downscaled copy of `frame` and scale boxes back to full
    resolution. Returns a list of detection dicts."""
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (imgsz, imgsz))
    results = model(small, classes=[PERSON_CLASS], imgsz=imgsz, verbose=False)
    raw_boxes = results[0].boxes

    sx, sy = w / imgsz, h / imgsz
    detections = []
    for box in raw_boxes:
        x1s, y1s, x2s, y2s = box.xyxy[0].tolist()
        x1, y1, x2, y2 = int(x1s * sx), int(y1s * sy), int(x2s * sx), int(y2s * sy)
        conf = float(box.conf[0])
        bh = int(y2 - y1)
        detections.append({
            "xyxy": [x1, y1, x2, y2],
            "conf": conf,
            "bbox_height_px": bh,
            "distance_ft": estimate_distance(bh),
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
        dist = det["distance_ft"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), status_color, 2)
        cv2.putText(
            frame,
            f"{dist:.1f}ft",
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
