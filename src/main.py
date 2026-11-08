
from src.ui.gui_manager import GUIManager


class SASHAMain:

    def __init__(self, logger):
        self.logger = logger
        self.logger.info("SASHA application initialized")

        self.app = GUIManager(self.logger)

    def run(self):
        if not self.app.startup_ok:
            self.logger.error("GUI startup failed; refusing to enter the event loop")
            return 1

        try:
            return self.app.exec()

        except Exception:
            self.logger.exception("SASHA execution failed")
            raise
        finally:
            if self.app.camera_panel is not None:
                self.app.camera_panel.stop_camera()
            self.logger.info("SASHA application exited")
