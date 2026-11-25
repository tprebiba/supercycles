"""
Edit mode of the scenario window: every operation that changes a scenario.

EditingMixin holds the methods of ScenarioViewer (main_window.py) used in edit mode; it is not
used on its own. It relies on the window for: self.schedule / self.entry (the scenario shown),
self.selected_name (the supercycle shown), self.refresh() and the widgets built there.

Every edit goes through apply_edit(): an undo point is kept, the change is made with the methods of
Supercycle / Schedule, and if they refuse (PlacementError, ...) nothing changes and the reason is
shown in a pop-up.
"""
import math
from typing import Callable, Optional

from matplotlib.backends.qt_compat import QtGui, QtWidgets

from supercycles.gui.common import MAX_UNDO, QMessageBox, ask, colour_icon, describe
from supercycles.gui.edit_widgets import NewSupercycleDialog
from supercycles.supercycle import PlacementError, Supercycle


class EditingMixin:
    """Edit-mode methods of ScenarioViewer (see the module docstring)."""

    # ================================================================== edit mode
    def set_edit_mode(self, enabled: bool) -> None:
        self.edit_mode = enabled
        self.edit_action.setChecked(enabled)
        for widget in [self.supercycle_buttons, self.edit_bar, self.palette_tabs]:
            widget.setVisible(enabled)
        triggers = QtWidgets.QAbstractItemView.EditTrigger
        self.supercycle_table.setEditTriggers(
            triggers.DoubleClicked | triggers.EditKeyPressed if enabled else triggers.NoEditTriggers)
        self.supercycle_canvas.drop_callback = self._cycle_dropped if enabled else None
        self.mode_label.setText('<b style="color:#c05000">EDIT MODE</b>' if enabled else 'view mode')
        self.refresh()

    def apply_edit(self, label: str, change: Callable) -> bool:
        """
        Run an edit of the current scenario. On failure nothing changes and the reason is shown.
        On success: undo point, '*' on the scenario, views refreshed, and a pop-up if the edit
        created new errors (length / power limit) in the selected supercycle.
        """
        entry = self.entry
        before = entry.schedule.copy()
        errors_before = self._errors_of_selected()
        try:
            change()
        except (PlacementError, ValueError, KeyError) as error:
            entry.schedule = before                       # whatever happened, back to the start
            QMessageBox.warning(self, 'Not possible', f'Cannot {label}:\n\n{error}')
            self.refresh()
            return False
        entry.undo = (entry.undo + [(label, before)])[-MAX_UNDO:]
        entry.redo.clear()
        entry.dirty = True
        self._after_change()
        self.statusBar().showMessage(f'Done: {label}', 4000)
        new_errors = [e for e in self._errors_of_selected() if e not in errors_before]
        if new_errors:
            QMessageBox.warning(self, 'Limits exceeded', f'{self.selected_name}:\n\n' + '\n'.join(new_errors))
        return True

    def _errors_of_selected(self) -> list:
        sc = self.schedule.supercycles.get(self.selected_name)
        return [issue.message for issue in sc.validate() if issue.level == 'error'] if sc else []

    def _after_change(self) -> None:
        self._refresh_combo()
        self.refresh()

    def undo(self) -> None:
        self._step_history(self.entry.undo, self.entry.redo, 'Undone')

    def redo(self) -> None:
        self._step_history(self.entry.redo, self.entry.undo, 'Redone')

    def _step_history(self, source: list, target: list, verb: str) -> None:
        if not source:
            return
        label, schedule = source.pop()
        target.append((label, self.entry.schedule))
        self.entry.schedule = schedule
        self.entry.dirty = True
        if self.selected_name not in schedule.supercycles:
            self.selected_name = None
        self._after_change()
        self.statusBar().showMessage(f'{verb}: {label}', 4000)

    # ------------------------------------------------------------------ edits: list of supercycles
    def new_supercycle(self) -> None:
        templates = {}
        for scenario_name, schedule in self.comparison_choices().items():
            for name, sc in schedule.supercycles.items():
                templates[f'{scenario_name} / {name}'] = sc
        catalogue = self.schedule.catalogue
        dialog = NewSupercycleDialog(self, templates, catalogue.max_supercycle_length_s, catalogue.basic_period_s)
        if not dialog.exec():
            return
        name = dialog.name.text().strip()
        template = templates.get(dialog.template.currentText())
        share = dialog.share.value()

        def change():
            if template is None:
                self.schedule.new_supercycle(name, dialog.period.value(), share)
            else:   # rebuilt with the catalogue of this scenario (beams may differ between scenarios)
                data = dict(template.to_dict(), name=name)
                self.schedule.add_supercycle(Supercycle.from_dict(data, self.schedule.catalogue), share)
        if self.apply_edit(f'add supercycle {name!r}', change):
            self.select_supercycle(name)

    def duplicate_supercycle(self) -> None:
        sc = self._selected_or_warn()
        if sc is None:
            return
        name = self._unique_supercycle_name(f'{sc.name} (copy)')
        if self.apply_edit(f'duplicate {sc.name!r}',
                           lambda: self.schedule.add_supercycle(sc.copy(name), 0.0,
                                                                sc.name not in self.schedule.not_in_averages)):
            self.select_supercycle(name)

    def _unique_supercycle_name(self, name: str) -> str:
        candidate, n = name, 2
        while candidate in self.schedule.supercycles:
            candidate, n = f'{name} {n}', n + 1
        return candidate

    def remove_supercycle(self) -> None:
        sc = self._selected_or_warn()
        if sc is not None:
            name = sc.name
            self.selected_name = None
            self.apply_edit(f'remove supercycle {name!r}', lambda: self.schedule.remove_supercycle(name))

    def move_supercycle(self, step: int) -> None:
        sc = self._selected_or_warn()
        if sc is not None:
            self.apply_edit(f'move {sc.name!r}', lambda: self.schedule.move_supercycle(sc.name, step))

    def toggle_in_averages(self) -> None:
        sc = self._selected_or_warn()
        if sc is not None:
            now = sc.name not in self.schedule.not_in_averages
            self.apply_edit(f'{"leave out of" if now else "include in"} the averages {sc.name!r}',
                            lambda: self.schedule.set_in_averages(sc.name, not now))

    def rescale_shares(self) -> None:
        self.apply_edit('rescale the shares to 100 %', lambda: self.schedule.rescale_shares(keep=('Downtime',)))

    def _supercycle_item_changed(self, item: QtWidgets.QTableWidgetItem) -> None:
        """Edited cell of the supercycles table: name (column 0) or share (column 1)."""
        if self._filling:
            return
        old_name = self._row_names[item.row()]
        text = item.text().strip()
        if item.column() == 0:
            self.selected_name = text
            if not self.apply_edit(f'rename {old_name!r}', lambda: self.schedule.rename_supercycle(old_name, text)):
                self.selected_name = old_name
        elif item.column() == 1:
            try:
                share = float(text.replace('%', ''))
            except ValueError:
                QMessageBox.warning(self, 'Not a number', f'{text!r} is not a share in %')
                self.refresh()
                return
            self.apply_edit(f'set the share of {old_name!r}', lambda: self.schedule.set_share(old_name, share))

    def set_run_length(self, hours: float) -> None:
        if hours != self.schedule.run_length_hours:
            self.apply_edit('change the run length', lambda: setattr(self.schedule, 'run_length_hours', float(hours)))

    # ------------------------------------------------------------------ edits: one supercycle
    def _selected_or_warn(self) -> Optional[Supercycle]:
        sc = self.schedule.supercycles.get(self.selected_name)
        if sc is None:
            self.statusBar().showMessage('Select a supercycle first', 4000)
        return sc

    def _sc(self) -> Supercycle:
        """The selected supercycle of the current schedule (looked up again after each undo point)."""
        return self.schedule.supercycles[self.selected_name]

    def place_cycle(self, key: str, bp: int) -> None:
        """Place a cycle at a BP; if something is in the way, offer to replace it or to insert."""
        sc = self._selected_or_warn()
        if sc is None:
            return
        machine, cycle_id = key.split('.', 1)
        try:
            blocking = sc.conflicts(machine, cycle_id, bp)
        except PlacementError as error:
            QMessageBox.warning(self, 'Not possible', str(error))
            return
        if not blocking:
            self.apply_edit(f'place {key} at BP {bp}', lambda: self._sc().add(machine, cycle_id, bp))
            return
        length = sc.catalogue.cycle(key).length_bp
        choice = ask(self, f'Place {key}',
                     f'{key} at BP {bp} (with its injections) collides with:\n\n  {describe(blocking)}\n\n'
                     f'Replace: remove these cycles (with their injections) and place {key}.\n'
                     f'Insert: lengthen the supercycle by {length} BP and place {key} at BP {bp}; '
                     f'the cycles from there on move later.',
                     ['Replace', 'Insert'])
        if choice == 'Replace':
            self.apply_edit(f'place {key} at BP {bp} (replacing {len(blocking)} cycle(s))',
                            lambda: self._sc().replace(machine, cycle_id, bp))
        elif choice == 'Insert':
            self.insert_cycle(key, bp)

    def insert_cycle(self, key: str, bp: Optional[int]) -> None:
        """Insert a cycle at a BP (or after the last one of its machine if bp is None), lengthening the supercycle."""
        sc = self._selected_or_warn()
        if sc is None:
            return
        machine, cycle_id = key.split('.', 1)
        where = 'at the end' if bp is None else f'at BP {bp}'
        trial = sc.copy()
        try:
            trial.insert(machine, cycle_id, bp)
            replace = False
        except PlacementError as error:
            answer = ask(self, f'Insert {key}', f'Even after lengthening the supercycle:\n\n{error}\n\n'
                                                f'Remove the cycles in the way?', ['Remove them and insert'])
            if answer is None:
                return
            replace = True
        self.apply_edit(f'insert {key} {where}', lambda: self._sc().insert(machine, cycle_id, bp, replace_conflicts=replace))

    def append_cycle(self, key: str) -> None:
        """
        After the last cycle of its machine: in the free BPs there if it fits (e.g. when building a
        supercycle of a chosen period), otherwise lengthening the supercycle.
        """
        sc = self._selected_or_warn()
        if sc is None:
            return
        machine, cycle_id = key.split('.', 1)
        at_bp = sc.end_slot(machine, cycle_id)
        if at_bp is None:
            self.insert_cycle(key, None)
        else:
            self.place_cycle(key, at_bp)

    def _cycle_dropped(self, key: str, x: float, y: float) -> None:
        """A cycle dropped from the palette at display position (x, y)."""
        position = self._grid_position(x, y)
        if position is None:
            self.statusBar().showMessage('Drop the cycle on the supercycle grid (upper plot)', 4000)
            return
        _, bp = position
        self.place_cycle(key, bp)

    def _grid_position(self, x: float, y: float):
        """(machine, BP) under the display position (x, y) of the grid plot, or None."""
        sc = self.schedule.supercycles.get(self.selected_name)
        if self.grid_ax is None or sc is None or not self.grid_ax.bbox.contains(x, y):
            return None
        xdata, ydata = self.grid_ax.transData.inverted().transform((x, y))
        bp = int(min(max(math.floor(xdata) + 1, 1), sc.period_bp))
        row = int(min(max(math.floor(ydata), 0), len(sc.machines) - 1))
        return sc.machines[row], bp

    def _grid_clicked(self, event) -> None:
        """Left click: what is there (status bar). Right click (edit mode): menu of operations."""
        position = self._grid_position(event.x, event.y) if event.inaxes is self.grid_ax else None
        if position is None:
            return
        machine, bp = position
        sc = self._sc()
        placement = sc.timeline(machine)[bp - 1]
        if event.button == 1:
            if placement is None:
                self.statusBar().showMessage(f'{machine} BP {bp}: free')
            else:
                root = sc.root(placement)
                part = '' if root is placement else f', injection for {root.cycle.key} at BP {root.start_bp}'
                self.statusBar().showMessage(f'{machine} BP {bp}: {placement.cycle.key} (#{placement.id}), '
                                             f'BP {placement.start_bp}–{sc.wrap(placement.start_bp + placement.cycle.length_bp - 1)}{part}')
        elif event.button == 3 and self.edit_mode:
            self._grid_menu(machine, bp, placement).exec(QtGui.QCursor.pos())

    def _grid_menu(self, machine: str, bp: int, placement) -> QtWidgets.QMenu:
        sc = self._sc()
        menu = QtWidgets.QMenu(self)
        title = menu.addAction(f'{machine} BP {bp}' + (f' – {placement.cycle.key}' if placement else ' – free'))
        title.setEnabled(False)
        cycles = sc.catalogue.cycles_of(machine)

        def cycle_submenu(text, slot):
            submenu = menu.addMenu(text)
            for cycle in cycles:
                act = submenu.addAction(colour_icon(cycle.colour), f'{cycle.id}  ({cycle.length_bp} BP)')
                act.triggered.connect(lambda _=False, key=cycle.key: slot(key))
            return submenu

        cycle_submenu('Place cycle here', lambda key: self.place_cycle(key, bp))
        cycle_submenu('Insert cycle here (lengthens the supercycle)', lambda key: self.insert_cycle(key, bp))
        cycle_submenu(f'Append cycle after the last {machine} cycle', self.append_cycle)
        menu.addSeparator()
        if placement is not None:
            root = sc.root(placement)
            what = root.cycle.key if root is placement else f'{root.cycle.key} at BP {root.start_bp} (this is its injection)'
            menu.addAction(f'Remove {what}, with its injections').triggered.connect(
                lambda: self.apply_edit(f'remove {root.cycle.key} at BP {root.start_bp}', lambda: self._sc().remove(root.id)))
            menu.addAction(f'Remove {root.cycle.key} and close the gap').triggered.connect(
                lambda: self.remove_and_close(root))
            menu.addSeparator()
        menu.addAction('Insert empty BP(s) before this BP…').triggered.connect(lambda: self.insert_bps(bp))
        menu.addAction('Remove this BP (all machines)').triggered.connect(
            lambda: self.apply_edit(f'remove BP {bp}', lambda: self._sc().remove_bps(bp, 1)))
        cycle_submenu(f'Fill the free {machine} BPs with', self.fill)
        menu.addAction(f'Clear {machine} (remove its cycles that are not injections)').triggered.connect(
            lambda: self.clear_machine(machine))
        return menu

    def remove_and_close(self, root) -> None:
        """Remove a cycle and shorten the supercycle by its length (cycles starting in the gap go too)."""
        sc = self._sc()
        start, n = root.start_bp, root.cycle.length_bp
        trial = sc.copy()
        trial.remove(root.id)
        also = [p for p in trial.cycles_starting_in(start, n)]
        if also and ask(self, 'Close the gap', f'Removing BP {start}–{start + n - 1} also removes the cycles '
                                               f'starting there:\n\n  {describe(also)}', ['Remove them too']) is None:
            return

        def change():
            self._sc().remove(root.id)
            self._sc().remove_bps(start, n, remove_cycles=True)
        self.apply_edit(f'remove {root.cycle.key} at BP {start} and close the gap', change)

    def insert_bps(self, bp: int) -> None:
        n, ok = QtWidgets.QInputDialog.getInt(self, 'Insert BPs', f'Number of empty BPs to insert before BP {bp}:', 1, 1, 100)
        if ok:
            self.apply_edit(f'insert {n} BP(s) at BP {bp}', lambda: self._sc().insert_bps(bp, n))

    def fill(self, key: str) -> None:
        machine, cycle_id = key.split('.', 1)
        self.apply_edit(f'fill the free {machine} BPs with {cycle_id}', lambda: self._sc().fill(machine, cycle_id))

    def clear_machine(self, machine: str) -> None:
        def change():
            sc = self._sc()
            for placement in [p for p in sc.placements_on(machine) if p.parent is None]:
                sc.remove(placement.id)
        self.apply_edit(f'clear {machine}', change)

    def set_period(self) -> None:
        sc = self._selected_or_warn()
        if sc is None:
            return
        new, old = self.period_spin.value(), sc.period_bp
        if new > old:
            self.apply_edit(f'lengthen to {new} BP', lambda: self._sc().insert_bps(old + 1, new - old))
        elif new < old:
            self.apply_edit(f'shorten to {new} BP', lambda: self._sc().remove_bps(new + 1, old - new))

    def _fill_menu(self) -> QtWidgets.QMenu:
        """Menu of the 'Fill free BPs' button: machine > cycle type."""
        menu = QtWidgets.QMenu(self)
        for machine in reversed(list(self.schedule.catalogue.machines)):
            submenu = menu.addMenu(machine)
            for cycle in self.schedule.catalogue.cycles_of(machine):
                act = submenu.addAction(colour_icon(cycle.colour), cycle.id)
                act.triggered.connect(lambda _=False, key=cycle.key: self.fill(key))
        return menu
