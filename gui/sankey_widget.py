"""Adapter Sankey widget that delegates to `gui.widgets.native_sankey.NativeSankeyWidget`.

This keeps a single canonical rendering implementation in `native_sankey.py`
while preserving the original `SankeyWidget` API used across the codebase.
"""
from typing import Any, Optional, Dict

from PyQt6.QtWidgets import QWidget, QVBoxLayout


class SankeyWidget(QWidget):
    """Adapter around `NativeSankeyWidget`.

    The original `SankeyWidget` used a dict-based data model; the
    adapter accepts either that dict format or `gui.widgets.native_sankey.SankeyData`.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Lazy import native widget to avoid top-level dependency during tests
        from gui.widgets.native_sankey import NativeSankeyWidget

        self._native = NativeSankeyWidget(parent=self)
        layout.addWidget(self._native)

    def set_data(self, data: Any):
        """Accept either a dict (legacy) or a `SankeyData` instance.

        If a dict is provided, convert to `NodeData`/`LinkData`/`SankeyData`.
        """
        # Lazy imports
        from gui.widgets import native_sankey as native_mod

        if data is None:
            return

        # If already SankeyData, pass through
        if isinstance(data, native_mod.SankeyData):
            self._native.render_sankey(data, style_opts=getattr(data, 'style', None) or {})
            return

        # Convert legacy dict format -> SankeyData
        nodes = []
        links = []

        legacy_nodes = data.get('nodes', [])
        legacy_links = data.get('links', [])
        style = data.get('style', {})

        # Map indices to generated ids
        for i, n in enumerate(legacy_nodes):
            node_id = n.get('id', str(i))
            nd = native_mod.NodeData(id=node_id, label=n.get('label', ''), x=float(n.get('x', 0.0)), y=float(n.get('y', 0.0)), height=float(n.get('height', 0.0)), color=n.get('color', '#cccccc'))
            nodes.append(nd)

        for l in legacy_links:
            src = str(l.get('source'))
            tgt = str(l.get('target'))
            ld = native_mod.LinkData(source_id=src, target_id=tgt, value=float(l.get('value', 0.0)), y_source_offset=float(l.get('y_source_offset', 0.0)), y_target_offset=float(l.get('y_target_offset', 0.0)), color=l.get('color', '#999999'))
            links.append(ld)

        sankey_data = native_mod.SankeyData(nodes=nodes, links=links)
        self._native.render_sankey(sankey_data, style_opts=style)

    def render_dual(self, shadow_data: Any, filled_data: Any, style_opts: Optional[Dict[str, Any]] = None):
        """Render a dual-layer Sankey (shadow + filled). Accepts either SankeyData or legacy dicts."""
        from gui.widgets import native_sankey as native_mod

        def ensure_sankey(obj):
            if isinstance(obj, native_mod.SankeyData):
                return obj
            # assume dict
            nodes = []
            links = []
            for i, n in enumerate(obj.get('nodes', [])):
                nodes.append(native_mod.NodeData(id=n.get('id', str(i)), label=n.get('label', ''), x=float(n.get('x', 0.0)), y=float(n.get('y', 0.0)), height=float(n.get('height', 0.0)), color=n.get('color', '#cccccc')))
            for l in obj.get('links', []):
                links.append(native_mod.LinkData(source_id=str(l.get('source')), target_id=str(l.get('target')), value=float(l.get('value', 0.0)), y_source_offset=float(l.get('y_source_offset', 0.0)), y_target_offset=float(l.get('y_target_offset', 0.0)), color=l.get('color', '#999999')))
            return native_mod.SankeyData(nodes=nodes, links=links)

        s_shadow = ensure_sankey(shadow_data)
        s_filled = ensure_sankey(filled_data)
        self._native.render_sankey_dual(s_shadow, s_filled, style_opts=style_opts or {})

    def export_to_image(self, filepath: str):
        """Delegate image export to native widget."""
        self._native.export_image(filepath)
