import sys
import signal

from PySide6.QtCore import QTimer, Slot
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QWidget
)

from src.ui.models import ObservableDict
from src.ui.camera import CameraPanel
from src.ui.settings.layout import SettingsPanel
from src.scanning.worker import ScanWorker


class GUIManager(QApplication):
    def __init__(self, logger):
        super().__init__(sys.argv)
        self.logger = logger
        self.logger.info("Initializing up GUIManager")

        self.window = None
        self.camera_panel = None
        self.main_grid = None
        self.menu_bar = None
        self.scan_worker = None

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

            self.shared_state.value_change.connect(self.camera_panel.state_update)
            self.settings_panel.ai_config.start_requested.connect(self.start_scan)
            self.settings_panel.ai_config.stop_requested.connect(self.stop_scan)
            self.camera_panel.frame_ready.connect(self._send_frame)
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

    @Slot()
    def start_scan(self):
        if self.scan_worker is not None:
            self.logger.info("Scan request ignored: worker already active")
            return
        if self.camera_panel.camera is None:
            self.logger.warning("Scan request ignored: no camera is open")
            return

        self.logger.info("Starting scan worker")
        worker = ScanWorker()
        self.scan_worker = worker

        worker.ready.connect(lambda: self.settings_panel.ai_config.set_scanning(True))
        worker.result.connect(self._send_result)
        worker.error.connect(self._scan_error)
        worker.finished.connect(self._scan_finished)
        worker.start()

    @Slot()
    def stop_scan(self):
        if self.scan_worker is not None:
            self.logger.info("Stopping scan worker")
            self.scan_worker.stop()

    @Slot(object)
    def _send_frame(self, frame):
        if self.scan_worker is not None:
            self.scan_worker.submit_frame(frame)

    @Slot(object)
    def _send_result(self, result):
        info = self.settings_panel.scan_info
        info.detected_faces_count_label.setText(str(result["detected_faces"]))
        info.new_data_count_label.setText(str(result["new_embeddings"]))

        self.camera_panel.faces_data = result["faces"]

    @Slot()
    def _scan_finished(self):
        self.logger.info("Scan worker finished")
        self.settings_panel.ai_config.set_scanning(False)
        self.scan_worker.deleteLater()
        self.scan_worker = None
        self.camera_panel.faces_data = []

    @Slot(object)
    def _scan_error(self, message):
        self.logger.error("Scan: %s", message)


