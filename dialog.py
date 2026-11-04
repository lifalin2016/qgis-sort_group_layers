# -*- coding: utf-8 -*-
from qgis.PyQt.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QVBoxLayout,
)


class SortGroupLayersDialog(QDialog):
    """Options dialog for sorting layers in one or more groups."""

    def __init__(self, group_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sort group layers")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        if len(group_names) == 1:
            info = "Group: <b>{}</b>".format(self._esc(group_names[0]))
        else:
            shown = ", ".join(self._esc(n) for n in group_names[:6])
            if len(group_names) > 6:
                shown += ", ... (+{})".format(len(group_names) - 6)
            info = "{} groups: <b>{}</b>".format(len(group_names), shown)
        label = QLabel(info)
        label.setWordWrap(True)
        layout.addWidget(label)

        self.chk_topology = QCheckBox(
            "Sort layers by topology (points before lines before polygons)")
        self.chk_topology.setChecked(True)
        layout.addWidget(self.chk_topology)

        self.chk_name = QCheckBox("Sort layers by layer name")
        self.chk_name.setChecked(True)
        layout.addWidget(self.chk_name)

        self.chk_recursive = QCheckBox(
            "Perform sorting recursively in any sub group")
        self.chk_recursive.setChecked(False)
        layout.addWidget(self.chk_recursive)

        row = QHBoxLayout()
        row.addWidget(QLabel("Place sub groups:"))
        self.cmb_subgroups = QComboBox()
        self.cmb_subgroups.addItem("At the top", "top")
        self.cmb_subgroups.addItem("At the bottom", "bottom")
        self.cmb_subgroups.setCurrentIndex(0)
        row.addWidget(self.cmb_subgroups)
        row.addStretch(1)
        layout.addLayout(row)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    @staticmethod
    def _esc(text):
        return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;"))

    def options(self):
        return {
            "topology": self.chk_topology.isChecked(),
            "name": self.chk_name.isChecked(),
            "recursive": self.chk_recursive.isChecked(),
            "subgroups_top": self.cmb_subgroups.currentData() == "top",
        }
