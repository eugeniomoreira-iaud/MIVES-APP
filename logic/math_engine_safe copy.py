"""
MIVES Mathematical Engine
Implements exponential value functions per Boix-Cots et al. (2022)
"""
import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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

    def generate_matrix_chart(self, indicators_data):
        """Generate matrix of indicator curves"""
        n = len(indicators_data)
        if n == 0: return go.Figure()
        cols = 3
        rows = (n // cols) + (1 if n % cols > 0 else 0)
        fig = make_subplots(rows=rows, cols=cols, subplot_titles=[d['name'] for d in indicators_data])
        
        for i, d in enumerate(indicators_data):
            r, c_idx = (i // cols) + 1, (i % cols) + 1
            x0, x1 = d['xmin'], d['xmax']
            margin = abs(x1 - x0) * 0.1
            if margin == 0: margin = 1
            plot_min, plot_max = min(x0, x1) - margin, max(x0, x1) + margin
            
            x_vals = np.linspace(plot_min, plot_max, 50)
            y_vals = [self.calculate_mives_value(v, x0, x1, d['c'], d['k'], d['p']) for v in x_vals]
            
            fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', line=dict(color='#95a5a6', width=2)), row=r, col=c_idx)
            if 'actual' in d:
                sat = self.calculate_mives_value(d['actual'], x0, x1, d['c'], d['k'], d['p'])
                fig.add_trace(go.Scatter(x=[d['actual']], y=[sat], mode='markers', marker=dict(color='red', size=8)), row=r, col=c_idx)
                
        fig.update_layout(height=rows*200, showlegend=False, template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))
        return fig

#############################

    def generate_sankey_from_tree_item(self, root_item, style_opts=None, scenario_scores=None):
        """
        Generate Sankey with forced node ordering and proportional spacing.
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
        chart_width = s.get('chart_width', 1200)
        chart_height = int(chart_width * s.get('chart_height_ratio', 0.6))
        
        # Track nodes by depth for positioning
        nodes_by_depth = {}
        max_depth = [0]
        
        # Helper: Get local weight from tree widget
        def get_local_weight(item):
            try:
                return float(item.text(1).replace('%', '')) / 100.0
            except:
                return 0.0
        
        # Traverse tree and build Sankey data
        def traverse(item, parent_idx=None, parent_absolute_weight=1.0, depth=0):
            if not item:
                return
            
            uid = item.data(0, Qt.ItemDataRole.UserRole)
            if not uid:
                return
            
            label = item.text(0)
            local_weight = get_local_weight(item)
            absolute_weight = parent_absolute_weight * local_weight
            
            if absolute_weight < 0.001:
                absolute_weight = 0.001
            
            if depth > max_depth[0]:
                max_depth[0] = depth
            
            if label not in uid_to_idx:
                idx = len(labels)
                uid_to_idx[label] = idx
                labels.append(label)
                
                if depth not in nodes_by_depth:
                    nodes_by_depth[depth] = []
                nodes_by_depth[depth].append(idx)
                
                if scenario_scores and uid in scenario_scores:
                    score = scenario_scores[uid]
                    r = int(255 * (1 - score))
                    g = int(255 * score)
                    node_colors.append(f'rgb({r},{g},50)')
                else:
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
            label = root_item.text(0)
            
            if uid and label:
                idx = len(labels)
                uid_to_idx[label] = idx
                labels.append(label)
                nodes_by_depth[0] = [idx]
                
                if scenario_scores and uid in scenario_scores:
                    score = scenario_scores[uid]
                    r = int(255 * (1 - score))
                    g = int(255 * score)
                    node_colors.append(f'rgb({r},{g},50)')
                else:
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
        
        # Assign Y positions with spacing that accounts for bar heights
        vertical_margin = 0.05
        available_height = 1.0 - (2 * vertical_margin)

        for depth, node_indices in nodes_by_depth.items():
            num_nodes = len(node_indices)
            
            if num_nodes == 1:
                node_y[node_indices[0]] = 0.5
            else:
                total_value_at_depth = sum(values[i] for i, (s, t) in enumerate(zip(source, target)) 
                                           if t in node_indices or (depth == 0 and node_indices[0] == 0))
                
                if depth == 0:
                    total_value_at_depth = 1.0
                
                if depth > 0 and total_value_at_depth == 0:
                    for idx in node_indices:
                        for i, t in enumerate(target):
                            if t == idx:
                                total_value_at_depth += values[i]
                
                if total_value_at_depth > 0:
                    # Calculate gap space needed
                    num_gaps = num_nodes - 1
                    gap_size = 0.02  # 2% per gap
                    total_gap_space = num_gaps * gap_size if num_gaps > 0 else 0
                    
                    # Remaining space for actual node bars
                    space_for_nodes = available_height - total_gap_space
                    
                    # Ensure we have positive space
                    if space_for_nodes < 0.1:
                        space_for_nodes = available_height * 0.8
                        gap_size = (available_height - space_for_nodes) / max(num_gaps, 1)
                    
                    y_cursor = vertical_margin
                    
                    for idx in node_indices:
                        node_value = 0
                        
                        if depth == 0:
                            node_value = 1.0
                        else:
                            for i, t in enumerate(target):
                                if t == idx:
                                    node_value += values[i]
                        
                        # Proportional height within the available space for nodes
                        node_height = (node_value / total_value_at_depth) * space_for_nodes
                        
                        # Position at center of this node's space
                        node_y[idx] = y_cursor + (node_height / 2.0)
                        
                        # Move cursor down (bar height + gap)
                        y_cursor += node_height + gap_size
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
                    family=s.get('title_font_family', 'Arial')
                ),
                x=0.5,
                xanchor='center'
            ),
            font=dict(
                size=s.get('font_size', 12), 
                family=s.get('font_family', 'Arial'),
                color=s.get('font_color', '#000000')
            ),
            autosize=True,
            margin=dict(l=10, r=10, t=60, b=10),
            plot_bgcolor=plot_bg,
            paper_bgcolor=paper_bg
        )
        
        return fig

#############################

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
