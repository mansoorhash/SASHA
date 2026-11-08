import cv2
import logging
from pygrabber.dshow_graph import FilterGraph

logger = logging.getLogger("SASHA.camera.driver")

class CameraDriver:
    _cameras = {}

    @classmethod
    def detect_cameras(cls):
        cls._cameras = {}
        logger.info("Detecting cameras")

        try:
            devices = FilterGraph().get_input_devices()
            for index, name in enumerate(devices):
                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                try:
                    if cap.isOpened():
                        cls._cameras[name] = index
                    else:
                        logger.warning("Camera %s (%s) could not be opened", index, name)
                finally:
                    cap.release()
            logger.info("Detected %s usable camera(s)", len(cls._cameras))
        except Exception:
            logger.exception("Error enumerating DirectShow cameras")

    
    @classmethod
    def cameras(cls):
        return cls._cameras

    def __init__(self, index=0):
        self.index = index
        self.cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            self.cap.release()
            raise RuntimeError(f"Camera {index} unavailable")

    def get_frame(self):
        ret, frame = self.cap.read()
        return frame if ret else None

    def read(self):
        frame = self.get_frame()
        return frame if frame is not None else None

    def release(self):
        self.cap.release()
