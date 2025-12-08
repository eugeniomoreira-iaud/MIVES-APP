"""
Native Qt Sankey Diagram Widget
Drop-in replacement for QWebEngineView + Plotly
Compatible with existing MIVES style controls
"""

from dataclasses import dataclass
from typing import List, Optional
from PyQt6.QtWidgets import (QGraphicsView, QGraphicsScene, 
                             QGraphicsRectItem, QGraphicsPathItem, 
                             QGraphicsSimpleTextItem)
from PyQt6.QtGui import QPen, QBrush, QColor, QPainter, QPainterPath, QFont
from PyQt6.QtCore import Qt, QRectF


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class NodeData:
    """Represents a single node in the Sankey diagram"""
    id: str
    label: str
    x: float        # Normalized 0.0 - 1.0
    y: float        # Normalized 0.0 - 1.0
    height: float   # Normalized 0.0 - 1.0
    color: str      # Hex color or rgb(a) string


@dataclass
class LinkData:
    """Represents a single flow link between nodes"""
    source_id: str
    target_id: str
    value: float           # Normalized height/thickness
    y_source_offset: float # Vertical offset from source node top
    y_target_offset: float # Vertical offset from target node top
    color: str             # Hex color or rgb(a) string


@dataclass
class SankeyData:
    """Complete Sankey diagram data structure"""
    nodes: List[NodeData]
    links: List[LinkData]


# ============================================================================
# GRAPHICS SCENE (Rendering Engine)
# ============================================================================

