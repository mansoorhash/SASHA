
from PySide6.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout,
    QHBoxLayout, QPushButton, QSizePolicy, QComboBox
)

from src.ui.settings.camera import CameraConfiguration
from src.ui.settings.ai_model import FaceScanningConfiguration


class SettingsPanel(QWidget):
    def __init__(self, state):
        super().__init__()
        self.shared_state = state

        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Settings Container
        self.settings_container = QGroupBox("Settings")
        settings_layout = QVBoxLayout(self.settings_container)

        #Camera Container
        self.camera_config = CameraConfiguration(self.shared_state)
        settings_layout.addWidget(self.camera_config)
        settings_layout.addSpacing(10)
        
        #AI Container
        self.ai_config = FaceScanningConfiguration(self.shared_state)
        settings_layout.addWidget(self.ai_config)

        settings_layout.addStretch()
        self.layout.addWidget(self.settings_container)