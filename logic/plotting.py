"""Plotting helpers for MIVES-APP.

Centralized, consistent plotting helpers. All Plotly imports are done
inside the functions so the plotting module may be imported safely in
environments that do not have Plotly available until plotting is required.
"""
from typing import Any, Dict, List, Optional

import numpy as np


def generate_single_curve(mives_logic: Any,
                          name: str,
                          x_sat_0: float,
                          x_sat_1: float,
                          units: str,
                          C: float,
                          K: float,
                          P: float,
                          style_opts: Optional[Dict[str, Any]] = None,
                          actual_val: Optional[float] = None) -> Any:
    """Generate a Plotly figure for a single MIVES value function.

    The function accepts a `mives_logic` instance that exposes
    `calculate_mives_value(x, x_sat_0, x_sat_1, C, K, P)` so tests can supply
    a lightweight stub if needed. Parameters and ordering match the caller in
    `logic/math_engine.py`.
    """
    try:
        from plotly import graph_objects as go  # type: ignore
    except Exception:
        raise

    s = style_opts or {}

    try:
        margin = abs(x_sat_1 - x_sat_0) * 0.1
        if margin == 0:
            margin = 1.0
        x_min_plot = min(x_sat_0, x_sat_1) - margin
        x_max_plot = max(x_sat_0, x_sat_1) + margin
        # Reduce to 100 points for better performance (was 150)
        # Visual quality is nearly identical with fewer points
        x_vals = np.linspace(x_min_plot, x_max_plot, 100)
        y_vals = [mives_logic.calculate_mives_value(float(v), x_sat_0, x_sat_1, C, K, P) for v in x_vals]
    except Exception:
        x_vals, y_vals = [], []

    fig = go.Figure()

    fill_arg = 'tozeroy' if s.get('fill', False) else 'none'
    fig.add_trace(go.Scatter(
        x=x_vals, y=y_vals, mode='lines', fill=fill_arg, name='Value Function',
        line=dict(color=s.get('color', '#2980b9'), width=s.get('width', 3), dash=s.get('dash', 'solid'))
    ))

    if actual_val is not None:
        sat = mives_logic.calculate_mives_value(actual_val, x_sat_0, x_sat_1, C, K, P)
        fig.add_trace(go.Scatter(x=[actual_val], y=[sat], mode='markers', marker=dict(color='red', size=14, line=dict(width=2, color='white')), name='Actual'))

    direction = "Increasing" if x_sat_1 > x_sat_0 else "Decreasing"

    font_family = s.get('font_family', 'Arial')
    font_size_title = s.get('font_size_title', 16)
    font_size_axes = s.get('font_size_axes', 12)
    axis_line_width = s.get('axis_line_width', 2)
    axis_line_color = s.get('axis_line_color', '#333333')
    show_axis_top = s.get('show_axis_top', True)
    show_axis_bottom = s.get('show_axis_bottom', True)
    show_axis_left = s.get('show_axis_left', True)
    show_axis_right = s.get('show_axis_right', True)
    grid_show = s.get('grid', True)
    grid_line_width = s.get('grid_line_width', 1)
    grid_line_color = s.get('grid_line_color', '#e0e0e0')
    grid_line_dash = s.get('grid_line_dash', 'solid')
    background_color = s.get('background_color', '#ffffff')

    if font_size_title <= 16:
        top_margin = 90
    else:
        extra_space = (font_size_title - 16) * 2.5
        top_margin = int(90 + extra_space)

    fig.update_layout(
        title=dict(text=f"<b>{name}</b><br><sub>{direction} | P={P}, K={K}, C={C}</sub>", x=0.01, y=0.96, xanchor='left', yanchor='top', font=dict(family=font_family, size=font_size_title)),
        xaxis_title=dict(text=units, font=dict(family=font_family, size=font_size_axes)),
        yaxis_title=dict(text="Value (0-1)", font=dict(family=font_family, size=font_size_axes)),
        margin=dict(l=60, r=20, t=top_margin, b=50), autosize=True, showlegend=False, plot_bgcolor=background_color, paper_bgcolor=background_color,
        font=dict(family=font_family, size=font_size_axes),
        xaxis=dict(showgrid=grid_show, gridcolor=grid_line_color, gridwidth=grid_line_width, griddash=grid_line_dash, linewidth=axis_line_width, linecolor=axis_line_color, mirror=True if (show_axis_top and show_axis_bottom) else False, showline=show_axis_bottom, ticks='outside' if show_axis_bottom else ''),
        yaxis=dict(showgrid=grid_show, gridcolor=grid_line_color, gridwidth=grid_line_width, griddash=grid_line_dash, linewidth=axis_line_width, linecolor=axis_line_color, mirror=True if (show_axis_left and show_axis_right) else False, showline=show_axis_left, ticks='outside' if show_axis_left else '', range=[-0.05, 1.05])
    )

    shapes = []
    if show_axis_top and not (show_axis_top and show_axis_bottom):
        shapes.append(dict(type='line', xref='paper', yref='paper', x0=0, y0=1, x1=1, y1=1, line=dict(color=axis_line_color, width=axis_line_width)))
    if show_axis_right and not (show_axis_left and show_axis_right):
        shapes.append(dict(type='line', xref='paper', yref='paper', x0=1, y0=0, x1=1, y1=1, line=dict(color=axis_line_color, width=axis_line_width)))

    if shapes:
        fig.update_layout(shapes=shapes)
    return fig


