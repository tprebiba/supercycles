"""
Compare window (Tools > Compare scenarios): two open scenarios side by side, B compared to A.
All numbers come from supercycles.schedule.compare_schedules.
"""
from typing import TYPE_CHECKING

import matplotlib
import numpy as np

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.figure import Figure

from supercycles.gui.common import (DECREASE_COLOUR, FIGURE_STYLE, INCREASE_COLOUR, Qt, fill_table,
                                    make_table)
from supercycles.schedule import compare_schedules

if TYPE_CHECKING:                 # only for the type hint (avoids a circular import)
    from supercycles.gui.main_window import ScenarioViewer


class CompareWindow(QtWidgets.QWidget):
    """Two scenarios side by side: B compared to A (tables from compare_schedules)."""

    QUANTITIES = {'Protons per run': 'protons_per_run', 'Cycles per run': 'cycles_per_run',
                  'Average current [uA]': 'average_current_uA', 'Average flux [p/s]': 'average_flux_p_per_s'}

    def __init__(self, viewer: 'ScenarioViewer'):
        super().__init__()
        self.viewer = viewer
        self.setWindowTitle('Supercycles – compare scenarios')
        self.resize(1300, 800)

        self.combo_a, self.combo_b = QtWidgets.QComboBox(), QtWidgets.QComboBox()
        self.quantity = QtWidgets.QComboBox()
        self.quantity.addItems(list(self.QUANTITIES))
        refresh = QtWidgets.QPushButton('Refresh')
        top = QtWidgets.QHBoxLayout()
        for label, widget in [('A:', self.combo_a), ('B:', self.combo_b), ('Facilities quantity:', self.quantity)]:
            top.addWidget(QtWidgets.QLabel(label))
            top.addWidget(widget, stretch=1 if label != 'Facilities quantity:' else 0)
        top.addWidget(refresh)

        # facilities: table + bar chart of the relative change
        self.facility_table = make_table()
        self.figure = Figure(figsize=(6, 4), dpi=100, layout='constrained')
        self.canvas = FigureCanvasQTAgg(self.figure)
        facilities = QtWidgets.QSplitter(Qt.Orientation.Horizontal)
        facilities.addWidget(self.facility_table)
        facilities.addWidget(self.canvas)
        facilities.setSizes([750, 550])

        self.supercycle_table, self.cycle_table, self.run_table = make_table(), make_table(), make_table()
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(facilities, 'Facilities')
        self.tabs.addTab(self.supercycle_table, 'Supercycles')
        self.tabs.addTab(self.cycle_table, 'Cycles')
        self.tabs.addTab(self.run_table, 'Run')

        self.legend = QtWidgets.QLabel()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.legend)
        layout.addWidget(self.tabs, stretch=1)

        self.reload_choices()
        for combo in (self.combo_a, self.combo_b, self.quantity):
            combo.currentTextChanged.connect(self.update_tables)
        refresh.clicked.connect(self.reload_choices)

    def reload_choices(self):
        """Re-read the open scenarios of the viewer (they may have been edited meanwhile)."""
        self.choices = self.viewer.comparison_choices()          # label -> Schedule
        for combo, default in [(self.combo_a, 0), (self.combo_b, 1)]:
            current = combo.currentText()
            combo.blockSignals(True)
            combo.clear()
            combo.addItems(list(self.choices))
            combo.setCurrentText(current if current in self.choices else list(self.choices)[min(default, len(self.choices) - 1)])
            combo.blockSignals(False)
        self.update_tables()

    def select(self, label_a: str, label_b: str):
        self.combo_a.setCurrentText(label_a)
        self.combo_b.setCurrentText(label_b)

    def update_tables(self, *_):
        a, b = self.choices.get(self.combo_a.currentText()), self.choices.get(self.combo_b.currentText())
        if a is None or b is None:
            return
        tables = compare_schedules(a, b)
        self.legend.setText(f'<b>A</b> = {self.combo_a.currentText()}    <b>B</b> = {self.combo_b.currentText()}'
                            f'    (change = B − A, change % relative to A)')

        # facilities: the chosen quantity only
        quantity_label = self.quantity.currentText()
        quantity = self.QUANTITIES[quantity_label]
        facilities = tables['facilities']
        columns = ['facility', 'machine'] + [f'{quantity} {s}' for s in ['A', 'B', 'change', 'change %']]
        fill_table(self.facility_table, facilities[columns],
                   ['Facility', 'Machine', 'A', 'B', 'Change', 'Change [%]'])
        self._plot_changes(facilities['facility'], facilities[f'{quantity} change %'], quantity_label)

        fill_table(self.supercycle_table, tables['supercycles'],
                   [c.replace('share_%', 'share [%]').replace('length_s', 'length [s]')
                    for c in tables['supercycles'].columns])
        fill_table(self.cycle_table, tables['cycles'])
        fill_table(self.run_table, tables['run'], ['Quantity', 'A', 'B', 'Change', 'Change [%]'])

    def _plot_changes(self, facilities, changes, quantity_label):
        """Horizontal bars of the relative change per facility (blue: more in B, red: less)."""
        keep = ~np.isnan(changes.to_numpy(float))
        names, values = list(facilities[keep])[::-1], changes[keep].to_numpy(float)[::-1]
        self.figure.clear()
        with matplotlib.rc_context(FIGURE_STYLE):
            ax = self.figure.add_subplot()
            if len(values):
                colours = [INCREASE_COLOUR if v >= 0 else DECREASE_COLOUR for v in values]
                bars = ax.barh(names, values, color=colours, height=0.6)
                ax.bar_label(bars, [f'{v:+.1f} %' for v in values], padding=3, fontsize=7)
                span = max(abs(values).max(), 1) * 1.3
                ax.set_xlim(-span, span)
            ax.axvline(0, color='#888888', lw=0.8)
            ax.set(xlabel='change of B relative to A [%]', title=f'{quantity_label}: B vs A')
            ax.grid(axis='x', color='#e5e5e5', lw=0.6)
            ax.set_axisbelow(True)
            for side in ['top', 'right']:
                ax.spines[side].set_visible(False)
