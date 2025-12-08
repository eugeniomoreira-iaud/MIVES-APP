"""
MIVES Assessment Tool - Entry Point
Modular structure for maintainability and packaging

Usage:
    python main.py

Build executable:
    pyinstaller --onefile --windowed --name "MIVES_Tool" main.py
"""
import logging
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication


# Configure simple logging for startup/runtime errors
LOG_LEVEL = logging.INFO
logging.basicConfig(
    level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger("mives.main")


def resource_path(relative_path: str) -> str:
    """Return absolute path to a resource, works during development and when frozen by PyInstaller.

    Args:
        relative_path: Path relative to the project root or to the frozen bundle.

    Returns:
        Absolute path as string.
    """
    # PyInstaller sets this attribute when bundling
    base_path = getattr(sys, "_MEIPASS", None)
    if base_path is None:
        base_path = Path(__file__).resolve().parent
    return str(Path(base_path) / relative_path)


# Import MainWindow with a tolerant fallback so running as a module or as a script works
try:
    from gui.main_window import MainWindow
except Exception:
    try:
        # If executed as a package (python -m), relative import may be necessary
        from .gui.main_window import MainWindow  # type: ignore
    except Exception:
        logger.exception("Failed to import MainWindow from gui.main_window")
        raise


def main(argv: Optional[list] = None) -> None:
    """Application entry point.

    Args:
        argv: Optional list of argv to pass to QApplication (defaults to ``sys.argv``).
    """
    argv = argv if argv is not None else sys.argv

    logger.info("Starting MIVES Tool (version %s)", "17.0")

    # Create QApplication
    app = QApplication(argv)

    # Set application metadata
    app.setApplicationName("MIVES Tool")
    app.setOrganizationName("Heritage Research")
    app.setApplicationVersion("17.0")

    try:
        window = MainWindow()
        window.show()

        # Start event loop and exit with returned code
        exit_code = app.exec()
        logger.info("Application exited with code %s", exit_code)
        sys.exit(exit_code)
    except Exception:
        logger.exception("Unhandled exception while running the application")
        # Ensure any unexpected exception results in non-zero exit code
        sys.exit(1)


if __name__ == "__main__":
    main()
