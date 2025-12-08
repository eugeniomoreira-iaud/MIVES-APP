"""
MIVES Mathematical Engine
Implements exponential value functions per Boix-Cots et al. (2022)
"""
import logging
import math
from typing import Any, Dict, List, Optional, Tuple
from functools import lru_cache

import numpy as np


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1024)
def _calculate_mives_value_cached(
    x: float,
    x_sat_0: float,
    x_sat_1: float,
    C: float,
    K: float,
    P: float,
) -> float:
    """
    Cached version of MIVES exponential satisfaction calculation.
    This is a pure function suitable for memoization.
    
    Note: Only hashable (immutable) arguments can be cached, so this works
    with float parameters but caller must ensure proper types.
    """
    try:
        dist_x = abs(float(x) - float(x_sat_0))
        dist_max = abs(float(x_sat_1) - float(x_sat_0))

        # Direction Logic: short-circuit values outside saturation
        is_increasing = x_sat_1 > x_sat_0
        if is_increasing:
            if x <= x_sat_0:
                return 0.0
            if x >= x_sat_1:
                return 1.0
        else:
            if x >= x_sat_0:
                return 0.0
            if x <= x_sat_1:
                return 1.0

        # Prevent division by zero / extremely small denominators
        C = max(float(C), 1e-4)

        # Compute normalization factor B robustly
        try:
            phi_max = math.exp(-float(K) * math.pow(dist_max / C, float(P)))
            B = 1.0 if abs(1.0 - phi_max) < 1e-12 else 1.0 / (1.0 - phi_max)
        except (ValueError, OverflowError) as exc:
            logger.debug("phi_max computation failed: %s", exc)
            B = 1.0

        try:
            phi_x = math.exp(-float(K) * math.pow(dist_x / C, float(P)))
            value = B * (1.0 - phi_x)
        except (ValueError, OverflowError) as exc:
            logger.debug("phi_x computation failed: %s", exc)
            value = 0.0

        return float(max(0.0, min(1.0, value)))
    except Exception as exc:
        logger.exception("Unexpected error calculating mives value: %s", exc)
        return 0.0


class MivesLogic:
    """Pure MIVES computation - No GUI dependencies"""
    def calculate_mives_value(
        self,
        x: float,
        x_sat_0: float,
        x_sat_1: float,
        C: float,
        K: float,
        P: float,
    ) -> float:
        """
        Calculate the MIVES exponential satisfaction value for a single measurement.

        The implementation follows the exponential formulation used in Boix-Cots et al. (2022).
        This method now uses an LRU cache for improved performance with repeated calculations.

        Args:
            x: Observed value.
            x_sat_0: Saturation lower bound.
            x_sat_1: Saturation upper bound.
            C: Shape constant (scale).
            K: Shape constant (rate).
            P: Shape constant (power).

        Returns:
            Normalized satisfaction value between 0.0 and 1.0.
        """
        # Convert to float to ensure hashability for cache
        # The try-except is for backwards compatibility with any non-numeric inputs
        try:
            return _calculate_mives_value_cached(
                float(x), float(x_sat_0), float(x_sat_1),
                float(C), float(K), float(P)
            )
        except (TypeError, ValueError) as e:
            # Log unexpected type issues for debugging
            logger.warning("Unexpected type in calculate_mives_value: %s. Using uncached calculation.", e)
            return self._calculate_mives_value_uncached(x, x_sat_0, x_sat_1, C, K, P)
    
    def _calculate_mives_value_uncached(
        self,
        x: float,
        x_sat_0: float,
        x_sat_1: float,
        C: float,
        K: float,
        P: float,
    ) -> float:
        """Uncached fallback version of calculate_mives_value."""
        try:
            dist_x = abs(float(x) - float(x_sat_0))
            dist_max = abs(float(x_sat_1) - float(x_sat_0))

            # Direction Logic: short-circuit values outside saturation
            is_increasing = x_sat_1 > x_sat_0
            if is_increasing:
                if x <= x_sat_0:
                    return 0.0
                if x >= x_sat_1:
                    return 1.0
            else:
                if x >= x_sat_0:
                    return 0.0
                if x <= x_sat_1:
                    return 1.0

            # Prevent division by zero / extremely small denominators
            C = max(float(C), 1e-4)

            # Compute normalization factor B robustly
            try:
                phi_max = math.exp(-float(K) * math.pow(dist_max / C, float(P)))
                B = 1.0 if abs(1.0 - phi_max) < 1e-12 else 1.0 / (1.0 - phi_max)
            except (ValueError, OverflowError) as exc:
                logger.debug("phi_max computation failed: %s", exc)
                B = 1.0

            try:
                phi_x = math.exp(-float(K) * math.pow(dist_x / C, float(P)))
                value = B * (1.0 - phi_x)
            except (ValueError, OverflowError) as exc:
                logger.debug("phi_x computation failed: %s", exc)
                value = 0.0

            return float(max(0.0, min(1.0, value)))
        except Exception as exc:  # defensive: unexpected types
            logger.exception("Unexpected error calculating mives value: %s", exc)
            return 0.0

    def generate_single_curve(
        self,
        name: str,
        x_sat_0: float,
        x_sat_1: float,
        units: str,
        C: float,
        K: float,
        P: float,
        style_opts: Optional[Dict[str, Any]] = None,
        actual_val: Optional[float] = None,
    ) -> Any:
        """
        Generate a Plotly figure showing a single MIVES value function curve.

        The function performs a lazy import of Plotly to avoid requiring the
        heavy dependency unless the plotting function is used.

        Returns:
            Plotly `Figure` object (typed as Any to avoid hard dependency in signatures).
        """
        # Delegate plotting to logic.plotting to avoid heavy top-level deps
        from logic.plotting import generate_single_curve as _plot

        return _plot(self, name, x_sat_0, x_sat_1, units, C, K, P, style_opts, actual_val)

    def generate_matrix_chart(self, indicators_data: List[Dict[str, Any]], style_opts: Optional[Dict[str, Any]] = None) -> Any:
        """
        Generate a matrix (grid) of indicator curves using Plotly.

        Lazy-imports Plotly so this module can be used for pure computation without
        requiring Plotly to be installed.
        """
        # Delegate plotting to logic.plotting
        from logic.plotting import generate_matrix_chart as _plot

        return _plot(self, indicators_data, style_opts)

