import logging

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Slot

logger = logging.getLogger("SASHA.settings.face_scanning")

class ScanInfoPanel(QWidget):

    def __init__(self, state):
        super().__init__()

        self.shared_state = state
        self.scanning = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        camera_combo_label = QLabel("Scan Info")

        layout.addWidget(camera_combo_label)

        detected_faces = QHBoxLayout()
        detected_faces_label = QLabel("Detected Faces: ")
        self.detected_faces_count_label = QLabel("0")

        detected_faces.addWidget(detected_faces_label)
        detected_faces.addStretch(1)
        detected_faces.addWidget(self.detected_faces_count_label)

        new_data = QHBoxLayout()
        new_data_label = QLabel("Embeddings added:")
        self.new_data_count_label = QLabel("0")

        new_data.addWidget(new_data_label)
        new_data.addStretch(1)
        new_data.addWidget(self.new_data_count_label)

        layout.addLayout(detected_faces)
        layout.addLayout(new_data)
