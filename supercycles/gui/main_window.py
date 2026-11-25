"""
Main window of the GUI: builds the window, keeps the open scenarios (file menu) and draws the
views of the scenario shown. The edit-mode operations are in editing.py (EditingMixin).
"""
import os

import matplotlib

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.qt_compat import QtGui, QtWidgets
from matplotlib.figure import Figure

from supercycles.catalogue import load_catalogue
from supercycles.gui.common import (FACILITY_ORDER, FIGURE_STYLE, REPOSITORY, OpenScenario, QMessageBox, Qt,
                                    fill_table, make_table, titled)
from supercycles.gui.compare_window import CompareWindow
from supercycles.gui.edit_widgets import CyclePalette, GridCanvas
from supercycles.gui.editing import EditingMixin
from supercycles.plotting import plot_magnet_current, plot_supercycle
from supercycles.schedule import Schedule


class ScenarioViewer(EditingMixin, QtWidgets.QMainWindow):
    """
    Main window: view mode (this file) and edit mode (the methods of EditingMixin, editing.py).
    """

    def __init__(self, scenario_modules: dict, initial: str = None, files=()):
        super().__init__()
        # name -> OpenScenario; modules are read when first shown
        self.open = {name: None for name in scenario_modules}
        self.scenario_modules = scenario_modules          # name -> module of the scenarios package
        self.current_name = None
        self.edit_mode = False
        self.selected_name = None                         # selected supercycle
        self.grid_ax = None                               # axes of the supercycle grid plot
        self.compare_window = None
        self._filling = False                             # True while tables are filled by code
        self.setWindowTitle('Supercycles – scenario viewer')
        self.resize(1650, 980)

        self._build_actions()

        # top bar: scenario choice and description
        self.scenario_combo = QtWidgets.QComboBox()
        self.scenario_combo.setMinimumWidth(280)
        self.description_label = QtWidgets.QLabel()
        self.mode_label = QtWidgets.QLabel()
        top = QtWidgets.QHBoxLayout()
        top.addWidget(QtWidgets.QLabel('Scenario:'))
        top.addWidget(self.scenario_combo)
        top.addWidget(self.description_label, stretch=1)
        top.addWidget(self.mode_label)

        # left: run summary and list of supercycles (+ edit buttons)
        self.run_form = QtWidgets.QFormLayout()
        run_box = QtWidgets.QGroupBox('Run')
        run_box.setLayout(self.run_form)
        self.supercycle_table = make_table(selectable_rows=True)
        self.supercycle_box = titled('Supercycles (click to view)', self.supercycle_table)
        self.supercycle_buttons = self._build_supercycle_buttons()
        self.supercycle_box.layout().addWidget(self.supercycle_buttons)
        left = QtWidgets.QWidget()
        left_layout = QtWidgets.QVBoxLayout(left)
        left_layout.addWidget(run_box)
        left_layout.addWidget(self.supercycle_box, stretch=1)

        # right: tabs
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self._build_supercycle_tab(), 'Supercycle')
        self.tabs.addTab(self._build_facilities_tab(), 'Facilities')
        self.tabs.addTab(self._build_time_sharing_tab(), 'Time sharing')

        splitter = QtWidgets.QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(self.tabs)
        splitter.setSizes([580, 1070])

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        layout.addLayout(top)
        layout.addWidget(splitter, stretch=1)
        self.setCentralWidget(central)
        self.statusBar()

        # signals
        self.scenario_combo.currentIndexChanged.connect(self._combo_changed)
        self.supercycle_table.itemSelectionChanged.connect(self._selection_changed)
        self.supercycle_table.itemChanged.connect(self._supercycle_item_changed)
        self.supercycle_canvas.mpl_connect('button_press_event', self._grid_clicked)
        self.supercycle_canvas.drop_callback = None

        for path in files:
            self.open_file(path, show=False)
        self._refresh_combo()
        first = initial if initial in self.open else next(iter(self.open))
        self.show_scenario(first)
        self.set_edit_mode(False)

    # ================================================================== building the window
    def _build_actions(self) -> None:
        menu_file = self.menuBar().addMenu('&File')
        menu_edit = self.menuBar().addMenu('&Edit')
        menu_tools = self.menuBar().addMenu('&Tools')

        def action(menu, text, slot, shortcut=None):
            act = menu.addAction(text)
            act.triggered.connect(slot)
            if shortcut:
                act.setShortcut(QtGui.QKeySequence(shortcut))
            return act

        action(menu_file, 'New scenario…', self.new_scenario, 'Ctrl+N')
        action(menu_file, 'Open…', self.open_file_dialog, 'Ctrl+O')
        menu_file.addSeparator()
        action(menu_file, 'Save', self.save, 'Ctrl+S')
        action(menu_file, 'Save as…', self.save_as, 'Ctrl+Shift+S')
        menu_file.addSeparator()
        action(menu_file, 'Duplicate scenario', self.duplicate_scenario, 'Ctrl+D')
        action(menu_file, 'Revert to saved', self.revert)
        action(menu_file, 'Close scenario', self.close_scenario, 'Ctrl+W')

        self.edit_action = action(menu_edit, 'Edit mode', lambda checked: self.set_edit_mode(checked), 'Ctrl+E')
        self.edit_action.setCheckable(True)
        self.undo_action = action(menu_edit, 'Undo', self.undo, 'Ctrl+Z')
        self.redo_action = action(menu_edit, 'Redo', self.redo, 'Ctrl+Shift+Z')
        compare = action(menu_tools, 'Compare scenarios…', self.show_compare, 'Ctrl+K')

        toolbar = self.addToolBar('Main')
        toolbar.setMovable(False)
        for act in [self.edit_action, self.undo_action, self.redo_action, compare]:
            toolbar.addAction(act)

    def _build_supercycle_buttons(self) -> QtWidgets.QWidget:
        """Buttons under the supercycles table (edit mode only)."""
        buttons = [('New…', 'Add a supercycle, empty or copied from any open scenario', self.new_supercycle),
                   ('Duplicate', 'Copy of the selected supercycle (0 % of the run)', self.duplicate_supercycle),
                   ('Remove', 'Remove the selected supercycle', self.remove_supercycle),
                   ('▲', 'Move up', lambda: self.move_supercycle(-1)),
                   ('▼', 'Move down', lambda: self.move_supercycle(+1)),
                   ('Avg. on/off', 'Include the selected supercycle in the averaged fluxes/currents, or not',
                    self.toggle_in_averages),
                   ('Rescale to 100 %', "Scale all shares except 'Downtime' so that they sum to 100 %",
                    self.rescale_shares)]
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        for text, tip, slot in buttons:
            button = QtWidgets.QPushButton(text)
            button.setToolTip(tip)
            button.clicked.connect(slot)
            layout.addWidget(button)
        layout.addStretch()
        return widget

    def _build_supercycle_tab(self) -> QtWidgets.QWidget:
        self.supercycle_figure = Figure(figsize=(10, 5.5), dpi=100, layout='constrained')
        self.supercycle_canvas = GridCanvas(self.supercycle_figure)
        self.supercycle_facility_table = make_table()
        self.issues_label = QtWidgets.QLabel()
        self.issues_label.setWordWrap(True)

        # edit mode: toolbar above the plot and palette on its left
        self.edit_bar = QtWidgets.QWidget()
        bar = QtWidgets.QHBoxLayout(self.edit_bar)
        bar.setContentsMargins(0, 0, 0, 0)
        self.period_spin = QtWidgets.QSpinBox()
        self.period_spin.setRange(1, 500)
        self.period_spin.setSuffix(' BP')
        set_period = QtWidgets.QPushButton('Set period')
        set_period.setToolTip('Add or remove BPs at the end of the supercycle (before the injections '
                              'that wrap around)')
        set_period.clicked.connect(self.set_period)
        self.fill_button = QtWidgets.QPushButton('Fill free BPs ▾')
        self.fill_button.setToolTip('Place a cycle at every free BP of a machine where it fits')
        hint = QtWidgets.QLabel('drag a cycle onto the grid · double-click: append · right-click the grid: more')
        hint.setStyleSheet('color: grey')
        for widget in [QtWidgets.QLabel('Period:'), self.period_spin, set_period, self.fill_button]:
            bar.addWidget(widget)
        bar.addWidget(hint, stretch=1)

        self.palettes = {}
        self.palette_tabs = QtWidgets.QTabWidget()
        self.palette_tabs.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        self.palette_tabs.setMinimumWidth(210)

        plot_area = QtWidgets.QWidget()
        plot_layout = QtWidgets.QVBoxLayout(plot_area)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.addWidget(self.edit_bar)
        plot_layout.addWidget(self.supercycle_canvas, stretch=1)
        top = QtWidgets.QSplitter(Qt.Orientation.Horizontal)
        top.addWidget(self.palette_tabs)
        top.addWidget(plot_area)
        top.setSizes([190, 900])

        bottom = QtWidgets.QWidget()
        bottom_layout = QtWidgets.QVBoxLayout(bottom)
        bottom_layout.addWidget(self.issues_label)
        bottom_layout.addWidget(titled('Delivered per repetition of the supercycle',
                                       self.supercycle_facility_table))

        splitter = QtWidgets.QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(top)
        splitter.addWidget(bottom)
        splitter.setSizes([580, 280])
        return splitter

    def _build_palettes(self, catalogue) -> None:
        """One palette per machine (SPS first: supercycles are usually built from the SPS down)."""
        self.palette_tabs.clear()
        self.palettes = {}
        for machine in reversed(list(catalogue.machines)):
            palette = CyclePalette(catalogue, machine)
            palette.itemDoubleClicked.connect(
                lambda item: self.append_cycle(item.data(Qt.ItemDataRole.UserRole)))
            self.palettes[machine] = palette
            self.palette_tabs.addTab(palette, machine)

    def _build_facilities_tab(self) -> QtWidgets.QWidget:
        self.per_supercycle_table = make_table()
        self.per_run_table = make_table()
        splitter = QtWidgets.QSplitter(Qt.Orientation.Vertical)
        splitter.addWidget(titled('Cycles per repetition of each supercycle, and ISOLDE current',
                                  self.per_supercycle_table))
        self.per_run_box = titled('Over the run', self.per_run_table)    # title set per scenario
        splitter.addWidget(self.per_run_box)
        return splitter

    def _build_time_sharing_tab(self) -> QtWidgets.QWidget:
        self.sharing_figure = Figure(figsize=(10, 6), dpi=100, layout='constrained')
        self.sharing_canvas = FigureCanvasQTAgg(self.sharing_figure)
        return self.sharing_canvas

    # ================================================================== open scenarios
    @property
    def entry(self) -> OpenScenario:
        """The scenario shown (modules of the scenarios package are built when first shown)."""
        name = self.current_name
        if self.open[name] is None:
            module = self.scenario_modules[name]
            self.open[name] = OpenScenario(Schedule.from_scenario(module), 'module', module=module)
        return self.open[name]

    @property
    def schedule(self) -> Schedule:
        return self.entry.schedule

    def _unique_name(self, name: str) -> str:
        candidate, n = name, 2
        while candidate in self.open:
            candidate, n = f'{name} ({n})', n + 1
        return candidate

    def _refresh_combo(self) -> None:
        """Scenario list; '*' marks unsaved changes."""
        self.scenario_combo.blockSignals(True)
        self.scenario_combo.clear()
        for name, entry in self.open.items():
            self.scenario_combo.addItem(name + (' *' if entry is not None and entry.dirty else ''), name)
        if self.current_name in self.open:
            self.scenario_combo.setCurrentIndex(list(self.open).index(self.current_name))
        self.scenario_combo.blockSignals(False)

    def _combo_changed(self, index: int) -> None:
        if index >= 0:
            self.show_scenario(self.scenario_combo.itemData(index))

    def show_scenario(self, name: str) -> None:
        self.current_name = name
        self.selected_name = None
        self._build_palettes(self.schedule.catalogue)
        self._refresh_combo()
        self.refresh()

    def add_open_scenario(self, entry: OpenScenario, show: bool = True) -> str:
        name = self._unique_name(entry.schedule.name or 'scenario')
        entry.schedule.name = name
        self.open[name] = entry
        if show:
            self.show_scenario(name)
        return name

    def comparison_choices(self) -> dict:
        """Open scenarios for the compare window (+ the saved version of those with unsaved changes)."""
        choices = {}
        for name in self.open:
            if self.open[name] is None:                   # module not shown yet: build it now
                module = self.scenario_modules[name]
                self.open[name] = OpenScenario(Schedule.from_scenario(module), 'module', module=module)
            entry = self.open[name]
            choices[name + (' *' if entry.dirty else '')] = entry.schedule
            if entry.dirty and entry.source != 'new':
                choices[f'{name} (as saved)'] = entry.saved_version()
        return choices

    # ================================================================== file menu
    def new_scenario(self) -> None:
        name, ok = QtWidgets.QInputDialog.getText(self, 'New scenario', 'Name of the new scenario:',
                                                  text='new scenario')
        if not ok or not name.strip():
            return
        hours, ok = QtWidgets.QInputDialog.getDouble(self, 'New scenario', 'Run length [h]:',
                                                     self.schedule.run_length_hours, 1, 20000, 0)
        if not ok:
            return
        schedule = Schedule.empty(name.strip(), hours, catalogue=load_catalogue())
        self.add_open_scenario(OpenScenario(schedule, 'new', dirty=True))
        self.set_edit_mode(True)

    def open_file_dialog(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Open scenario', os.path.join(REPOSITORY, 'scenarios'),
                                                        'Scenario files (*.yaml *.yml)')
        if path:
            self.open_file(path)

    def open_file(self, path: str, show: bool = True) -> None:
        try:
            schedule = Schedule.load(path)
        except Exception as error:                        # any problem in the file: tell, do not crash
            QMessageBox.critical(self, 'Cannot open scenario', f'{path}\n\n{error}')
            return
        self.add_open_scenario(OpenScenario(schedule, 'file', path=path), show=show)

    def save(self) -> bool:
        entry = self.entry
        if entry.source != 'file':
            return self.save_as()
        entry.schedule.save(entry.path)
        entry.dirty = False
        self._refresh_combo()
        self.statusBar().showMessage(f'Saved to {entry.path}', 5000)
        return True

    def save_as(self) -> bool:
        entry = self.entry
        default = entry.path or os.path.join(REPOSITORY, 'scenarios', f'{self.current_name}.yaml')
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save scenario as', default,
                                                        'Scenario files (*.yaml *.yml)')
        if not path:
            return False
        if not path.endswith(('.yaml', '.yml')):
            path += '.yaml'
        was_module = entry.source == 'module'
        entry.schedule.save(path)
        entry.source, entry.path, entry.module, entry.dirty = 'file', path, None, False
        # the scenario is now known by its file name
        new_name = os.path.splitext(os.path.basename(path))[0]
        if new_name != self.current_name:
            old_name, new_name = self.current_name, self._unique_name(new_name)
            self.open = {(new_name if n == old_name else n): e for n, e in self.open.items()}
            if was_module:                                # keep the original of the package in the list
                self.open[old_name] = None
            entry.schedule.name = new_name
            entry.schedule.save(path)                     # with its new name
            self.current_name = new_name
        self._refresh_combo()
        self.refresh()
        self.statusBar().showMessage(f'Saved to {path}', 5000)
        return True

    def duplicate_scenario(self) -> None:
        copy = self.schedule.copy(f'{self.current_name} (copy)')
        self.add_open_scenario(OpenScenario(copy, 'new', dirty=True))

    def revert(self) -> None:
        entry = self.entry
        saved = entry.saved_version()
        if saved is None or not entry.dirty:
            return
        if QMessageBox.question(self, 'Revert', f'Discard the unsaved changes of {self.current_name}?') \
                != QMessageBox.StandardButton.Yes:
            return
        entry.undo.append(('revert', entry.schedule))
        saved.name = self.current_name
        entry.schedule, entry.dirty = saved, False
        self._after_change()

    def close_scenario(self) -> None:
        if len(self.open) == 1:
            return
        entry = self.open[self.current_name]
        if entry is not None and entry.dirty and not self._confirm_discard([self.current_name]):
            return
        names = list(self.open)
        index = names.index(self.current_name)
        del self.open[self.current_name]
        self.show_scenario(list(self.open)[max(index - 1, 0)])

    def _confirm_discard(self, names) -> bool:
        return QMessageBox.question(self, 'Unsaved changes', 'Unsaved changes in: ' + ', '.join(names)
                                    + '\n\nDiscard them?') == QMessageBox.StandardButton.Yes

    def closeEvent(self, event):
        dirty = [name for name, entry in self.open.items() if entry is not None and entry.dirty]
        if dirty and not self._confirm_discard(dirty):
            event.ignore()
            return
        if self.compare_window is not None:
            self.compare_window.close()
        event.accept()

    def show_compare(self) -> None:
        if self.compare_window is None:
            self.compare_window = CompareWindow(self)
        else:
            self.compare_window.reload_choices()
        self.compare_window.show()
        self.compare_window.raise_()

    # ================================================================== views
    def refresh(self) -> None:
        """Redraw everything from the current schedule (after loading, switching, or an edit)."""
        if self.current_name is None:
            return
        s = self.schedule
        entry = self.entry
        first_line = (s.description or '').strip().splitlines()
        origin = {'module': 'scenarios package', 'file': entry.path, 'new': 'not saved yet'}[entry.source]
        self.description_label.setText('   ' + (first_line[0] if first_line else '') + f'   [{origin}]')
        self.setWindowTitle(f'Supercycles – {self.current_name}{" *" if entry.dirty else ""}')
        self.undo_action.setEnabled(bool(entry.undo))
        self.redo_action.setEnabled(bool(entry.redo))
        self.fill_button.setMenu(self._fill_menu())
        self._show_run_summary()
        self._show_supercycle_list()
        self._show_facilities()
        self._show_time_sharing()
        self.show_selected_supercycle()

    def _show_run_summary(self) -> None:
        s = self.schedule
        while self.run_form.rowCount():
            self.run_form.removeRow(0)
        machines = s.availability_table().to_dict('records')
        if self.edit_mode:
            hours = QtWidgets.QDoubleSpinBox()
            hours.setRange(1, 20000)
            hours.setDecimals(1)
            hours.setSuffix(' h')
            hours.setValue(s.run_length_hours)
            hours.editingFinished.connect(lambda: self.set_run_length(hours.value()))
            self.run_form.addRow('Run length [h]:', hours)
        rows = [
            ('Reference', s.reference or '–'),
            ('Run length', f'{s.run_length_hours:.0f} h = {s.run_length_days:.1f} days = '
                           f'{s.run_length_days / 7:.1f} weeks'),
            ('Availability', '    '.join(f"{m['machine']} {m['availability_%']:.0f} %" for m in machines)),
            ('Downtime', '    '.join(f"{m['machine']} {m['downtime_hours']:.0f} h" for m in machines)),
            ('Supercycles', f'{len(s.supercycles)}'),
            ('Not in averages', ', '.join(s.not_in_averages) or '–'),
        ]
        for label, value in rows:
            self.run_form.addRow(label + ':', QtWidgets.QLabel(value))

    def _show_supercycle_list(self) -> None:
        s = self.schedule
        table = s.supercycle_table()
        table['in_averages'] = ['yes' if value else 'no' for value in table['in_averages']]
        table = table[['supercycle', 'share_%', 'length_s', 'period_bp', 'repetitions', 'hours', 'in_averages']]
        self._filling = True
        fill_table(self.supercycle_table, table,
                   ['Supercycle', 'Share of run [%]', 'Length [s]', 'BP', 'Played', 'Hours', 'Avg.'])
        self._row_names = list(table['supercycle'])
        for row, name in enumerate(self._row_names):
            for col in range(table.shape[1]):
                item = self.supercycle_table.item(row, col)
                if col == 1:                              # full precision when editing
                    item.setData(Qt.ItemDataRole.EditRole, f'{s.time_shares[name]:.6g}')
                if col > 1 or not self.edit_mode:         # only name and share are editable
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if col == 2 and s.supercycles[name].length_s > s.catalogue.max_supercycle_length_s:
                    item.setForeground(QtGui.QColor('red'))
        if self.selected_name not in s.supercycles:
            self.selected_name = self._row_names[0] if self._row_names else None
        if self.selected_name is not None:
            self.supercycle_table.selectRow(self._row_names.index(self.selected_name))
        self._filling = False

        total = s.total_share
        warning = '' if abs(total - 100) < 1e-6 else '  ≠ 100 % !'
        hint = 'double-click a name or a share to edit it' if self.edit_mode else 'click to view'
        self.supercycle_box.setTitle(f'Supercycles ({hint}) – shares sum to {total:.6g} %{warning}')

    def _show_facilities(self) -> None:
        s = self.schedule
        cycles = s.per_supercycle_table('cycles_per_supercycle')
        if not cycles.empty:
            columns = [f for f in FACILITY_ORDER if f in cycles.columns]
            columns += [f for f in cycles.columns if f not in columns]
            cycles = cycles[columns]
            currents = s.per_supercycle_table('current_uA')
            if 'ISOLDE' in currents.columns:
                cycles['ISOLDE [uA]'] = currents['ISOLDE']
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
        self.sharing_figure.clear()
        if table.empty:
            self.sharing_canvas.draw()
            return
        colours = ['tab:blue' if averaged else 'lightgrey' for averaged in table['in_averages']]
        availability = '  '.join(f'{m} {100 * s.availability(m):.0f} %' for m in ['SPS', 'PS', 'PSB'])
        with matplotlib.rc_context(FIGURE_STYLE):
            ax = self.sharing_figure.add_subplot()
            bars = ax.barh(table['supercycle'], table['share_%'], color=colours)
            ax.bar_label(bars, [f'{p:.1f} %  ({h:.0f} h)' for p, h in zip(table['share_%'], table['hours'])], padding=3)
            ax.set(xlabel='share of the run [%]  (grey: not in the averages)',
                   xlim=(0, max(table['share_%'].max(), 1) * 1.35),
                   title=f'{s.name}: {s.run_length_hours:.0f} h run;  availability {availability};  '
                         f'shares sum to {s.total_share:.4g} %')
        self.sharing_canvas.draw()

    # ------------------------------------------------------------------ supercycle
    def select_supercycle(self, name: str) -> None:
        self.selected_name = name
        self.refresh()

    def _selection_changed(self) -> None:
        if self._filling:
            return
        rows = self.supercycle_table.selectionModel().selectedRows()
        if rows:
            self.selected_name = self._row_names[rows[0].row()]
            self.show_selected_supercycle()

    def show_selected_supercycle(self) -> None:
        self.supercycle_figure.clear()
        self.grid_ax = None
        sc = self.schedule.supercycles.get(self.selected_name)
        if sc is None:
            self.supercycle_canvas.draw()
            self.issues_label.setText('No supercycle: add one in edit mode (Ctrl+E), button "New…".'
                                      if self.edit_mode else 'No supercycle.')
            self.supercycle_facility_table.clear()
            return
        name = sc.name
        with matplotlib.rc_context(FIGURE_STYLE):
            ax_grid, ax_current = self.supercycle_figure.subplots(2, 1, height_ratios=[1.3, 1])
            plot_supercycle(sc, ax=ax_grid, fontsize=6)
            plot_magnet_current(sc, 'SPS', ax=ax_current)
            ax_grid.set_title(f'{sc.name}  –  {sc.period_bp} BP = {sc.length_s:.1f} s, '
                              f'{self.schedule.time_shares[name]:.4g} % of the run, '
                              f'played {self.schedule.repetitions(name):.0f} times')
        self.grid_ax = ax_grid
        self.supercycle_canvas.draw()
        self.period_spin.setValue(sc.period_bp)

        issues = sc.validate()
        errors = [i for i in issues if i.level == 'error']
        text = '; '.join(str(i) for i in issues) if issues else 'No issues found by validate().'
        self.issues_label.setText(('<b style="color:red">Issues:</b> ' if errors else '<b>Issues:</b> ' if issues else '')
                                  + text)
        fill_table(self.supercycle_facility_table, sc.facility_table(),
                   ['Facility', 'Machine', 'Cycles', 'Protons', 'Flux [p/s]', 'Current [uA]'])
