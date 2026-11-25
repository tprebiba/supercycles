"""
Shared pieces of the GUI: constants, small table / dialog helpers, and OpenScenario (a scenario
open in the GUI, with its origin and its undo / redo history).
"""
import math
import os
from dataclasses import dataclass, field
from typing import Optional

from matplotlib.backends.qt_compat import QtCore, QtGui, QtWidgets
from matplotlib.colors import to_hex

from supercycles.schedule import Schedule

FIGURE_STYLE = {'font.size': 8}   # figures are embedded in panels: smaller fonts than default
# facilities shown as columns of the per-supercycle table (others are added after them)
FACILITY_ORDER = ['NorthArea', 'SHiP', 'LHC', 'AWAKE', 'HiRadMat', 'nTOF', 'EAST_T8', 'EAST_T9',
                  'EAST_TN', 'AD', 'ISOLDE', 'MD']
# repository root (contains the scenarios package): supercycles/gui/common.py -> 3 levels up
REPOSITORY = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAX_UNDO = 100                    # undo points kept per scenario
INCREASE_COLOUR, DECREASE_COLOUR = '#257de0', '#ec4647'   # comparison bars: B above / below A

Qt = QtCore.Qt
QMessageBox = QtWidgets.QMessageBox


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def format_value(value) -> str:
    """Readable text for a table cell: integers as such, otherwise ~4 significant digits."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return '–'
    if isinstance(value, str):
        return value
    if float(value).is_integer() and abs(value) < 1e6:
        return f'{int(value)}'
    if abs(value) >= 1e6 or abs(value) < 1e-2:
        return f'{value:.3e}'
    if abs(value) >= 100:
        return f'{value:.0f}'
    return f'{value:.4g}'


def make_table(selectable_rows=False) -> QtWidgets.QTableWidget:
    table = QtWidgets.QTableWidget()
    table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
    table.verticalHeader().setVisible(False)
    table.setAlternatingRowColors(True)
    if selectable_rows:
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
    return table


def fill_table(table: QtWidgets.QTableWidget, dataframe, headers=None) -> None:
    """Show a pandas DataFrame (index ignored) in a QTableWidget."""
    table.clear()
    table.setRowCount(len(dataframe))
    table.setColumnCount(len(dataframe.columns))
    table.setHorizontalHeaderLabels(headers or [str(c) for c in dataframe.columns])
    for row, values in enumerate(dataframe.itertuples(index=False)):
        for col, value in enumerate(values):
            item = QtWidgets.QTableWidgetItem(format_value(value))
            if not isinstance(value, str):
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, col, item)
    table.resizeColumnsToContents()


def titled(title: str, widget: QtWidgets.QWidget) -> QtWidgets.QGroupBox:
    box = QtWidgets.QGroupBox(title)
    layout = QtWidgets.QVBoxLayout(box)
    layout.addWidget(widget)
    return box


def colour_icon(colour: str) -> QtGui.QIcon:
    """Small square of a cycle colour, for the palette and the menus."""
    pixmap = QtGui.QPixmap(12, 12)
    pixmap.fill(QtGui.QColor(to_hex(colour)))
    return QtGui.QIcon(pixmap)


def ask(parent, title: str, text: str, buttons: list) -> Optional[str]:
    """Question with custom buttons (+ Cancel). Returns the text of the button clicked, or None."""
    box = QMessageBox(parent)
    box.setWindowTitle(title)
    box.setText(text)
    box.setIcon(QMessageBox.Icon.Question)
    for label in buttons:
        box.addButton(label, QMessageBox.ButtonRole.AcceptRole)
    cancel = box.addButton(QMessageBox.StandardButton.Cancel)
    box.exec()
    clicked = box.clickedButton()
    return None if clicked is cancel or clicked is None else clicked.text()


def describe(placements) -> str:
    """'SPS.deGauss at BP 10, PS.ZERO at BP 9' (for messages)."""
    return ', '.join(f'{p.cycle.key} at BP {p.start_bp}' for p in placements)


# ---------------------------------------------------------------------------
# An open scenario, with its origin and its edit history
# ---------------------------------------------------------------------------
@dataclass
class OpenScenario:
    schedule: Schedule
    source: str                       # 'module' (scenarios package), 'file' (YAML) or 'new'
    module: object = None             # scenarios package module, for source == 'module'
    path: Optional[str] = None        # YAML file, for source == 'file'
    dirty: bool = False               # changed since loaded / saved
    undo: list = field(default_factory=list)   # [(label, Schedule before the edit)]
    redo: list = field(default_factory=list)

    def saved_version(self) -> Optional[Schedule]:
        """The scenario as on disk (None for a new, never saved one)."""
        if self.source == 'module':
            return Schedule.from_scenario(self.module)
        if self.source == 'file':
            return Schedule.load(self.path)
        return None

