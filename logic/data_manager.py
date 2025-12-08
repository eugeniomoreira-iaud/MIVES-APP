"""
MIVES Data Import/Export Manager
Handles CSV operations for structure and function parameters
"""
import csv
from logic.tree_utils import get_local_weight_fast


class DataManager:
    """Static methods for CSV import/export"""
    
    @staticmethod
    def export_structure_csv(tree_widget, filepath):
        """Export tree structure to CSV from QTreeWidget"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['SimplifiedID', 'ParentID', 'Weight', 'Type', 'Name'])
            
            def write(item):
                from PyQt6.QtCore import Qt
                sid = item.text(0).split(':')[0].strip()
                pid = item.parent().text(0).split(':')[0].strip() if item.parent() else "None"
                d = item.data(1, Qt.ItemDataRole.UserRole) or {}
                writer.writerow([sid, pid, item.text(1), item.text(2), 
                               d.get('custom_name','Element')])
                for i in range(item.childCount()): 
                    write(item.child(i))
            
            root = tree_widget.topLevelItem(0)
            if root: 
                write(root)
    
    @staticmethod
    def export_functions_csv(tree_widget, filepath):
        """Export indicator value functions to CSV"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['SimplifiedID', 'X_Sat_0', 'X_Sat_1', 'Units', 'P', 'K', 'C'])
            
            def write(item):
                from PyQt6.QtCore import Qt
                if item.text(2) == "Indicator":
                    sid = item.text(0).split(':')[0].strip()
                    d = item.data(1, Qt.ItemDataRole.UserRole) or {}
                    writer.writerow([
                        sid, 
                        d.get('xmin',0), 
                        d.get('xmax',100), 
                        d.get('units',''), 
                        d.get('p',1), 
                        d.get('k',0), 
                        d.get('c',50)
                    ])
                for i in range(item.childCount()): 
                    write(item.child(i))
            
            root = tree_widget.topLevelItem(0)
            if root: 
                write(root)
    
    @staticmethod
    def import_structure_csv(tree_widget, filepath):
        """Import tree structure from CSV"""
        import uuid
        from PyQt6.QtWidgets import QTreeWidgetItem
        from PyQt6.QtCore import Qt
        
        with open(filepath, 'r', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        
        tree_widget.clear()
        item_map = {}
        
        # Create Root
        root_row = next((r for r in rows if r['ParentID'] == 'None'), None)
        if not root_row:
            raise ValueError("No Root found in CSV")
        
        root = QTreeWidgetItem(["", root_row['Weight'], root_row['Type']])
        root.setData(0, Qt.ItemDataRole.UserRole, str(uuid.uuid4()))
        root.setData(1, Qt.ItemDataRole.UserRole, {'custom_name': root_row['Name']})
        tree_widget.addTopLevelItem(root)
        item_map[root_row['SimplifiedID']] = root
        
        # Add children
        for row in rows:
            if row['ParentID'] == 'None': 
                continue
            if row['ParentID'] in item_map:
                parent = item_map[row['ParentID']]
                child = QTreeWidgetItem(["", row['Weight'], row['Type']])
                child.setData(0, Qt.ItemDataRole.UserRole, str(uuid.uuid4()))
                child.setData(1, Qt.ItemDataRole.UserRole, {'custom_name': row['Name']})
                parent.addChild(child)
                item_map[row['SimplifiedID']] = child
        
        tree_widget.expandAll()
    
    @staticmethod
    def import_functions_csv(tree_widget, filepath):
        """Import value functions from CSV"""
        from PyQt6.QtCore import Qt
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            func_data = {row['SimplifiedID']: row for row in reader}
        
        def update(item):
            sid = item.text(0).split(':')[0].strip()
            if sid in func_data:
                row = func_data[sid]
                d = item.data(1, Qt.ItemDataRole.UserRole) or {}
                d.update({
                    'xmin': float(row['X_Sat_0']), 
                    'xmax': float(row['X_Sat_1']), 
                    'units': row['Units'],
                    'p': float(row['P']), 
                    'k': float(row['K']), 
                    'c': float(row['C'])
                })
                item.setData(1, Qt.ItemDataRole.UserRole, d)
            for i in range(item.childCount()): 
                update(item.child(i))
        
        root = tree_widget.topLevelItem(0)
        if root: 
            update(root)
    
    @staticmethod
    def validate_weights(tree_widget):
        """Validate that child weights sum to 100% at each level"""
        errors = []
        
        def check(item):
            total = 0.0
            child_count = item.childCount()
            for i in range(child_count):
                child = item.child(i)
                try:
                    # Use optimized weight extraction
                    total += get_local_weight_fast(child) * 100.0
                except: 
                    pass
                check(child)
            if child_count > 0 and abs(total - 100.0) > 0.1:
                errors.append(f"{item.text(0)}: Children sum to {total}%")
        
        root = tree_widget.topLevelItem(0)
        if root: 
            check(root)
        return errors
