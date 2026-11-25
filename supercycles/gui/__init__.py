"""
Scenario viewer and editor: load a scenario, browse its supercycles and what it delivers,
build or modify scenarios, save them and compare them.

Run from the repository root:
    python -m supercycles.gui                        # first scenario of the scenarios package
    python -m supercycles.gui run4_ship_ft9p6        # a given scenario of the package
    python -m supercycles.gui my_scenario.yaml       # a scenario file saved from the GUI

Layout
------
    menu: File (new / open / save / save as / duplicate / revert)   Edit (edit mode, undo, redo)
          Tools (compare scenarios)
    [ Scenario: <combo> ]  description of the scenario
    +----------------------------+--------------------------------------------------+
    | Run: length, downtime, ... | Tabs:                                            |
    |                            |   Supercycle   - plot of the selected supercycle |
    | Supercycles table          |                  + what it delivers per repetition|
    | (click a row to view it)   |   Facilities   - per supercycle and over the run |
    |                            |   Time sharing - share of the run per supercycle |
    +----------------------------+--------------------------------------------------+

Modes
-----
View mode (default) only displays. Edit mode (Ctrl+E) adds:
  * Supercycles table: double-click a name or a share to change it; buttons to add (empty or as a
    copy of any supercycle of any open scenario), duplicate, remove, reorder, include in / leave
    out of the averages, and rescale the shares to 100 %. The run length becomes editable.
  * Supercycle tab: a palette of the cycle types of each machine. Drag a cycle onto the grid to
    place it at that BP (its injections follow), or double-click it to append it after the last
    cycle of its machine (the supercycle gets longer). Right-click the grid for the other
    operations: place / insert / remove a cycle, insert or remove BPs, fill the free BPs.
    When a cycle does not fit, a dialog offers to replace what is in the way or to insert it
    (lengthening the supercycle).
  * Undo / redo (Ctrl+Z / Ctrl+Shift+Z), and a pop-up when an edit creates a new error
    (length or power limit).
Scenarios of the scenarios package are never modified on disk: an edited one is marked with '*'
and is saved with File > Save as (YAML). File > Duplicate keeps the original next to the copy,
e.g. to compare them (Tools > Compare scenarios).

Files
-----
    __init__.py        main(): start the GUI
    main_window.py     ScenarioViewer: window, open scenarios and file menu, views (view mode)
    editing.py         EditingMixin: the edit-mode operations of ScenarioViewer
    edit_widgets.py    CyclePalette, GridCanvas (drag and drop), NewSupercycleDialog
    compare_window.py  CompareWindow
    common.py          constants, table helpers, OpenScenario

Qt is imported through matplotlib, so any installed binding works (PyQt5, PyQt6, PySide6).
The GUI only displays and forwards edits: all numbers and all changes go through Supercycle and
Schedule (see their editing methods).
"""
import os
import sys

from matplotlib.backends.qt_compat import QtWidgets

from supercycles.gui.common import REPOSITORY
from supercycles.gui.main_window import ScenarioViewer


# ---------------------------------------------------------------------------
def main(argv=None) -> None:
    argv = sys.argv[1:] if argv is None else argv
    # the scenarios package lives next to the supercycles package, in the repository root
    if REPOSITORY not in sys.path:
        sys.path.insert(0, REPOSITORY)
    import scenarios

    files = [a for a in argv if a.endswith(('.yaml', '.yml'))]
    names = [a for a in argv if a not in files]
    initial = names[0] if names else (os.path.splitext(os.path.basename(files[0]))[0] if files else None)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    window = ScenarioViewer(scenarios.ALL, initial=initial, files=files)
    window.show()
    app.exec()