class NativeSankeyScene(QGraphicsScene):
    """
    QGraphicsScene that renders Sankey nodes and links.
    Supports dual-layer rendering (shadow + filled).
    """

    def __init__(self, sankey_data: SankeyData, width: int, height: int, 
                 style_opts: dict, shadow_data: Optional[SankeyData] = None):
        super().__init__(0, 0, width, height)

        self.sankey_data = sankey_data
        self.shadow_data = shadow_data  # Optional background layer
        self.canvas_width = width
        self.canvas_height = height
        self.style_opts = style_opts or {}

        # Extract style parameters
        self.node_width_px = self.style_opts.get('thickness', 20)
        self.padding = 50

        # Set background color
        bg_color = self.style_opts.get('background_color', '#ffffff')
        if not self.style_opts.get('transparent_bg', False):
            self.setBackgroundBrush(QBrush(QColor(bg_color)))

        # Draw in correct order
        if self.shadow_data:
            # Dual-layer mode: Draw shadow first, then filled
            self._draw_links(self.shadow_data)
            self._draw_nodes(self.shadow_data)
            self._draw_links(self.sankey_data)
            self._draw_nodes(self.sankey_data)
        else:
            # Single-layer mode
            self._draw_links(self.sankey_data)
            self._draw_nodes(self.sankey_data)
        
        self._draw_title()

    def _to_px(self, x_norm: float, y_norm: float) -> tuple:
        """Convert normalized coordinates (0-1) to pixel coordinates"""
        draw_w = self.canvas_width - 2 * self.padding
        draw_h = self.canvas_height - 2 * self.padding

        px = self.padding + x_norm * draw_w
        py = self.padding + y_norm * draw_h
        return px, py

    def _scale_h(self, h_norm: float) -> float:
        """Convert normalized height to pixels"""
        draw_h = self.canvas_height - 2 * self.padding
        return h_norm * draw_h

    def _parse_color(self, color_str: str) -> QColor:
        """Parse hex or rgba() color string to QColor"""
        import re

        # Try rgba() format
        rgba_match = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)', color_str)
        if rgba_match:
            r, g, b, a = rgba_match.groups()
            color = QColor(int(r), int(g), int(b))
            if a:
                color.setAlpha(int(float(a) * 255))
            return color

        # Try hex format
        return QColor(color_str)

    def _draw_nodes(self, data: SankeyData):
        """Draw all nodes as rectangles with labels"""
        # Style parameters
        node_line_color = self.style_opts.get('node_line_color', '#ffffff')
        node_line_width = self.style_opts.get('node_line_width', 0.5)
        label_font_family = self.style_opts.get('label_font_family', 'Arial')
        label_font_size = self.style_opts.get('label_font_size', 12)
        label_font_color = self.style_opts.get('label_font_color', '#000000')

        for node in data.nodes:
            px, py = self._to_px(node.x, node.y)
            ph = self._scale_h(node.height)

            # Create node rectangle
            rect = QGraphicsRectItem(px, py, self.node_width_px, ph)
            rect.setBrush(QBrush(self._parse_color(node.color)))
            
            # MODIFIED: Shadow nodes (empty label) never have borders
            # Filled nodes (with labels) respect style settings
            if node.label == "":
                # Shadow node - force no border
                rect.setPen(QPen(Qt.PenStyle.NoPen))
            else:
                # Filled node - apply border if width > 0
                if node_line_width > 0:
                    rect.setPen(QPen(self._parse_color(node_line_color), node_line_width))
                else:
                    rect.setPen(QPen(Qt.PenStyle.NoPen))
            
            rect.setToolTip(f"{node.label}\nValue: {node.height:.3f}")

            self.addItem(rect)

            # Create label (only if label is not empty)
            if node.label:
                text = QGraphicsSimpleTextItem(node.label)
                text.setBrush(QBrush(self._parse_color(label_font_color)))

                # Set font
                font = QFont()
                font.setFamily(label_font_family)
                font.setPointSize(label_font_size)
                text.setFont(font)

                # Calculate centered vertical position
                text_rect = text.boundingRect()
                text_width = text_rect.width()
                text_height = text_rect.height()

                # Center text vertically on bar
                text_y = py + (ph / 2.0) - (text_height / 2.0)

                # Position horizontally based on column
                if node.x < 0.1:
                    # First column: label on the right
                    text_x = px + self.node_width_px + 5
                else:
                    # Other columns: label on the left
                    text_x = px - text_width - 5

                text.setPos(text_x, text_y)
                self.addItem(text)

    def _draw_links(self, data: SankeyData):
        """Draw all links as filled Bézier curves"""
        # Create lookup for node data
        node_lookup = {n.id: n for n in data.nodes}

        for link in data.links:
            src = node_lookup.get(link.source_id)
            tgt = node_lookup.get(link.target_id)

            if not src or not tgt:
                continue

            # Source point (right edge of source node)
            sx, sy = self._to_px(src.x, src.y)
            sy += self._scale_h(link.y_source_offset)
            sx += self.node_width_px

            # Target point (left edge of target node)
            tx, ty = self._to_px(tgt.x, tgt.y)
            ty += self._scale_h(link.y_target_offset)

            # Link height
            link_h = self._scale_h(link.value)

            # Calculate Bézier control points (sigmoid curve)
            dist = (tx - sx) * 0.5
            c1x = sx + dist
            c1y = sy
            c2x = tx - dist
            c2y = ty

            # Create filled path (4 Bézier curves forming a closed shape)
            path = QPainterPath()
            path.moveTo(sx, sy)
            path.cubicTo(c1x, c1y, c2x, c2y, tx, ty)
            path.lineTo(tx, ty + link_h)
            path.cubicTo(c2x, c2y + link_h, c1x, c1y + link_h, sx, sy + link_h)
            path.closeSubpath()

            item = QGraphicsPathItem(path)

            # Apply color with transparency
            link_color = self._parse_color(link.color)
            item.setBrush(QBrush(link_color))
            item.setPen(QPen(Qt.PenStyle.NoPen))  # No border

            self.addItem(item)

    def _draw_title(self):
        """Draw title if enabled"""
        if not self.style_opts.get('show_title', False):
            return

        title_text = self.style_opts.get('title_text', '')
        if not title_text:
            return

        title_font_size = self.style_opts.get('title_font_size', 20)
        title_font_family = self.style_opts.get('title_font_family', 'Arial')
        title_color = self.style_opts.get('title_color', '#000000')

        # Create title
        title = QGraphicsSimpleTextItem(title_text)
        title.setBrush(QBrush(self._parse_color(title_color)))

        font = QFont()
        font.setFamily(title_font_family)
        font.setPointSize(title_font_size)
        font.setBold(True)
        title.setFont(font)

        # Center title at top
        title_width = title.boundingRect().width()
        title_x = (self.canvas_width - title_width) / 2.0
        title_y = 10

        title.setPos(title_x, title_y)
        self.addItem(title)



