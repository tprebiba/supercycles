"""
Scenario viewer: load a scenario, browse its supercycles and what it delivers.

Run from the repository root:
    python -m supercycles.gui                 # first scenario
    python -m supercycles.gui run4_ship_ft9p6 # a given scenario

Layout
------
    [ Scenario: <combo> ]  description of the scenario
    +----------------------------+--------------------------------------------------+
    | Run: length, downtime, ... | Tabs:                                            |
    |                            |   Supercycle   - plot of the selected supercycle |
    | Supercycles table          |                  + what it delivers per repetition|
    | (click a row to view it)   |   Facilities   - per supercycle and over the run |
    |                            |   Time sharing - share of the run per supercycle |
    +----------------------------+--------------------------------------------------+

Qt is imported through matplotlib, so any installed binding works (PyQt5, PyQt6, PySide6).
The GUI only displays: all numbers come from Supercycle and Schedule.
"""
import math
import os
import sys

import matplotlib

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.figure import Figure

from supercycles.plotting import plot_magnet_current, plot_supercycle
from supercycles.schedule import Schedule

# facilities shown as columns of the per-supercycle table (others are added after them)
FIGURE_STYLE = {'font.size': 8}   # figures are embedded in panels: smaller fonts than default
FACILITY_ORDER = ['NorthArea', 'SHiP', 'LHC', 'AWAKE', 'HiRadMat', 'nTOF', 'EAST_T8', 'EAST_T9',
                  'EAST_TN', 'AD', 'ISOLDE', 'MD']


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
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, col, item)
    table.resizeColumnsToContents()


