import threading

import cv2


class CameraStream:
    """Background-thread frame grabber. Always serves the latest frame so
    inference never blocks the capture loop."""

    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        if not self.cap.isOpened():
            raise RuntimeError(f"Unable to open camera at index {src}")
        # Keep only the latest frame in the OS-side buffer.
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.ret, self.frame = self.cap.read()
        self._lock = threading.Lock()
        self._running = True
        threading.Thread(target=self._update, daemon=True).start()

    def _update(self):
        while self._running:
            ret, frame = self.cap.read()
            if not ret:
                continue
            with self._lock:
                self.ret, self.frame = ret, frame

    def read(self):
        with self._lock:
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()

    def release(self):
        self._running = False
        self.cap.release()


# Backwards-compatible function API used by older callers.
def open_camera(index=0):
    return CameraStream(index)


def read_frame(stream):
    ret, frame = stream.read()
    if not ret:
        return None
    return frame


def release_camera(stream):
    stream.release()
    cv2.destroyAllWindows()
