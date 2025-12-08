"""
Scenario Evaluation Tab (Dynamic)
"""
import csv
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame,
                             QSplitter, QTableWidget, QTableWidgetItem, QHeaderView,
                             QFileDialog, QMessageBox)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from logic.math_engine import MivesLogic
from gui.widgets.native_sankey import NativeSankeyWidget



class ScenarioTab(QWidget):
    """Scenario evaluation tab with input table and live results"""
    
    def __init__(self, tree_widget, style_manager, parent=None):
        super().__init__(parent)
        self.tree_widget = tree_widget
        self.style_manager = style_manager
        self.mives_engine = MivesLogic()
        self.inputs = {}
        self.rows_map = {}
        
        # Connect to style change signals
        self.style_manager.style_changed.connect(self.on_style_changed)
        self.style_manager.matrix_style_changed.connect(self.on_matrix_style_changed)
        
        self.setup_ui()
        self.load_indicators()

    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        # expose main splitter so container can synchronize sizes across tabs
        self.main_splitter = splitter
        
        # Left Panel: Input Table
        left_frame = QFrame()
        l_lay = QVBoxLayout(left_frame)
        
        io_box = QHBoxLayout()
        btn_imp = QPushButton("📂 Import Values")
        btn_imp.clicked.connect(self.import_values)
        btn_exp = QPushButton("💾 Export Values")
        btn_exp.clicked.connect(self.export_values)
        io_box.addWidget(btn_imp)
        io_box.addWidget(btn_exp)
        l_lay.addLayout(io_box)
        
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Root\n(MIVES Index)", "Requirement", "Criterion", "Indicator", 
            "Units", "Range", "Actual", "Satisfaction", "Index"
        ])
        
        # Configure intelligent column resizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Root column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Requirement
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Criterion
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)       # Indicator
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Units
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Range
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Interactive)       # Actual
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Satisfaction
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.ResizeToContents)  # Index
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.cellChanged.connect(self.on_cell_change)
        l_lay.addWidget(self.table)
        
        splitter.addWidget(left_frame)
        
        # Right Panel: Charts Only (no style controls)
        chart_splitter = QSplitter(Qt.Orientation.Vertical)
        # expose chart splitter for synchronization (Sankey / Matrix vertical split)
        self.chart_splitter = chart_splitter
        
        # Sankey
        s_frame = QFrame()
        s_lay = QVBoxLayout(s_frame)
        btn_s_img = QPushButton("📷 Export Sankey")
        btn_s_img.clicked.connect(lambda: self.export_sankey_image())
        s_lay.addWidget(btn_s_img)
        self.sankey_view = NativeSankeyWidget()
        s_lay.addWidget(self.sankey_view)
        chart_splitter.addWidget(s_frame)
        
        # Matrix
        m_frame = QFrame()
        m_lay = QVBoxLayout(m_frame)
        btn_m_img = QPushButton("📷 Export Matrix")
        btn_m_img.clicked.connect(lambda: self.export_chart_image(self.web_matrix, "scenario_matrix.png"))
        m_lay.addWidget(btn_m_img)
        self.web_matrix = QWebEngineView()
        m_lay.addWidget(self.web_matrix)
        chart_splitter.addWidget(m_frame)
        
        splitter.addWidget(chart_splitter)
        splitter.setSizes([400, 800])
        layout.addWidget(splitter)

    def on_style_changed(self):
        """Called when shared styles change - refresh this tab's Sankey"""
        self.refresh_sankey()
    
    def refresh_sankey(self):
        """Refresh only the Sankey diagram"""
        root = self.tree_widget.topLevelItem(0)
        if not root:
            return
        
        scores = self.mives_engine.calculate_tree_scores_from_tree_item(root, self.inputs)
        
        # Use native dual-layer rendering for scenarios
        shadow_data, filled_data = self.mives_engine.generate_scenario_sankey_data(
            root, 
            scores,
            self.style_manager.style_opts
        )
        self.sankey_view.render_sankey_dual(shadow_data, filled_data, self.style_manager.style_opts)

    def find_requirement(self, item):
        """Traverse up the tree to find the parent Requirement"""
        current = item
        while current:
            if current.text(2) == "Requirement":
                return current.text(0)
            current = current.parent()
        return "Unknown"
    
    def load_indicators(self):
        """Load all indicators from tree into table with Root as first column (merged vertically)"""
        self.table.blockSignals(True)
        self.table.setRowCount(0)
        self.rows_map = {}
        
        root = self.tree_widget.topLevelItem(0)
        if not root:
            self.table.blockSignals(False)
            return
        
        root_uid = root.data(0, Qt.ItemDataRole.UserRole)
        root_name = root.text(0)
        
        indicators = []
        
        def find_ind(item):
            if item.text(2) == "Indicator":
                parent_txt = item.parent().text(0) if item.parent() else "Unknown"
                req_txt = self.find_requirement(item)
                # Store parent items for satisfaction lookup
                parent_item = item.parent()
                parent_uid = parent_item.data(0, Qt.ItemDataRole.UserRole) if parent_item else None
                req_item = item
                while req_item and req_item.text(2) != "Requirement":
                    req_item = req_item.parent()
                req_uid = req_item.data(0, Qt.ItemDataRole.UserRole) if req_item else None
                
                indicators.append((req_txt, parent_txt, item, req_uid, parent_uid))
            
            for i in range(item.childCount()):
                find_ind(item.child(i))
        
        find_ind(root)
        
        self.table.setRowCount(len(indicators))
        
        # Track spans for merged cells
        last_req = None
        last_crit = None
        req_start_row = 0
        crit_start_row = 0
        req_uid_map = {}
        crit_uid_map = {}
        
        for row, (req_txt, crit_txt, item, req_uid, parent_uid) in enumerate(indicators):
            uid = item.data(0, Qt.ItemDataRole.UserRole)
            data = item.data(1, Qt.ItemDataRole.UserRole) or {}
            
            # Column 0: ROOT (will be merged across all rows later)
            root_cell = QTableWidgetItem(f"🏆 {root_name}")
            root_cell.setFlags(root_cell.flags() ^ Qt.ItemFlag.ItemIsEditable)
            font = root_cell.font()
            font.setBold(True)
            font.setPointSize(font.pointSize() + 3)
            root_cell.setFont(font)
            root_cell.setBackground(QBrush(QColor(255, 215, 0)))  # Gold
            self.table.setItem(row, 0, root_cell)
            
            # Column 1: Requirement (read-only, with spanning)
            if req_txt != last_req:
                if row > 0 and last_req is not None:
                    span_len = row - req_start_row
                    if span_len > 1:  # Only span if more than 1 cell
                        self.table.setSpan(req_start_row, 1, span_len, 1)
                    if last_req in req_uid_map:
                        req_uid_map[last_req]['span'] = (req_start_row, span_len)
                
                last_req = req_txt
                req_start_row = row
                req_item = QTableWidgetItem(req_txt)
                req_item.setFlags(req_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 1, req_item)
                
                if req_uid and req_txt not in req_uid_map:
                    req_uid_map[req_txt] = {'uid': req_uid, 'row': row}
            else:
                req_item = QTableWidgetItem(req_txt)
                req_item.setFlags(req_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 1, req_item)
            
            # Column 2: Criterion (read-only, with spanning)
            if crit_txt != last_crit:
                if row > 0 and last_crit is not None and crit_start_row < row:
                    span_len = row - crit_start_row
                    if span_len > 1:  # Only span if more than 1 cell
                        self.table.setSpan(crit_start_row, 2, span_len, 1)
                    if last_crit in crit_uid_map:
                        crit_uid_map[last_crit]['span'] = (crit_start_row, span_len)
                
                last_crit = crit_txt
                crit_start_row = row
                crit_item = QTableWidgetItem(crit_txt)
                crit_item.setFlags(crit_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 2, crit_item)
                
                if parent_uid and crit_txt not in crit_uid_map:
                    crit_uid_map[crit_txt] = {'uid': parent_uid, 'row': row}
            else:
                crit_item = QTableWidgetItem(crit_txt)
                crit_item.setFlags(crit_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 2, crit_item)
            
            # Column 3: Indicator (read-only)
            id_name = item.text(0)
            it = QTableWidgetItem(id_name)
            it.setFlags(it.flags() ^ Qt.ItemFlag.ItemIsEditable)
            it.setData(Qt.ItemDataRole.UserRole, item)
            self.table.setItem(row, 3, it)
            
            # Column 4: Units (read-only)
            units_item = QTableWidgetItem(data.get('units', ''))
            units_item.setFlags(units_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 4, units_item)
            
            # Column 5: Range (read-only)
            x_min = data.get('xmin', 0)
            x_max = data.get('xmax', 100)
            range_item = QTableWidgetItem(f"{x_min}/{x_max}")
            range_item.setFlags(range_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 5, range_item)
            
            # Column 6: Actual (EDITABLE, highlighted)
            actual_val = self.inputs.get(uid, x_min)
            val_item = QTableWidgetItem(str(actual_val))
            val_item.setBackground(QBrush(QColor(255, 255, 200)))
            self.table.setItem(row, 6, val_item)
            
            # Column 7: Satisfaction (read-only)
            sat_item = QTableWidgetItem("0.000")
            sat_item.setFlags(sat_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 7, sat_item)
            
            # Column 8: Index (read-only)
            idx_item = QTableWidgetItem("0.000")
            idx_item.setFlags(idx_item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 8, idx_item)
            
            self.rows_map[row] = uid
        
        # Apply final spans (only if span > 1)
        if len(indicators) > 0:
            # Merge ROOT column across ALL rows (always > 1 if there are indicators)
            if len(indicators) > 1:
                self.table.setSpan(0, 0, len(indicators), 1)
            
            # Merge requirements
            req_span = len(indicators) - req_start_row
            if req_span > 1:  # Only span if more than 1 cell
                self.table.setSpan(req_start_row, 1, req_span, 1)
            if last_req in req_uid_map:
                req_uid_map[last_req]['span'] = (req_start_row, req_span)
            
            # Merge criteria
            crit_span = len(indicators) - crit_start_row
            if crit_span > 1:  # Only span if more than 1 cell
                self.table.setSpan(crit_start_row, 2, crit_span, 1)
            if last_crit in crit_uid_map:
                crit_uid_map[last_crit]['span'] = (crit_start_row, crit_span)
        
        # Store root UID and mappings
        self.root_uid = root_uid
        self.req_uid_map = req_uid_map
        self.crit_uid_map = crit_uid_map
        
        self.table.blockSignals(False)
        self.recalculate()
        self.enable_manual_resize()

    def on_cell_change(self, row, col):
        """Handle value changes in Actual column"""
        if col == 6:
            try:
                val = float(self.table.item(row, 6).text())
                self.inputs[self.rows_map[row]] = val
                self.recalculate()
            except (ValueError, AttributeError):
                pass
    
    def recalculate(self):
        """Recalculate all scores and update visualizations"""
        root = self.tree_widget.topLevelItem(0)
        if not root:
            return
        
        scores = self.mives_engine.calculate_tree_scores_from_tree_item(root, self.inputs)
        
        self.table.blockSignals(True)
        
        # Update ROOT cell (column 0, merged across all rows)
        if self.table.rowCount() > 0:
            root_satisfaction = scores.get(self.root_uid, 0.0)
            root_cell = self.table.item(0, 0)
            if root_cell:
                root_name = root.text(0)
                root_cell.setText(f"{root_name}\n({root_satisfaction:.3f})")
        
        # Update INDICATORS
        for row, uid in self.rows_map.items():
            item = self.table.item(row, 3).data(Qt.ItemDataRole.UserRole)
            
            absolute_weight = self.mives_engine.calculate_absolute_weight_from_item(item)
            satisfaction = scores.get(uid, 0.0)
            index_contribution = absolute_weight * satisfaction
            
            self.table.item(row, 7).setText(f"{satisfaction:.3f}")
            self.table.item(row, 8).setText(f"{index_contribution:.3f}")
        
        # Update REQUIREMENT merged cells with satisfaction
        for req_name, info in self.req_uid_map.items():
            req_uid = info['uid']
            req_row = info['row']
            req_satisfaction = scores.get(req_uid, 0.0)
            
            req_cell = self.table.item(req_row, 1)
            if req_cell:
                req_cell.setText(f"{req_name}\n({req_satisfaction:.2f})")
        
        # Update CRITERION merged cells with satisfaction
        for crit_name, info in self.crit_uid_map.items():
            crit_uid = info['uid']
            crit_row = info['row']
            crit_satisfaction = scores.get(crit_uid, 0.0)
            
            crit_cell = self.table.item(crit_row, 2)
            if crit_cell:
                crit_cell.setText(f"{crit_name}\n({crit_satisfaction:.2f})")
        
        self.table.blockSignals(False)
        
        # Update Sankey
        shadow_data, filled_data = self.mives_engine.generate_scenario_sankey_data(
            root,
            scores,
            self.style_manager.style_opts
        )
        self.sankey_view.render_sankey_dual(shadow_data, filled_data, self.style_manager.style_opts)
        
        # Update Matrix
        ind_data_list = []
        for row, uid in self.rows_map.items():
            item = self.table.item(row, 3).data(Qt.ItemDataRole.UserRole)
            d = item.data(1, Qt.ItemDataRole.UserRole) or {}
            d['actual'] = self.inputs.get(uid, d.get('xmin', 0))
            d['name'] = d.get('custom_name', '')
            d.setdefault('xmin', 0)
            d.setdefault('xmax', 100)
            d.setdefault('c', 50)
            d.setdefault('k', 0.1)
            d.setdefault('p', 1.0)
            ind_data_list.append(d)
        
        m_fig = self.mives_engine.generate_matrix_chart(
            ind_data_list,
            style_opts=self.style_manager.matrix_style_opts
        )
        self.web_matrix.setHtml(m_fig.to_html(include_plotlyjs='cdn'))

    def export_values(self):
        """Export scenario values to CSV"""
        path, _ = QFileDialog.getSaveFileName(self, "Save Scenario", "", "CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(["SimplifiedID", "Value"])
                for row in range(self.table.rowCount()):
                    item = self.table.item(row, 3)
                    sid = item.text().split(':')[0].strip()
                    val = self.table.item(row, 6).text()
                    w.writerow([sid, val])
            QMessageBox.information(self, "Success", "Scenario exported.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def import_values(self):
        """Import scenario values from CSV"""
        path, _ = QFileDialog.getOpenFileName(self, "Open Scenario", "", "CSV (*.csv)")
        if not path:
            return
        try:
            id_map = {}
            for row in range(self.table.rowCount()):
                item = self.table.item(row, 3)
                sid = item.text().split(':')[0].strip()
                uid = self.rows_map[row]
                id_map[sid] = uid
            
            with open(path, 'r') as f:
                r = csv.DictReader(f)
                for row in r:
                    sid = row["SimplifiedID"]
                    if sid in id_map:
                        self.inputs[id_map[sid]] = float(row["Value"])
            
            self.load_indicators()
            QMessageBox.information(self, "Success", "Scenario imported.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def export_chart_image(self, web_view, filename):
        """Export chart as PNG with scale multiplier"""
        path, _ = QFileDialog.getSaveFileName(self, "Save", filename, "PNG (*.png)")
        if not path:
            return
        
        # Get scale from style manager
        scale = self.style_manager.export_scale
        
        # Get current display size
        current_w = web_view.width()
        current_h = web_view.height()
        
        # Calculate scaled dimensions
        export_w = int(current_w * scale)
        export_h = int(current_h * scale)
        
        # Capture and scale the image
        from PyQt6.QtCore import Qt
        pixmap = web_view.grab()
        
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
    
    def export_sankey_image(self):
        """Export Sankey chart as PNG with scale multiplier"""
        path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Sankey", 
            "scenario_sankey.png", 
            "PNG (*.png)"
        )
        if not path:
            return
        
        # Get scale from style manager
        scale = self.style_manager.export_scale
        self.sankey_view.export_image(path, scale)
    
    def on_matrix_style_changed(self):
        """Called when matrix styles change - refresh this tab's Matrix"""
        self.refresh_matrix()

    def refresh_matrix(self):
        """Refresh only the Matrix diagram"""
        root = self.tree_widget.topLevelItem(0)
        if not root:
            return
        
        ind_data_list = []
        for row, uid in self.rows_map.items():
            item = self.table.item(row, 3).data(Qt.ItemDataRole.UserRole)
            d = item.data(1, Qt.ItemDataRole.UserRole) or {}
            d['actual'] = self.inputs.get(uid, d.get('xmin', 0))
            d['name'] = d.get('custom_name', '')
            d.setdefault('xmin', 0)
            d.setdefault('xmax', 100)
            d.setdefault('c', 50)
            d.setdefault('k', 0.1)
            d.setdefault('p', 1.0)
            ind_data_list.append(d)
        
        m_fig = self.mives_engine.generate_matrix_chart(
            ind_data_list,
            style_opts=self.style_manager.matrix_style_opts
        )
        self.web_matrix.setHtml(m_fig.to_html(include_plotlyjs='cdn'))
        
    def enable_manual_resize(self):
        """Switch all columns to manual resize mode after initial auto-sizing"""
        header = self.table.horizontalHeader()
        for col in range(self.table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Interactive)