# ============================================================================
# MAIN WIDGET (Drop-in Replacement for QWebEngineView)
# ============================================================================

class NativeSankeyWidget(QGraphicsView):
    """
    Native Qt Sankey renderer with adaptive aspect ratio.
    Supports both single-layer and dual-layer (shadow + filled) rendering.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # Rendering settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Default white background
        self.setBackgroundBrush(QBrush(QColor("#ffffff")))

        # Store current data for re-rendering on resize
        self._current_sankey_data = None
        self._current_shadow_data = None
        self._current_style_opts = None

    def render_sankey(self, sankey_data: SankeyData, style_opts: Optional[dict] = None):
        """
        Render single-layer Sankey diagram (Tab 3 visualization).

        Args:
            sankey_data: SankeyData object with nodes and links
            style_opts: Style dictionary
        """
        style_opts = style_opts or {}

        # Store for re-rendering on resize
        self._current_sankey_data = sankey_data
        self._current_shadow_data = None  # No shadow layer
        self._current_style_opts = style_opts

        # Update background based on style
        bg_color = style_opts.get('background_color', '#ffffff')
        if not style_opts.get('transparent_bg', False):
            self.setBackgroundBrush(QBrush(QColor(bg_color)))
        else:
            self.setBackgroundBrush(QBrush(Qt.GlobalColor.transparent))

        # Render the scene
        self._render_scene()

    def render_sankey_dual(self, shadow_data: SankeyData, filled_data: SankeyData, 
                          style_opts: Optional[dict] = None):
        """
        Render dual-layer Sankey diagram (Scenario tabs).

        Args:
            shadow_data: Background layer (full potential)
            filled_data: Foreground layer (achievement)
            style_opts: Style dictionary
        """
        style_opts = style_opts or {}

        # Store for re-rendering on resize
        self._current_shadow_data = shadow_data
        self._current_sankey_data = filled_data
        self._current_style_opts = style_opts

        # Update background
        bg_color = style_opts.get('background_color', '#ffffff')
        if not style_opts.get('transparent_bg', False):
            self.setBackgroundBrush(QBrush(QColor(bg_color)))
        else:
            self.setBackgroundBrush(QBrush(Qt.GlobalColor.transparent))

        # Render the scene
        self._render_scene()

    def _render_scene(self):
        """Internal method to create and set the scene with current dimensions."""
        if not self._current_sankey_data:
            return

        # Use actual widget dimensions for adaptive aspect ratio
        canvas_width = max(self.width(), 400)
        canvas_height = max(self.height(), 400)

        # Create scene (supports both single and dual layer)
        scene = NativeSankeyScene(
            self._current_sankey_data,
            canvas_width,
            canvas_height,
            self._current_style_opts,
            shadow_data=self._current_shadow_data  # Optional shadow layer
        )
        self.setScene(scene)

        # Fill the entire view (no letterboxing)
        self._fit_to_view()

    def _fit_to_view(self):
        """Scale scene to fill the entire view."""
        if self.scene():
            scene_rect = self.scene().sceneRect()
            self.fitInView(scene_rect, Qt.AspectRatioMode.IgnoreAspectRatio)

    def resizeEvent(self, event):
        """Handle window resize - re-render to adapt to new proportions."""
        super().resizeEvent(event)
        if self._current_sankey_data:
            # Re-render with new window proportions
            self._render_scene()

    def grab_pixmap(self, scale: float = 1.0):
        """
        Export as QPixmap (for saving images).

        Args:
            scale: Scale multiplier (1.0 = current size, 2.0 = 2x size)

        Returns:
            QPixmap
        """
        current_w = self.width()
        current_h = self.height()

        export_w = int(current_w * scale)
        export_h = int(current_h * scale)

        pixmap = self.grab()
        scaled_pixmap = pixmap.scaled(
            export_w, export_h,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        return scaled_pixmap

    def export_image(self, path: str, scale: float = 1.0):
        """
        Export to image file.

        Args:
            path: Output file path (supports .png, .jpg, .bmp, etc.)
            scale: Scale multiplier
        """
        pixmap = self.grab_pixmap(scale)
        pixmap.save(path)
