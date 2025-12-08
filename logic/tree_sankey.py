"""
GUI-adapter functions for building Sankey data and traversing QTreeWidgetItems.

This module centralizes all PyQt6 / Plotly dependencies for tree-to-sankey
transformations so the core `math_engine` remains usable without GUI
dependencies during unit tests or headless execution.
"""
from typing import Any, Dict, List, Optional, Tuple


def generate_sankey_from_tree_item(root_item: Any, style_opts: Optional[Dict[str, Any]] = None) -> Any:
    """Generate single-layer Plotly Sankey from a QTreeWidgetItem tree.

    Returns a Plotly `Figure`.
    """
    # Local imports to avoid top-level GUI dependency
    from PyQt6.QtCore import Qt
    import plotly.graph_objects as go

    # (Implementation copied from previous math_engine, adapted to function scope)
    labels = []
    source = []
    target = []
    values = []
    node_colors = []
    node_x = []
    node_y = []
    uid_to_idx = {}

    s = style_opts or {}

    default_node_color = s.get("node_color", "#27ae60")
    link_color = s.get("link_color", "rgba(180, 180, 180, 0.4)")
    show_node_weight = s.get("show_node_weight", True)

    nodes_by_depth = {}
    max_depth = [0]

    def get_local_weight(item: Any) -> float:
        try:
            return float(item.text(1).replace("%", "")) / 100.0
        except Exception:
            return 0.0

    def build_label(name: str, weight_pct: Optional[float]) -> str:
        if show_node_weight and weight_pct is not None:
            return f"{name} ({weight_pct:.1f}%)"
        return name

    def traverse(item: Any, parent_idx: Optional[int] = None, parent_absolute_weight: float = 1.0, depth: int = 0):
        if not item:
            return

        uid = item.data(0, Qt.ItemDataRole.UserRole)
        if not uid:
            return

        name = item.text(0)
        local_weight = get_local_weight(item)
        absolute_weight = parent_absolute_weight * local_weight

        if absolute_weight < 0.001:
            absolute_weight = 0.001

        if depth > max_depth[0]:
            max_depth[0] = depth

        weight_pct = local_weight * 100 if depth > 0 else None
        label = build_label(name, weight_pct)

        if label not in uid_to_idx:
            idx = len(labels)
            uid_to_idx[label] = idx
            labels.append(label)

            if depth not in nodes_by_depth:
                nodes_by_depth[depth] = []
            nodes_by_depth[depth].append(idx)

            node_colors.append(default_node_color)

        current_idx = uid_to_idx[label]

        if parent_idx is not None:
            source.append(parent_idx)
            target.append(current_idx)
            values.append(absolute_weight)

        for i in range(item.childCount()):
            traverse(item.child(i), current_idx, absolute_weight, depth + 1)

    # Build the data structure
    if root_item:
        uid = root_item.data(0, Qt.ItemDataRole.UserRole)
        name = root_item.text(0)

        if uid and name:
            label = build_label(name, None)
            idx = len(labels)
            uid_to_idx[label] = idx
            labels.append(label)
            nodes_by_depth[0] = [idx]
            node_colors.append(default_node_color)

            for i in range(root_item.childCount()):
                traverse(root_item.child(i), idx, 1.0, depth=1)

    # Calculate positions
    total_nodes = len(labels)
    if total_nodes == 0:
        return go.Figure()

    node_x = [0.0] * total_nodes
    node_y = [0.0] * total_nodes

    num_depths = max_depth[0] + 1
    for depth, node_indices in nodes_by_depth.items():
        x_pos = depth / (num_depths - 1) if num_depths > 1 else 0.5
        for idx in node_indices:
            node_x[idx] = x_pos

    vertical_fill = s.get("vertical_fill", 0.95)
    vertical_margin = (1.0 - vertical_fill) / 2.0
    available_height = 1.0 - (2 * vertical_margin)
    gap = 0.02

    # Simplified positioning logic (keeps previous behavior)
    for depth, node_indices in nodes_by_depth.items():
        num_nodes = len(node_indices)
        if num_nodes == 1:
            node_y[node_indices[0]] = 0.5
        else:
            total_value_at_depth = 1.0 if depth == 0 else sum(values[i] for i, (_, t) in enumerate(zip(source, target)) if t in node_indices)
            if total_value_at_depth > 0:
                node_heights = []
                for idx in node_indices:
                    node_value = 1.0 if depth == 0 else sum(values[i] for i, t in enumerate(target) if t == idx)
                    height = (node_value / total_value_at_depth) * available_height
                    node_heights.append(height)

                total_used = sum(node_heights) + gap * (num_nodes - 1)
                y_start = vertical_margin + (available_height - total_used) / 2.0
                y_cursor = y_start
                for idx, node_height in zip(node_indices, node_heights):
                    node_y[idx] = y_cursor + (node_height / 2.0)
                    y_cursor += node_height + gap
            else:
                spacing = available_height / (num_nodes + 1)
                for i, idx in enumerate(node_indices):
                    node_y[idx] = vertical_margin + (i + 1) * spacing

    if not labels or not source:
        return go.Figure()

    fig = go.Figure(data=[
        go.Sankey(
            arrangement="fixed",
            node=dict(
                pad=s.get("pad", 15),
                thickness=s.get("thickness", 20),
                line=dict(color=s.get("node_line_color", "black"), width=s.get("node_line_width", 0.5)),
                label=labels,
                color=node_colors,
                x=node_x,
                y=node_y,
            ),
            link=dict(source=source, target=target, value=values, color=link_color),
        )
    ])

    title_text = s.get("title_text", "") if s.get("show_title", False) else ""
    bg_color = s.get("background_color", "#ffffff")
    plot_bg = "rgba(0,0,0,0)" if s.get("transparent_bg", False) else bg_color
    paper_bg = "rgba(0,0,0,0)" if s.get("transparent_bg", False) else bg_color

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=s.get("title_font_size", 20), family=s.get("title_font_family", "Arial"), color=s.get("title_color", "#000000")), x=0.5, xanchor="center"),
        font=dict(size=s.get("label_font_size", 12), family=s.get("label_font_family", "Arial"), color=s.get("label_font_color", "#000000")),
        autosize=True,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor=plot_bg,
        paper_bgcolor=paper_bg,
    )

    return fig


