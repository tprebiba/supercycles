"""
Run 4 with SHiP. SFTPRO with 9.6 s flat top (SFTLONG, 15.6 s cycle).

Reference: reference_docs/beam_sharing_table_example.xlsx, sheet 'Run 4 with SHiP (SFTPRO FT=9.6s'.
Every supercycle below reproduces the sheet BP by BP (checked by the tests), except where a
comment says otherwise.
"""
from supercycles import Supercycle, load_catalogue

SHEET = 'Run 4 with SHiP (SFTPRO FT=9.6s'
CATALOGUE = load_catalogue()

RUN_LENGTH_HOURS = 5148        # scheduled run length
SPS_AVAILABILITY = 0.8          # fraction of the run with beam in the SPS

# Share of the run given to each supercycle [%] (sums to 100). As in the sheet: the share of the
# SPS beam time x SPS_AVAILABILITY, and the rest of the run to the 'Downtime' supercycle, in which
# the PS and PSB still run part of the time.
TIME_SHARES = {
    'Physics':                     28.5 * SPS_AVAILABILITY,
    'Physics with parallel MD':    20.8 * SPS_AVAILABILITY,
    'LHC filling':                 14.5 * SPS_AVAILABILITY,
    'LHC setup':                   10 * SPS_AVAILABILITY,
    'Dedicated MD':                5 * SPS_AVAILABILITY,
    'Thursday MD (long parallel)': 4 * SPS_AVAILABILITY,
    'AWAKE':                       8.8 * SPS_AVAILABILITY,
    'AWAKE with parallel MD':      3.9 * SPS_AVAILABILITY,
    'HiRadMat':                    3.5 * SPS_AVAILABILITY,
    'Scrubbing':                   1 * SPS_AVAILABILITY,
    'Downtime':                    100 * (1 - SPS_AVAILABILITY),
}

# Supercycles left out of the averaged fluxes and currents (as in the sheet)
NOT_IN_AVERAGES = ['Dedicated MD', 'Downtime']


def physics():
    """SPS: SFTLONG + 9x Zero + 5x SHiP."""
    sc = Supercycle('Physics', period_bp=52, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTLONG', 1)
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'TOF'), (7, 'EAST_T8'), (9, 'ZERO'), (10, 'TOF'),
                 (11, 'EAST_T8'), (13, 'TOF'), (14, 'TOF'), (15, 'ZERO'), (16, 'ZERO'), (17, 'TOF'),
                 (18, 'ZERO'), (19, 'ZERO'), (20, 'EAST_T9'), (24, 'EAST_T9'), (26, 'ZERO'),
                 (27, 'TOF'), (30, 'EAST_T8'), (32, 'EAST_TN'), (36, 'ZERO'), (37, 'ZERO'),
                 (38, 'EAST_T8'), (42, 'EAST_T9'), (44, 'ZERO'), (45, 'TOF'), (48, 'EAST_T8'),
                 (50, 'EAST_TN')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


def physics_with_parallel_md():
    """SPS: SFTLONG + MD_parallel + 3x Zero + 5x SHiP."""
    sc = Supercycle('Physics with parallel MD', period_bp=52, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTLONG', 1)
    sc.add('SPS', 'MD_parallel')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'TOF'), (7, 'EAST_T8'), (9, 'TOF'), (10, 'TOF'),
                 (11, 'EAST_T8'), (15, 'TOF'), (16, 'MD'), (19, 'ZERO'), (20, 'EAST_T9'),
                 (24, 'EAST_T9'), (26, 'ZERO'), (27, 'ZERO'), (30, 'EAST_T8'), (32, 'EAST_TN'),
                 (36, 'TOF'), (37, 'ZERO'), (38, 'EAST_T8'), (42, 'EAST_T9'), (44, 'TOF'), (45, 'ZERO'),
                 (48, 'EAST_T8'), (50, 'EAST_TN')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 17)
    sc.fill('PSB', 'ISOLDE')
    return sc


def lhc_filling():
    """SPS: 2x SHiP + LHC_filling."""
    sc = Supercycle('LHC filling', period_bp=32, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SHiP', 1)
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'LHC_filling')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'TOF'), (5, 'TOF'), (8, 'EAST_TN'), (10, 'dG'), (23, 'EAST_T8'),
                 (25, 'TOF'), (26, 'TOF'), (27, 'EAST_T9'), (29, 'TOF'), (30, 'EAST_T8')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


def lhc_setup():
    """SPS: 4x SHiP + LHC_pilot_2inj."""
    sc = Supercycle('LHC setup', period_bp=35, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SHiP', 1)
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'LHC_pilot_2inj')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (8, 'TOF'), (9, 'TOF'), (10, 'EAST_T8'),
                 (14, 'EAST_T9'), (16, 'EAST_TN'), (20, 'EAST_T8'), (22, 'TOF'), (23, 'dG'),
                 (28, 'EAST_T8'), (30, 'EAST_T9'), (32, 'MD_short'), (34, 'TOF')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 32)
    sc.fill('PSB', 'ISOLDE')
    return sc


def dedicated_md():
    """SPS: 2x MD_dedicated."""
    sc = Supercycle('Dedicated MD', period_bp=40, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'MD_dedicated', 2)
    sc.add('SPS', 'MD_dedicated')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(12, 'MD_short'), (14, 'TOF'), (15, 'EAST_T9'), (17, 'EAST_T8'), (19, 'dG'),
                 (32, 'MD_short'), (34, 'TOF'), (35, 'EAST_TN'), (37, 'TOF'), (38, 'TOF'), (39, 'dG')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 4)
    sc.add('PSB', 'MD', 12)
    sc.add('PSB', 'MD', 32)
    sc.fill('PSB', 'ISOLDE')
    return sc


