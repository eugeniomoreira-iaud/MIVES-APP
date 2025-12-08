"""
Custom Sankey Diagram Widget using QPainter
"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QFont


class SankeyWidget(QWidget):
    """Custom widget to draw Sankey diagrams with full control"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sankey_data = None
        self.setMinimumSize(800, 600)
        
    def set_data(self, data):
        """
        Set Sankey data and trigger repaint
        
        Expected data structure:
        {
            'nodes': [
                {
                    'label': str,
                    'x': float (0-1),
                    'y': float (0-1),
                    'height': float (0-1),
                    'color': str (hex or rgb),
                    'value': float
                }
            ],
            'links': [
                {
                    'source': int (node index),
                    'target': int (node index),
                    'value': float,
                    'color': str
                }
            ],
            'style': {
                'node_width': int (pixels),
                'label_size': int,
                'label_font': str,
                'background': str
            }
        }
        """
        self.sankey_data = data
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Draw the Sankey diagram"""
        if not self.sankey_data:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get widget dimensions
        width = self.width()
        height = self.height()
        
        # Apply background
        style = self.sankey_data.get('style', {})
        bg_color = QColor(style.get('background', '#ffffff'))
        painter.fillRect(0, 0, width, height, bg_color)
        
        # Draw links first (so they appear behind nodes)
        self._draw_links(painter, width, height)
        
        # Draw nodes on top
        self._draw_nodes(painter, width, height)
        
        painter.end()
    
    def _draw_links(self, painter, width, height):
        """Draw curved links between nodes"""
        links = self.sankey_data.get('links', [])
        nodes = self.sankey_data.get('nodes', [])
        style = self.sankey_data.get('style', {})
        node_width = style.get('node_width', 20)
        
        for link in links:
            source_node = nodes[link['source']]
            target_node = nodes[link['target']]
            
            # Calculate positions
            x1 = source_node['x'] * width + node_width
            y1 = source_node['y'] * height
            x2 = target_node['x'] * width
            y2 = target_node['y'] * height
            
            # Link height proportional to value
            link_height = link['value'] * height
            
            # Create curved path (Bezier curve)
            path = QPainterPath()
            
            # Start at right edge of source node
            path.moveTo(x1, y1 - link_height / 2)
            
            # Control points for smooth curve
            ctrl_x = (x1 + x2) / 2
            ctrl1 = QPointF(ctrl_x, y1 - link_height / 2)
            ctrl2 = QPointF(ctrl_x, y2 - link_height / 2)
            
            # Top curve to target
            path.cubicTo(ctrl1, ctrl2, QPointF(x2, y2 - link_height / 2))
            
            # Line down right edge
            path.lineTo(x2, y2 + link_height / 2)
            
            # Bottom curve back
            ctrl3 = QPointF(ctrl_x, y2 + link_height / 2)
            ctrl4 = QPointF(ctrl_x, y1 + link_height / 2)
            path.cubicTo(ctrl3, ctrl4, QPointF(x1, y1 + link_height / 2))
            
            # Close path
            path.closeSubpath()
            
            # Draw filled path
            color = QColor(link['color'])
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(path)
    
    def _draw_nodes(self, painter, width, height):
        """Draw node rectangles and labels"""
        nodes = self.sankey_data.get('nodes', [])
        style = self.sankey_data.get('style', {})
        node_width = style.get('node_width', 20)
        label_size = style.get('label_size', 10)
        label_font = style.get('label_font', 'Arial')
        
        font = QFont(label_font, label_size)
        painter.setFont(font)
        
        for node in nodes:
            x = node['x'] * width
            y = node['y'] * height
            node_height = node['height'] * height
            
            # Draw node rectangle
            rect = QRectF(x, y - node_height / 2, node_width, node_height)
            
            color = QColor(node['color'])
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor('#000000'), 0.5))
            painter.drawRect(rect)
            
            # Draw label to the right of node
            label_x = x + node_width + 5
            label_y = y
            
            painter.setPen(QColor('#000000'))
            painter.drawText(
                int(label_x), 
                int(label_y - label_size / 2), 
                200,  # Max label width
                label_size * 2, 
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                node['label']
            )
    
    def export_to_image(self, filepath):
        """Export the diagram to PNG"""
        from PyQt6.QtGui import QPixmap
        pixmap = QPixmap(self.size())
        self.render(pixmap)
        pixmap.save(filepath)
