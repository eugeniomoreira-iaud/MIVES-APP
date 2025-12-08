"""
Tab 3: Sankey Visualization (Enhanced)
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QSplitter, QSpinBox, QColorDialog, QFileDialog,
                             QScrollArea, QGroupBox, QComboBox, QCheckBox, QDoubleSpinBox,
                             QLineEdit, QSizePolicy)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from logic.math_engine import MivesLogic
from gui.styles import DEFAULT_SANKEY_STYLE


class VizTab(QWidget):
    """Sankey diagram visualization tab with enhanced styling"""
    
    def __init__(self, tree_widget, parent=None):
        super().__init__(parent)
        self.tree_widget = tree_widget
        self.mives_engine = MivesLogic()
        self.style_opts = DEFAULT_SANKEY_STYLE.copy()
        self.setup_ui()
    
    def setup_ui(self):
        # Clear existing layout if any
        if self.layout():
            QWidget().setLayout(self.layout())
            
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Style Controls (Scrollable)
        style_scroll = QScrollArea()
        style_scroll.setWidgetResizable(True)
        style_scroll.setFrameShape(QFrame.Shape.StyledPanel)
        style_scroll.setFixedWidth(340)
        
        style_content = QWidget()
        sl = QVBoxLayout(style_content)
        sl.setContentsMargins(10, 10, 10, 10)
        sl.setSpacing(15)
        
        sl.addWidget(QLabel("<b>Sankey Styling</b>"))
        
        # === TITLE ===
        title_group = QGroupBox("Chart Title")
        title_lay = QVBoxLayout(title_group)
        
        c_show_title = QCheckBox("Show Title")
        c_show_title.setChecked(self.style_opts['show_title'])
        c_show_title.toggled.connect(lambda v: self.update_style('show_title', v))
        title_lay.addWidget(c_show_title)
        
        title_lay.addWidget(QLabel("Title Text:"))
        le_title = QLineEdit()
        le_title.setText(self.style_opts['title_text'])
        le_title.textChanged.connect(lambda v: self.update_style('title_text', v))
        title_lay.addWidget(le_title)
        
        sl.addWidget(title_group)
        
        # === DIMENSIONS & LAYOUT ===
        dim_group = QGroupBox("Dimensions & Layout")
        dim_lay = QVBoxLayout(dim_group)
        
        dim_lay.addWidget(QLabel("Vertical Fill % (Canvas Usage):"))
        sb_vfill = QDoubleSpinBox()
        sb_vfill.setRange(0.1, 1.0)
        sb_vfill.setSingleStep(0.05)
        sb_vfill.setValue(self.style_opts['vertical_fill'])
        sb_vfill.valueChanged.connect(lambda v: self.update_style('vertical_fill', v))
        dim_lay.addWidget(sb_vfill)
        
        dim_lay.addWidget(QLabel("Image Width (px):"))
        self.sb_width = QSpinBox()
        self.sb_width.setRange(400, 5000)
        self.sb_width.setValue(self.style_opts['chart_width'])
        self.sb_width.valueChanged.connect(self.on_width_changed)
        dim_lay.addWidget(self.sb_width)
        
        self.lbl_height = QLabel("")
        self.lbl_height.setStyleSheet("color: #555; font-style: italic;")
        dim_lay.addWidget(self.lbl_height)
        self.update_height_label()
        
        sl.addWidget(dim_group)
        
        # === LEVEL LABELS ===
        level_group = QGroupBox("Level Labels")
        level_lay = QVBoxLayout(level_group)
        
        c_show_levels = QCheckBox("Show Level Labels")
        c_show_levels.setChecked(self.style_opts['show_level_labels'])
        c_show_levels.toggled.connect(lambda v: self.update_style('show_level_labels', v))
        level_lay.addWidget(c_show_levels)
        
        level_grid = QHBoxLayout()
        c_idx = QCheckBox("Idx"); c_idx.setChecked(self.style_opts['show_index_label'])
        c_idx.toggled.connect(lambda v: self.update_style('show_index_label', v))
        c_req = QCheckBox("Req"); c_req.setChecked(self.style_opts['show_requirement_label'])
        c_req.toggled.connect(lambda v: self.update_style('show_requirement_label', v))
        c_cri = QCheckBox("Cri"); c_cri.setChecked(self.style_opts['show_criterion_label'])
        c_cri.toggled.connect(lambda v: self.update_style('show_criterion_label', v))
        c_ind = QCheckBox("Ind"); c_ind.setChecked(self.style_opts['show_indicator_label'])
        c_ind.toggled.connect(lambda v: self.update_style('show_indicator_label', v))
        level_grid.addWidget(c_idx); level_grid.addWidget(c_req); level_grid.addWidget(c_cri); level_grid.addWidget(c_ind)
        level_lay.addLayout(level_grid)
        
        sl.addWidget(level_group)
        
        # === NODE STYLE ===
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
        
        node_lay.addWidget(QLabel("Thickness (0 to hide):"))
        sb_thick = QSpinBox()
        sb_thick.setValue(self.style_opts['thickness'])
        sb_thick.setRange(0, 200)
        sb_thick.valueChanged.connect(lambda v: self.update_style('thickness', v))
        node_lay.addWidget(sb_thick)
        
        node_lay.addWidget(QLabel("Border Width:"))
        sb_bw = QDoubleSpinBox()
        sb_bw.setValue(self.style_opts['node_line_width'])
        sb_bw.setRange(0, 10)
        sb_bw.setSingleStep(0.5)
        sb_bw.valueChanged.connect(lambda v: self.update_style('node_line_width', v))
        node_lay.addWidget(sb_bw)
        
        node_lay.addWidget(QLabel("Vertical Spacing:"))
        sb_pad = QSpinBox()
        sb_pad.setValue(self.style_opts['pad'])
        sb_pad.setRange(0, 100)
        sb_pad.valueChanged.connect(lambda v: self.update_style('pad', v))
        node_lay.addWidget(sb_pad)
        
        sl.addWidget(node_group)
        
        # === LINK STYLE ===
        link_group = QGroupBox("Links")
        link_lay = QVBoxLayout(link_group)
        
        btn_link_c = QPushButton("Link Color")
        btn_link_c.clicked.connect(lambda: self.pick_link_color())
        link_lay.addWidget(btn_link_c)
        
        link_lay.addWidget(QLabel("Opacity (1.0 = Solid):"))
        sb_op = QDoubleSpinBox()
        sb_op.setRange(0.0, 1.0)
        sb_op.setSingleStep(0.1)
        sb_op.setValue(self.style_opts['link_opacity'])
        sb_op.valueChanged.connect(lambda v: self.update_link_opacity(v))
        link_lay.addWidget(sb_op)
        
        sl.addWidget(link_group)
        
        # === ACTIONS ===
        sl.addSpacing(20)
        btn_save = QPushButton("📷 Save Image")
        btn_save.clicked.connect(self.export_image)
        sl.addWidget(btn_save)
        
        sl.addStretch()
        
        style_content.setLayout(sl)
        style_scroll.setWidget(style_content)
        splitter.addWidget(style_scroll)
        
        # Chart View
        self.web_view = QWebEngineView()
        self.web_view.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # ADD: Horizontal expand
            QSizePolicy.Policy.Expanding   # ADD: Vertical expand
        )
        splitter.addWidget(self.web_view)
        splitter.setSizes([340, 860])  # Adjust ratio as needed
        
        layout.addWidget(splitter)
        
        # Render initial
        self.refresh_chart()
    
    def on_width_changed(self, val):
        """Handle image width change and update feedback label"""
        self.style_opts['chart_width'] = val
        self.update_height_label()
        self.refresh_chart()
        
    def update_height_label(self):
        """Calculate and display the resulting height based on aspect ratio"""
        w = self.style_opts['chart_width']
        ratio = self.style_opts['chart_height_ratio']
        h = int(w * ratio)
        self.lbl_height.setText(f"Resulting Image Size: {w} x {h} px")

    def update_style(self, key, value):
        self.style_opts[key] = value
        self.refresh_chart()
        
    def update_link_opacity(self, value):
        """Update link opacity and force refresh"""
        self.style_opts['link_opacity'] = value
        self.refresh_chart()

    def pick_color(self, key):
        current = self.style_opts.get(key, '#000000')
        c = QColorDialog.getColor(QColor(current))
        if c.isValid():
            self.style_opts[key] = c.name()
            self.refresh_chart()
            
    def pick_link_color(self):
        """Pick base link color"""
        current = self.style_opts.get('link_color', "rgba(180, 180, 180, 0.4)")
        c = QColorDialog.getColor()
        if c.isValid():
            opacity = self.style_opts.get('link_opacity', 0.4)
            self.style_opts['link_color'] = f"rgba({c.red()},{c.green()},{c.blue()},{opacity})"
            self.refresh_chart()
    
    def refresh_chart(self):
        """Generate and display the Sankey diagram"""
        root = self.tree_widget.topLevelItem(0)
        if not root:
            return
             
        fig = self.mives_engine.generate_sankey_from_tree_item(root, self.style_opts)
        html = fig.to_html(include_plotlyjs='cdn')
        self.web_view.setHtml(html)
    
    def refresh_viz(self):
        """Alias for refresh_chart() - called from main_window"""
        self.refresh_chart()
        
    def export_image(self):
        """Export the current view to PNG"""
        path, _ = QFileDialog.getSaveFileName(self, "Save Chart", "mives_sankey.png", "PNG Files (*.png)")
        if path:
            self.web_view.grab().save(path)
