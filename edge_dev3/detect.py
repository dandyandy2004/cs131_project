import cv2
from ultralytics import YOLO
from blacklist import get_app, match_face

MODEL_PATH = "yolov8n.pt"
PERSON_CLASS = 0
INFER_IMGSZ = 320


def load_model(path=MODEL_PATH):
    model = YOLO(path)
    model.overrides["verbose"] = False
    return model


def detect_persons(model, frame, imgsz=INFER_IMGSZ):
    """Run YOLO on a downscaled copy of `frame` and scale boxes back to full resolution."""
    h, w = frame.shape[:2]
    small = cv2.resize(frame, (imgsz, imgsz))
    results = model(small, classes=[PERSON_CLASS], imgsz=imgsz, verbose=False)
    raw_boxes = results[0].boxes

    sx, sy = w / imgsz, h / imgsz
    detections = []
    for box in raw_boxes:
        x1s, y1s, x2s, y2s = box.xyxy[0].tolist()
        x1, y1, x2, y2 = int(x1s * sx), int(y1s * sy), int(x2s * sx), int(y2s * sy)
        detections.append({
            "xyxy": [x1, y1, x2, y2],
            "conf": float(box.conf[0]),
            "identity": None,
            "face_sim": 0.0,
        })
    return detections


def identify_faces(frame, detections):
    """Run InsightFace on frame, assign blacklist identity to each YOLO person box."""
    if not detections:
        return detections
    faces = get_app().get(frame)
    for face in faces:
        fx1, fy1, fx2, fy2 = face.bbox.astype(int)
        face_cx = (fx1 + fx2) / 2
        face_cy = (fy1 + fy2) / 2
        for det in detections:
            x1, y1, x2, y2 = det["xyxy"]
            if x1 <= face_cx <= x2 and y1 <= face_cy <= y2:
                name, sim = match_face(face.normed_embedding)
                det["identity"] = name
                det["face_sim"] = sim
                break
    return detections


def classify(detections):
    if not detections:
        return "GREEN - clear", (0, 255, 0), False
    known = [d["identity"] for d in detections if d["identity"]]
    if known:
        return "RED - " + ", ".join(sorted(set(known))), (0, 0, 255), True
    return "RED - unknown person", (0, 0, 255), True


def annotate_frame(frame, detections, status, status_color):
    for det in detections:
        x1, y1, x2, y2 = det["xyxy"]
        conf = det["conf"]
        name_label = det["identity"] if det["identity"] else "unknown"
        cv2.rectangle(frame, (x1, y1), (x2, y2), status_color, 2)
        cv2.putText(frame, name_label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        cv2.putText(frame, f"person {conf:.0%}", (x1, y2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    cv2.putText(frame, status, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
    return frame