def generate_sankey_data(root_item: Any, style_opts: Optional[Dict[str, Any]] = None) -> Any:
    """Generate native Sankey data (nodes/links) for GUI-native rendering.

    Returns an object with `nodes` and `links` attributes (keeps compatibility with
    GUI widget `native_sankey` data classes).
    """
    from PyQt6.QtCore import Qt
    from gui.widgets.native_sankey import NodeData, LinkData, SankeyData

    s = style_opts or {}

    default_node_color = s.get("node_color", "#27ae60")
    link_color = s.get("link_color", "rgba(180, 180, 180, 0.4)")
    show_node_weight = s.get("show_node_weight", True)
    vertical_fill = s.get("vertical_fill", 0.95)
    gap_normalized = s.get("pad", 15) / 1000.0

    color_scheme = {0: default_node_color, 1: default_node_color, 2: default_node_color, 3: default_node_color}

    nodes = []
    links = []
    nodes_by_depth = {}
    uid_to_idx = {}

    def get_local_weight(item: Any) -> float:
        try:
            return float(item.text(1).replace("%", "")) / 100.0
        except Exception:
            return 0.0

    def build_label(name: str, weight_pct: Optional[float]) -> str:
        if show_node_weight and weight_pct is not None:
            return f"{name} ({weight_pct:.0f}%)"
        return name

    max_depth = [0]

    def traverse(item: Any, parent_idx: Optional[int] = None, parent_weight: float = 1.0, depth: int = 0):
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

        weight_pct = local_weight * 100 if depth > 0 else None
        label = build_label(name, weight_pct)

        if label not in uid_to_idx:
            idx = len(nodes)
            uid_to_idx[label] = idx
            node = NodeData(id=uid, label=label, x=0.0, y=0.0, height=absolute_weight, color=color_scheme.get(depth, default_node_color))
            nodes.append(node)

            if depth not in nodes_by_depth:
                nodes_by_depth[depth] = []
            nodes_by_depth[depth].append(idx)

        current_idx = uid_to_idx[label]

        if parent_idx is not None:
            link = LinkData(source_id=nodes[parent_idx].id, target_id=uid, value=absolute_weight, y_source_offset=0.0, y_target_offset=0.0, color=link_color)
            links.append(link)

        for i in range(item.childCount()):
            traverse(item.child(i), current_idx, absolute_weight, depth + 1)

    # Build root
    if root_item:
        uid = root_item.data(0, Qt.ItemDataRole.UserRole)
        name = root_item.text(0)

        if uid and name:
            label = build_label(name, None)
            idx = len(nodes)
            uid_to_idx[label] = idx
            node = NodeData(id=uid, label=label, x=0.0, y=0.0, height=1.0, color=color_scheme.get(0, default_node_color))
            nodes.append(node)
            nodes_by_depth[0] = [idx]

            for i in range(root_item.childCount()):
                traverse(root_item.child(i), idx, 1.0, depth=1)

    if len(nodes) == 0:
        return SankeyData(nodes=[], links=[])

    # Assign X positions
    num_depths = max_depth[0] + 1
    for depth, node_indices in nodes_by_depth.items():
        x_pos = depth / (num_depths - 1) if num_depths > 1 else 0.5
        for idx in node_indices:
            nodes[idx].x = x_pos

    # Scale & Y positions
    vertical_margin = (1.0 - vertical_fill) / 2.0
    available_height = 1.0 - 2 * vertical_margin
    max_overflow_ratio = 1.0

    for depth in sorted(nodes_by_depth.keys()):
        node_indices = nodes_by_depth[depth]
        num_nodes = len(node_indices)
        total_height = sum(nodes[idx].height for idx in node_indices)
        total_gap = gap_normalized * (num_nodes - 1) if num_nodes > 1 else 0
        needed_height = total_height + total_gap
        if needed_height > available_height:
            overflow_ratio = needed_height / available_height
            if overflow_ratio > max_overflow_ratio:
                max_overflow_ratio = overflow_ratio

    global_scale = 1.0 / max_overflow_ratio if max_overflow_ratio > 1.0 else 1.0

    for node in nodes:
        node.height = node.height * global_scale

    for link in links:
        link.value = link.value * global_scale

    # Y placement sequential
    for depth in sorted(nodes_by_depth.keys()):
        node_indices = nodes_by_depth[depth]
        current_y = vertical_margin
        for idx in node_indices:
            nodes[idx].y = current_y
            current_y += nodes[idx].height + gap_normalized

    # Link offsets
    source_offsets = {}
    for link in links:
        if link.source_id not in source_offsets:
            source_offsets[link.source_id] = 0.0
        link.y_source_offset = source_offsets[link.source_id]
        source_offsets[link.source_id] += link.value

    return SankeyData(nodes=nodes, links=links)


