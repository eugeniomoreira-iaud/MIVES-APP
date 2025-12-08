"""
Optimized utility functions for tree traversal and data access.
This module provides cached versions of common tree operations to improve performance.
"""
from typing import Any, Dict
from functools import lru_cache


class TreeItemCache:
    """Cache for tree item properties to avoid repeated Qt object access."""
    
    def __init__(self):
        self._weight_cache: Dict[Any, float] = {}
        self._text_cache: Dict[tuple, str] = {}
        self._data_cache: Dict[tuple, Any] = {}
    
    def get_weight(self, item: Any) -> float:
        """Get local weight of an item with caching."""
        uid = None
        try:
            # Get UID for cache key
            from PyQt6.QtCore import Qt
            uid = item.data(0, Qt.ItemDataRole.UserRole)
            
            # Check cache
            if uid in self._weight_cache:
                return self._weight_cache[uid]
            
            # Parse and cache weight
            weight_text = item.text(1)
            # Optimize: check if '%' exists before replacing (faster than unconditional replace)
            if '%' in weight_text:
                weight = float(weight_text.replace("%", "")) / 100.0
            else:
                weight = float(weight_text) / 100.0
            
            self._weight_cache[uid] = weight
            return weight
        except Exception:
            # Cache error case too
            if uid is not None:
                self._weight_cache[uid] = 0.0
            return 0.0
    
    def get_text(self, item: Any, column: int) -> str:
        """Get text from item column with caching."""
        uid = None
        try:
            from PyQt6.QtCore import Qt
            uid = item.data(0, Qt.ItemDataRole.UserRole)
            cache_key = (uid, column)
            
            if cache_key in self._text_cache:
                return self._text_cache[cache_key]
            
            text = item.text(column)
            self._text_cache[cache_key] = text
            return text
        except Exception:
            return ""
    
    def get_data(self, item: Any, column: int, role: int) -> Any:
        """Get data from item with caching."""
        try:
            from PyQt6.QtCore import Qt
            uid = item.data(0, Qt.ItemDataRole.UserRole)
            cache_key = (uid, column, role)
            
            if cache_key in self._data_cache:
                return self._data_cache[cache_key]
            
            data = item.data(column, role)
            self._data_cache[cache_key] = data
            return data
        except Exception:
            return None
    
    def clear(self):
        """Clear all caches."""
        self._weight_cache.clear()
        self._text_cache.clear()
        self._data_cache.clear()


def get_local_weight_fast(item: Any) -> float:
    """
    Fast version of get_local_weight without caching overhead.
    Use this for one-time traversals where caching overhead isn't worthwhile.
    
    Note: This maintains the original behavior where weights are always divided by 100.
    Examples: "50%" -> 0.5, "25%" -> 0.25
    If the value doesn't contain '%', it's still divided by 100 for consistency.
    """
    try:
        weight_text = item.text(1)
        # Optimize: check if '%' exists before replacing (faster than unconditional replace)
        if '%' in weight_text:
            return float(weight_text.replace("%", "")) / 100.0
        else:
            # Still divide by 100 to maintain original behavior
            return float(weight_text) / 100.0
    except Exception:
        return 0.0


def collect_indicators(tree_widget, cache: TreeItemCache = None) -> list:
    """
    Efficiently collect all indicator items from tree.
    Uses single traversal with optional caching.
    
    Args:
        tree_widget: QTreeWidget to traverse
        cache: Optional TreeItemCache for property access
        
    Returns:
        List of indicator items
    """
    indicators = []
    
    def traverse(item):
        if not item:
            return
        
        # Check if this is an indicator
        if cache:
            item_type = cache.get_text(item, 2)
        else:
            item_type = item.text(2)
        
        if item_type == "Indicator":
            indicators.append(item)
        
        # Traverse children
        child_count = item.childCount()
        for i in range(child_count):
            traverse(item.child(i))
    
    root = tree_widget.topLevelItem(0)
    if root:
        traverse(root)
    
    return indicators


def batch_get_item_data(items: list, column: int, role: int) -> Dict[Any, Any]:
    """
    Batch fetch data from multiple items efficiently.
    
    Args:
        items: List of QTreeWidgetItems
        column: Column index
        role: Qt data role
        
    Returns:
        Dictionary mapping item UID to data value
    """
    from PyQt6.QtCore import Qt
    
    result = {}
    for item in items:
        try:
            uid = item.data(0, Qt.ItemDataRole.UserRole)
            if uid:
                result[uid] = item.data(column, role)
        except Exception:
            pass
    
    return result
