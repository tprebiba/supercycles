"""
supercycles: modelling of supercycles and beam sharing in the CERN injectors (PSB, PS, SPS).

    Catalogue    machines, facilities and cycle types, read from supercycles/data/catalogue/*.yaml
    Supercycle   one supercycle of the whole chain, on a fixed BP period with wrap-around
    plotting     plot_supercycle, plot_magnet_current
"""
from supercycles._version import __version__
from supercycles.catalogue import (Beam, Catalogue, CatalogueError, CycleType, Facility,
                                   Injection, Machine, load_catalogue)
from supercycles.supercycle import Issue, Placement, PlacementError, Supercycle
