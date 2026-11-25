"""
Widgets of the edit mode: the cycle palette (drag source), the grid canvas (drop target) and the
dialog for a new supercycle.
"""
from typing import Callable, Optional

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.qt_compat import QtCore, QtWidgets

from supercycles.gui.common import Qt, colour_icon


class CyclePalette(QtWidgets.QListWidget):
    """Cycle types of one machine. Dragging an item carries its key (e.g. 'SPS.SFTPRO') as text."""

    def __init__(self, catalogue, machine: str):
        super().__init__()
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.DragOnly)
        self.set_catalogue(catalogue, machine)

    def set_catalogue(self, catalogue, machine: str) -> None:
        self.clear()
        for cycle in catalogue.cycles_of(machine):
            item = QtWidgets.QListWidgetItem(colour_icon(cycle.colour), f'{cycle.id}  ({cycle.length_bp} BP)')
            item.setData(Qt.ItemDataRole.UserRole, cycle.key)
            injections = ', '.join(f'{i.cycle} @ {i.bp_offset:+d}' for i in cycle.injections) or 'none'
            beam = f'{cycle.beam.destination}' if cycle.beam else 'no beam (feeds the next machine)'
            item.setToolTip(f'{cycle.key}: {cycle.length_bp} BP, beam: {beam}\ninjections: {injections}')
            self.addItem(item)

    def mimeTypes(self):
        return ['text/plain']

    def mimeData(self, items):
        data = QtCore.QMimeData()
        data.setText(items[0].data(Qt.ItemDataRole.UserRole))
        return data


class GridCanvas(FigureCanvasQTAgg):
    """Figure canvas that accepts cycles dropped from a CyclePalette (only when drop_callback is set)."""

    def __init__(self, figure):
        super().__init__(figure)
        self.setAcceptDrops(True)
        self.drop_callback: Optional[Callable] = None    # f(cycle_key, x_display, y_display)

    def dragEnterEvent(self, event):
        if self.drop_callback and event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if self.drop_callback and event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        position = event.position() if hasattr(event, 'position') else event.pos()
        x, y = self.mouseEventCoords(position)            # matplotlib display coordinates
        event.acceptProposedAction()
        self.drop_callback(event.mimeData().text(), x, y)


class NewSupercycleDialog(QtWidgets.QDialog):
    """Name, period and share of a new supercycle; empty or a copy of any open supercycle."""

    def __init__(self, parent, templates: dict, max_length_s: float, basic_period_s: float):
        super().__init__(parent)
        self.setWindowTitle('New supercycle')
        self.templates = templates                      # label -> Supercycle
        self.name = QtWidgets.QLineEdit('New supercycle')
        self.template = QtWidgets.QComboBox()
        self.template.addItems(['(empty)'] + list(templates))
        self.period = QtWidgets.QSpinBox()
        self.period.setRange(1, 500)
        self.period.setValue(int(max_length_s // basic_period_s // 2))
        self.period_label = QtWidgets.QLabel()
        self.share = QtWidgets.QDoubleSpinBox()
        self.share.setRange(0, 100)
        self.share.setDecimals(3)
        self.share.setSuffix(' %')
        self.basic_period_s, self.max_length_s = basic_period_s, max_length_s

        form = QtWidgets.QFormLayout(self)
        form.addRow('Name:', self.name)
        form.addRow('Start from:', self.template)
        form.addRow('Period [BP]:', self.period)
        form.addRow('', self.period_label)
        form.addRow('Share of the run:', self.share)
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok
                                             | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self.period.valueChanged.connect(self._update_period_label)
        self.template.currentTextChanged.connect(self._template_changed)
        self._update_period_label()

    def _update_period_label(self):
        length = self.period.value() * self.basic_period_s
        limit = '' if length <= self.max_length_s else f'  – longer than the {self.max_length_s:g} s limit!'
        self.period_label.setText(f'= {length:.1f} s{limit}')

    def _template_changed(self, label):
        template = self.templates.get(label)
        self.period.setEnabled(template is None)
        if template is not None:
            self.period.setValue(template.period_bp)
            self.name.setText(template.name)
