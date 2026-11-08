import sys
import signal

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QWidget
)

from src.ui.models import ObservableDict
from src.ui.camera import CameraPanel
from src.ui.settings.layout import SettingsPanel


class GUIManager(QApplication):
    def __init__(self, logger):
        super().__init__(sys.argv)
        self.logger = logger
        self.logger.info("Initializing up GUIManager")

        self.window = None
        self.camera_panel = None
        self.main_grid = None
        self.menu_bar = None

        self.shared_state = ObservableDict()

        signal.signal(signal.SIGINT, self._handle_sigint)
        self._signal_timer = QTimer(self)
        self._signal_timer.timeout.connect(lambda: None)
        self._signal_timer.start(100)

        self.logger.info("GUIManager initialized")

        self.startup_ok = self.start()

    def _handle_sigint(self, signum, frame):
        self.logger.info("Ctrl+C received; shutting down SASHA")
        if self.camera_panel is not None:
            self.camera_panel.stop_camera()
        self.quit()

    def start(self):
        try:
            self.logger.info("Attempting to Start GUI...")

            self.window = QMainWindow()
            self.window.setWindowTitle("SASHA")
            self.window.resize(1200, 800)
            container = QWidget()
            self.window.setCentralWidget(container)

            # Main layout
            main_layout = QHBoxLayout(container)
            main_layout.setSpacing(8)

            # Components
            self.settings_panel = SettingsPanel(state=self.shared_state)
            self.camera_panel = CameraPanel(
                state=self.shared_state, logger=self.logger.getChild("camera")
            )

            self.shared_state.value_change.connect(self.camera_panel._state_update)
            self.aboutToQuit.connect(self.camera_panel.stop_camera)

            # Add components
            main_layout.addWidget(self.camera_panel, 4)
            main_layout.addWidget(self.settings_panel, 1)

            self.window.show() 

            self.logger.info("GUI started successfully")
            return True
        except Exception:
            self.logger.exception("Error starting GUI")
            return False