def generate_scenario_sankey_data(root_item: Any, scenario_scores: Optional[Dict[Any, float]] = None, style_opts: Optional[Dict[str, Any]] = None) -> Tuple[Any, Any]:
    """Generate two-layer SankeyData (shadow, filled) from a QTreeWidgetItem and scenario scores.

    Returns:
        (shadow_sankeydata, filled_sankeydata)
    """
    from PyQt6.QtCore import Qt
    from gui.widgets.native_sankey import NodeData, LinkData, SankeyData

    s = style_opts or {}
    scores = scenario_scores or {}

    shadow_color = s.get("shadow_node_color", "rgba(200, 200, 200, 0.3)")
    shadow_node_color = shadow_color
    shadow_link_color = shadow_color
    filled_node_color = s.get("node_color", "#27ae60")
    filled_link_color = s.get("link_color", "rgba(39, 174, 96, 0.6)")
    show_node_weight = s.get("show_node_weight", True)
    vertical_fill = s.get("vertical_fill", 0.95)
    gap_normalized = s.get("pad", 15) / 1000.0

    shadow_nodes = []
    filled_nodes = []
    shadow_links = []
    filled_links = []
    nodes_by_depth = {}
    uid_to_idx = {}
    node_satisfaction = {}

    def get_local_weight(item: Any) -> float:
        try:
            return float(item.text(1).replace("%", "")) / 100.0
        except Exception:
            return 0.0

    def build_label(name: str, satisfaction_score: Optional[float]) -> str:
        if show_node_weight and satisfaction_score is not None:
            return f"{name} ({satisfaction_score:.2f})"
        return name

    max_depth = [0]

    def traverse(item: Any, parent_idx: Optional[int] = None, parent_weight: float = 1.0, depth: int = 0):
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

        satisfaction = scores.get(uid, 0.0)
        label = build_label(name, satisfaction)

        if label not in uid_to_idx:
            idx = len(shadow_nodes)
            uid_to_idx[label] = idx
            node_satisfaction[idx] = satisfaction

            shadow_node = NodeData(id=uid, label="", x=0.0, y=0.0, height=absolute_weight, color=shadow_node_color)
            shadow_nodes.append(shadow_node)

            filled_height = absolute_weight * satisfaction
            filled_node = NodeData(id=uid, label=label, x=0.0, y=0.0, height=filled_height, color=filled_node_color)
            filled_nodes.append(filled_node)

            if depth not in nodes_by_depth:
                nodes_by_depth[depth] = []
            nodes_by_depth[depth].append(idx)

        current_idx = uid_to_idx[label]

        if parent_idx is not None:
            shadow_link = LinkData(source_id=shadow_nodes[parent_idx].id, target_id=uid, value=absolute_weight, y_source_offset=0.0, y_target_offset=0.0, color=shadow_link_color)
            shadow_links.append(shadow_link)

            child_satisfaction = node_satisfaction.get(current_idx, 0.0)
            filled_value = absolute_weight * child_satisfaction
            filled_link = LinkData(source_id=filled_nodes[parent_idx].id, target_id=uid, value=filled_value, y_source_offset=0.0, y_target_offset=0.0, color=filled_link_color)
            filled_links.append(filled_link)

        for i in range(item.childCount()):
            traverse(item.child(i), current_idx, absolute_weight, depth + 1)

    # Build root
    if root_item:
        uid = root_item.data(0, Qt.ItemDataRole.UserRole)
        name = root_item.text(0)
        if uid and name:
            satisfaction = scores.get(uid, 0.0)
            label = build_label(name, satisfaction)
            idx = len(shadow_nodes)
            uid_to_idx[label] = idx
            node_satisfaction[idx] = satisfaction

            shadow_node = NodeData(id=uid, label="", x=0.0, y=0.0, height=1.0, color=shadow_node_color)
            shadow_nodes.append(shadow_node)

            filled_node = NodeData(id=uid, label=label, x=0.0, y=0.0, height=satisfaction, color=s.get('root_highlight_color', filled_node_color))
            filled_nodes.append(filled_node)

            nodes_by_depth[0] = [idx]

            for i in range(root_item.childCount()):
                traverse(root_item.child(i), idx, 1.0, depth=1)

    if len(shadow_nodes) == 0:
        return SankeyData(nodes=[], links=[]), SankeyData(nodes=[], links=[])

    num_depths = max_depth[0] + 1
    for depth, node_indices in nodes_by_depth.items():
        x_pos = depth / (num_depths - 1) if num_depths > 1 else 0.5
        for idx in node_indices:
            shadow_nodes[idx].x = x_pos
            filled_nodes[idx].x = x_pos

    vertical_margin = (1.0 - vertical_fill) / 2.0
    available_height = 1.0 - 2 * vertical_margin
    max_overflow_ratio = 1.0

    for depth in sorted(nodes_by_depth.keys()):
        node_indices = nodes_by_depth[depth]
        num_nodes = len(node_indices)
        total_height = sum(shadow_nodes[idx].height for idx in node_indices)
        total_gap = gap_normalized * (num_nodes - 1) if num_nodes > 1 else 0
        needed_height = total_height + total_gap
        if needed_height > available_height:
            overflow_ratio = needed_height / available_height
            if overflow_ratio > max_overflow_ratio:
                max_overflow_ratio = overflow_ratio

    global_scale = 1.0 / max_overflow_ratio if max_overflow_ratio > 1.0 else 1.0

    for i in range(len(shadow_nodes)):
        shadow_nodes[i].height *= global_scale
        filled_nodes[i].height *= global_scale

    for link in shadow_links:
        link.value *= global_scale
    for link in filled_links:
        link.value *= global_scale

    for depth in sorted(nodes_by_depth.keys()):
        node_indices = nodes_by_depth[depth]
        current_y = vertical_margin
        for idx in node_indices:
            shadow_nodes[idx].y = current_y
            shadow_height = shadow_nodes[idx].height
            filled_height = filled_nodes[idx].height
            y_offset = (shadow_height - filled_height) / 2.0
            filled_nodes[idx].y = current_y + y_offset
            current_y += shadow_height + gap_normalized

    source_offsets = {}
    for link in shadow_links:
        if link.source_id not in source_offsets:
            source_offsets[link.source_id] = 0.0
        link.y_source_offset = source_offsets[link.source_id]
        source_offsets[link.source_id] += link.value

    source_offsets = {}
    for link in filled_links:
        if link.source_id not in source_offsets:
            source_offsets[link.source_id] = 0.0
        link.y_source_offset = source_offsets[link.source_id]
        source_offsets[link.source_id] += link.value

    return (SankeyData(nodes=shadow_nodes, links=shadow_links), SankeyData(nodes=filled_nodes, links=filled_links))


