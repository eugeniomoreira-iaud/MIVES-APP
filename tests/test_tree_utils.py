"""
Tests for tree_utils optimization module
"""
import pytest
from logic.tree_utils import get_local_weight_fast


class MockTreeItem:
    """Mock QTreeWidgetItem for testing without PyQt6"""
    
    def __init__(self, text_values):
        self._text_values = text_values
    
    def text(self, column):
        return self._text_values.get(column, "")


def test_get_local_weight_fast_with_percent():
    """Test weight parsing with percent sign"""
    item = MockTreeItem({0: "Test", 1: "25%", 2: "Indicator"})
    weight = get_local_weight_fast(item)
    assert weight == 0.25


def test_get_local_weight_fast_without_percent():
    """Test weight parsing without percent sign"""
    item = MockTreeItem({0: "Test", 1: "0.25", 2: "Indicator"})
    weight = get_local_weight_fast(item)
    assert weight == 0.0025  # Divided by 100


def test_get_local_weight_fast_invalid():
    """Test weight parsing with invalid input"""
    item = MockTreeItem({0: "Test", 1: "invalid", 2: "Indicator"})
    weight = get_local_weight_fast(item)
    assert weight == 0.0


def test_get_local_weight_fast_zero():
    """Test weight parsing with zero"""
    item = MockTreeItem({0: "Test", 1: "0%", 2: "Indicator"})
    weight = get_local_weight_fast(item)
    assert weight == 0.0


def test_get_local_weight_fast_hundred():
    """Test weight parsing with 100%"""
    item = MockTreeItem({0: "Test", 1: "100%", 2: "Indicator"})
    weight = get_local_weight_fast(item)
    assert weight == 1.0


def test_get_local_weight_fast_performance():
    """Test that optimized version is efficient"""
    import time
    
    # Create many items
    items = [MockTreeItem({0: f"Item{i}", 1: f"{i}%", 2: "Indicator"}) 
             for i in range(1000)]
    
    # Time repeated parsing
    start = time.time()
    for _ in range(10):
        for item in items:
            get_local_weight_fast(item)
    elapsed = time.time() - start
    
    # Should complete reasonably fast (10,000 operations in well under 1 second)
    print(f"10,000 weight parses in {elapsed:.4f}s")
    assert elapsed < 1.0, "Weight parsing should be fast"


def test_get_local_weight_fast_edge_cases():
    """Test edge cases for weight parsing"""
    # Empty string
    item1 = MockTreeItem({0: "Test", 1: "", 2: "Indicator"})
    assert get_local_weight_fast(item1) == 0.0
    
    # Large value
    item2 = MockTreeItem({0: "Test", 1: "500%", 2: "Indicator"})
    assert get_local_weight_fast(item2) == 5.0
    
    # Decimal with percent
    item3 = MockTreeItem({0: "Test", 1: "33.33%", 2: "Indicator"})
    assert abs(get_local_weight_fast(item3) - 0.3333) < 0.0001
    
    # Negative value
    item4 = MockTreeItem({0: "Test", 1: "-10%", 2: "Indicator"})
    assert get_local_weight_fast(item4) == -0.1
