"""
supercycles: modelling of supercycles and beam sharing in the CERN injectors (PSB, PS, SPS).

    Catalogue    machines, facilities and cycle types, read from supercycles/data/catalogue/*.yaml
    Supercycle   one supercycle of the whole chain, on a fixed BP period with wrap-around
    Schedule     time sharing of a run between supercycles, and what the run delivers
    plotting     plot_supercycle, plot_magnet_current
    gui          scenario viewer:  python -m supercycles.gui  (needs PyQt5, PyQt6 or PySide6)
"""
from supercycles._version import __version__
from supercycles.catalogue import (Beam, Catalogue, CatalogueError, CycleType, Facility,
                                   Injection, Machine, load_catalogue)
from supercycles.supercycle import Issue, Placement, PlacementError, Supercycle
from supercycles.schedule import Schedule
