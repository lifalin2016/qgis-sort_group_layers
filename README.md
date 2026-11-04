# Sort Group Layers

Keep your Layers panel tidy with one click. **Sort Group Layers** adds a *Sort group layers ...* entry to the right-click menu of layer groups, and sorts the layers inside by geometry type and/or name.

Works with QGIS 3 and QGIS 4.

## Installation

1. In QGIS, open **Plugins → Manage and Install Plugins → Install from ZIP**.
2. Select `sort_group_layers.zip` and click **Install Plugin**.
3. Make sure **Sort Group Layers** is ticked in the *Installed* list.

## How to use

1. In the Layers panel, right-click a layer group.
   *To sort several groups in one go, select them first (hold Ctrl or Shift), then right-click one of them.*
2. Choose **Sort group layers ...**.
3. Pick your options and click **OK**.

## Options

| Option | Default | What it does |
|---|---|---|
| Sort layers by topology | On | Points first, then lines, then polygons |
| Sort layers by layer name | On | Alphabetical, ignoring upper/lower case. Numbers sort naturally (`Layer 2` comes before `Layer 10`) |
| Perform sorting recursively in any sub group | Off | Also sorts the layers inside all sub groups |
| Place sub groups | At the top | Puts sub groups **at the top** or **at the bottom** of the group, sorted alphabetically |

## Example

Before:

```
Roads
Buildings
Water points
Municipalities
Aerial photo
Archive   (sub group)
Bus stops
```

After sorting with the default options:

```
Archive   (sub group)
Bus stops
Water points
Roads
Buildings
Municipalities
Aerial photo
```

Point layers come first, then lines, then polygons, then anything else such as tables and rasters. Layers of the same type are sorted by name.

## Good to know

- **Sort order with topology on:** points, lines, polygons, other vector layers and tables, rasters and other non-vector layers, and finally layers with a broken data source.
- **Only sub groups:** if you turn off both layer options, layers stay as they are and only the sub groups are moved and sorted.
- **Your layers are safe:** visibility, styling and layer settings are kept, and no layers are removed from the project.
- **No undo:** QGIS can't undo changes to the Layers panel, so save your project first if you want to be able to go back.
- **Menu entry missing?** It only shows up when you right-click a *group*, not a single layer.

## Changelog

- **1.0.1** – Added the *Place sub groups* option (top or bottom, sorted alphabetically). OK is no longer disabled when both layer options are off.
- **1.0.0** – First release.