#############################

    def generate_sankey_from_tree_item(self, root_item: Any, style_opts: Optional[Dict[str, Any]] = None) -> Any:
        """Delegate to logic.tree_sankey.generate_sankey_from_tree_item to keep GUI coupling outside math_engine."""
        from logic.tree_sankey import generate_sankey_from_tree_item as _gen

        return _gen(root_item, style_opts)

#############################

    def generate_sankey_data(self, root_item: Any, style_opts: Optional[Dict[str, Any]] = None) -> Any:
        """Delegate to logic.tree_sankey.generate_sankey_data to decouple GUI details."""
        from logic.tree_sankey import generate_sankey_data as _gen

        return _gen(root_item, style_opts)

    def generate_scenario_sankey_data(self, root_item, scenario_scores, style_opts=None):
        """
        Generate dual-layer native Sankey data for scenario evaluation.
        
        Returns:
            tuple: (shadow_data, filled_data) - Two SankeyData objects
            - shadow_data: Full potential (100% capacity) in muted colors
            - filled_data: Achievement scaled by satisfaction scores
        """
        from PyQt6.QtCore import Qt
        from gui.widgets.native_sankey import NodeData, LinkData, SankeyData

        s = style_opts or {}
        scores = scenario_scores or {}

        # Extract style options - MODIFIED: unified shadow color
        shadow_color = s.get('shadow_node_color', 'rgba(200, 200, 200, 0.3)')  # Same for nodes and links
        shadow_node_color = shadow_color
        shadow_link_color = shadow_color
        filled_node_color = s.get('node_color', '#27ae60')
        filled_link_color = s.get('link_color', 'rgba(39, 174, 96, 0.6)')
        show_node_weight = s.get('show_node_weight', True)  # In scenarios, this shows SATISFACTION
        vertical_fill = s.get('vertical_fill', 0.95)
        gap_normalized = s.get('pad', 15) / 1000.0

        # Data structures
        shadow_nodes = []
        filled_nodes = []
        shadow_links = []
        filled_links = []
        nodes_by_depth = {}
        uid_to_idx = {}
        node_satisfaction = {}

        # Helpers
        def get_local_weight(item):
            try:
                return float(item.text(1).replace('%', '')) / 100.0
            except:
                return 0.0

        # Build label with SATISFACTION as decimal (0.0-1.0)
        def build_label(name, satisfaction_score):
            if show_node_weight and satisfaction_score is not None:
                # Show satisfaction as decimal value (e.g., 0.75 instead of 75%)
                return f"{name} ({satisfaction_score:.2f})"
            return name

        # Traverse tree and build structure
        max_depth = [0]

        def traverse(item, parent_idx=None, parent_weight=1.0, depth=0):
            if not item:
                return

            uid = item.data(0, Qt.ItemDataRole.UserRole)
            if not uid:
                return

            name = item.text(0)
            local_weight = get_local_weight(item)
            absolute_weight = parent_weight * local_weight

            if absolute_weight < 0.001:
                absolute_weight = 0.001

            if depth > max_depth[0]:
                max_depth[0] = depth

            # Get satisfaction score for this node
            satisfaction = scores.get(uid, 0.0)
            
            # Build label with satisfaction
            label = build_label(name, satisfaction)

            # Create nodes for BOTH layers
            if label not in uid_to_idx:
                idx = len(shadow_nodes)
                uid_to_idx[label] = idx
                node_satisfaction[idx] = satisfaction

                # Shadow node (full potential)
                shadow_node = NodeData(
                    id=uid,
                    label="",  # Empty label for shadow
                    x=0.0,
                    y=0.0,
                    height=absolute_weight,
                    color=shadow_node_color
                )
                shadow_nodes.append(shadow_node)

                # Filled node (achievement)
                filled_height = absolute_weight * satisfaction
                filled_node = NodeData(
                    id=uid,
                    label=label,  # Visible label with satisfaction
                    x=0.0,
                    y=0.0,
                    height=filled_height,
                    color=filled_node_color
                )
                filled_nodes.append(filled_node)

                if depth not in nodes_by_depth:
                    nodes_by_depth[depth] = []
                nodes_by_depth[depth].append(idx)

            current_idx = uid_to_idx[label]

            # Create links for BOTH layers
            if parent_idx is not None:
                # Shadow link (full potential)
                shadow_link = LinkData(
                    source_id=shadow_nodes[parent_idx].id,
                    target_id=uid,
                    value=absolute_weight,
                    y_source_offset=0.0,
                    y_target_offset=0.0,
                    color=shadow_link_color
                )
                shadow_links.append(shadow_link)

                # Filled link (achievement)
                child_satisfaction = node_satisfaction.get(current_idx, 0.0)
                filled_value = absolute_weight * child_satisfaction
                filled_link = LinkData(
                    source_id=filled_nodes[parent_idx].id,
                    target_id=uid,
                    value=filled_value,
                    y_source_offset=0.0,
                    y_target_offset=0.0,
                    color=filled_link_color
                )
                filled_links.append(filled_link)

            for i in range(item.childCount()):
                traverse(item.child(i), current_idx, absolute_weight, depth + 1)

        # Build root node
        if root_item:
            uid = root_item.data(0, Qt.ItemDataRole.UserRole)
            name = root_item.text(0)

            if uid and name:
                satisfaction = scores.get(uid, 0.0)
                # MODIFIED: Show root satisfaction prominently in label
                label = build_label(name, satisfaction)  # Changed from None
                
                idx = len(shadow_nodes)
                uid_to_idx[label] = idx
                node_satisfaction[idx] = satisfaction

                # Shadow root
                shadow_node = NodeData(
                    id=uid, label="", x=0.0, y=0.0, height=1.0,
                    color=shadow_node_color
                )
                shadow_nodes.append(shadow_node)

                # Filled root - HIGHLIGHT COLOR
                filled_node = NodeData(
                    id=uid, 
                    label=label, 
                    x=0.0, 
                    y=0.0, 
                    height=satisfaction,
                    color=s.get('root_highlight_color', filled_node_color)  # Special color for root
                )
                filled_nodes.append(filled_node)

                nodes_by_depth[0] = [idx]

                for i in range(root_item.childCount()):
                    traverse(root_item.child(i), idx, 1.0, depth=1)

        # Delegate to the refactored module (keeps compatibility)
        from logic.tree_sankey import generate_scenario_sankey_data as _gen

        return _gen(root_item, scenario_scores, style_opts)

    
    def generate_scenario_sankey(self, root_item, scenario_scores, style_opts=None):
        """
        Generate dual-layer Sankey: Shadow (potential) + Filled (achievement).
        
        Shadow layer: Full structure in muted colors (background)
        Filled layer: Satisfaction-proportional bars centered within shadow (foreground)
        
        Used exclusively by Scenario tabs.
        """
        from PyQt6.QtCore import Qt
        import plotly.graph_objects as go
        
        from logic.tree_sankey import generate_scenario_sankey as _gen

        return _gen(root_item, scenario_scores, style_opts)


    def calculate_tree_scores_from_tree_item(self, root_item: Any, input_values: Dict[Any, float]) -> Dict[Any, float]:
        """Delegate tree scoring to `logic.tree_sankey.calculate_tree_scores_from_tree_item`."""
        from logic.tree_sankey import calculate_tree_scores_from_tree_item as _calc

        return _calc(root_item, input_values)
        
    def calculate_absolute_weight_from_item(self, item: Any) -> float:
        """Delegate absolute weight calculation to `logic.tree_sankey.calculate_absolute_weight_from_item`."""
        from logic.tree_sankey import calculate_absolute_weight_from_item as _calc

        return _calc(item)
