# MIVES-APP

Modular PyQt6 desktop application implementing the MIVES (Integrated Value Model for Sustainable Assessment) methodology. The app lets you build indicator trees, tune value functions, and visualize scenario results with Sankey diagrams and matrix charts.

## Features
- Build and edit criterion/indicator trees with weights.
- Define exponential value functions and preview curves.
- Generate Sankey diagrams (Plotly or native) and matrix charts for scenarios.
- Import/export data through the logic layer without GUI dependencies.

## Requirements
- Python 3.8 or newer (tested with Python 3.12)
- System GUI support for PyQt6 (X11/Wayland/macOS/Windows)
- Dependencies are pinned in `requirements.txt`; install them with `pip install -r requirements.txt`.

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
# For running tests
pip install pytest
```

## Running the application
```bash
python main.py
```
The entry point configures a `QApplication`, sets app metadata, and launches `MainWindow`. Run from a machine with GUI support (or an X server if remote/headless).

## Testing
Unit tests live under `tests/`. After installing dependencies and `pytest`:
```bash
python -m pytest
```

## Packaging
Use PyInstaller to build a standalone binary:
```bash
pyinstaller --onefile --windowed --name "MIVES Tool" main.py
# No static assets are bundled by default. If you add assets (e.g., logos), include them with:
# Linux/macOS:
# pyinstaller --onefile --windowed --name "MIVES Tool" --add-data "path/to/assets:assets" main.py
# Windows:
# pyinstaller --onefile --windowed --name "MIVES Tool" --add-data "path\\to\\assets;assets" main.py
```

## Repository layout
- `main.py` – Application entry point (logging, QApplication, MainWindow).
- `logic/` – GUI-free logic (MIVES math engine, plotting helpers, Sankey data).
- `gui/` – PyQt6 interface, tabs, and custom widgets (native Sankey renderer).
- `tests/` – Unit tests for the logic layer.

## License
MIT License. See `LICENSE.txt` in this repository for details.
