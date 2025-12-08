"""
Application-wide style definitions
"""

APP_STYLES = """
QMainWindow {
    background-color: #f5f5f5;
}

QPushButton {
    padding: 6px 12px;
    border-radius: 4px;
    background-color: #3498db;
    color: white;
    border: none;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #1f6391;
}

QTreeWidget {
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
}

QTableWidget {
    border: 1px solid #ddd;
    border-radius: 4px;
    gridline-color: #e0e0e0;
    background-color: white;
}

QTabWidget::pane {
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
}

QTabBar::tab {
    background-color: #ecf0f1;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}

QTabBar::tab:selected {
    background-color: white;
    font-weight: bold;
}

QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox {
    padding: 4px 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
}
"""

# Default style options for charts
DEFAULT_FUNC_STYLE = {
    'color': '#2980b9',
    'width': 3,
    'grid': True,
    'dash': 'solid',
    'fill': False,
    'markers': False,
    'threshold': None,
    # Extended styling options
    'font_family': 'Arial',
    'font_size_title': 16,
    'font_size_axes': 12,
    'axis_line_width': 2,
    'axis_line_color': '#333333',
    # Individual axis line visibility
    'show_axis_top': True,
    'show_axis_bottom': True,
    'show_axis_left': True,
    'show_axis_right': True,
    # Grid styling
    'grid_line_width': 1,
    'grid_line_color': '#e0e0e0',
    'grid_line_dash': 'solid',
    'background_color': '#ffffff'
}

DEFAULT_SANKEY_STYLE = {
    # Nodes
    'node_color': "#27ae60",
    'thickness': 20,
    'pad': 15,
    'node_line_width': 0.5,
    'node_line_color': '#000000',
    
    # Links
    'link_color': "rgba(180, 180, 180, 0.4)",
    'link_opacity': 0.4,
    'link_color_mode': 'Solid',
    'link_line_width': 0,
    'link_line_color': '#000000',
    
    # Node Labels
    'label_font_size': 12,
    'label_font_family': 'Arial',
    'label_font_color': '#000000',
    'show_node_weight': True,       # NEW: Show weight percentage
    
    # Font (general)
    'font_size': 12,
    'font_family': 'Arial',
    'font_weight': 'Normal',
    'font_color': '#000000',
    
    # Chart Title
    'show_title': True,
    'title_text': 'MIVES Assessment',
    'title_font_size': 20,
    'title_font_family': 'Arial',
    'title_color': '#000000',
    
    # Level Labels
    'show_level_labels': True,
    'level_label_font_size': 14,
    'level_label_font_family': 'Arial',
    'level_label_color': '#333333',
    'show_index_label': True,
    'show_requirement_label': True,
    'show_criterion_label': True,
    'show_indicator_label': True,
    
    # Layout / Dimensions
    'vertical_fill': 0.95,
    'chart_width': 1200,
    'chart_height_ratio': 0.6,
    
    'label_position': 'Auto',
    'orientation': 'Horizontal',
    'margin_top': 80,
    'margin_bottom': 10,
    'margin_left': 10,
    'margin_right': 10,
    
    # Background
    'background_color': '#ffffff',
    'transparent_bg': False
}

DEFAULT_SANKEY_STYLE = {
    'show_title': False,
    'title_text': 'MIVES Assessment',
    'title_font_size': 20,
    'title_font_family': 'Arial',
    'title_color': '#000000',
    'vertical_fill': 0.95,
    'thickness': 20,
    'pad': 15,
    'node_color': '#27ae60',
    'node_line_color': 'black',
    'node_line_width': 0.5,
    'link_color': 'rgba(39, 174, 96, 0.6)',
    'link_opacity': 0.6,
    'label_font_family': 'Arial',
    'label_font_size': 12,
    'label_font_color': '#000000',
    'show_node_weight': True,
    'background_color': '#ffffff',
    'transparent_bg': False,
    
    # Shadow layer colors (for scenario dual-layer Sankey)
    'shadow_node_color': 'rgba(200, 200, 200, 0.3)',
    'shadow_link_color': 'rgba(200, 200, 200, 0.3)',
    'node_line_width': 0,
}