def generate_scenario_sankey(root_item: Any, scenario_scores: Optional[Dict[Any, float]] = None, style_opts: Optional[Dict[str, Any]] = None) -> Any:
    """Create a dual-layer Plotly Sankey (shadow + filled) for scenarios.

    Returns a Plotly `Figure` with two Sankey traces.
    """
    from PyQt6.QtCore import Qt
    import plotly.graph_objects as go

    s = style_opts or {}
    scores = scenario_scores or {}

    shadow_node_color = s.get('shadow_node_color', '#E0E0E0')
    shadow_link_color = s.get('shadow_link_color', 'rgba(200,200,200,0.3)')
    filled_node_color = s.get('node_color', '#27ae60')
    filled_link_color = s.get('link_color', 'rgba(39,174,96,0.6)')
    show_node_weight = s.get('show_node_weight', True)

    labels = []
    shadow_labels = []
    source = []
    target = []
    shadow_values = []
    filled_values = []
    node_x = []
    shadow_node_y = []
    uid_to_idx = {}
    node_satisfaction = {}

    nodes_by_depth = {}
    max_depth = [0]

    def get_local_weight(item: Any) -> float:
        try:
            return float(item.text(1).replace('%', '')) / 100.0
        except Exception:
            return 0.0

    def build_label(name: str, weight_pct: Optional[float]) -> str:
        if show_node_weight and weight_pct is not None:
            return f"{name} ({weight_pct:.1f}%)"
        return name

    def traverse(item: Any, parent_idx: Optional[int] = None, parent_absolute_weight: float = 1.0, depth: int = 0):
        if not item:
            return

        uid = item.data(0, Qt.ItemDataRole.UserRole)
        if not uid:
            return

        name = item.text(0)
        local_weight = get_local_weight(item)
        absolute_weight = parent_absolute_weight * local_weight

        if absolute_weight < 0.001:
            absolute_weight = 0.001

        if depth > max_depth[0]:
            max_depth[0] = depth

        weight_pct = local_weight * 100 if depth > 0 else None
        label = build_label(name, weight_pct)

        if label not in uid_to_idx:
            idx = len(labels)
            uid_to_idx[label] = idx
            labels.append(label)
            shadow_labels.append('')

            if depth not in nodes_by_depth:
                nodes_by_depth[depth] = []
            nodes_by_depth[depth].append(idx)

            satisfaction = scores.get(uid, 0.0)
            node_satisfaction[idx] = satisfaction

        current_idx = uid_to_idx[label]

        if parent_idx is not None:
            source.append(parent_idx)
            target.append(current_idx)
            shadow_values.append(absolute_weight)
            child_satisfaction = node_satisfaction.get(current_idx, 0.0)
            filled_link_value = absolute_weight * child_satisfaction
            filled_values.append(max(filled_link_value, 0.0001) if filled_link_value > 0 else 0.0001)

        for i in range(item.childCount()):
            traverse(item.child(i), current_idx, absolute_weight, depth + 1)

    if root_item:
        uid = root_item.data(0, Qt.ItemDataRole.UserRole)
        name = root_item.text(0)
        if uid and name:
            label = build_label(name, None)
            idx = len(labels)
            uid_to_idx[label] = idx
            labels.append(label)
            shadow_labels.append('')
            nodes_by_depth[0] = [idx]

            satisfaction = scores.get(uid, 0.0)
            node_satisfaction[idx] = satisfaction

            for i in range(root_item.childCount()):
                traverse(root_item.child(i), idx, 1.0, depth=1)

    total_nodes = len(labels)
    if total_nodes == 0 or not source:
        return go.Figure()

    node_x = [0.0] * total_nodes
    shadow_node_y = [0.0] * total_nodes

    num_depths = max_depth[0] + 1
    for depth, node_indices in nodes_by_depth.items():
        x_pos = depth / (num_depths - 1) if num_depths > 1 else 0.5
        for idx in node_indices:
            node_x[idx] = x_pos

    vertical_fill = s.get('vertical_fill', 0.95)
    vertical_margin = (1.0 - vertical_fill) / 2.0
    available_height = 1.0 - (2 * vertical_margin)
    gap = 0.02

    max_overflow_ratio = 1.0
    for depth, node_indices in nodes_by_depth.items():
        num_nodes = len(node_indices)
        if num_nodes <= 1:
            continue
        total_gap_height = gap * (num_nodes - 1)
        needed_ratio = (available_height + total_gap_height) / available_height
        if needed_ratio > max_overflow_ratio:
            max_overflow_ratio = needed_ratio

    global_scale = 1.0 / max_overflow_ratio if max_overflow_ratio > 1.0 else 1.0

    for depth, node_indices in nodes_by_depth.items():
        num_nodes = len(node_indices)
        if num_nodes == 1:
            shadow_node_y[node_indices[0]] = 0.5
        else:
            total_value_at_depth = 0.0
            if depth == 0:
                total_value_at_depth = 1.0
            else:
                for idx in node_indices:
                    for i, t in enumerate(target):
                        if t == idx:
                            total_value_at_depth += shadow_values[i]

            if total_value_at_depth > 0:
                node_heights = []
                for idx in node_indices:
                    node_value = 0
                    if depth == 0:
                        node_value = 1.0
                    else:
                        for i, t in enumerate(target):
                            if t == idx:
                                node_value += shadow_values[i]

                    height = (node_value / total_value_at_depth) * available_height * global_scale
                    node_heights.append(height)

                total_used = sum(node_heights) + gap * (num_nodes - 1)
                y_start = vertical_margin + (available_height - total_used) / 2.0
                y_cursor = y_start
                for idx, node_height in zip(node_indices, node_heights):
                    shadow_node_y[idx] = y_cursor + (node_height / 2.0)
                    y_cursor += node_height + gap
            else:
                spacing = available_height / (num_nodes + 1)
                for i, idx in enumerate(node_indices):
                    shadow_node_y[idx] = vertical_margin + (i + 1) * spacing

    filled_node_y = shadow_node_y.copy()

    shadow_trace = go.Sankey(
        arrangement='fixed',
        node=dict(
            pad=s.get('pad', 15),
            thickness=s.get('thickness', 20),
            line=dict(color=shadow_node_color, width=0),
            label=shadow_labels,
            color=shadow_node_color,
            x=node_x,
            y=shadow_node_y
        ),
        link=dict(source=source, target=target, value=shadow_values, color=shadow_link_color)
    )

    filled_node_colors = [filled_node_color] * total_nodes

    filled_trace = go.Sankey(
        arrangement='fixed',
        node=dict(
            pad=s.get('pad', 15),
            thickness=s.get('thickness', 20),
            line=dict(color=s.get('node_line_color', 'black'), width=s.get('node_line_width', 0.5)),
            label=labels,
            color=filled_node_colors,
            x=node_x,
            y=filled_node_y
        ),
        link=dict(source=source, target=target, value=filled_values, color=filled_link_color)
    )

    fig = go.Figure(data=[shadow_trace, filled_trace])

    title_text = s.get('title_text', '') if s.get('show_title', False) else ''
    bg_color = s.get('background_color', '#ffffff')
    plot_bg = 'rgba(0,0,0,0)' if s.get('transparent_bg', False) else bg_color
    paper_bg = 'rgba(0,0,0,0)' if s.get('transparent_bg', False) else bg_color

    fig.update_layout(
        title=dict(text=title_text, font=dict(size=s.get('title_font_size', 20), family=s.get('title_font_family', 'Arial'), color=s.get('title_color', '#000000')), x=0.5, xanchor='center'),
        font=dict(size=s.get('label_font_size', 12), family=s.get('label_font_family', 'Arial'), color=s.get('label_font_color', '#000000')),
        autosize=True,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor=plot_bg,
        paper_bgcolor=paper_bg
    )

    return fig


