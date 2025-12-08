"""
Scenarios Container Tab (Nested Tab Management with Shared Style Controls)
"""
import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTabBar, 
                             QMessageBox, QSplitter, QScrollArea, QFrame, QGroupBox,
                             QLabel, QSpinBox, QDoubleSpinBox, QPushButton, QCheckBox,
                             QLineEdit, QColorDialog, QComboBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from gui.tabs.scenarios import ScenarioTab


class ScenariosContainerTab(QWidget):
    """Container tab with shared style controls and nested scenario tabs"""
    
    def __init__(self, tree_widget, style_manager, parent=None):
        super().__init__(parent)
        self.tree_widget = tree_widget
        self.style_manager = style_manager
        self.scenario_counter = 0
        # Shared column sizes for ScenarioTab input tables. Keeps columns
        # synchronized across existing and newly created scenario tabs.
        self._shared_col_sizes = []
        # Shared splitter sizes for layout synchronization across scenario tabs
        self._shared_main_splitter_sizes = []
        self._shared_chart_splitter_sizes = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Main splitter: Style Controls | Scenario Tabs
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # === LEFT: Shared Style Control Panel ===
        self.style_sidebar = self.create_style_sidebar()
        main_splitter.addWidget(self.style_sidebar)
        
        # === RIGHT: Nested Scenario Tabs ===
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(5, 5, 5, 5)
        
        self.scenario_tabs = QTabWidget()
        self.scenario_tabs.setTabsClosable(True)
        self.scenario_tabs.tabCloseRequested.connect(self.close_scenario_tab)
        
        # Add "+" tab
        self.add_new_tab_button = QWidget()
        self.scenario_tabs.addTab(self.add_new_tab_button, "+")
        
        # Connect signals
        self.scenario_tabs.tabBarClicked.connect(self.handle_tab_click)
        self.scenario_tabs.currentChanged.connect(self.on_scenario_tab_change)
        
        right_layout.addWidget(self.scenario_tabs)
        main_splitter.addWidget(right_container)
        
        main_splitter.setSizes([280, 1120])
        layout.addWidget(main_splitter)
        
        # Create first scenario automatically
        self.create_scenario()
    
    def create_style_sidebar(self):
        """Create shared style controls for all scenarios (Sankey + Matrix)"""
        sidebar = QScrollArea()
        sidebar.setWidgetResizable(True)
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setFixedWidth(320)
        
        content = QWidget()
        sl = QVBoxLayout(content)
        sl.setContentsMargins(10, 10, 10, 10)
        sl.setSpacing(15)
        
        sl.addWidget(QLabel("<b>Scenario Styles</b>"))
        sl.addWidget(QLabel("<i>Shared by all scenarios</i>"))
        
        # ========== SANKEY STYLES ==========
        sl.addWidget(QLabel("<b>— Sankey Diagram —</b>"))
        
        # === TITLE ===
        title_group = QGroupBox("Chart Title")
        title_lay = QVBoxLayout(title_group)
        
        c_show_title = QCheckBox("Show Title")
        c_show_title.setChecked(self.style_manager.style_opts['show_title'])
        c_show_title.toggled.connect(lambda v: self.update_style('show_title', v))
        title_lay.addWidget(c_show_title)
        
        title_lay.addWidget(QLabel("Title Text:"))
        le_title = QLineEdit()
        le_title.setText(self.style_manager.style_opts['title_text'])
        le_title.textChanged.connect(lambda v: self.update_style('title_text', v))
        title_lay.addWidget(le_title)
        
        title_lay.addWidget(QLabel("Title Font Size:"))
        sb_title_size = QSpinBox()
        sb_title_size.setRange(10, 32)
        sb_title_size.setValue(self.style_manager.style_opts.get('title_font_size', 20))
        sb_title_size.valueChanged.connect(lambda v: self.update_style('title_font_size', v))
        title_lay.addWidget(sb_title_size)
        
        btn_title_color = QPushButton("Title Color")
        btn_title_color.clicked.connect(lambda: self.pick_color('title_color'))
        title_lay.addWidget(btn_title_color)
        
        sl.addWidget(title_group)
        
        # === EXPORT SETTINGS ===
        export_group = QGroupBox("Export Settings")
        export_lay = QVBoxLayout(export_group)
        
        export_lay.addWidget(QLabel("Export Scale Multiplier:"))
        self.sb_export_scale = QDoubleSpinBox()
        self.sb_export_scale.setRange(0.25, 5.0)
        self.sb_export_scale.setSingleStep(0.25)
        self.sb_export_scale.setValue(self.style_manager.export_scale)
        self.sb_export_scale.setDecimals(2)
        self.sb_export_scale.valueChanged.connect(self.on_export_scale_changed)
        export_lay.addWidget(self.sb_export_scale)
        
        self.lbl_export_info = QLabel("Scale: 1.0× (Normal size)")
        self.lbl_export_info.setStyleSheet("color: #555; font-style: italic;")
        export_lay.addWidget(self.lbl_export_info)
        
        sl.addWidget(export_group)
        
        # === LAYOUT ===
        layout_group = QGroupBox("Layout")
        layout_lay = QVBoxLayout(layout_group)
        
        layout_lay.addWidget(QLabel("Vertical Fill:"))
        sb_vfill = QDoubleSpinBox()
        sb_vfill.setRange(0.1, 1.0)
        sb_vfill.setSingleStep(0.05)
        sb_vfill.setValue(self.style_manager.style_opts['vertical_fill'])
        sb_vfill.valueChanged.connect(lambda v: self.update_style('vertical_fill', v))
        layout_lay.addWidget(sb_vfill)
        
        sl.addWidget(layout_group)
        
        # === NODE LABELS ===
        label_group = QGroupBox("Node Labels")
        label_lay = QVBoxLayout(label_group)
        
        label_lay.addWidget(QLabel("Font Family:"))
        cb_font = QComboBox()
        cb_font.addItems(['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana', 'Georgia'])
        cb_font.setCurrentText(self.style_manager.style_opts.get('label_font_family', 'Arial'))
        cb_font.currentTextChanged.connect(lambda v: self.update_style('label_font_family', v))
        label_lay.addWidget(cb_font)
        
        label_lay.addWidget(QLabel("Font Size:"))
        sb_label_size = QSpinBox()
        sb_label_size.setRange(6, 24)
        sb_label_size.setValue(self.style_manager.style_opts.get('label_font_size', 12))
        sb_label_size.valueChanged.connect(lambda v: self.update_style('label_font_size', v))
        label_lay.addWidget(sb_label_size)
        
        btn_label_color = QPushButton("Font Color")
        btn_label_color.clicked.connect(lambda: self.pick_color('label_font_color'))
        label_lay.addWidget(btn_label_color)
        
        c_show_weight = QCheckBox("Show Weights (%)")
        c_show_weight.setChecked(self.style_manager.style_opts.get('show_node_weight', True))
        c_show_weight.toggled.connect(lambda v: self.update_style('show_node_weight', v))
        label_lay.addWidget(c_show_weight)
        
        sl.addWidget(label_group)
        
        # === NODES ===
        node_group = QGroupBox("Nodes")
        node_lay = QVBoxLayout(node_group)
        
        h_col = QHBoxLayout()
        btn_nc = QPushButton("Fill Color")
        btn_nc.clicked.connect(lambda: self.pick_color('node_color'))
        h_col.addWidget(btn_nc)
        btn_lc = QPushButton("Border Color")
        btn_lc.clicked.connect(lambda: self.pick_color('node_line_color'))
        h_col.addWidget(btn_lc)
        node_lay.addLayout(h_col)
        
        node_lay.addWidget(QLabel("Thickness:"))
        sb_thick = QSpinBox()
        sb_thick.setValue(self.style_manager.style_opts['thickness'])
        sb_thick.setRange(0, 200)
        sb_thick.valueChanged.connect(lambda v: self.update_style('thickness', v))
        node_lay.addWidget(sb_thick)
        
        node_lay.addWidget(QLabel("Border Width:"))
        sb_bw = QDoubleSpinBox()
        sb_bw.setValue(self.style_manager.style_opts.get('node_line_width', 0.5))
        sb_bw.setRange(0, 10)
        sb_bw.setSingleStep(0.5)
        sb_bw.valueChanged.connect(lambda v: self.update_style('node_line_width', v))
        node_lay.addWidget(sb_bw)
        
        node_lay.addWidget(QLabel("Spacing:"))
        sb_pad = QSpinBox()
        sb_pad.setValue(self.style_manager.style_opts['pad'])
        sb_pad.setRange(0, 100)
        sb_pad.valueChanged.connect(lambda v: self.update_style('pad', v))
        node_lay.addWidget(sb_pad)
        
        sl.addWidget(node_group)
        
        # === LINKS ===
        link_group = QGroupBox("Links")
        link_lay = QVBoxLayout(link_group)
        
        btn_link_c = QPushButton("Link Color")
        btn_link_c.clicked.connect(self.pick_link_color)
        link_lay.addWidget(btn_link_c)
        
        link_lay.addWidget(QLabel("Opacity:"))
        sb_op = QDoubleSpinBox()
        sb_op.setRange(0.0, 1.0)
        sb_op.setSingleStep(0.1)
        sb_op.setValue(self.style_manager.style_opts['link_opacity'])
        sb_op.valueChanged.connect(lambda v: self.update_link_opacity(v))
        link_lay.addWidget(sb_op)
        
        sl.addWidget(link_group)
        
        # === SHADOW LAYER ===
        shadow_group = QGroupBox("Shadow Layer (Background)")
        shadow_lay = QVBoxLayout(shadow_group)

        btn_shadow_node = QPushButton("Shadow Node Color")
        btn_shadow_node.clicked.connect(lambda: self.pick_color('shadow_node_color'))
        shadow_lay.addWidget(btn_shadow_node)

        btn_shadow_link = QPushButton("Shadow Link Color")
        btn_shadow_link.clicked.connect(self.pick_shadow_link_color)
        shadow_lay.addWidget(btn_shadow_link)

        sl.addWidget(shadow_group)

        
        # ========== MATRIX STYLES ==========
        sl.addSpacing(20)
        sl.addWidget(QLabel("<b>— Matrix Diagram —</b>"))
        
        # === CURVE STYLE ===
        curve_group = QGroupBox("Curve")
        curve_lay = QVBoxLayout(curve_group)
        
        btn_curve_color = QPushButton("Curve Color")
        btn_curve_color.clicked.connect(self.pick_matrix_curve_color)
        curve_lay.addWidget(btn_curve_color)
        
        curve_lay.addWidget(QLabel("Line Width:"))
        sp_curve_width = QSpinBox()
        sp_curve_width.setValue(self.style_manager.matrix_style_opts['width'])
        sp_curve_width.setRange(1, 10)
        sp_curve_width.valueChanged.connect(lambda v: self.update_matrix_style('width', v))
        curve_lay.addWidget(sp_curve_width)
        
        curve_lay.addWidget(QLabel("Line Style:"))
        cb_curve_dash = QComboBox()
        cb_curve_dash.addItems(["solid", "dash", "dot", "dashdot"])
        cb_curve_dash.setCurrentText(self.style_manager.matrix_style_opts['dash'])
        cb_curve_dash.currentTextChanged.connect(lambda v: self.update_matrix_style('dash', v))
        curve_lay.addWidget(cb_curve_dash)
        
        sl.addWidget(curve_group)
        
        # === FONT STYLE ===
        matrix_font_group = QGroupBox("Fonts")
        matrix_font_lay = QVBoxLayout(matrix_font_group)
        
        matrix_font_lay.addWidget(QLabel("Font Family:"))
        cb_matrix_font = QComboBox()
        cb_matrix_font.addItems(['Arial', 'Times New Roman', 'Courier New', 'Verdana', 
                                 'Helvetica', 'Georgia', 'Calibri', 'Open Sans'])
        cb_matrix_font.setCurrentText(self.style_manager.matrix_style_opts['font_family'])
        cb_matrix_font.currentTextChanged.connect(lambda v: self.update_matrix_style('font_family', v))
        matrix_font_lay.addWidget(cb_matrix_font)
        
        matrix_font_lay.addWidget(QLabel("Title Size:"))
        sp_matrix_title = QSpinBox()
        sp_matrix_title.setValue(self.style_manager.matrix_style_opts['font_size_title'])
        sp_matrix_title.setRange(8, 48)
        sp_matrix_title.valueChanged.connect(lambda v: self.update_matrix_style('font_size_title', v))
        matrix_font_lay.addWidget(sp_matrix_title)
        
        matrix_font_lay.addWidget(QLabel("Axis Labels Size:"))
        sp_matrix_axes = QSpinBox()
        sp_matrix_axes.setValue(self.style_manager.matrix_style_opts['font_size_axes'])
        sp_matrix_axes.setRange(8, 24)
        sp_matrix_axes.valueChanged.connect(lambda v: self.update_matrix_style('font_size_axes', v))
        matrix_font_lay.addWidget(sp_matrix_axes)
        
        sl.addWidget(matrix_font_group)
        
        # === AXIS STYLE ===
        matrix_axis_group = QGroupBox("Axis Lines")
        matrix_axis_lay = QVBoxLayout(matrix_axis_group)
        
        btn_matrix_axis_color = QPushButton("Axis Color")
        btn_matrix_axis_color.clicked.connect(self.pick_matrix_axis_color)
        matrix_axis_lay.addWidget(btn_matrix_axis_color)
        
        matrix_axis_lay.addWidget(QLabel("Axis Width:"))
        sp_matrix_axis_w = QSpinBox()
        sp_matrix_axis_w.setValue(self.style_manager.matrix_style_opts['axis_line_width'])
        sp_matrix_axis_w.setRange(1, 5)
        sp_matrix_axis_w.valueChanged.connect(lambda v: self.update_matrix_style('axis_line_width', v))
        matrix_axis_lay.addWidget(sp_matrix_axis_w)
        
        matrix_axis_lay.addWidget(QLabel("Visible Lines:"))
        
        c_matrix_axis_top = QCheckBox("Top")
        c_matrix_axis_top.setChecked(self.style_manager.matrix_style_opts['show_axis_top'])
        c_matrix_axis_top.toggled.connect(lambda v: self.update_matrix_style('show_axis_top', v))
        matrix_axis_lay.addWidget(c_matrix_axis_top)
        
        c_matrix_axis_bottom = QCheckBox("Bottom")
        c_matrix_axis_bottom.setChecked(self.style_manager.matrix_style_opts['show_axis_bottom'])
        c_matrix_axis_bottom.toggled.connect(lambda v: self.update_matrix_style('show_axis_bottom', v))
        matrix_axis_lay.addWidget(c_matrix_axis_bottom)
        
        c_matrix_axis_left = QCheckBox("Left")
        c_matrix_axis_left.setChecked(self.style_manager.matrix_style_opts['show_axis_left'])
        c_matrix_axis_left.toggled.connect(lambda v: self.update_matrix_style('show_axis_left', v))
        matrix_axis_lay.addWidget(c_matrix_axis_left)
        
        c_matrix_axis_right = QCheckBox("Right")
        c_matrix_axis_right.setChecked(self.style_manager.matrix_style_opts['show_axis_right'])
        c_matrix_axis_right.toggled.connect(lambda v: self.update_matrix_style('show_axis_right', v))
        matrix_axis_lay.addWidget(c_matrix_axis_right)
        
        sl.addWidget(matrix_axis_group)
        
        # === GRID STYLE ===
        matrix_grid_group = QGroupBox("Grid")
        matrix_grid_lay = QVBoxLayout(matrix_grid_group)
        
        c_matrix_grid = QCheckBox("Show Grid")
        c_matrix_grid.setChecked(self.style_manager.matrix_style_opts['grid'])
        c_matrix_grid.toggled.connect(lambda v: self.update_matrix_style('grid', v))
        matrix_grid_lay.addWidget(c_matrix_grid)
        
        btn_matrix_grid_color = QPushButton("Grid Color")
        btn_matrix_grid_color.clicked.connect(self.pick_matrix_grid_color)
        matrix_grid_lay.addWidget(btn_matrix_grid_color)
        
        matrix_grid_lay.addWidget(QLabel("Grid Width:"))
        sp_matrix_grid_w = QSpinBox()
        sp_matrix_grid_w.setValue(self.style_manager.matrix_style_opts['grid_line_width'])
        sp_matrix_grid_w.setRange(1, 5)
        sp_matrix_grid_w.valueChanged.connect(lambda v: self.update_matrix_style('grid_line_width', v))
        matrix_grid_lay.addWidget(sp_matrix_grid_w)
        
        matrix_grid_lay.addWidget(QLabel("Grid Style:"))
        cb_matrix_grid_dash = QComboBox()
        cb_matrix_grid_dash.addItems(["solid", "dash", "dot", "dashdot"])
        cb_matrix_grid_dash.setCurrentText(self.style_manager.matrix_style_opts['grid_line_dash'])
        cb_matrix_grid_dash.currentTextChanged.connect(lambda v: self.update_matrix_style('grid_line_dash', v))
        matrix_grid_lay.addWidget(cb_matrix_grid_dash)
        
        sl.addWidget(matrix_grid_group)
        
        # === BACKGROUND ===
        matrix_bg_group = QGroupBox("Background")
        matrix_bg_lay = QVBoxLayout(matrix_bg_group)
        
        btn_matrix_bg_color = QPushButton("Background Color")
        btn_matrix_bg_color.clicked.connect(self.pick_matrix_background_color)
        matrix_bg_lay.addWidget(btn_matrix_bg_color)
        
        sl.addWidget(matrix_bg_group)
        
        # === ACTIONS ===
        sl.addSpacing(20)
        
        btn_reset = QPushButton("🔄 Reset to Defaults")
        btn_reset.clicked.connect(self.reset_styles)
        sl.addWidget(btn_reset)
        
        sl.addStretch()
        
        sidebar.setWidget(content)
        return sidebar

    def update_style(self, key, value):
        """Update shared style - triggers update in all scenario tabs"""
        self.style_manager.update_style(key, value)
    
    def pick_color(self, key):
        """Pick a color for shared style"""
        current = self.style_manager.style_opts.get(key, '#000000')
        c = QColorDialog.getColor(QColor(current))
        if c.isValid():
            self.style_manager.update_style(key, c.name())
    
    def pick_link_color(self):
        """Pick link color for shared style"""
        c = QColorDialog.getColor()
        if c.isValid():
            opacity = self.style_manager.style_opts.get('link_opacity', 0.4)
            new_color = f"rgba({c.red()},{c.green()},{c.blue()},{opacity})"
            self.style_manager.update_style('link_color', new_color)
    
    def update_link_opacity(self, value):
        """Update link opacity in shared style"""
        self.style_manager.style_opts['link_opacity'] = value
        current_color = self.style_manager.style_opts.get('link_color', 'rgba(180, 180, 180, 0.4)')
        
        rgba_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', current_color)
        if rgba_match:
            r, g, b = rgba_match.groups()
            new_color = f"rgba({r},{g},{b},{value})"
        else:
            new_color = f"rgba(180,180,180,{value})"
        
        self.style_manager.update_style('link_color', new_color)
    
    def handle_tab_click(self, index):
        """Handle clicks on "+" tab"""
        if index == self.scenario_tabs.count() - 1:
            self.create_scenario()
    
    def create_scenario(self):
        """Create a new scenario sub-tab"""
        root = self.tree_widget.topLevelItem(0)
        if not root:
            QMessageBox.warning(self, "No Structure", "Please create a tree structure first in Tab 1.")
            return
        
        # Check if there are indicators
        has_indicators = False
        def check_indicators(item):
            nonlocal has_indicators
            if item.text(2) == "Indicator":
                has_indicators = True
                return
            for i in range(item.childCount()):
                check_indicators(item.child(i))
        check_indicators(root)
        
        if not has_indicators:
            QMessageBox.warning(self, "No Indicators", 
                              "Please add at least one indicator to the tree.")
            return
        
        # Create new scenario tab (simplified - no style controls)
        self.scenario_counter += 1
        scenario = ScenarioTab(self.tree_widget, self.style_manager)

        # Insert tab and select it
        idx = self.scenario_tabs.insertTab(self.scenario_tabs.count() - 1, scenario, f"Scenario {self.scenario_counter}")
        self.scenario_tabs.setCurrentIndex(idx)

        # Ensure the scenario has loaded its indicators (ScenarioTab.__init__ already calls load_indicators)
        # Apply shared column sizes if available
        try:
            header = scenario.table.horizontalHeader()
            # If we already have stored sizes, apply them to the new tab
            if self._shared_col_sizes:
                header.blockSignals(True)
                for col_index, col_size in enumerate(self._shared_col_sizes):
                    if col_index < scenario.table.columnCount():
                        header.resizeSection(col_index, col_size)
                header.blockSignals(False)
            else:
                # If this is the first scenario, capture its initial sizes as shared
                sizes = []
                for c in range(scenario.table.columnCount()):
                    sizes.append(header.sectionSize(c))
                self._shared_col_sizes = sizes

            # Connect its resize signal so changes propagate to other tabs
            self._connect_tab_resize_signals(scenario)
            # Connect splitter signals to synchronize layouts across scenario tabs
            try:
                # Apply stored main splitter sizes or capture initial
                if hasattr(scenario, 'main_splitter'):
                    if self._shared_main_splitter_sizes:
                        scenario.main_splitter.blockSignals(True)
                        scenario.main_splitter.setSizes(self._shared_main_splitter_sizes)
                        scenario.main_splitter.blockSignals(False)
                    else:
                        self._shared_main_splitter_sizes = scenario.main_splitter.sizes()

                    # Connect to propagate moves
                    scenario.main_splitter.splitterMoved.connect(lambda pos, index, tab=scenario: self._on_main_splitter_moved(tab))

                # Chart splitter (vertical) sizes
                if hasattr(scenario, 'chart_splitter'):
                    if self._shared_chart_splitter_sizes:
                        scenario.chart_splitter.blockSignals(True)
                        scenario.chart_splitter.setSizes(self._shared_chart_splitter_sizes)
                        scenario.chart_splitter.blockSignals(False)
                    else:
                        self._shared_chart_splitter_sizes = scenario.chart_splitter.sizes()

                    scenario.chart_splitter.splitterMoved.connect(lambda pos, index, tab=scenario: self._on_chart_splitter_moved(tab))
            except Exception:
                pass
        except Exception:
            # Be tolerant if the table isn't ready; still continue
            pass

        self.update_close_buttons()

    def _connect_tab_resize_signals(self, scenario_tab):
        """Connect the scenario tab's table header resize signal to the
        container handler which will propagate the new size to other tabs.

        Uses a bound lambda to pass the source tab reference to the handler.
        """
        header = scenario_tab.table.horizontalHeader()
        # PyQt6 signal: sectionResized(int logicalIndex, int oldSize, int newSize)
        header.sectionResized.connect(lambda index, old, new, tab=scenario_tab: self._on_column_resized(tab, index, old, new))

    def _on_main_splitter_moved(self, source_tab):
        """Propagate main horizontal splitter sizes from source_tab to others.
        Optimized to batch updates and reduce redundant operations."""
        try:
            sizes = source_tab.main_splitter.sizes()
        except Exception:
            return

        # Update shared cache
        self._shared_main_splitter_sizes = sizes

        # Collect tabs that need updates using list comprehension
        tab_count = self.scenario_tabs.count() - 1
        tabs_to_update = [
            tab for i in range(tab_count)
            if (tab := self.scenario_tabs.widget(i)) is not source_tab 
            and hasattr(tab, 'main_splitter')
        ]

        # Apply updates in batch
        for tab in tabs_to_update:
            try:
                tab.main_splitter.blockSignals(True)
                tab.main_splitter.setSizes(sizes)
                tab.main_splitter.blockSignals(False)
            except Exception:
                pass

    def _on_chart_splitter_moved(self, source_tab):
        """Propagate chart vertical splitter sizes from source_tab to others.
        Optimized to batch updates and reduce redundant operations."""
        try:
            sizes = source_tab.chart_splitter.sizes()
        except Exception:
            return

        self._shared_chart_splitter_sizes = sizes

        # Collect tabs that need updates using list comprehension
        tab_count = self.scenario_tabs.count() - 1
        tabs_to_update = [
            tab for i in range(tab_count)
            if (tab := self.scenario_tabs.widget(i)) is not source_tab 
            and hasattr(tab, 'chart_splitter')
        ]

        # Apply updates in batch
        for tab in tabs_to_update:
            try:
                tab.chart_splitter.blockSignals(True)
                tab.chart_splitter.setSizes(sizes)
                tab.chart_splitter.blockSignals(False)
            except Exception:
                pass

    def _on_column_resized(self, source_tab, logicalIndex, oldSize, newSize):
        """Propagate a column resize from `source_tab` to all other scenario tabs.
        Optimized to batch collection and updates.

        Temporarily blocks signals on target headers to avoid recursion.
        Also updates the shared column size cache so newly created tabs use
        the latest sizes.
        """
        # Update shared cache
        if logicalIndex >= len(self._shared_col_sizes):
            self._shared_col_sizes.extend([0] * (logicalIndex + 1 - len(self._shared_col_sizes)))
        self._shared_col_sizes[logicalIndex] = newSize

        # Batch collect tabs and headers that need updates
        updates = []
        tab_count = self.scenario_tabs.count() - 1
        for i in range(tab_count):
            tab = self.scenario_tabs.widget(i)
            if tab is not source_tab and hasattr(tab, 'table'):
                header = tab.table.horizontalHeader()
                # Only include if column exists
                if logicalIndex < tab.table.columnCount():
                    updates.append((header, logicalIndex, newSize))

        # Apply all updates in batch
        for header, col_idx, size in updates:
            try:
                header.blockSignals(True)
                header.resizeSection(col_idx, size)
                header.blockSignals(False)
            except Exception:
                pass
    
    def close_scenario_tab(self, index):
        """Close a scenario sub-tab"""
        if index < self.scenario_tabs.count() - 1:
            self.scenario_tabs.removeTab(index)
    
    def update_close_buttons(self):
        """Disable close button for "+" tab"""
        tab_bar = self.scenario_tabs.tabBar()
        if self.scenario_tabs.count() > 0:
            tab_bar.setTabButton(
                self.scenario_tabs.count() - 1, 
                QTabBar.ButtonPosition.RightSide, 
                None
            )
    
    def on_scenario_tab_change(self, index):
        """Refresh scenario tab when switching"""
        if index >= 0 and index < self.scenario_tabs.count() - 1:
            current_tab = self.scenario_tabs.widget(index)
            if isinstance(current_tab, ScenarioTab):
                current_tab.load_indicators()
    
    def refresh_all_scenarios(self):
        """Refresh all scenario tabs"""
        for i in range(self.scenario_tabs.count() - 1):
            tab = self.scenario_tabs.widget(i)
            if isinstance(tab, ScenarioTab):
                tab.load_indicators()
                
    def reset_styles(self):
        """Reset all styles to defaults"""
        from gui.styles import DEFAULT_SANKEY_STYLE, DEFAULT_FUNC_STYLE
        
        # Reset Sankey styles
        for key, value in DEFAULT_SANKEY_STYLE.items():
            self.style_manager.style_opts[key] = value
        
        # Reset Matrix styles
        for key, value in DEFAULT_FUNC_STYLE.items():
            self.style_manager.matrix_style_opts[key] = value
        
        # Reset export scale
        self.style_manager.set_export_scale(1.0)
        self.sb_export_scale.setValue(1.0)
        
        # Trigger updates
        self.style_manager.style_changed.emit()
        self.style_manager.matrix_style_changed.emit()
        
        # Recreate sidebar
        old_sidebar = self.style_sidebar
        parent_splitter = old_sidebar.parent()
        
        self.style_sidebar = self.create_style_sidebar()
        
        if isinstance(parent_splitter, QSplitter):
            parent_splitter.replaceWidget(0, self.style_sidebar)

    def on_export_scale_changed(self, scale):
        """Handle export scale change"""
        self.style_manager.set_export_scale(scale)
        self.lbl_export_info.setText(f"Scale: {scale:.2f}× ({'Larger' if scale > 1 else 'Smaller' if scale < 1 else 'Normal'} size)")
        
    def update_matrix_style(self, key, value):
        """Update matrix style - triggers update in all scenario tabs"""
        self.style_manager.update_matrix_style(key, value)

    def pick_matrix_curve_color(self):
        """Pick curve color for matrix"""
        c = QColorDialog.getColor(QColor(self.style_manager.matrix_style_opts['color']))
        if c.isValid():
            self.style_manager.update_matrix_style('color', c.name())

    def pick_matrix_axis_color(self):
        """Pick axis color for matrix"""
        c = QColorDialog.getColor(QColor(self.style_manager.matrix_style_opts['axis_line_color']))
        if c.isValid():
            self.style_manager.update_matrix_style('axis_line_color', c.name())

    def pick_matrix_grid_color(self):
        """Pick grid color for matrix"""
        c = QColorDialog.getColor(QColor(self.style_manager.matrix_style_opts['grid_line_color']))
        if c.isValid():
            self.style_manager.update_matrix_style('grid_line_color', c.name())

    def pick_matrix_background_color(self):
        """Pick background color for matrix"""
        c = QColorDialog.getColor(QColor(self.style_manager.matrix_style_opts['background_color']))
        if c.isValid():
            self.style_manager.update_matrix_style('background_color', c.name())

    def pick_shadow_link_color(self):
        """Pick shadow link color with fixed low opacity"""
        c = QColorDialog.getColor()
        if c.isValid():
            new_color = f"rgba({c.red()},{c.green()},{c.blue()},0.3)"
            self.style_manager.update_style('shadow_link_color', new_color)


