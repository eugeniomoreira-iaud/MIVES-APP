"""
MIVES Logic Layer
Pure computation without GUI dependencies
"""
__version__ = "1.0.0"

from logic.math_engine import MivesLogic
from logic.data_manager import DataManager

__all__ = ['MivesLogic', 'DataManager']