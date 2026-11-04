# -*- coding: utf-8 -*-
"""Sort Group Layers - QGIS plugin (QGIS 3.x and 4.x)."""


def classFactory(iface):
    from .plugin import SortGroupLayersPlugin
    return SortGroupLayersPlugin(iface)
