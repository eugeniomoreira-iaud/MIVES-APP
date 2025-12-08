"""
MIVES Mathematical Engine
Implements exponential value functions per Boix-Cots et al. (2022)
"""
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from gui.widgets.native_sankey import NodeData, LinkData, SankeyData


class MivesLogic:
    """Pure MIVES computation - No GUI dependencies"""
    
    def calculate_mives_value(self, x, x_sat_0, x_sat_1, C, K, P):
        """Calculates value using the MIVES exponential formula."""
        dist_x = abs(x - x_sat_0)
        dist_max = abs(x_sat_1 - x_sat_0)
        
        # Direction Logic
        is_increasing = x_sat_1 > x_sat_0
        if is_increasing:
            if x <= x_sat_0: return 0.0
            if x >= x_sat_1: return 1.0
        else:
            if x >= x_sat_0: return 0.0
            if x <= x_sat_1: return 1.0

        if C <= 0.0001: 
            C = 0.0001
        
        # Factor B
        try:
            phi_max = math.exp(-K * math.pow(dist_max / C, P))
            if abs(1.0 - phi_max) < 1e-9:
                B = 1.0
            else:
                B = 1.0 / (1.0 - phi_max)
        except (ValueError, OverflowError):
            B = 1.0

        # Value
        try:
            phi_x = math.exp(-K * math.pow(dist_x / C, P))
            value = B * (1.0 - phi_x)
        except (ValueError, OverflowError):
            value = 0.0
            
        return max(0.0, min(1.0, value))

    def generate_single_curve(self, name, x_sat_0, x_sat_1, units, C, K, P, 
                             style_opts=None, actual_val=None):
        """Generate single value function curve with enhanced styling"""
        try:
            margin = abs(x_sat_1 - x_sat_0) * 0.1
            if margin == 0: 
                margin = 1.0
            x_min_plot = min(x_sat_0, x_sat_1) - margin
            x_max_plot = max(x_sat_0, x_sat_1) + margin
            x_vals = np.linspace(x_min_plot, x_max_plot, 150)
            y_vals = [self.calculate_mives_value(v, x_sat_0, x_sat_1, C, K, P) for v in x_vals]
        except Exception:
            x_vals, y_vals = [], []

        s = style_opts or {}
        fig = go.Figure()
        
        # Main Curve
        fill_arg = 'tozeroy' if s.get('fill', False) else 'none'
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals, 
            mode='lines', fill=fill_arg,
            name='Value Function', 
            line=dict(
                color=s.get('color', '#2980b9'), 
                width=s.get('width', 3), 
                dash=s.get('dash', 'solid')
            )
        ))
        
        # Scenario Marker (if provided)
        if actual_val is not None:
            sat = self.calculate_mives_value(actual_val, x_sat_0, x_sat_1, C, K, P)
            fig.add_trace(go.Scatter(
                x=[actual_val], y=[sat], mode='markers', 
                marker=dict(color='red', size=14, line=dict(width=2, color='white')), 
                name='Actual'
            ))

        direction = "Increasing" if x_sat_1 > x_sat_0 else "Decreasing"
        
        # Enhanced styling
        font_family = s.get('font_family', 'Arial')
        font_size_title = s.get('font_size_title', 16)
        font_size_axes = s.get('font_size_axes', 12)
        axis_line_width = s.get('axis_line_width', 2)
        axis_line_color = s.get('axis_line_color', '#333333')
        
        # Individual axis line visibility
        show_axis_top = s.get('show_axis_top', True)
        show_axis_bottom = s.get('show_axis_bottom', True)
        show_axis_left = s.get('show_axis_left', True)
        show_axis_right = s.get('show_axis_right', True)
        
        grid_show = s.get('grid', True)
        grid_line_width = s.get('grid_line_width', 1)
        grid_line_color = s.get('grid_line_color', '#e0e0e0')
        grid_line_dash = s.get('grid_line_dash', 'solid')
        background_color = s.get('background_color', '#ffffff')
        
        # BALANCED DYNAMIC TOP MARGIN
        if font_size_title <= 16:
            top_margin = 90 
        else:
            extra_space = (font_size_title - 16) * 2.5
            top_margin = int(90 + extra_space)
        
        fig.update_layout(
            title=dict(
                text=f"<b>{name}</b><br><sub>{direction} | P={P}, K={K}, C={C}</sub>", 
                x=0.01, y=0.96, xanchor='left', yanchor='top',
                font=dict(family=font_family, size=font_size_title)
            ),
            xaxis_title=dict(text=units, font=dict(family=font_family, size=font_size_axes, weight='bold')),
            yaxis_title=dict(text="Value (0-1)", font=dict(family=font_family, size=font_size_axes, weight='bold')),
            margin=dict(l=60, r=20, t=top_margin, b=50),
            autosize=True, 
            showlegend=False,
            plot_bgcolor=background_color,
            paper_bgcolor=background_color,
            font=dict(family=font_family, size=font_size_axes),
            xaxis=dict(
                showgrid=grid_show, gridcolor=grid_line_color, gridwidth=grid_line_width, griddash=grid_line_dash,
                linewidth=axis_line_width, linecolor=axis_line_color,
                mirror=True if (show_axis_top and show_axis_bottom) else False,
                showline=show_axis_bottom, ticks='outside' if show_axis_bottom else ''
            ),
            yaxis=dict(
                showgrid=grid_show, gridcolor=grid_line_color, gridwidth=grid_line_width, griddash=grid_line_dash,
                linewidth=axis_line_width, linecolor=axis_line_color,
                mirror=True if (show_axis_left and show_axis_right) else False,
                showline=show_axis_left, ticks='outside' if show_axis_left else '',
                range=[-0.05, 1.05]
            )
        )
        
        shapes = []
        if show_axis_top and not (show_axis_top and show_axis_bottom):
            shapes.append(dict(type='line', xref='paper', yref='paper', x0=0, y0=1, x1=1, y1=1,
                               line=dict(color=axis_line_color, width=axis_line_width)))
        if show_axis_right and not (show_axis_left and show_axis_right):
            shapes.append(dict(type='line', xref='paper', yref='paper', x0=1, y0=0, x1=1, y1=1,
                               line=dict(color=axis_line_color, width=axis_line_width)))
        
        if shapes: fig.update_layout(shapes=shapes)
        return fig

    def generate_matrix_chart(self, indicators_data, style_opts=None):
        """Generate matrix of indicator curves with styling options"""
        n = len(indicators_data)
        if n == 0: 
            return go.Figure()
        
        s = style_opts or {}
        
        cols = 3
        rows = (n // cols) + (1 if n % cols > 0 else 0)
        fig = make_subplots(rows=rows, cols=cols, subplot_titles=[d['name'] for d in indicators_data])
        
        # Extract style options
        curve_color = s.get('color', '#2980b9')
        curve_width = s.get('width', 3)
        curve_dash = s.get('dash', 'solid')
        
        for i, d in enumerate(indicators_data):
            r, c_idx = (i // cols) + 1, (i % cols) + 1
            x0, x1 = d['xmin'], d['xmax']
            margin = abs(x1 - x0) * 0.1
            if margin == 0: 
                margin = 1
            plot_min, plot_max = min(x0, x1) - margin, max(x0, x1) + margin
            
            x_vals = np.linspace(plot_min, plot_max, 50)
            y_vals = [self.calculate_mives_value(v, x0, x1, d['c'], d['k'], d['p']) for v in x_vals]
            
            # Apply curve styling
            fig.add_trace(
                go.Scatter(
                    x=x_vals, 
                    y=y_vals, 
                    mode='lines', 
                    line=dict(color=curve_color, width=curve_width, dash=curve_dash)
                ), 
                row=r, 
                col=c_idx
            )
            
            # Add actual value marker if present
            if 'actual' in d:
                sat = self.calculate_mives_value(d['actual'], x0, x1, d['c'], d['k'], d['p'])
                fig.add_trace(
                    go.Scatter(
                        x=[d['actual']], 
                        y=[sat], 
                        mode='markers', 
                        marker=dict(color='red', size=8)
                    ), 
                    row=r, 
                    col=c_idx
                )
        
        # Apply layout styling
        font_family = s.get('font_family', 'Arial')
        font_size_title = s.get('font_size_title', 16)
        font_size_axes = s.get('font_size_axes', 12)
        axis_line_width = s.get('axis_line_width', 2)
        axis_line_color = s.get('axis_line_color', '#333333')
        
        # Individual axis line visibility
        show_axis_top = s.get('show_axis_top', True)
        show_axis_bottom = s.get('show_axis_bottom', True)
        show_axis_left = s.get('show_axis_left', True)
        show_axis_right = s.get('show_axis_right', True)
        
        # Grid styling
        grid_show = s.get('grid', True)
        grid_line_width = s.get('grid_line_width', 1)
        grid_line_color = s.get('grid_line_color', '#e0e0e0')
        grid_line_dash = s.get('grid_line_dash', 'solid')
        
        background_color = s.get('background_color', '#ffffff')
        
        # Update all subplots with styling
        fig.update_xaxes(
            showgrid=grid_show,
            gridcolor=grid_line_color,
            gridwidth=grid_line_width,
            griddash=grid_line_dash,
            linewidth=axis_line_width,
            linecolor=axis_line_color,
            mirror=True if (show_axis_top and show_axis_bottom) else False,
            showline=show_axis_bottom,
            ticks='outside' if show_axis_bottom else ''
        )
        
        fig.update_yaxes(
            showgrid=grid_show,
            gridcolor=grid_line_color,
            gridwidth=grid_line_width,
            griddash=grid_line_dash,
            linewidth=axis_line_width,
            linecolor=axis_line_color,
            mirror=True if (show_axis_left and show_axis_right) else False,
            showline=show_axis_left,
            ticks='outside' if show_axis_left else '',
            range=[-0.05, 1.05]
        )
        
        fig.update_layout(
            height=rows*200,
            showlegend=False,
            plot_bgcolor=background_color,
            paper_bgcolor=background_color,
            font=dict(family=font_family, size=font_size_axes),
            margin=dict(l=40, r=20, t=60, b=20)
        )
        
        # Update subplot titles font
        fig.update_annotations(font=dict(family=font_family, size=font_size_title))
        
        return fig

#############################

    def generate_sankey_from_tree_item(self, root_item, style_opts=None):
        """
        Generate single-layer Sankey for structure visualization (Tab 3).
        All node colors controlled by style options.
        """
        from PyQt6.QtCore import Qt
        import plotly.graph_objects as go
        
        # Data structures
        labels = []
        source = []
        target = []
        values = []
        node_colors = []
        node_x = []
        node_y = []
        uid_to_idx = {}
        
        s = style_opts or {}
        
        # Extract style options
        default_node_color = s.get('node_color', '#27ae60')
        link_color = s.get('link_color', 'rgba(180, 180, 180, 0.4)')
        show_node_weight = s.get('show_node_weight', True)
        
        # Track nodes by depth for positioning
        nodes_by_depth = {}
        max_depth = [0]
        
        # Helper: Get local weight from tree widget
        def get_local_weight(item):
            try:
                return float(item.text(1).replace('%', '')) / 100.0
            except:
                return 0.0
        
        # Helper: Build formatted label
        def build_label(name, weight_pct):
            if show_node_weight and weight_pct is not None:
                return f"{name} ({weight_pct:.1f}%)"
            return name
        
        # Traverse tree and build Sankey data
        def traverse(item, parent_idx=None, parent_absolute_weight=1.0, depth=0):
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
                
                # Always use style-controlled node color
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
                
                # Always use style-controlled node color
                node_colors.append(default_node_color)
                
                for i in range(root_item.childCount()):
                    traverse(root_item.child(i), idx, 1.0, depth=1)
        
        # Calculate positions
        total_nodes = len(labels)
        if total_nodes == 0:
            return go.Figure()
        
        node_x = [0.0] * total_nodes
        node_y = [0.0] * total_nodes
        
        # Assign X positions based on depth
        num_depths = max_depth[0] + 1
        for depth, node_indices in nodes_by_depth.items():
            if num_depths > 1:
                x_pos = depth / (num_depths - 1)
            else:
                x_pos = 0.5
            
            for idx in node_indices:
                node_x[idx] = x_pos
        
        # Assign Y positions with unified scaling
        vertical_fill = s.get('vertical_fill', 0.95)
        vertical_margin = (1.0 - vertical_fill) / 2.0
        available_height = 1.0 - (2 * vertical_margin)
        gap = 0.02

        # Calculate max overflow ratio
        max_overflow_ratio = 1.0
        for depth, node_indices in nodes_by_depth.items():
            num_nodes = len(node_indices)
            if num_nodes == 1:
                continue
            
            total_value_at_depth = sum(values[i] for i, (s_idx, t) in enumerate(zip(source, target)) 
                                       if t in node_indices or (depth == 0 and node_indices[0] == 0))
            
            if depth == 0:
                total_value_at_depth = 1.0
            
            if depth > 0 and total_value_at_depth == 0:
                for idx in node_indices:
                    for i, t in enumerate(target):
                        if t == idx:
                            total_value_at_depth += values[i]
            
            if total_value_at_depth > 0:
                total_gap_height = gap * (num_nodes - 1)
                needed_ratio = (available_height + total_gap_height) / available_height
                if needed_ratio > max_overflow_ratio:
                    max_overflow_ratio = needed_ratio

        global_scale = 1.0 / max_overflow_ratio if max_overflow_ratio > 1.0 else 1.0

        # Position nodes
        for depth, node_indices in nodes_by_depth.items():
            num_nodes = len(node_indices)
            
            if num_nodes == 1:
                node_y[node_indices[0]] = 0.5
            else:
                total_value_at_depth = sum(values[i] for i, (s_idx, t) in enumerate(zip(source, target)) 
                                           if t in node_indices or (depth == 0 and node_indices[0] == 0))
                
                if depth == 0:
                    total_value_at_depth = 1.0
                
                if depth > 0 and total_value_at_depth == 0:
                    for idx in node_indices:
                        for i, t in enumerate(target):
                            if t == idx:
                                total_value_at_depth += values[i]
                
                if total_value_at_depth > 0:
                    node_heights = []
                    for idx in node_indices:
                        node_value = 0
                        if depth == 0:
                            node_value = 1.0
                        else:
                            for i, t in enumerate(target):
                                if t == idx:
                                    node_value += values[i]
                        
                        height = (node_value / total_value_at_depth) * available_height * global_scale
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
        
        # Validate data
        if not labels or not source:
            return go.Figure()
        
        # Create Sankey figure
        fig = go.Figure(data=[go.Sankey(
            arrangement='fixed',
            node=dict(
                pad=s.get('pad', 15),
                thickness=s.get('thickness', 20),
                line=dict(
                    color=s.get('node_line_color', 'black'), 
                    width=s.get('node_line_width', 0.5)
                ),
                label=labels,
                color=node_colors,
                x=node_x,
                y=node_y
            ),
            link=dict(
                source=source,
                target=target,
                value=values,
                color=link_color
            )
        )])
        
        # Update layout
        title_text = ""
        if s.get('show_title', False):
            title_text = s.get('title_text', '')
        
        bg_color = s.get('background_color', '#ffffff')
        plot_bg = 'rgba(0,0,0,0)' if s.get('transparent_bg', False) else bg_color
        paper_bg = 'rgba(0,0,0,0)' if s.get('transparent_bg', False) else bg_color
        
        fig.update_layout(
            title=dict(
                text=title_text, 
                font=dict(
                    size=s.get('title_font_size', 20),
                    family=s.get('title_font_family', 'Arial'),
                    color=s.get('title_color', '#000000')
                ),
                x=0.5,
                xanchor='center'
            ),
            font=dict(
                size=s.get('label_font_size', 12),
                family=s.get('label_font_family', 'Arial'),
                color=s.get('label_font_color', '#000000')
            ),
            autosize=True,
            margin=dict(l=10, r=10, t=60, b=10),
            plot_bgcolor=plot_bg,
            paper_bgcolor=paper_bg
        )
        
        return fig

#############################

    def generate_sankey_data(self, root_item, style_opts=None):
        """
        Generate native Sankey data structure from QTreeWidget.

        This method replaces generate_sankey_from_tree_item() for native rendering.
        Returns SankeyData instead of Plotly figure.

        Args:
            root_item: QTreeWidgetItem root node
            style_opts: Style dictionary (same as Plotly version)

        Returns:
            SankeyData object with nodes and links
        """
        from PyQt6.QtCore import Qt
        from gui.widgets.native_sankey import NodeData, LinkData, SankeyData

        s = style_opts or {}

        # Extract style options
        default_node_color = s.get('node_color', '#27ae60')
        link_color = s.get('link_color', 'rgba(180, 180, 180, 0.4)')
        show_node_weight = s.get('show_node_weight', True)
        vertical_fill = s.get('vertical_fill', 0.95)
        gap_normalized = s.get('pad', 15) / 1000.0  # Convert pad to normalized gap

        # Color scheme by depth
        color_scheme = {
            0: default_node_color,  # Root
            1: default_node_color,  # Requirements
            2: default_node_color,  # Criteria
            3: default_node_color,  # Indicators
        }

        # Data structures
        nodes = []
        links = []
        nodes_by_depth = {}
        uid_to_idx = {}

        # Helper: Get local weight from tree widget
        def get_local_weight(item):
            try:
                return float(item.text(1).replace('%', '')) / 100.0
            except:
                return 0.0

        # Helper: Build formatted label
        def build_label(name, weight_pct):
            if show_node_weight and weight_pct is not None:
                return f"{name} ({weight_pct:.0f}%)"
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

            # Build label
            weight_pct = local_weight * 100 if depth > 0 else None
            label = build_label(name, weight_pct)

            # Create node
            if label not in uid_to_idx:
                idx = len(nodes)
                uid_to_idx[label] = idx

                node = NodeData(
                    id=uid,
                    label=label,
                    x=0.0,  # Will be set later
                    y=0.0,  # Will be set later
                    height=absolute_weight,
                    color=color_scheme.get(depth, default_node_color)
                )
                nodes.append(node)

                # Track by depth
                if depth not in nodes_by_depth:
                    nodes_by_depth[depth] = []
                nodes_by_depth[depth].append(idx)

            current_idx = uid_to_idx[label]

            # Create link from parent
            if parent_idx is not None:
                link = LinkData(
                    source_id=nodes[parent_idx].id,
                    target_id=uid,
                    value=absolute_weight,
                    y_source_offset=0.0,  # Will be calculated later
                    y_target_offset=0.0,
                    color=link_color
                )
                links.append(link)

            # Traverse children
            for i in range(item.childCount()):
                traverse(item.child(i), current_idx, absolute_weight, depth + 1)

        # Build root node
        if root_item:
            uid = root_item.data(0, Qt.ItemDataRole.UserRole)
            name = root_item.text(0)

            if uid and name:
                label = build_label(name, None)
                idx = len(nodes)
                uid_to_idx[label] = idx

                node = NodeData(
                    id=uid,
                    label=label,
                    x=0.0,
                    y=0.0,
                    height=1.0,
                    color=color_scheme.get(0, default_node_color)
                )
                nodes.append(node)
                nodes_by_depth[0] = [idx]

                # Traverse children
                for i in range(root_item.childCount()):
                    traverse(root_item.child(i), idx, 1.0, depth=1)

        # Validate
        if len(nodes) == 0:
            return SankeyData(nodes=[], links=[])

        # ===================================================================
        # STEP 1: Calculate X positions based on depth
        # ===================================================================
        num_depths = max_depth[0] + 1
        for depth, node_indices in nodes_by_depth.items():
            x_pos = depth / (num_depths - 1) if num_depths > 1 else 0.5
            for idx in node_indices:
                nodes[idx].x = x_pos

        # ===================================================================
        # STEP 2: Calculate GLOBAL scale factor (CRITICAL for Visual = Math)
        # ===================================================================
        vertical_margin = (1.0 - vertical_fill) / 2.0
        available_height = 1.0 - 2 * vertical_margin
        max_overflow_ratio = 1.0

        for depth in sorted(nodes_by_depth.keys()):
            node_indices = nodes_by_depth[depth]
            num_nodes = len(node_indices)

            # Calculate total height at this depth
            total_height = sum(nodes[idx].height for idx in node_indices)
            total_gap = gap_normalized * (num_nodes - 1) if num_nodes > 1 else 0

            # Check if scaling needed
            needed_height = total_height + total_gap
            if needed_height > available_height:
                overflow_ratio = needed_height / available_height
                if overflow_ratio > max_overflow_ratio:
                    max_overflow_ratio = overflow_ratio

        # Global scale (same for ALL levels)
        global_scale = 1.0 / max_overflow_ratio if max_overflow_ratio > 1.0 else 1.0

        # ===================================================================
        # STEP 3: Apply GLOBAL scale to ALL nodes
        # ===================================================================
        for node in nodes:
            node.height = node.height * global_scale

        # ===================================================================
        # STEP 4: Calculate Y positions with sequential placement
        # ===================================================================
        for depth in sorted(nodes_by_depth.keys()):
            node_indices = nodes_by_depth[depth]

            # Place nodes sequentially (all already scaled)
            current_y = vertical_margin
            for idx in node_indices:
                nodes[idx].y = current_y
                current_y += nodes[idx].height + gap_normalized

        # ===================================================================
        # STEP 5: Apply GLOBAL scale to ALL links
        # ===================================================================
        for link in links:
            link.value = link.value * global_scale

        # ===================================================================
        # STEP 6: Calculate link offsets (using globally scaled values)
        # ===================================================================
        source_offsets = {}  # source_id -> current offset
        for link in links:
            if link.source_id not in source_offsets:
                source_offsets[link.source_id] = 0.0
            link.y_source_offset = source_offsets[link.source_id]
            source_offsets[link.source_id] += link.value

        return SankeyData(nodes=nodes, links=links)

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

        if len(shadow_nodes) == 0:
            return SankeyData(nodes=[], links=[]), SankeyData(nodes=[], links=[])

        # ===================================================================
        # POSITIONING: Use SHADOW dimensions (full potential)
        # ===================================================================
        num_depths = max_depth[0] + 1
        for depth, node_indices in nodes_by_depth.items():
            x_pos = depth / (num_depths - 1) if num_depths > 1 else 0.5
            for idx in node_indices:
                shadow_nodes[idx].x = x_pos
                filled_nodes[idx].x = x_pos

        # Calculate global scale based on SHADOW heights
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

        # Apply global scale to ALL nodes and links
        for i in range(len(shadow_nodes)):
            shadow_nodes[i].height *= global_scale
            filled_nodes[i].height *= global_scale

        for link in shadow_links:
            link.value *= global_scale
        for link in filled_links:
            link.value *= global_scale

        # Calculate Y positions (IDENTICAL for both layers - centered alignment)
        for depth in sorted(nodes_by_depth.keys()):
            node_indices = nodes_by_depth[depth]
            current_y = vertical_margin
            
            for idx in node_indices:
                # SHADOW Y position
                shadow_nodes[idx].y = current_y
                
                # FILLED Y position - centered within shadow
                shadow_height = shadow_nodes[idx].height
                filled_height = filled_nodes[idx].height
                y_offset = (shadow_height - filled_height) / 2.0
                filled_nodes[idx].y = current_y + y_offset
                
                current_y += shadow_height + gap_normalized

        # Calculate link offsets for SHADOW
        source_offsets = {}
        for link in shadow_links:
            if link.source_id not in source_offsets:
                source_offsets[link.source_id] = 0.0
            link.y_source_offset = source_offsets[link.source_id]
            source_offsets[link.source_id] += link.value

        # Calculate link offsets for FILLED
        source_offsets = {}
        for link in filled_links:
            if link.source_id not in source_offsets:
                source_offsets[link.source_id] = 0.0
            link.y_source_offset = source_offsets[link.source_id]
            source_offsets[link.source_id] += link.value

        return (
            SankeyData(nodes=shadow_nodes, links=shadow_links),
            SankeyData(nodes=filled_nodes, links=filled_links)
        )

    
    def generate_scenario_sankey(self, root_item, scenario_scores, style_opts=None):
        """
        Generate dual-layer Sankey: Shadow (potential) + Filled (achievement).
        
        Shadow layer: Full structure in muted colors (background)
        Filled layer: Satisfaction-proportional bars centered within shadow (foreground)
        
        Used exclusively by Scenario tabs.
        """
        from PyQt6.QtCore import Qt
        import plotly.graph_objects as go
        
        s = style_opts or {}
        scores = scenario_scores or {}
        
        # Style options
        shadow_node_color = s.get('shadow_node_color', '#E0E0E0')
        shadow_link_color = s.get('shadow_link_color', 'rgba(200,200,200,0.3)')
        filled_node_color = s.get('node_color', '#27ae60')
        filled_link_color = s.get('link_color', 'rgba(39,174,96,0.6)')
        show_node_weight = s.get('show_node_weight', True)
        
        # Data structures for BOTH layers
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
        
        # Helper: Get local weight from tree widget
        def get_local_weight(item):
            try:
                return float(item.text(1).replace('%', '')) / 100.0
            except:
                return 0.0
        
        # Helper: Build formatted label
        def build_label(name, weight_pct):
            if show_node_weight and weight_pct is not None:
                return f"{name} ({weight_pct:.1f}%)"
            return name
        
        # Phase 1: Traverse tree and build node data
        def traverse(item, parent_idx=None, parent_absolute_weight=1.0, depth=0):
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
                
                # Store satisfaction score
                satisfaction = scores.get(uid, 0.0)
                node_satisfaction[idx] = satisfaction
            
            current_idx = uid_to_idx[label]
            
            if parent_idx is not None:
                source.append(parent_idx)
                target.append(current_idx)
                shadow_values.append(absolute_weight)
                
                # Filled link value: scaled by child's satisfaction
                child_satisfaction = node_satisfaction.get(current_idx, 0.0)
                filled_link_value = absolute_weight * child_satisfaction
                filled_values.append(max(filled_link_value, 0.0001) if filled_link_value > 0 else 0.0001)
            
            for i in range(item.childCount()):
                traverse(item.child(i), current_idx, absolute_weight, depth + 1)
        
        # Build root node first
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
        
        # Validate data
        total_nodes = len(labels)
        if total_nodes == 0 or not source:
            return go.Figure()
        
        # Phase 2: Calculate positions (based on SHADOW values)
        node_x = [0.0] * total_nodes
        shadow_node_y = [0.0] * total_nodes
        
        # X positions based on depth
        num_depths = max_depth[0] + 1
        for depth, node_indices in nodes_by_depth.items():
            x_pos = depth / (num_depths - 1) if num_depths > 1 else 0.5
            for idx in node_indices:
                node_x[idx] = x_pos
        
        # Y positions with unified scaling
        vertical_fill = s.get('vertical_fill', 0.95)
        vertical_margin = (1.0 - vertical_fill) / 2.0
        available_height = 1.0 - (2 * vertical_margin)
        gap = 0.02
        
        # Calculate max overflow ratio
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
        
        # Calculate Y positions
        for depth, node_indices in nodes_by_depth.items():
            num_nodes = len(node_indices)
            
            if num_nodes == 1:
                shadow_node_y[node_indices[0]] = 0.5
            else:
                # Calculate total value at this depth
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
        
        # Phase 3: FILLED Y positions - IDENTICAL to shadow (centered alignment)
        filled_node_y = shadow_node_y.copy()
        
        # Phase 4: Create Shadow Sankey trace
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
            link=dict(
                source=source,
                target=target,
                value=shadow_values,
                color=shadow_link_color
            )
        )
        
        # Phase 5: Create Filled Sankey trace
        filled_node_colors = [filled_node_color] * total_nodes
        
        filled_trace = go.Sankey(
            arrangement='fixed',
            node=dict(
                pad=s.get('pad', 15),
                thickness=s.get('thickness', 20),
                line=dict(
                    color=s.get('node_line_color', 'black'),
                    width=s.get('node_line_width', 0.5)
                ),
                label=labels,
                color=filled_node_colors,
                x=node_x,
                y=filled_node_y
            ),
            link=dict(
                source=source,
                target=target,
                value=filled_values,
                color=filled_link_color
            )
        )
        
        # Phase 6: Create figure with both traces
        fig = go.Figure(data=[shadow_trace, filled_trace])
        
        # Layout
        title_text = ""
        if s.get('show_title', False):
            title_text = s.get('title_text', '')
        
        bg_color = s.get('background_color', '#ffffff')
        plot_bg = 'rgba(0,0,0,0)' if s.get('transparent_bg', False) else bg_color
        paper_bg = 'rgba(0,0,0,0)' if s.get('transparent_bg', False) else bg_color
        
        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(
                    size=s.get('title_font_size', 20),
                    family=s.get('title_font_family', 'Arial'),
                    color=s.get('title_color', '#000000')
                ),
                x=0.5,
                xanchor='center'
            ),
            font=dict(
                size=s.get('label_font_size', 12),
                family=s.get('label_font_family', 'Arial'),
                color=s.get('label_font_color', '#000000')
            ),
            autosize=True,
            margin=dict(l=10, r=10, t=60, b=10),
            plot_bgcolor=plot_bg,
            paper_bgcolor=paper_bg
        )
        
        return fig


    def calculate_tree_scores_from_tree_item(self, root_item, input_values):
        """Calculate scores from QTreeWidgetItem (GUI compatibility)"""
        from PyQt6.QtCore import Qt
        
        scores = {}
        def process(item):
            uid = item.data(0, Qt.ItemDataRole.UserRole)
            if item.text(2) == "Indicator":
                f_data = item.data(1, Qt.ItemDataRole.UserRole) or {}
                x0, x1 = f_data.get('xmin', 0), f_data.get('xmax', 100)
                C, K, P = f_data.get('c', 100), f_data.get('k', 0.1), f_data.get('p', 1.0)
                val = input_values.get(uid, x0)
                sat = self.calculate_mives_value(val, x0, x1, C, K, P)
                scores[uid] = sat
                return sat
            else:
                total_score, total_weight = 0.0, 0.0
                for i in range(item.childCount()):
                    child = item.child(i)
                    try: w = float(child.text(1).replace('%',''))/100.0
                    except: w = 0.0
                    total_score += process(child) * w
                    total_weight += w
                final = total_score / total_weight if total_weight > 0 else 0
                scores[uid] = final
                return final
        if root_item: process(root_item)
        return scores
        
    def calculate_absolute_weight_from_item(self, item):
        """
        Calculate absolute weight by multiplying all parent weights from root to indicator.
        Returns a float between 0 and 1 representing the indicator's total weight in the final index.
        """
        weights = []
        current = item
        
        # Traverse up the tree collecting weights
        while current:
            try:
                weight = float(current.text(1).replace('%', '')) / 100.0
                weights.append(weight)
            except (ValueError, AttributeError):
                weights.append(1.0)
            current = current.parent()
        
        # Multiply all weights (excluding root which is always 100%)
        absolute_weight = 1.0
        for w in weights[:-1]:  # Exclude root
            absolute_weight *= w
        
        return absolute_weight
