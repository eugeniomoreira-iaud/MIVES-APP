# MIVES-APP

Modular PyQt6 application implementing the MIVES assessment tool, with a GUI layer separated from core computation logic.

## Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Code Map](#code-map)
- [Data Flow](#data-flow)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Configuration & Data](#configuration--data)
- [Visualization](#visualization)
- [Testing](#testing)
- [Extending](#extending)
- [License](#license)

## Overview
- **Purpose**: Build and evaluate MIVES indicator trees, edit value functions, run scenarios, and visualize results (Sankey + matrix).
- **Stack**: Python, PyQt6 for UI; Plotly helpers plus a native QGraphics Sankey renderer to avoid heavy web engine deps.
- **Entry point**: `main.py` launches the QApplication and GUI.

## Architecture
- **logic/** (GUI-free): Core MIVES computations, data IO, validation, plotting helpers, and Sankey data generation.
- **gui/**: PyQt6 application (main window, styles, widgets, tab system).
- **assets/**: Static assets (e.g., `logo.png`).
- **tests/**: Unit tests for computation.

## Code Map
```
MIVES-Project/
├── main.py              # Entry point — creates QApplication and launches GUI.
├── requirements.txt     # Pinned dependencies.
├── README.md            # This file.
├── LICENSE.txt          # MIT license.
│
├── logic/               # Core, GUI-independent logic and helpers.
│   ├── __init__.py      # Exports (MivesLogic, DataManager).
│   ├── math_engine.py   # Core MIVES computations (MivesLogic) + plotting delegators.
│   ├── data_manager.py  # CSV import/export helpers and weight validation.
│   ├── plotting.py      # Plotly plotting helpers (curves, matrix charts).
│   └── tree_sankey.py   # Tree traversal, Sankey data generation, scoring.
│
├── gui/                 # PyQt6 UI layer.
│   ├── __init__.py
│   ├── main_window.py   # MainWindow with tabs and style managers.
│   ├── styles.py        # Qt stylesheet + default plotting/sankey styles.
│   ├── sankey_widget.py # Adapter between legacy dict data and native widget.
│   │
│   ├── widgets/
│   │   ├── __init__.py
│   │   └── native_sankey.py # QGraphics-based Sankey renderer (NodeData, LinkData, SankeyData).
│   │
│   └── tabs/
│       ├── __init__.py
│       ├── builder.py   # Tab 1 — structure builder (create/manage tree).
│       ├── functions.py # Tab 2 — value-function editor + previews/exports.
│       ├── viz.py       # Tab 3 — Sankey visualization and style controls.
│       ├── scenarios_container.py # Manages scenario tabs and shared styles.
│       └── scenarios.py # Scenario evaluation (inputs, Sankey, matrix).
│
├── tests/
│   └── test_math_engine.py # Tests for MivesLogic (numeric stability, bounds).
│
└── assets/
    └── logo.png         # Project logo.
```

## Data Flow
1. **Define structure** in **Builder** tab (`gui/tabs/builder.py`): create/manage indicator tree and weights.
2. **Configure value functions** in **Functions** tab (`gui/tabs/functions.py`): edit utility curves, preview/export.
3. **Run scenarios** in **Scenarios** tab (`gui/tabs/scenarios.py` + `scenarios_container.py`): input data, evaluate, inspect matrices/Sankey.
4. **Visualize** in **Viz** tab (`gui/tabs/viz.py`): Sankey and style controls.
5. **Compute** via `logic/math_engine.py` (`MivesLogic`): scoring, normalization, aggregation.
6. **Export / plot** via `logic/plotting.py` (Plotly helpers) or native renderer in `gui/widgets/native_sankey.py`.
7. **Data IO** via `logic/data_manager.py`: CSV import/export, weight validation.
8. **Sankey data** via `logic/tree_sankey.py`: traversal, scoring, Sankey data generation consumed by GUI widgets.

## Installation
```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the App
```bash
python main.py
```
- Launches the PyQt6 GUI with tabs for building structures, editing functions, running scenarios, and visualizing Sankey/matrix results.

## Configuration & Data
- **Indicator trees/weights**: defined via the Builder tab; persisted/imported through `logic/data_manager.py` (CSV helpers).
- **Value functions**: configured in Functions tab; previews/export handled by `functions.py` with plotting helpers.
- **Scenarios**: managed in Scenarios tab; uses `MivesLogic` for evaluation and `tree_sankey.py` for Sankey data.

## Visualization
- **Plotly-based** charts via `logic/plotting.py` for curves/matrix.
- **Native Sankey** (`gui/widgets/native_sankey.py`) to avoid heavy Plotly/QWebEngine for exports; fed by `tree_sankey.py` data.

## Testing
```bash
pytest
```
- Current coverage: `tests/test_math_engine.py` (MivesLogic stability and bounds). Add more tests alongside modules in `logic/` and GUI integration where feasible.

## Extending
- **New indicators/weights**: extend configs/inputs and validations in `data_manager.py`.
- **Computation**: add methods in `math_engine.py`; ensure coverage in `tests/`.
- **Visuals**: add chart helpers in `plotting.py` or new render modes in `native_sankey.py`.
- **UI**: add/modify tabs under `gui/tabs/`; register in `main_window.py`.
- **Styling**: extend `styles.py` for consistent theming across tabs and charts.

## License
MIT — see `LICENSE.txt`.
