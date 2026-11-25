"""
Scenarios: sets of supercycles with their time shares, one module per scenario.

Each module defines SHEET, CATALOGUE, RUN_LENGTH_HOURS, SPS_AVAILABILITY, TIME_SHARES,
NOT_IN_AVERAGES, one function per supercycle, and supercycles() returning them all by name.
"""
from scenarios import (run3, run4_ship_ft4p8, run4_ship_ft9p6, run4_ship_ft9p6_pushed_sps_power,
                       run4_ship_5p2e13_ft9p6)

ALL = {
    'run3': run3,
    'run4_ship_ft4p8': run4_ship_ft4p8,
    'run4_ship_ft9p6': run4_ship_ft9p6,
    'run4_ship_ft9p6_pushed_sps_power': run4_ship_ft9p6_pushed_sps_power,
    'run4_ship_5p2e13_ft9p6': run4_ship_5p2e13_ft9p6,
}