def calculate_tree_scores_from_tree_item(root_item: Any, input_values: Dict[Any, float]) -> Dict[Any, float]:
    """Calculate scores from a QTreeWidgetItem tree using MIVES value functions.

    This function is GUI-dependent (QTreeWidgetItem) but kept here to centralize
    tree traversal logic.
    """
    from PyQt6.QtCore import Qt
    from logic.math_engine import MivesLogic

    logic = MivesLogic()
    scores: Dict[Any, float] = {}

    def process(item: Any) -> float:
        uid = item.data(0, Qt.ItemDataRole.UserRole)
        if item.text(2) == "Indicator":
            f_data = item.data(1, Qt.ItemDataRole.UserRole) or {}
            x0, x1 = f_data.get('xmin', 0), f_data.get('xmax', 100)
            C, K, P = f_data.get('c', 100), f_data.get('k', 0.1), f_data.get('p', 1.0)
            val = input_values.get(uid, x0)
            sat = logic.calculate_mives_value(val, x0, x1, C, K, P)
            scores[uid] = sat
            return sat
        else:
            total_score, total_weight = 0.0, 0.0
            for i in range(item.childCount()):
                child = item.child(i)
                try:
                    w = float(child.text(1).replace('%',''))/100.0
                except Exception:
                    w = 0.0
                total_score += process(child) * w
                total_weight += w
            final = total_score / total_weight if total_weight > 0 else 0
            scores[uid] = final
            return final

    if root_item:
        process(root_item)
    return scores


def calculate_absolute_weight_from_item(item: Any) -> float:
    """Calculate absolute weight multiplying parent weights up to root."""
    weights: List[float] = []
    current = item
    while current:
        try:
            weight = float(current.text(1).replace('%', '')) / 100.0
            weights.append(weight)
        except Exception:
            weights.append(1.0)
        current = current.parent()

    absolute_weight = 1.0
    for w in weights[:-1]:
        absolute_weight *= w

    return absolute_weight
