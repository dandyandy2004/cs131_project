import cv2
from ultralytics import YOLO

def person_detect_status():
    window_title = "Camera A - Person Detection"

    # Load YOLOv8 nano model (downloads automatically ~6MB, fastest option)
    model = YOLO("yolov8n.pt")

    video_capture = cv2.VideoCapture(0)

    if not video_capture.isOpened():
        print("Unable to open camera")
        return

    try:
        cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)

        while True:
            ret, frame = video_capture.read()

            if not ret:
                print("Could not read frame")
                continue

            # Run YOLO detection, only look for class 0 = person
            results = model(frame, classes=[0], verbose=False)

            # Get bounding boxes
            boxes = results[0].boxes

            if len(boxes) > 0:
                status = "RED - person detected"
                status_color = (0, 0, 255)
            else:
                status = "GREEN - clear"
                status_color = (0, 255, 0)

            print("Camera A:", status)

            # Draw one box per detected person
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

            # Status label in top-left
            cv2.putText(
                frame,
                status,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                status_color,
                2,
            )

            cv2.imshow(window_title, frame)

            keyCode = cv2.waitKey(10) & 0xFF
            if keyCode == 27 or keyCode == ord("q"):
                break

    finally:
        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    person_detect_status()