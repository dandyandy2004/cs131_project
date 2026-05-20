import cv2

def gstreamer_pipeline(
    capture_width=1920,
    capture_height=1080,
    display_width=960,
    display_height=540,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink drop=True"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

def face_detect_status():
    window_title = "Camera A Face Detection"

    face_cascade = cv2.CascadeClassifier(
        "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
    )

    eye_cascade = cv2.CascadeClassifier(
        "/usr/share/opencv4/haarcascades/haarcascade_eye.xml"
    )

    video_capture = cv2.VideoCapture(gstreamer_pipeline(), cv2.CAP_GSTREAMER)

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

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            # Main project logic
            if len(faces) > 0:
                status = "RED - face/person detected"
                status_color = (0, 0, 255)
            else:
                status = "GREEN - clear"
                status_color = (0, 255, 0)

            print("Camera A:", status)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                roi_gray = gray[y : y + h, x : x + w]
                roi_color = frame[y : y + h, x : x + w]

                eyes = eye_cascade.detectMultiScale(roi_gray)

                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(
                        roi_color,
                        (ex, ey),
                        (ex + ew, ey + eh),
                        (0, 255, 0),
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

            cv2.imshow(window_title, frame)

            keyCode = cv2.waitKey(10) & 0xFF

            if keyCode == 27 or keyCode == ord("q"):
                break

    finally:
        video_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    face_detect_status()