import cv2


def open_camera(index=0):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open camera at index {index}")
    return cap


def read_frame(cap):
    ret, frame = cap.read()
    if not ret:
        return None
    return frame


def release_camera(cap):
    cap.release()
    cv2.destroyAllWindows()
