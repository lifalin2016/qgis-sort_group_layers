# -*- coding: utf-8 -*-
import os
import re

from qgis.PyQt.QtCore import QEvent, QObject, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QApplication, QDialog, QMenu

try:  # Qt6: QAction lives in QtGui
    from qgis.PyQt.QtGui import QAction
except ImportError:  # Qt5: QAction lives in QtWidgets
    from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsLayerTree, QgsVectorLayer

from .dialog import SortGroupLayersDialog

ACTION_NAME = "sortGroupLayersAction"
MENU_TEXT = "Sort group layers ..."


# ---------------------------------------------------------------- sorting --

def _natural_key(text):
    """Case-insensitive natural sort key ('layer2' < 'layer10')."""
    return [int(t) if t.isdigit() else t.casefold()
            for t in re.split(r"(\d+)", text)]


def _topology_rank(layer_node):
    """Points (0) < lines (1) < polygons (2) < other vector / tables (3)
    < non-vector layers such as rasters (4) < broken layers (5)."""
    layer = layer_node.layer()
    if layer is None:
        return 5
    if not isinstance(layer, QgsVectorLayer):
        return 4
    geom_type = layer.geometryType()
    value = getattr(geom_type, "value", geom_type)  # enum differences 3.x/4.x
    try:
        value = int(value)
    except (TypeError, ValueError):
        return 3
    return value if value in (0, 1, 2) else 3


def _is_descendant(group, candidates):
    parent = group.parent()
    while parent is not None:
        if any(parent is c for c in candidates):
            return True
        parent = parent.parent()
    return False


def _depth(node):
    depth = 0
    parent = node.parent()
    while parent is not None:
        depth += 1
        parent = parent.parent()
    return depth


def sort_group(group, by_topology, by_name, recursive, subgroups_top):
    """Sort the children of *group*.

    Layers are sorted by topology and/or name. Sub groups are sorted
    alphabetically and placed above or below the layers."""
    children = list(group.children())
    layer_nodes = [c for c in children if QgsLayerTree.isLayer(c)]
    group_nodes = [c for c in children if QgsLayerTree.isGroup(c)]

    def layer_key(node):
        return (
            _topology_rank(node) if by_topology else 0,
            _natural_key(node.name()) if by_name else [],
        )

    sorted_layers = sorted(layer_nodes, key=layer_key)  # stable sort
    sorted_groups = sorted(group_nodes, key=lambda n: _natural_key(n.name()))

    if subgroups_top:
        desired = sorted_groups + sorted_layers
    else:
        desired = sorted_layers + sorted_groups

    if any(a is not b for a, b in zip(desired, children)):
        # 1) insert clones first so a layer is never absent from the tree
        #    (removing the last node of a layer could remove it from the project)
        for i, node in enumerate(desired):
            group.insertChildNode(i, node.clone())
        # 2) remove the originals
        for node in children:
            group.removeChildNode(node)

    if recursive:
        # re-read the children: sub groups may have been replaced by clones
        for child in list(group.children()):
            if QgsLayerTree.isGroup(child):
                sort_group(child, by_topology, by_name, True, subgroups_top)


# ------------------------------------------------------- context menu hook --

class _ContextMenuWatcher(QObject):
    """Notices right-clicks in the layer tree view and calls back once the
    context menu is open, so an action can be added to it.

    QGIS owns (and deletes) the layer tree menu provider, so wrapping it is
    not safe; this approach leaves QGIS' own menu untouched."""

    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self._callback = callback

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.ContextMenu:
            # The menu is created and exec()'d after this filter returns;
            # a 0 ms timer fires inside the menu's own event loop.
            QTimer.singleShot(0, self._callback)
        return False


class SortGroupLayersPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.icon = QIcon(os.path.join(self.plugin_dir, "icon.svg"))
        self.watcher = None
        self._watched = []

    # QGIS plugin API ------------------------------------------------------
    def initGui(self):
        view = self.iface.layerTreeView()
        self.watcher = _ContextMenuWatcher(self._on_context_menu)
        self._watched = [view, view.viewport()]
        for w in self._watched:
            w.installEventFilter(self.watcher)

    def unload(self):
        for w in self._watched:
            try:
                w.removeEventFilter(self.watcher)
            except RuntimeError:
                pass
        self._watched = []
        if self.watcher is not None:
            self.watcher.deleteLater()
            self.watcher = None

    # Menu injection -------------------------------------------------------
    def _selected_groups(self):
        groups = []
        for node in self.iface.layerTreeView().selectedNodes():
            if QgsLayerTree.isGroup(node) and not any(node is g for g in groups):
                groups.append(node)
        return groups

    def _on_context_menu(self, retry=True):
        menu = QApplication.activePopupWidget()
        if not isinstance(menu, QMenu):
            if retry:
                QTimer.singleShot(30, lambda: self._on_context_menu(False))
            return
        if not self._selected_groups():
            return
        if any(a.objectName() == ACTION_NAME for a in menu.actions()):
            return

        menu.addSeparator()
        action = QAction(self.icon, MENU_TEXT, menu)
        action.setObjectName(ACTION_NAME)
        # Defer so the dialog opens after the popup menu has fully closed
        action.triggered.connect(lambda *_: QTimer.singleShot(0, self.run))
        menu.addAction(action)

    # Main action ----------------------------------------------------------
    def run(self):
        groups = self._selected_groups()
        if not groups:
            return

        dlg = SortGroupLayersDialog([g.name() for g in groups],
                                    self.iface.mainWindow())
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        opts = dlg.options()
        if opts["recursive"]:
            # a selected group inside another selected group is covered
            # by the recursion of its ancestor
            groups = [g for g in groups if not _is_descendant(g, groups)]

        # Deepest groups first: sorting a parent re-creates its sub groups,
        # which would invalidate a selected sub group processed afterwards.
        groups.sort(key=_depth, reverse=True)

        for group in groups:
            sort_group(group, opts["topology"], opts["name"],
                       opts["recursive"], opts["subgroups_top"])

        self.iface.messageBar().pushSuccess(
            "Sort group layers",
            "Sorted layers in {} group{}.".format(
                len(groups), "" if len(groups) == 1 else "s"))