def titled(title: str, widget: QtWidgets.QWidget) -> QtWidgets.QGroupBox:
    box = QtWidgets.QGroupBox(title)
    layout = QtWidgets.QVBoxLayout(box)
    layout.addWidget(widget)
    return box


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------
class ScenarioViewer(QtWidgets.QMainWindow):

    def __init__(self, scenario_modules: dict, initial: str = None):
        super().__init__()
        self.scenario_modules = scenario_modules          # name -> module of the scenarios package
        self.schedule = None
        self.setWindowTitle('Supercycles – scenario viewer')
        self.resize(1600, 950)

        # top bar: scenario choice and description
        self.scenario_combo = QtWidgets.QComboBox()
        self.scenario_combo.addItems(list(scenario_modules))
        self.description_label = QtWidgets.QLabel()
        top = QtWidgets.QHBoxLayout()
        top.addWidget(QtWidgets.QLabel('Scenario:'))
        top.addWidget(self.scenario_combo)
        top.addWidget(self.description_label, stretch=1)

        # left: run summary and list of supercycles
        self.run_form = QtWidgets.QFormLayout()
        run_box = QtWidgets.QGroupBox('Run')
        run_box.setLayout(self.run_form)
        self.supercycle_table = make_table(selectable_rows=True)
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        left_layout.addWidget(run_box)
        left_layout.addWidget(titled('Supercycles (click to view)', self.supercycle_table), stretch=1)

        # right: tabs
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self._build_supercycle_tab(), 'Supercycle')
        self.tabs.addTab(self._build_facilities_tab(), 'Facilities')
        self.tabs.addTab(self._build_time_sharing_tab(), 'Time sharing')

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(self.tabs)
        splitter.setSizes([560, 1040])

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.addLayout(top)
        layout.addWidget(splitter, stretch=1)
        self.setCentralWidget(central)

        # signals
        self.scenario_combo.currentTextChanged.connect(self.load_scenario)
        self.supercycle_table.itemSelectionChanged.connect(self.show_selected_supercycle)

        self.scenario_combo.setCurrentText(initial or next(iter(scenario_modules)))
        self.load_scenario(self.scenario_combo.currentText())

    # ------------------------------------------------------------------ tab builders
    def _build_supercycle_tab(self) -> QtWidgets.QWidget:
        self.supercycle_figure = Figure(figsize=(10, 5.5), dpi=100, layout='constrained')
        self.supercycle_canvas = FigureCanvasQTAgg(self.supercycle_figure)
        self.supercycle_facility_table = make_table()
        self.issues_label = QtWidgets.QLabel()
        self.issues_label.setWordWrap(True)

        bottom = QtWidgets.QWidget()
        bottom_layout = QtWidgets.QVBoxLayout(bottom)
        bottom_layout.addWidget(self.issues_label)
        bottom_layout.addWidget(titled('Delivered per repetition of the supercycle',
                                       self.supercycle_facility_table))

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        splitter.addWidget(self.supercycle_canvas)
        splitter.addWidget(bottom)
        splitter.setSizes([560, 300])
        return splitter

    def _build_facilities_tab(self) -> QtWidgets.QWidget:
        self.per_supercycle_table = make_table()
        self.per_run_table = make_table()
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        splitter.addWidget(titled('Cycles per repetition of each supercycle, and ISOLDE current',
                                  self.per_supercycle_table))
        self.per_run_box = titled('Over the run', self.per_run_table)    # title set per scenario
        splitter.addWidget(self.per_run_box)
        return splitter

    def _build_time_sharing_tab(self) -> QtWidgets.QWidget:
        self.sharing_figure = Figure(figsize=(10, 6), dpi=100, layout='constrained')
        self.sharing_canvas = FigureCanvasQTAgg(self.sharing_figure)
        return self.sharing_canvas

    # ------------------------------------------------------------------ scenario
    def load_scenario(self, name: str) -> None:
        module = self.scenario_modules[name]
        self.schedule = Schedule.from_scenario(module)
        self.description_label.setText('   ' + (module.__doc__ or '').strip().splitlines()[0])
        self._show_run_summary(module)
        self._show_supercycle_list()
        self._show_facilities()
        self._show_time_sharing()
        self.supercycle_table.selectRow(0)

    def _show_run_summary(self, module) -> None:
        s = self.schedule
        while self.run_form.rowCount():
            self.run_form.removeRow(0)
        machines = s.availability_table().to_dict('records')
        rows = [
            ('Reference sheet', getattr(module, 'SHEET', '–')),
            ('Run length', f'{s.run_length_hours:.0f} h = {s.run_length_days:.1f} days = '
                           f'{s.run_length_days / 7:.1f} weeks'),
            ('Availability', '    '.join(f"{m['machine']} {m['availability_%']:.0f} %" for m in machines)),
            ('Downtime', '    '.join(f"{m['machine']} {m['downtime_hours']:.0f} h" for m in machines)),
            ('Supercycles', f'{len(s.supercycles)}   (time shares sum to {sum(s.time_shares.values()):g} %)'),
            ('Not in averages', ', '.join(s.not_in_averages) or '–'),
        ]
        for label, value in rows:
            self.run_form.addRow(label + ':', QtWidgets.QLabel(value))

    def _show_supercycle_list(self) -> None:
        table = self.schedule.supercycle_table()
        table['in_averages'] = ['yes' if value else 'no' for value in table['in_averages']]
        table = table[['supercycle', 'share_%', 'length_s', 'period_bp', 'repetitions', 'hours', 'in_averages']]
        fill_table(self.supercycle_table, table,
                   ['Supercycle', 'Share of run [%]', 'Length [s]', 'BP', 'Played', 'Hours', 'Avg.'])

    def _show_facilities(self) -> None:
        s = self.schedule
        cycles = s.per_supercycle_table('cycles_per_supercycle')
        columns = [f for f in FACILITY_ORDER if f in cycles.columns]
        columns += [f for f in cycles.columns if f not in columns]
        cycles = cycles[columns]
        cycles['ISOLDE [uA]'] = s.per_supercycle_table('current_uA')['ISOLDE']
        cycles.insert(0, 'share of run [%]', [s.time_shares[name] for name in cycles.index])
        cycles = cycles.reset_index()
        fill_table(self.per_supercycle_table, cycles)

        excluded = ', '.join(s.not_in_averages) or 'nothing'
        self.per_run_box.setTitle(f'Over the run: cycles and protons from all supercycles; '
                                  f'flux and current averaged without {excluded}')
        per_run = s.facility_table()
        per_run['order'] = [FACILITY_ORDER.index(f) if f in FACILITY_ORDER else 99 for f in per_run['facility']]
        per_run = per_run.sort_values('order').drop(columns='order')
        fill_table(self.per_run_table, per_run,
                   ['Facility', 'Machine', 'Cycles / run', 'Cycles / day', 'Protons / run',
                    'Avg. flux [p/s]', 'Avg. current [uA]'])

    def _show_time_sharing(self) -> None:
        s = self.schedule
        table = s.supercycle_table()[::-1]                     # first supercycle on top
        colours = ['tab:blue' if averaged else 'lightgrey' for averaged in table['in_averages']]
        availability = '  '.join(f'{m} {100 * s.availability(m):.0f} %' for m in ['SPS', 'PS', 'PSB'])

        self.sharing_figure.clear()
        with matplotlib.rc_context(FIGURE_STYLE):
            ax = self.sharing_figure.add_subplot()
            bars = ax.barh(table['supercycle'], table['share_%'], color=colours)
            ax.bar_label(bars, [f'{p:.1f} %  ({h:.0f} h)' for p, h in zip(table['share_%'], table['hours'])], padding=3)
            ax.set(xlabel='share of the run [%]  (grey: not in the averages)', xlim=(0, table['share_%'].max() * 1.35),
                   title=f'{s.name}: {s.run_length_hours:.0f} h run;  availability {availability}')
        self.sharing_canvas.draw()

    # ------------------------------------------------------------------ supercycle
    def show_selected_supercycle(self) -> None:
        rows = self.supercycle_table.selectionModel().selectedRows()
        if not rows:
            return
        name = self.supercycle_table.item(rows[0].row(), 0).text()
        sc = self.schedule.supercycles[name]

        self.supercycle_figure.clear()
        with matplotlib.rc_context(FIGURE_STYLE):
            ax_grid, ax_current = self.supercycle_figure.subplots(2, 1, height_ratios=[1.3, 1])
            plot_supercycle(sc, ax=ax_grid, fontsize=6)
            plot_magnet_current(sc, 'SPS', ax=ax_current)
            ax_grid.set_title(f'{sc.name}  –  {sc.period_bp} BP = {sc.length_s:.1f} s, '
                              f'{self.schedule.time_shares[name]:.4g} % of the run, '
                              f'played {self.schedule.repetitions(name):.0f} times')
        self.supercycle_canvas.draw()

        issues = sc.validate()
        if issues:
            self.issues_label.setText('<b>Issues:</b> ' + '; '.join(str(i) for i in issues))
        else:
            self.issues_label.setText('No issues found by validate().')
        fill_table(self.supercycle_facility_table, sc.facility_table(),
                   ['Facility', 'Machine', 'Cycles', 'Protons', 'Flux [p/s]', 'Current [uA]'])


# ---------------------------------------------------------------------------
def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    # the scenarios package lives next to the supercycles package, in the repository root
    repository = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repository not in sys.path:
        sys.path.insert(0, repository)
    import scenarios

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = ScenarioViewer(scenarios.ALL, initial=argv[0] if argv else None)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
