from PySide6.QtWidgets import QGroupBox, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QImage, QPixmap

from src.drivers.camera import CameraDriver

class CameraPanel(QGroupBox):
    def __init__(self, state, logger):
        super().__init__("Camera Feed")
        self.shared_state = state
        self.logger = logger

        self.layout = QVBoxLayout(self)

        self.camera_label = QLabel("No cameras connected")
        self.camera_label.setAlignment(Qt.AlignCenter)

        self.camera = None
        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self._show_frame)

        self.layout.addWidget(self.camera_label)

    @Slot(str, object)
    def _state_update(self, key, value):
        if key != "selected_camera":
            return

        self.stop_camera()

        if value is None or value == -1:
            return self.camera_label.setText("No camera selected")

        try:
            self.camera_label.setText("Loading...")
            self.camera = CameraDriver(value)
        except RuntimeError as exc:
            self.logger.error("Could not open camera %s: %s", value, exc)
            return self.camera_label.setText(str(exc))
        except Exception:
            self.logger.exception("Unexpected error opening camera %s", value)
            return self.camera_label.setText("Camera unavailable")

        self.logger.info("Opened camera %s", value)
        self.frame_timer.start(33)

    @Slot()
    def _show_frame(self):
        try:
            frame = self.camera.read()
            if frame is None:
                self.logger.warning("Camera %s returned no frame", self.camera.index)
                self.stop_camera()
                self.camera_label.setText("Camera feed unavailable")
                return

            height, width, _ = frame.shape
            image = QImage(
                frame.data, width, height, frame.strides[0], QImage.Format.Format_BGR888
            ).copy()
            pixmap = QPixmap.fromImage(image)

            self.camera_label.setPixmap(
                pixmap.scaled(
                    self.camera_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
        except Exception:
            self.logger.exception("Error displaying camera %s", self.camera.index)
            self.stop_camera()
            self.camera_label.setText("Camera feed unavailable")

    def stop_camera(self):
        self.frame_timer.stop()
        if self.camera is not None:
            camera = self.camera
            self.camera = None
            try:
                camera.release()
                self.logger.info("Released camera %s", camera.index)
            except Exception:
                self.logger.exception("Failed to release camera %s", camera.index)
        self.camera_label.clear()
                