def thursday_md():
    """SPS: 5x SHiP + MD_dedicated."""
    sc = Supercycle('Thursday MD (long parallel)', period_bp=50, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SHiP', 1)
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'MD_dedicated')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (8, 'TOF'), (9, 'TOF'), (10, 'EAST_T8'),
                 (14, 'MD_short'), (16, 'EAST_T8'), (20, 'EAST_T9'), (22, 'EAST_T8'), (26, 'TOF'),
                 (27, 'TOF'), (28, 'dG'), (41, 'EAST_T8'), (43, 'EAST_T9'), (45, 'TOF'),
                 (46, 'EAST_TN'), (48, 'EAST_T8')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 14)
    sc.fill('PSB', 'ISOLDE')
    return sc


def awake():
    """SPS: SFTLONG + AWAKE + 3x Zero + 3x SHiP + AWAKE."""
    sc = Supercycle('AWAKE', period_bp=46, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTLONG', 1)
    sc.add('SPS', 'AWAKE')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'AWAKE')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'TOF'), (7, 'EAST_T8'), (9, 'EAST_T9'),
                 (11, 'EAST_T8'), (15, 'TOF'), (16, 'MD'), (19, 'EAST_T8'), (21, 'TOF'),
                 (24, 'EAST_TN'), (26, 'EAST_TN'), (30, 'ZERO'), (31, 'TOF'), (32, 'EAST_T8'),
                 (36, 'EAST_T9'), (38, 'ZERO'), (39, 'TOF'), (42, 'EAST_T8'), (44, 'EAST_T9')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 17)
    sc.fill('PSB', 'ISOLDE')
    return sc


def awake_with_parallel_md():
    """SPS: SFTLONG + AWAKE + MD_parallel + 2x SHiP + AWAKE."""
    sc = Supercycle('AWAKE with parallel MD', period_bp=43, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTLONG', 1)
    sc.add('SPS', 'AWAKE')
    sc.add('SPS', 'MD_parallel')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'AWAKE')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'TOF'), (7, 'EAST_TN'), (9, 'EAST_T9'),
                 (11, 'EAST_T8'), (15, 'TOF'), (16, 'MD'), (21, 'EAST_T8'), (23, 'EAST_TN'),
                 (27, 'EAST_T8'), (29, 'EAST_T9'), (33, 'TOF'), (34, 'ZERO'), (35, 'EAST_T8'),
                 (39, 'EAST_T9'), (41, 'TOF'), (42, 'ZERO')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 17)
    sc.fill('PSB', 'ISOLDE')
    return sc


def hiradmat():
    """SPS: SFTLONG + HIRADMT2 + 2x SHiP."""
    sc = Supercycle('HiRadMat', period_bp=45, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTLONG', 1)
    sc.add('SPS', 'HIRADMT2')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'TOF'), (7, 'EAST_T9'), (9, 'EAST_T8'), (11, 'dG'),
                 (24, 'EAST_T8'), (26, 'EAST_T9'), (28, 'TOF'), (29, 'EAST_TN'), (31, 'EAST_T8'),
                 (35, 'TOF'), (36, 'TOF'), (37, 'EAST_T8'), (41, 'TOF'), (42, 'TOF'), (43, 'ZERO'),
                 (44, 'ZERO')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


def scrubbing():
    """SPS: 5x SHiP + Scrubbing."""
    sc = Supercycle('Scrubbing', period_bp=50, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SHiP', 1)
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'Scrubbing')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (8, 'EAST_T9'), (10, 'EAST_T8'), (14, 'EAST_TN'),
                 (16, 'EAST_T8'), (20, 'EAST_T9'), (22, 'EAST_T8'), (26, 'TOF'), (27, 'EAST_T8'),
                 (41, 'EAST_T8'), (43, 'EAST_TN'), (45, 'TOF'), (46, 'TOF'), (47, 'EAST_T9'),
                 (49, 'TOF')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


def downtime():
    """SPS down; PS down 18 and PSB down 9 of the 36 BP (temporary model, as in the sheet)."""
    sc = Supercycle('Downtime', period_bp=36, catalogue=CATALOGUE)

    # Downtime: BPs without beam (BP 0 = BP period, BP -1 = BP period - 1)
    for bp in range(1, 37):
        sc.add('SPS', 'Downtime', bp)
    for bp in range(0, 18):
        sc.add('PS', 'Downtime', bp)
    for bp in range(-1, 8):
        sc.add('PSB', 'Downtime', bp)

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(18, 'EAST_T8'), (20, 'TOF'), (21, 'EAST_TN'), (23, 'TOF'), (24, 'EAST_T9'),
                 (26, 'TOF'), (27, 'EAST_T8'), (29, 'TOF'), (30, 'MD_short'), (32, 'EAST_T8'),
                 (34, 'EAST_T9')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 11)
    sc.add('PSB', 'MD', 30)
    sc.fill('PSB', 'ISOLDE')
    return sc


def supercycles():
    """All supercycles of the scenario, by name."""
    return {sc.name: sc for sc in [
        physics(),
        physics_with_parallel_md(),
        lhc_filling(),
        lhc_setup(),
        dedicated_md(),
        thursday_md(),
        awake(),
        awake_with_parallel_md(),
        hiradmat(),
        scrubbing(),
        downtime(),
    ]}


if __name__ == '__main__':
    for sc in supercycles().values():
        print(sc, end='\n\n')
