
import sys
import logging

from src.main import SASHAMain
from src.utils.logger import get_logger


def main():
    exit_code = 0
    logger = get_logger("SASHA")

    try:
        def handle_uncaught_exception(exc_type, exc_value, exc_tb):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_tb)
                return
            logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))

        sys.excepthook = handle_uncaught_exception
        logger.info("Starting SASHA application")

        app = SASHAMain(logger)
        exit_code = app.run()

    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received; shutting down SASHA")
        exit_code = 130

    except Exception:
        logger.exception("SASHA failed")
        exit_code = 1

    finally:
        logger.info("SASHA process exiting with code %s", exit_code)
        logging.shutdown()

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
