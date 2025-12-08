"""
MIVES Assessment Tool - Entry Point
Modular structure for maintainability and packaging

Usage:
    python main.py

Build executable:
    pyinstaller --onefile --windowed --name "MIVES_Tool" main.py
"""
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("MIVES Tool")
    app.setOrganizationName("Heritage Research")
    app.setApplicationVersion("17.0")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
