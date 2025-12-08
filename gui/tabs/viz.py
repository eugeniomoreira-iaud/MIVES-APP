"""
Tab 3: Sankey Visualization (Enhanced)
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QSplitter, QSpinBox, QColorDialog, QFileDialog,
                             QScrollArea, QGroupBox, QComboBox, QCheckBox, QDoubleSpinBox,
                             QLineEdit, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from logic.math_engine import MivesLogic
from gui.styles import DEFAULT_SANKEY_STYLE
import re
from gui.widgets.native_sankey import NativeSankeyWidget


class VizTab(QWidget):
    """Sankey diagram visualization tab with enhanced styling"""
    
    def __init__(self, tree_widget, parent=None):
        super().__init__(parent)
        self.tree_widget = tree_widget
        self.mives_engine = MivesLogic()
        self.style_opts = DEFAULT_SANKEY_STYLE.copy()
        self.setup_ui()
    
    def setup_ui(self):
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
        
        # === EXPORT SCALE ===
        scale_group = QGroupBox("Export Settings")
        scale_lay = QVBoxLayout(scale_group)
        
        scale_lay.addWidget(QLabel("Export Scale Multiplier:"))
        self.sb_scale = QDoubleSpinBox()
        self.sb_scale.setRange(0.25, 5.0)
        self.sb_scale.setSingleStep(0.25)
        self.sb_scale.setValue(1.0)
        self.sb_scale.setDecimals(2)
        self.sb_scale.valueChanged.connect(self.on_scale_changed)
        scale_lay.addWidget(self.sb_scale)
        
        self.lbl_dimensions = QLabel("Export size: calculating...")
        self.lbl_dimensions.setStyleSheet("color: #555; font-style: italic;")
        scale_lay.addWidget(self.lbl_dimensions)
        
        sl.addWidget(scale_group)
        
        # === LAYOUT ===
        layout_group = QGroupBox("Layout")
        layout_lay = QVBoxLayout(layout_group)
        
        layout_lay.addWidget(QLabel("Vertical Fill % (Canvas Usage):"))
        sb_vfill = QDoubleSpinBox()
        sb_vfill.setRange(0.1, 1.0)
        sb_vfill.setSingleStep(0.05)
        sb_vfill.setValue(self.style_opts['vertical_fill'])
        sb_vfill.valueChanged.connect(lambda v: self.update_style('vertical_fill', v))
        layout_lay.addWidget(sb_vfill)
        
        sl.addWidget(layout_group)
        
        
        # === NODE LABELS ===
        label_group = QGroupBox("Node Labels")
        label_lay = QVBoxLayout(label_group)
        
        # Font family
        label_lay.addWidget(QLabel("Font Family:"))
        cb_font = QComboBox()
        cb_font.addItems(['Arial', 'Helvetica', 'Times New Roman', 'Courier New', 'Verdana', 'Georgia'])
        cb_font.setCurrentText(self.style_opts.get('label_font_family', 'Arial'))
        cb_font.currentTextChanged.connect(lambda v: self.update_style('label_font_family', v))
        label_lay.addWidget(cb_font)
        
        # Font size
        label_lay.addWidget(QLabel("Font Size:"))
        sb_label_size = QSpinBox()
        sb_label_size.setRange(6, 24)
        sb_label_size.setValue(self.style_opts.get('label_font_size', 12))
        sb_label_size.valueChanged.connect(lambda v: self.update_style('label_font_size', v))
        label_lay.addWidget(sb_label_size)
        
        # Font color
        btn_label_color = QPushButton("Font Color")
        btn_label_color.clicked.connect(lambda: self.pick_color('label_font_color'))
        label_lay.addWidget(btn_label_color)
        
        # Show weight toggle only
        c_show_weight = QCheckBox("Show Weights (%)")
        c_show_weight.setChecked(self.style_opts.get('show_node_weight', True))
        c_show_weight.toggled.connect(lambda v: self.update_style('show_node_weight', v))
        label_lay.addWidget(c_show_weight)
        
        sl.addWidget(label_group)

        
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
        
        btn_reset = QPushButton("🔄 Reset Layout")
        btn_reset.clicked.connect(self.reset_layout)
        sl.addWidget(btn_reset)
        
        btn_save = QPushButton("📷 Save Image")
        btn_save.clicked.connect(self.export_image)
        sl.addWidget(btn_save)
        
        sl.addStretch()
        
        style_content.setLayout(sl)
        style_scroll.setWidget(style_content)
        splitter.addWidget(style_scroll)
        
        # Chart View
        self.sankey_view = NativeSankeyWidget()
        self.sankey_view.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        splitter.addWidget(self.sankey_view)
        splitter.setSizes([340, 860])
        
        layout.addWidget(splitter)
                
        self.refresh_chart()
    
    def on_scale_changed(self, scale):
        """Handle scale multiplier change (only affects export)"""
        self.update_dimensions_label()
        
    def update_dimensions_label(self):
        """Update the export dimensions label based on current widget size × scale"""
        if not hasattr(self, 'sb_scale'):
            return
            
        scale = self.sb_scale.value()
        
        # Get current widget display size
        current_w = self.sankey_view.width()
        current_h = self.sankey_view.height()
        
        # Calculate export size
        export_w = int(current_w * scale)
        export_h = int(current_h * scale)
        
        self.lbl_dimensions.setText(
            f"Export size: {export_w} × {export_h} px (Scale: {scale:.2f}×)"
        )

    def resizeEvent(self, event):
        """Update export size label when window is resized"""
        super().resizeEvent(event)
        QTimer.singleShot(50, self.update_dimensions_label)
    
    def update_style(self, key, value):
        self.style_opts[key] = value
        self.refresh_chart()
        
    def update_link_opacity(self, value):
        """Update link opacity by modifying the rgba string"""
        self.style_opts['link_opacity'] = value
        
        # Parse current link_color and rebuild with new opacity
        current_color = self.style_opts.get('link_color', 'rgba(180, 180, 180, 0.4)')
        
        # Try to extract RGB values from rgba string
        rgba_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', current_color)
        if rgba_match:
            r, g, b = rgba_match.groups()
            self.style_opts['link_color'] = f"rgba({r},{g},{b},{value})"
        else:
            # Fallback to default gray with new opacity
            self.style_opts['link_color'] = f"rgba(180,180,180,{value})"
        
        self.refresh_chart()
    
    def pick_color(self, key):
        current = self.style_opts.get(key, '#000000')
        c = QColorDialog.getColor(QColor(current))
        if c.isValid():
            self.style_opts[key] = c.name()
            self.refresh_chart()
            
    def pick_link_color(self):
        """Pick base link color and apply current opacity"""
        c = QColorDialog.getColor()
        if c.isValid():
            opacity = self.style_opts.get('link_opacity', 0.4)
            self.style_opts['link_color'] = f"rgba({c.red()},{c.green()},{c.blue()},{opacity})"
            self.refresh_chart()
    
    def refresh_chart(self):
        """Generate and display the Sankey diagram (responsive size)"""
        root = self.tree_widget.topLevelItem(0)
        if not root:
            return
             
        sankey_data = self.mives_engine.generate_sankey_data(root, self.style_opts)
        self.sankey_view.render_sankey(sankey_data, self.style_opts)
        
        # Update export size label after render
        QTimer.singleShot(100, self.update_dimensions_label)

    
    def refresh_viz(self):
        """Alias for refresh_chart() - called from main_window"""
        self.refresh_chart()
        
    def export_image(self):
        """Export the current view scaled by the multiplier"""
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Chart", 
            "mives_sankey.png", 
            "PNG Files (*.png)"
        )
        
        if not path:
            return
        
        # Export with scale multiplier
        scale = self.sb_scale.value()
        self.sankey_view.export_image(path, scale)

    def reset_layout(self):
        """Reset all styling parameters to defaults"""
        self.style_opts = DEFAULT_SANKEY_STYLE.copy()
        self.sb_scale.setValue(1.0)
        self.setup_ui()
        

