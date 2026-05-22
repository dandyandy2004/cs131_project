import cv2
import threading
from ultralytics import YOLO

class CameraStream:
    """Runs capture in a background thread so YOLO never blocks the webcam."""
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        # Buffer only 1 frame — always get the latest, not a stale queue
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.ret, self.frame = self.cap.read()
        self.lock = threading.Lock()
        self.running = True
        threading.Thread(target=self._update, daemon=True).start()

    def _update(self):
        while self.running:
            ret, frame = self.cap.read()
            with self.lock:
                self.ret, self.frame = ret, frame

    def read(self):
        with self.lock:
            return self.ret, self.frame.copy()

    def release(self):
        self.running = False
        self.cap.release()


def person_detect_status():
    window_title = "Camera A - Person Detection"

    model = YOLO("yolov8n.pt")
    model.overrides["verbose"] = False

    stream = CameraStream(0)

    # Cached detection state — persists between inference runs
    status = "GREEN - clear"
    status_color = (0, 255, 0)
    boxes_cache = []

    frame_count = 0
    INFER_EVERY = 3  # Run YOLO every N frames — tune this (3 = ~3x faster)

    try:
        while True:
            ret, frame = stream.read()
            if not ret:
                continue

            frame_count += 1

            # Only run inference every N frames
            if frame_count % INFER_EVERY == 0:
                # Downscale for inference, display full res
                small = cv2.resize(frame, (320, 240))
                results = model(small, classes=[0], imgsz=320)
                boxes_raw = results[0].boxes

                # Scale boxes back up to original frame size
                h, w = frame.shape[:2]
                sx, sy = w / 320, h / 240
                boxes_cache = []
                for box in boxes_raw:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    boxes_cache.append((
                        int(x1*sx), int(y1*sy),
                        int(x2*sx), int(y2*sy),
                        conf
                    ))

                if boxes_cache:
                    status = "RED - person detected"
                    status_color = (0, 0, 255)
                else:
                    status = "GREEN - clear"
                    status_color = (0, 255, 0)

                print("Camera A:", status)

            # Draw cached boxes on every frame (smooth display)
            for (x1, y1, x2, y2, conf) in boxes_cache:
                cv2.rectangle(frame, (x1, y1), (x2, y2), status_color, 2)
                cv2.putText(frame, f"person {conf:.0%}",
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, status_color, 2)

            cv2.putText(frame, status, (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)

            cv2.imshow(window_title, frame)

            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break

    finally:
        stream.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    person_detect_status()
