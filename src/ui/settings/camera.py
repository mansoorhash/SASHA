import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel
from PySide6.QtCore import Slot

from src.drivers.camera import CameraDriver

logger = logging.getLogger("SASHA.settings.camera")

class CameraConfiguration(QWidget):

    def __init__(self, state):
        super().__init__()

        self.shared_state = state

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        camera_combo_label = QLabel("Camera")
        self.camera_combo = QComboBox(placeholderText="Select Camera")
        self.camera_combo.currentIndexChanged.connect(self._camera_changed)

        layout.addWidget(camera_combo_label)
        layout.addWidget(self.camera_combo)

        if cam_list := self.initialize_cameras():
            for name, data in cam_list.items():
                self.camera_combo.addItem(name, userData=data)
        if self.camera_combo.count() == 0:
            self.camera_combo.addItem("No cameras detected", userData=-1)
        self.camera_combo.setCurrentIndex(-1)

    def initialize_cameras(self):
        camera_list = {}
        try:
            CameraDriver.detect_cameras()
            camera_list = CameraDriver.cameras()
        except Exception:
            logger.exception("Camera discovery failed")
            raise
        self.shared_state["camera_list"] = camera_list
        logger.info("Camera settings loaded with %s camera(s)", len(camera_list))
        return camera_list

    @Slot(int)
    def _camera_changed(self, index):
        camera_index = self.camera_combo.itemData(index) if index >= 0 else None
        self.shared_state["selected_camera"] = camera_index
        if camera_index is not None and camera_index >= 0:
            logger.info(
                "Selected camera %s (%s)", camera_index, self.camera_combo.itemText(index)
            )
        else:
            logger.info("Camera selection cleared")
