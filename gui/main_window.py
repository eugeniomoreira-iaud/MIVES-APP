"""
MIVES Main Application Window
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QTabBar, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from gui.tabs.builder import BuilderTab
from gui.tabs.functions import FunctionsTab
from gui.tabs.viz import VizTab
from gui.tabs.scenarios_container import ScenariosContainerTab
from gui.styles import APP_STYLES, DEFAULT_SANKEY_STYLE


class ScenarioStyleManager(QObject):
    """Manager for synchronized scenario tab styles"""
    style_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.style_opts = DEFAULT_SANKEY_STYLE.copy()
    
    def update_style(self, key, value):
        """Update a style parameter and notify all scenario tabs"""
        self.style_opts[key] = value
        self.style_changed.emit()


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIVES Assessment Tool v17 - Modular")
        self.resize(1400, 950)
        self.setStyleSheet(APP_STYLES)
        
        # Separate style managers
        self.viz_style_opts = DEFAULT_SANKEY_STYLE.copy()  # Tab 3 only
        self.scenario_style_manager = ScenarioStyleManager()  # All scenario tabs
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup main UI structure"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_lay = QVBoxLayout(main_widget)
        
        self.tabs = QTabWidget()
        main_lay.addWidget(self.tabs)
        
        # Create core tabs
        self.tab_builder = BuilderTab()
        self.tabs.addTab(self.tab_builder, "1. Structure")
        
        self.tab_functions = FunctionsTab(self.tab_builder.tree_widget)
        self.tabs.addTab(self.tab_functions, "2. Functions")
        
        self.tab_viz = VizTab(self.tab_builder.tree_widget)
        self.tabs.addTab(self.tab_viz, "3. Visualization")
        
        # Create scenarios container tab
        self.tab_scenarios = ScenariosContainerTab(
            self.tab_builder.tree_widget, 
            self.scenario_style_manager
        )
        self.tabs.addTab(self.tab_scenarios, "4. Scenarios")
        
        # Connect signals
        self.tabs.currentChanged.connect(self.on_tab_change)
    
    def on_tab_change(self, index):
        """Refresh tab content when switching"""
        if index == 1:  # Functions tab
            self.tab_functions.refresh_ind_list()
        elif index == 2:  # Viz tab
            self.tab_viz.refresh_viz()
        elif index == 3:  # Scenarios container
            self.tab_scenarios.refresh_all_scenarios()

class ScenarioStyleManager(QObject):
    """Manager for synchronized scenario tab styles"""
    style_changed = pyqtSignal()
    matrix_style_changed = pyqtSignal()  # NEW: separate signal for matrix
    export_scale_changed = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        from gui.styles import DEFAULT_SANKEY_STYLE, DEFAULT_FUNC_STYLE
        self.style_opts = DEFAULT_SANKEY_STYLE.copy()
        self.matrix_style_opts = DEFAULT_FUNC_STYLE.copy()  # NEW: matrix styles
        self.export_scale = 1.0
    
    def update_style(self, key, value):
        """Update a style parameter and notify all scenario tabs"""
        self.style_opts[key] = value
        self.style_changed.emit()
    
    def update_matrix_style(self, key, value):
        """Update matrix style parameter"""
        self.matrix_style_opts[key] = value
        self.matrix_style_changed.emit()
    
    def set_export_scale(self, scale):
        """Update export scale"""
        self.export_scale = scale
        self.export_scale_changed.emit(scale)