def generate_matrix_chart(mives_logic: Any, indicators_data: List[Dict[str, Any]], style_opts: Optional[Dict[str, Any]] = None) -> Any:
    """Generate a grid of indicator curves as a Plotly Figure.

    The function mirrors previous behavior but centralizes plotting code.
    """
    try:
        from plotly.subplots import make_subplots  # type: ignore
        from plotly import graph_objects as go  # type: ignore
    except Exception:
        raise

    n = len(indicators_data)
    if n == 0:
        return go.Figure()

    s = style_opts or {}
    cols = 3
    rows = (n // cols) + (1 if n % cols > 0 else 0)
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=[d.get('name', '') for d in indicators_data])

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
        y_vals = [mives_logic.calculate_mives_value(v, x0, x1, d['c'], d['k'], d['p']) for v in x_vals]

        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', line=dict(color=curve_color, width=curve_width, dash=curve_dash)), row=r, col=c_idx)

        if 'actual' in d:
            sat = mives_logic.calculate_mives_value(d['actual'], x0, x1, d['c'], d['k'], d['p'])
            fig.add_trace(go.Scatter(x=[d['actual']], y=[sat], mode='markers', marker=dict(color='red', size=8)), row=r, col=c_idx)

    # Styling
    font_family = s.get('font_family', 'Arial')
    font_size_title = s.get('font_size_title', 16)
    font_size_axes = s.get('font_size_axes', 12)
    axis_line_width = s.get('axis_line_width', 2)
    axis_line_color = s.get('axis_line_color', '#333333')
    show_axis_top = s.get('show_axis_top', True)
    show_axis_bottom = s.get('show_axis_bottom', True)
    show_axis_left = s.get('show_axis_left', True)
    show_axis_right = s.get('show_axis_right', True)
    grid_show = s.get('grid', True)
    grid_line_width = s.get('grid_line_width', 1)
    grid_line_color = s.get('grid_line_color', '#e0e0e0')
    grid_line_dash = s.get('grid_line_dash', 'solid')
    background_color = s.get('background_color', '#ffffff')

    fig.update_xaxes(showgrid=grid_show, gridcolor=grid_line_color, gridwidth=grid_line_width, griddash=grid_line_dash, linewidth=axis_line_width, linecolor=axis_line_color, mirror=True if (show_axis_top and show_axis_bottom) else False, showline=show_axis_bottom, ticks='outside' if show_axis_bottom else '')
    fig.update_yaxes(showgrid=grid_show, gridcolor=grid_line_color, gridwidth=grid_line_width, griddash=grid_line_dash, linewidth=axis_line_width, linecolor=axis_line_color, mirror=True if (show_axis_left and show_axis_right) else False, showline=show_axis_left, ticks='outside' if show_axis_left else '', range=[-0.05, 1.05])

    fig.update_layout(height=rows * 200, showlegend=False, plot_bgcolor=background_color, paper_bgcolor=background_color, font=dict(family=font_family, size=font_size_axes), margin=dict(l=40, r=20, t=60, b=20))
    fig.update_annotations(font=dict(family=font_family, size=font_size_title))
    return fig
