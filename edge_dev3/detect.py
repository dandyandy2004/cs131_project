import cv2
from ultralytics import YOLO

MODEL_PATH = "yolov8n.pt"
PERSON_CLASS = 0


def load_model(path=MODEL_PATH):
    return YOLO(path)


def detect_persons(model, frame):
    results = model(frame, classes=[PERSON_CLASS], verbose=False)
    boxes = results[0].boxes
    return boxes


def annotate_frame(frame, boxes, status, status_color):
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), status_color, 2)
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


def classify(boxes):
    if len(boxes) > 0:
        return "RED - person detected", (0, 0, 255), True
    return "GREEN - clear", (0, 255, 0), False
