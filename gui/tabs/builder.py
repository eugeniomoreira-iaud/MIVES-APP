"""
Tab 1: MIVES Tree Structure Builder
Requirement → Criterion → Indicator hierarchy
"""
import uuid
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                             QTreeWidgetItem, QLabel, QLineEdit, QPushButton, 
                             QFrame, QSplitter, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from logic.data_manager import DataManager


class BuilderTab(QWidget):
    """Tree structure builder tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_manager = DataManager()
        self.setup_ui()
        self.create_default_tree()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Tree Widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["ID : Name", "Weight (%)", "Type"])
        self.tree_widget.itemClicked.connect(self.on_node_select)
        splitter.addWidget(self.tree_widget)
        
        # Controls Panel
        controls = QFrame()
        c_lay = QVBoxLayout(controls)
        
        c_lay.addWidget(QLabel("<b>Properties</b>"))
        self.input_name = QLineEdit()
        c_lay.addWidget(QLabel("Name:"))
        c_lay.addWidget(self.input_name)
        
        self.input_weight = QLineEdit()
        c_lay.addWidget(QLabel("Weight:"))
        c_lay.addWidget(self.input_weight)
        
        btn_upd = QPushButton("Update")
        btn_upd.clicked.connect(self.update_node)
        c_lay.addWidget(btn_upd)
        
        c_lay.addSpacing(10)
        c_lay.addWidget(QLabel("<b>Actions</b>"))
        
        # Move buttons
        h_move = QHBoxLayout()
        btn_up = QPushButton("⬆️")
        btn_up.clicked.connect(self.move_up)
        btn_down = QPushButton("⬇️")
        btn_down.clicked.connect(self.move_down)
        h_move.addWidget(btn_up)
        h_move.addWidget(btn_down)
        c_lay.addLayout(h_move)
        
        btn_add = QPushButton("➕ Add Child")
        btn_add.clicked.connect(self.add_node)
        c_lay.addWidget(btn_add)
        
        btn_del = QPushButton("🗑️ Delete")
        btn_del.clicked.connect(self.delete_node)
        c_lay.addWidget(btn_del)
        
        btn_chk = QPushButton("⚠️ Check Weights")
        btn_chk.clicked.connect(self.check_weights)
        c_lay.addWidget(btn_chk)
        
        c_lay.addSpacing(20)
        c_lay.addWidget(QLabel("<b>Structure I/O</b>"))
        
        btn_exp = QPushButton("💾 Export Structure")
        btn_exp.clicked.connect(self.export_structure)
        c_lay.addWidget(btn_exp)
        
        btn_imp = QPushButton("📂 Import Structure")
        btn_imp.clicked.connect(self.import_structure)
        c_lay.addWidget(btn_imp)
        
        c_lay.addStretch()
        
        splitter.addWidget(controls)
        splitter.setSizes([700, 300])
        layout.addWidget(splitter)
    
    def create_default_tree(self):
        """Create initial demo tree"""
        self.tree_widget.clear()
        
        def mk(n, w, t):
            i = QTreeWidgetItem(["", w, t])
            i.setData(0, Qt.ItemDataRole.UserRole, str(uuid.uuid4()))
            i.setData(1, Qt.ItemDataRole.UserRole, {'custom_name': n})
            return i
        
        r = mk("Index", "100", "Root")
        self.tree_widget.addTopLevelItem(r)
        
        req = mk("Req 1", "50", "Requirement")
        r.addChild(req)
        
        crit = mk("Crit 1", "100", "Criterion")
        req.addChild(crit)
        
        ind = mk("Ind 1", "100", "Indicator")
        crit.addChild(ind)
        
        self.renumber_nodes()
        self.tree_widget.expandAll()
    
    def add_node(self):
        """Add child node to selected item"""
        p = self.tree_widget.currentItem()
        if not p:
            return
        
        pt = p.text(2)
        if pt == "Root":
            nt = "Requirement"
        elif pt == "Requirement":
            nt = "Criterion"
        elif pt == "Criterion":
            nt = "Indicator"
        else:
            return
        
        c = QTreeWidgetItem(["", "0", nt])
        c.setData(0, Qt.ItemDataRole.UserRole, str(uuid.uuid4()))
        c.setData(1, Qt.ItemDataRole.UserRole, {'custom_name': "New"})
        p.addChild(c)
        p.setExpanded(True)
        self.renumber_nodes()
    
    def delete_node(self):
        """Delete selected node"""
        i = self.tree_widget.currentItem()
        if i and i.parent():
            i.parent().removeChild(i)
            self.renumber_nodes()
    
    def move_up(self):
        """Move selected node up"""
        item = self.tree_widget.currentItem()
        if not item:
            return
        parent = item.parent() or self.tree_widget.invisibleRootItem()
        idx = parent.indexOfChild(item)
        if idx > 0:
            parent.takeChild(idx)
            parent.insertChild(idx-1, item)
            self.tree_widget.setCurrentItem(item)
            self.renumber_nodes()
    
    def move_down(self):
        """Move selected node down"""
        item = self.tree_widget.currentItem()
        if not item:
            return
        parent = item.parent() or self.tree_widget.invisibleRootItem()
        idx = parent.indexOfChild(item)
        if idx < parent.childCount() - 1:
            parent.takeChild(idx)
            parent.insertChild(idx+1, item)
            self.tree_widget.setCurrentItem(item)
            self.renumber_nodes()
    
    def on_node_select(self, item, col):
        """Load node properties when selected"""
        d = item.data(1, Qt.ItemDataRole.UserRole) or {}
        self.input_name.setText(d.get('custom_name', ''))
        self.input_weight.setText(item.text(1))
    
    def update_node(self):
        """Update selected node properties"""
        i = self.tree_widget.currentItem()
        if i:
            d = i.data(1, Qt.ItemDataRole.UserRole) or {}
            d['custom_name'] = self.input_name.text()
            i.setData(1, Qt.ItemDataRole.UserRole, d)
            i.setText(1, self.input_weight.text())
            self.renumber_nodes()
    
    def renumber_nodes(self):
        """Renumber all nodes with proper IDs"""
        r = self.tree_widget.topLevelItem(0)
        if not r:
            return
        
        counts = {"Requirement": 1, "Criterion": 1, "Indicator": 1}
        
        def trav(item):
            t = item.text(2)
            d = item.data(1, Qt.ItemDataRole.UserRole) or {}
            nm = d.get('custom_name', 'Elem')
            
            if t == "Root":
                txt = "MIVES Index"
            elif t in counts:
                p = "C" if t == "Criterion" else t[0].upper()
                txt = f"{p}{counts[t]:02d}: {nm}"
                counts[t] += 1
            else:
                txt = nm
            
            item.setText(0, txt)
            
            # Color coding
            if t == "Root":
                col = QColor(220, 220, 220)
            elif t == "Requirement":
                col = QColor(235, 235, 235)
            elif t == "Criterion":
                col = QColor(245, 245, 245)
            else:
                col = QColor(255, 255, 255)
            
            for c in range(3):
                item.setBackground(c, QBrush(col))
            
            for k in range(item.childCount()):
                trav(item.child(k))
        
        trav(r)
    
    def check_weights(self):
        """Validate AHP weights"""
        errors = self.data_manager.validate_weights(self.tree_widget)
        if errors:
            QMessageBox.warning(self, "Weight Warning", "\n".join(errors))
        else:
            QMessageBox.information(self, "OK", "All weights sum to 100%.")
    
    def export_structure(self):
        """Export tree to CSV"""
        path, _ = QFileDialog.getSaveFileName(self, "Save Structure", "", "CSV (*.csv)")
        if not path:
            return
        try:
            self.data_manager.export_structure_csv(self.tree_widget, path)
            QMessageBox.information(self, "Success", "Structure exported.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def import_structure(self):
        """Import tree from CSV"""
        path, _ = QFileDialog.getOpenFileName(self, "Open Structure", "", "CSV (*.csv)")
        if not path:
            return
        try:
            self.data_manager.import_structure_csv(self.tree_widget, path)
            self.renumber_nodes()
            QMessageBox.information(self, "Success", "Structure imported.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
