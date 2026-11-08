import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Slot

logger = logging.getLogger("SASHA.settings.face_scanning")

class FaceScanningConfiguration(QWidget):

    def __init__(self, state):
        super().__init__()

        self.shared_state = state
        self.scanning = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        camera_combo_label = QLabel("Face Scanning")

        self.camera_combo = QPushButton("Scan")
        self.camera_combo.clicked.connect(self._scanning_changed)
        self.camera_combo.setFixedWidth(120)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: gray; font-size: 16px;")

        self.face_state = QLabel("Unactive")

        layout.addWidget(camera_combo_label)

        scan_row = QHBoxLayout()
        scan_row.addWidget(self.camera_combo)
        scan_row.addStretch(1)

        status_row = QHBoxLayout()
        status_row.setSpacing(6)
        status_row.addWidget(self.status_dot)
        status_row.addWidget(self.face_state)
        scan_row.addLayout(status_row)

        layout.addLayout(scan_row)

        status_width = max(
            self.face_state.fontMetrics().horizontalAdvance(text)
            for text in ("Inactive", "Scanning")
        )
        self.face_state.setFixedWidth(status_width + 4)

    @Slot()
    def _scanning_changed(self):
        self.scanning = not self.scanning
        logger.info("Face scanning UI state changed to %s", "on" if self.scanning else "off")
        self.face_state.setText("Scanning" if self.scanning else "Inactive")
        self.camera_combo.setText("Stop" if self.scanning else "Scan")

        color = "green" if self.scanning else "gray"
        self.status_dot.setStyleSheet(f"color: {color}; font-size: 16px;")
