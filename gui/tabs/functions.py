"""
Tab 2: Value Function Editor (Enhanced)
"""
import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QSplitter, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDoubleSpinBox, QLineEdit, QComboBox,
                             QSpinBox, QCheckBox, QFileDialog, QMessageBox, QColorDialog,
                             QScrollArea, QGroupBox)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from logic.math_engine import MivesLogic
from logic.data_manager import DataManager
from logic.tree_utils import collect_indicators
from gui.styles import DEFAULT_FUNC_STYLE


class FunctionsTab(QWidget):
    """Value function editor tab with enhanced styling controls"""
    
    def __init__(self, tree_widget, parent=None):
        super().__init__(parent)
        self.tree_widget = tree_widget
        self.mives_engine = MivesLogic()
        self.data_manager = DataManager()
        self.current_indicator_item = None
        self.func_chart_style = DEFAULT_FUNC_STYLE.copy()
        self.export_scale = 1.0
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel: Indicator Table (WITH REQUIREMENTS COLUMN)
        left_frame = QFrame()
        l_lay = QVBoxLayout(left_frame)
        l_lay.addWidget(QLabel("<b>Indicators Hierarchy</b>"))
        
        self.ind_table = QTableWidget()
        self.ind_table.setColumnCount(3)
        self.ind_table.setHorizontalHeaderLabels(["Requirement", "Criterion", "Indicator"])
        self.ind_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.ind_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ind_table.verticalHeader().setVisible(False)
        self.ind_table.itemClicked.connect(self.on_table_click)
        l_lay.addWidget(self.ind_table)
        
        l_lay.addSpacing(10)
        
        # Batch export button
        btn_batch = QPushButton("📸 Batch Export Charts")
        btn_batch.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_batch.clicked.connect(self.batch_export_charts)
        l_lay.addWidget(btn_batch)
        
        l_lay.addSpacing(5)
        
        btn_exp = QPushButton("💾 Export Functions CSV")
        btn_exp.clicked.connect(self.export_functions)
        l_lay.addWidget(btn_exp)
        
        btn_imp = QPushButton("📂 Import Functions CSV")
        btn_imp.clicked.connect(self.import_functions)
        l_lay.addWidget(btn_imp)
        
        splitter.addWidget(left_frame)
        
        # Right Panel: Parameters + Preview
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Parameters Section
        params_container = QFrame()
        p_lay = QVBoxLayout(params_container)
        
        h_box = QHBoxLayout()
        h_box.addWidget(QLabel("<b>MIVES Parameters</b>"))
        h_box.addStretch()
        
        self.combo_preset = QComboBox()
        self.combo_preset.addItems(["Custom", "Linear", "Convex", "Concave", "S-Shape"])
        self.combo_preset.currentIndexChanged.connect(self.apply_preset)
        h_box.addWidget(QLabel("Preset:"))
        h_box.addWidget(self.combo_preset)
        p_lay.addLayout(h_box)
        
        # Range inputs
        range_box = QHBoxLayout()
        self.spin_x0 = QDoubleSpinBox()
        self.spin_x0.setRange(-1e9, 1e9)
        self.spin_x0.setDecimals(2)
        
        self.spin_x1 = QDoubleSpinBox()
        self.spin_x1.setRange(-1e9, 1e9)
        self.spin_x1.setDecimals(2)
        
        self.input_units = QLineEdit()
        
        v1 = QVBoxLayout()
        v1.addWidget(QLabel("X_sat=0"))
        v1.addWidget(self.spin_x0)
        
        v2 = QVBoxLayout()
        v2.addWidget(QLabel("X_sat=1"))
        v2.addWidget(self.spin_x1)
        
        v3 = QVBoxLayout()
        v3.addWidget(QLabel("Units"))
        v3.addWidget(self.input_units)
        
        range_box.addLayout(v1)
        range_box.addLayout(v2)
        range_box.addLayout(v3)
        p_lay.addLayout(range_box)
        
        # Math parameters
        math_box = QHBoxLayout()
        
        vp = QVBoxLayout()
        vp.addWidget(QLabel("P (Shape)"))
        self.spin_p = QDoubleSpinBox()
        self.spin_p.setRange(0.01, 50)
        self.spin_p.setSingleStep(0.1)
        self.spin_p.setValue(1)
        vp.addWidget(self.spin_p)
        math_box.addLayout(vp)
        
        vk = QVBoxLayout()
        vk.addWidget(QLabel("K (Y-Infl)"))
        self.spin_k = QDoubleSpinBox()
        self.spin_k.setRange(0, 50)
        self.spin_k.setSingleStep(0.1)
        self.spin_k.setValue(0.1)
        vk.addWidget(self.spin_k)
        math_box.addLayout(vk)
        
        vc = QVBoxLayout()
        vc.addWidget(QLabel("C (X-Infl)"))
        self.spin_c = QDoubleSpinBox()
        self.spin_c.setRange(0.0001, 1e9)
        self.spin_c.setSingleStep(10)
        self.spin_c.setValue(50)
        vc.addWidget(self.spin_c)
        math_box.addLayout(vc)
        
        p_lay.addLayout(math_box)
        
        btn_upd = QPushButton("🔄 Update & Apply")
        btn_upd.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")
        btn_upd.clicked.connect(self.save_and_preview)
        p_lay.addWidget(btn_upd)
        
        p_lay.addStretch()
        right_splitter.addWidget(params_container)
        
        # Preview Section with Enhanced Style Controls
        viz_container = QFrame()
        viz_lay = QVBoxLayout(viz_container)
        
        tb = QHBoxLayout()
        btn_settings = QPushButton("⚙️ Chart Styles")
        btn_settings.setCheckable(True)
        btn_settings.clicked.connect(self.toggle_style_sidebar)
        tb.addWidget(btn_settings)
        tb.addStretch()
        
        btn_save_img = QPushButton("📷 Save Image")
        btn_save_img.clicked.connect(self.export_preview_image)
        tb.addWidget(btn_save_img)
        viz_lay.addLayout(tb)
        
        self.chart_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # ENHANCED STYLE SIDEBAR
        self.style_sidebar = self.create_style_sidebar()
        self.chart_splitter.addWidget(self.style_sidebar)
        
        self.preview_web = QWebEngineView()
        self.chart_splitter.addWidget(self.preview_web)
        self.chart_splitter.setSizes([200, 800])
        
        viz_lay.addWidget(self.chart_splitter)
        right_splitter.addWidget(viz_container)
        right_splitter.setSizes([250, 600])
        
        splitter.addWidget(right_splitter)
        splitter.setSizes([400, 900])
        layout.addWidget(splitter)
        QTimer.singleShot(100, self.update_dimensions_label)
    
    def create_style_sidebar(self):
        """Create enhanced style control sidebar"""
        sidebar = QScrollArea()
        sidebar.setWidgetResizable(True)
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setVisible(False)
        
        content = QWidget()
        sl = QVBoxLayout(content)
        sl.setContentsMargins(10, 10, 10, 10)
        
        sl.addWidget(QLabel("<b>Chart Styling</b>"))
        
        # === EXPORT SETTINGS ===
        export_group = QGroupBox("Export Settings")
        export_lay = QVBoxLayout(export_group)
        
        export_lay.addWidget(QLabel("Export Scale Multiplier:"))
        self.sb_export_scale = QDoubleSpinBox()
        self.sb_export_scale.setRange(0.25, 5.0)
        self.sb_export_scale.setSingleStep(0.25)
        self.sb_export_scale.setValue(self.export_scale)
        self.sb_export_scale.setDecimals(2)
        self.sb_export_scale.valueChanged.connect(self.on_export_scale_changed)
        export_lay.addWidget(self.sb_export_scale)
        
        self.lbl_dimensions = QLabel("Export size: calculating...")
        self.lbl_dimensions.setStyleSheet("color: #555; font-style: italic;")
        export_lay.addWidget(self.lbl_dimensions)
        
        sl.addWidget(export_group)
        
        # === CURVE STYLE ===
        curve_group = QGroupBox("Curve")
        curve_lay = QVBoxLayout(curve_group)
        
        btn_color = QPushButton("Curve Color")
        btn_color.clicked.connect(self.pick_curve_color)
        curve_lay.addWidget(btn_color)
        
        curve_lay.addWidget(QLabel("Line Width:"))
        sp_width = QSpinBox()
        sp_width.setValue(self.func_chart_style['width'])
        sp_width.setRange(1, 10)
        sp_width.valueChanged.connect(lambda v: self.update_func_style('width', v))
        curve_lay.addWidget(sp_width)
        
        curve_lay.addWidget(QLabel("Line Style:"))
        cb_dash = QComboBox()
        cb_dash.addItems(["solid", "dash", "dot", "dashdot"])
        cb_dash.setCurrentText(self.func_chart_style['dash'])
        cb_dash.currentTextChanged.connect(lambda v: self.update_func_style('dash', v))
        curve_lay.addWidget(cb_dash)
        
        sl.addWidget(curve_group)
        
        # === FONT STYLE ===
        font_group = QGroupBox("Fonts")
        font_lay = QVBoxLayout(font_group)
        
        font_lay.addWidget(QLabel("Font Family:"))
        cb_font = QComboBox()
        cb_font.addItems(["Arial", "Times New Roman", "Courier New", "Verdana", 
                         "Helvetica", "Georgia", "Calibri", "Open Sans"])
        cb_font.setCurrentText(self.func_chart_style['font_family'])
        cb_font.currentTextChanged.connect(lambda v: self.update_func_style('font_family', v))
        font_lay.addWidget(cb_font)
        
        font_lay.addWidget(QLabel("Title Size:"))
        sp_title = QSpinBox()
        sp_title.setValue(self.func_chart_style['font_size_title'])
        sp_title.setRange(8, 48)
        sp_title.valueChanged.connect(lambda v: self.update_func_style('font_size_title', v))
        font_lay.addWidget(sp_title)
        
        font_lay.addWidget(QLabel("Axis Labels Size:"))
        sp_axes = QSpinBox()
        sp_axes.setValue(self.func_chart_style['font_size_axes'])
        sp_axes.setRange(8, 24)
        sp_axes.valueChanged.connect(lambda v: self.update_func_style('font_size_axes', v))
        font_lay.addWidget(sp_axes)
        
        sl.addWidget(font_group)
        
        # === AXIS STYLE (WITH INDIVIDUAL LINE CONTROLS) ===
        axis_group = QGroupBox("Axis Lines")
        axis_lay = QVBoxLayout(axis_group)
        
        btn_axis_color = QPushButton("Axis Color")
        btn_axis_color.clicked.connect(self.pick_axis_color)
        axis_lay.addWidget(btn_axis_color)
        
        axis_lay.addWidget(QLabel("Axis Width:"))
        sp_axis_w = QSpinBox()
        sp_axis_w.setValue(self.func_chart_style['axis_line_width'])
        sp_axis_w.setRange(1, 5)
        sp_axis_w.valueChanged.connect(lambda v: self.update_func_style('axis_line_width', v))
        axis_lay.addWidget(sp_axis_w)
        
        # INDIVIDUAL AXIS LINE TOGGLES
        axis_lay.addWidget(QLabel("Visible Lines:"))
        
        c_axis_top = QCheckBox("Top")
        c_axis_top.setChecked(self.func_chart_style['show_axis_top'])
        c_axis_top.toggled.connect(lambda v: self.update_func_style('show_axis_top', v))
        axis_lay.addWidget(c_axis_top)
        
        c_axis_bottom = QCheckBox("Bottom")
        c_axis_bottom.setChecked(self.func_chart_style['show_axis_bottom'])
        c_axis_bottom.toggled.connect(lambda v: self.update_func_style('show_axis_bottom', v))
        axis_lay.addWidget(c_axis_bottom)
        
        c_axis_left = QCheckBox("Left")
        c_axis_left.setChecked(self.func_chart_style['show_axis_left'])
        c_axis_left.toggled.connect(lambda v: self.update_func_style('show_axis_left', v))
        axis_lay.addWidget(c_axis_left)
        
        c_axis_right = QCheckBox("Right")
        c_axis_right.setChecked(self.func_chart_style['show_axis_right'])
        c_axis_right.toggled.connect(lambda v: self.update_func_style('show_axis_right', v))
        axis_lay.addWidget(c_axis_right)
        
        sl.addWidget(axis_group)
        
        # === GRID STYLE ===
        grid_group = QGroupBox("Grid")
        grid_lay = QVBoxLayout(grid_group)
        
        c_grid = QCheckBox("Show Grid")
        c_grid.setChecked(self.func_chart_style['grid'])
        c_grid.toggled.connect(lambda v: self.update_func_style('grid', v))
        grid_lay.addWidget(c_grid)
        
        btn_grid_color = QPushButton("Grid Color")
        btn_grid_color.clicked.connect(self.pick_grid_color)
        grid_lay.addWidget(btn_grid_color)
        
        grid_lay.addWidget(QLabel("Grid Width:"))
        sp_grid_w = QSpinBox()
        sp_grid_w.setValue(self.func_chart_style['grid_line_width'])
        sp_grid_w.setRange(1, 5)
        sp_grid_w.valueChanged.connect(lambda v: self.update_func_style('grid_line_width', v))
        grid_lay.addWidget(sp_grid_w)
        
        grid_lay.addWidget(QLabel("Grid Style:"))
        cb_grid_dash = QComboBox()
        cb_grid_dash.addItems(["solid", "dash", "dot", "dashdot"])
        cb_grid_dash.setCurrentText(self.func_chart_style['grid_line_dash'])
        cb_grid_dash.currentTextChanged.connect(lambda v: self.update_func_style('grid_line_dash', v))
        grid_lay.addWidget(cb_grid_dash)
        
        sl.addWidget(grid_group)
        
        # === BACKGROUND ===
        bg_group = QGroupBox("Background")
        bg_lay = QVBoxLayout(bg_group)
        
        btn_bg_color = QPushButton("Background Color")
        btn_bg_color.clicked.connect(self.pick_background_color)
        bg_lay.addWidget(btn_bg_color)
        
        sl.addWidget(bg_group)
        
        sl.addStretch()
        
        sidebar.setWidget(content)
        return sidebar
    
    def refresh_ind_list(self):
        """Refresh indicator table with Requirement -> Criterion -> Indicator hierarchy"""
        self.ind_table.setRowCount(0)
        
        indicators = []
        
        def find_requirement(item):
            """Traverse up to find the requirement"""
            current = item
            while current:
                if current.text(2) == "Requirement":
                    return current.text(0)
                current = current.parent()
            return "Unknown"
        
        def find(item):
            if item.text(2) == "Indicator":
                parent_txt = item.parent().text(0) if item.parent() else "Unknown"
                req_txt = find_requirement(item)
                indicators.append((req_txt, parent_txt, item))
            for i in range(item.childCount()):
                find(item.child(i))
        
        root = self.tree_widget.topLevelItem(0)
        if root:
            find(root)
        
        self.ind_table.setRowCount(len(indicators))
        
        # Group by requirement, then by criterion
        last_req = None
        last_crit = None
        req_start_row = 0
        crit_start_row = 0
        
        for r, (req_txt, crit_txt, item) in enumerate(indicators):
            # Column 0: Requirement (read-only)
            if req_txt != last_req:
                if r > 0 and last_req is not None:
                    span_len = r - req_start_row
                    if span_len > 1:
                        self.ind_table.setSpan(req_start_row, 0, span_len, 1)
                
                last_req = req_txt
                req_start_row = r
                req_item = QTableWidgetItem(req_txt)
                req_item.setFlags(req_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.ind_table.setItem(r, 0, req_item)
            else:
                req_item = QTableWidgetItem(req_txt)
                req_item.setFlags(req_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.ind_table.setItem(r, 0, req_item)
            
            # Column 1: Criterion (read-only)
            if crit_txt != last_crit:
                if r > 0 and last_crit is not None and crit_start_row < r:
                    span_len = r - crit_start_row
                    if span_len > 1:
                        self.ind_table.setSpan(crit_start_row, 1, span_len, 1)
                
                last_crit = crit_txt
                crit_start_row = r
                crit_item = QTableWidgetItem(crit_txt)
                crit_item.setFlags(crit_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.ind_table.setItem(r, 1, crit_item)
            else:
                crit_item = QTableWidgetItem(crit_txt)
                crit_item.setFlags(crit_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.ind_table.setItem(r, 1, crit_item)
            
            # Column 2: Indicator (read-only)
            id_name = item.text(0)
            it = QTableWidgetItem(id_name)
            it.setFlags(it.flags() ^ Qt.ItemFlag.ItemIsEditable)
            it.setData(Qt.ItemDataRole.UserRole, item)
            self.ind_table.setItem(r, 2, it)
        
        # Apply final spans
        if len(indicators) > 0:
            # Requirement span
            req_span = len(indicators) - req_start_row
            if req_span > 1:
                self.ind_table.setSpan(req_start_row, 0, req_span, 1)
            
            # Criterion span
            crit_span = len(indicators) - crit_start_row
            if crit_span > 1:
                self.ind_table.setSpan(crit_start_row, 1, crit_span, 1)

    def on_table_click(self, item):
        """Load indicator parameters when clicked"""
        row = item.row()
        ind_item = self.ind_table.item(row, 2)
        tree_item = ind_item.data(Qt.ItemDataRole.UserRole)
        self.load_indicator_params(tree_item)
    
    def load_indicator_params(self, item):
        """Load parameters from tree item"""
        self.current_indicator_item = item
        d = item.data(1, Qt.ItemDataRole.UserRole) or {}
        
        self.spin_x0.setValue(d.get('xmin', 0))
        self.spin_x1.setValue(d.get('xmax', 100))
        self.input_units.setText(d.get('units', ''))
        self.spin_p.setValue(d.get('p', 1.0))
        self.spin_k.setValue(d.get('k', 0.1))
        self.spin_c.setValue(d.get('c', 50))
        
        self.combo_preset.setCurrentIndex(0)
        self.update_preview()
    
    def save_and_preview(self):
        """Save parameters to tree and update preview"""
        if not self.current_indicator_item:
            return
        
        d = self.current_indicator_item.data(1, Qt.ItemDataRole.UserRole) or {}
        d.update({
            'xmin': self.spin_x0.value(),
            'xmax': self.spin_x1.value(),
            'units': self.input_units.text(),
            'p': self.spin_p.value(),
            'k': self.spin_k.value(),
            'c': self.spin_c.value()
        })
        self.current_indicator_item.setData(1, Qt.ItemDataRole.UserRole, d)
        self.update_preview()
    
    def update_preview(self):
        """Generate and display curve preview with enhanced styling"""
        if not self.current_indicator_item:
            return
        
        d = self.current_indicator_item.data(1, Qt.ItemDataRole.UserRole) or {}
        name = d.get('custom_name', 'Indicator')
        
        fig = self.mives_engine.generate_single_curve(
            name=name,
            x_sat_0=self.spin_x0.value(),
            x_sat_1=self.spin_x1.value(),
            units=self.input_units.text(),
            C=self.spin_c.value(),
            K=self.spin_k.value(),
            P=self.spin_p.value(),
            style_opts=self.func_chart_style
        )
        self.preview_web.setHtml(fig.to_html(include_plotlyjs='cdn'))
        
        # Update export size label after render
        QTimer.singleShot(100, self.update_dimensions_label)

    
    def apply_preset(self, index):
        """Apply preset P/K/C values"""
        presets = {
            1: {'p': 1.0, 'k': 0.0, 'c': 50},
            2: {'p': 2.0, 'k': 0.5, 'c': 50},
            3: {'p': 0.5, 'k': 0.5, 'c': 50},
            4: {'p': 3.0, 'k': 1.0, 'c': 50}
        }
        
        if index in presets:
            preset = presets[index]
            self.spin_p.setValue(preset['p'])
            self.spin_k.setValue(preset['k'])
            self.spin_c.setValue(preset['c'])
            self.update_preview()
    
    def toggle_style_sidebar(self, checked):
        """Show/hide style settings"""
        self.style_sidebar.setVisible(checked)
    
    def pick_curve_color(self):
        """Pick curve color"""
        c = QColorDialog.getColor(QColor(self.func_chart_style['color']))
        if c.isValid():
            self.func_chart_style['color'] = c.name()
            self.update_preview()
    
    def pick_axis_color(self):
        """Pick axis line color"""
        c = QColorDialog.getColor(QColor(self.func_chart_style['axis_line_color']))
        if c.isValid():
            self.func_chart_style['axis_line_color'] = c.name()
            self.update_preview()
    
    def pick_grid_color(self):
        """Pick grid line color"""
        c = QColorDialog.getColor(QColor(self.func_chart_style['grid_line_color']))
        if c.isValid():
            self.func_chart_style['grid_line_color'] = c.name()
            self.update_preview()
    
    def pick_background_color(self):
        """Pick chart background color"""
        c = QColorDialog.getColor(QColor(self.func_chart_style['background_color']))
        if c.isValid():
            self.func_chart_style['background_color'] = c.name()
            self.update_preview()
    
    def update_func_style(self, key, val):
        """Update style parameter"""
        self.func_chart_style[key] = val
        self.update_preview()
    
    def export_preview_image(self):
        """Export current preview as image with scale multiplier"""
        path, _ = QFileDialog.getSaveFileName(self, "Save", "curve.png", "PNG (*.png)")
        if not path:
            return
        
        # Get scale from control
        scale = self.export_scale
        
        # Get current display size
        current_w = self.preview_web.width()
        current_h = self.preview_web.height()
        
        # Calculate scaled dimensions
        export_w = int(current_w * scale)
        export_h = int(current_h * scale)
        
        # Capture and scale the image
        pixmap = self.preview_web.grab()
        
        if scale != 1.0:
            scaled_pixmap = pixmap.scaled(
                export_w, 
                export_h,
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            scaled_pixmap.save(path)
        else:
            pixmap.save(path)

    
    def convert_to_camel_case(self, text):
        """Convert indicator name to camelCase filename"""
        # Remove special characters and split into words
        clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        # Split into words
        words = clean_text.split()
        if not words:
            return "indicator"
        # First word lowercase, rest capitalized
        camel = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
        return camel if camel else "indicator"
    
    def batch_export_charts(self):
        """Export all indicator charts at once.
        Optimized to use efficient tree collection."""
        # Get folder selection
        folder = QFileDialog.getExistingDirectory(self, "Select Export Folder")
        if not folder:
            return
        
        # Collect all indicators using optimized function
        indicators = collect_indicators(self.tree_widget)
        
        if not indicators:
            QMessageBox.warning(self, "No Indicators", "No indicators found to export.")
            return
        
        # Export each indicator
        exported_count = 0
        errors = []
        
        for item in indicators:
            try:
                d = item.data(1, Qt.ItemDataRole.UserRole) or {}
                name = d.get('custom_name', 'Indicator')
                
                # Generate chart
                fig = self.mives_engine.generate_single_curve(
                    name=name,
                    x_sat_0=d.get('xmin', 0),
                    x_sat_1=d.get('xmax', 100),
                    units=d.get('units', ''),
                    C=d.get('c', 50),
                    K=d.get('k', 0.1),
                    P=d.get('p', 1.0),
                    style_opts=self.func_chart_style
                )
                
                # Convert name to camelCase
                camel_name = self.convert_to_camel_case(name)
                filename = f"{camel_name}.png"
                filepath = f"{folder}/{filename}"
                
                # Save as PNG
                fig.write_image(filepath, width=1200, height=800, scale=2)
                exported_count += 1
                
            except Exception as e:
                errors.append(f"{name}: {str(e)}")
        
        # Show results
        if errors:
            error_msg = "\n".join(errors[:5])  # Show first 5 errors
            if len(errors) > 5:
                error_msg += f"\n... and {len(errors)-5} more errors"
            QMessageBox.warning(
                self, 
                "Partial Export", 
                f"Exported {exported_count}/{len(indicators)} charts.\n\nErrors:\n{error_msg}"
            )
        else:
            QMessageBox.information(
                self, 
                "Success", 
                f"✅ Exported {exported_count} charts to:\n{folder}"
            )
    
    def export_functions(self):
        """Export all functions to CSV"""
        path, _ = QFileDialog.getSaveFileName(self, "Save Functions", "", "CSV (*.csv)")
        if not path:
            return
        try:
            self.data_manager.export_functions_csv(self.tree_widget, path)
            QMessageBox.information(self, "Success", "Functions exported.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def import_functions(self):
        """Import functions from CSV"""
        path, _ = QFileDialog.getOpenFileName(self, "Open Functions", "", "CSV (*.csv)")
        if not path:
            return
        try:
            self.data_manager.import_functions_csv(self.tree_widget, path)
            self.refresh_ind_list()
            QMessageBox.information(self, "Success", "Functions applied.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            
    def on_export_scale_changed(self, scale):
        """Handle scale multiplier change (only affects export)"""
        self.export_scale = scale
        self.update_dimensions_label()

    def update_dimensions_label(self):
        """Update the export dimensions label based on current widget size × scale"""
        if not hasattr(self, 'sb_export_scale'):
            return
            
        scale = self.sb_export_scale.value()
        
        # Get current widget display size
        current_w = self.preview_web.width()
        current_h = self.preview_web.height()
        
        # Calculate export size
        export_w = int(current_w * scale)
        export_h = int(current_h * scale)
        
        self.lbl_dimensions.setText(
            f"Export size: {export_w} × {export_h} px (Scale: {scale:.2f}×)"
        )

    def resizeEvent(self, event):
        """Update export size label when window is resized"""
        super().resizeEvent(event)
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, self.update_dimensions_label)
