"""
Run 4 with 5.2e13 SHiP. SHiP at 5.2e13 p per cycle; SFTPRO with 9.6 s flat top (SFTLONG, 15.6 s cycle).

Reference: reference_docs/beam_sharing_table_example.xlsx, sheet 'Run 4 with 5.2e13 SHiP (SFTPRO '.
Every supercycle below reproduces the sheet BP by BP (checked by the tests), except where a
comment says otherwise.
"""
from supercycles import Supercycle, load_catalogue

SHEET = 'Run 4 with 5.2e13 SHiP (SFTPRO '
CATALOGUE = load_catalogue().with_beam('SPS.SHiP', intensity=5.2e13)

RUN_LENGTH_HOURS = 5148        # scheduled run length
SPS_AVAILABILITY = 0.8          # fraction of the run with beam in the SPS

# Share of the run given to each supercycle [%] (sums to 100). As in the sheet: the share of the
# SPS beam time x SPS_AVAILABILITY, and the rest of the run to the 'Downtime' supercycle, in which
# the PS and PSB still run part of the time.
# This sheet gives the shares directly as % of the run.
# As in the sheet, they add up to 99.99 % (rounding).
TIME_SHARES = {
    'Physics':                     21.59,
    'Physics with parallel MD':    15.8,
    'LHC filling':                 12,
    'LHC setup':                   8,
    'Dedicated MD':                4.31,
    'Thursday MD (long parallel)': 2.91,
    'AWAKE':                       8.65,
    'AWAKE with parallel MD':      3.09,
    'HiRadMat':                    2.8,
    'Scrubbing':                   0.84,
    'Downtime':                    100 * (1 - SPS_AVAILABILITY),
}

# Supercycles left out of the averaged fluxes and currents (as in the sheet)
NOT_IN_AVERAGES = ['Dedicated MD', 'Downtime']


def physics():
    """SPS: SFTLONG + 9x Zero + 4x SHiP."""
    sc = Supercycle('Physics', period_bp=46, catalogue=CATALOGUE)

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

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'TOF'), (7, 'EAST_T9'), (9, 'ZERO'), (10, 'TOF'),
                 (11, 'EAST_T8'), (13, 'TOF'), (14, 'ZERO'), (15, 'EAST_TN'), (17, 'TOF'), (18, 'ZERO'),
                 (19, 'ZERO'), (20, 'EAST_T9'), (24, 'EAST_T8'), (26, 'ZERO'), (27, 'TOF'),
                 (30, 'EAST_TN'), (32, 'EAST_T8'), (36, 'MD_short'), (38, 'EAST_T9'), (42, 'EAST_T8'),
                 (44, 'ZERO'), (45, 'TOF')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 36)
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
                 (11, 'EAST_T8'), (15, 'TOF'), (16, 'ZERO'), (17, 'TOF'), (18, 'ZERO'), (19, 'ZERO'),
                 (20, 'EAST_T9'), (24, 'EAST_T9'), (26, 'ZERO'), (27, 'ZERO'), (30, 'EAST_T8'),
                 (32, 'EAST_TN'), (36, 'MD_short'), (38, 'EAST_T8'), (42, 'EAST_T9'), (44, 'TOF'),
                 (45, 'ZERO'), (48, 'EAST_T8'), (50, 'EAST_TN')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 36)
    sc.fill('PSB', 'ISOLDE')
    return sc


def lhc_filling():
    """SPS: SFTLONG + LHC_filling + SHiP."""
    sc = Supercycle('LHC filling', period_bp=39, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTLONG', 1)
    sc.add('SPS', 'LHC_filling')
    sc.add('SPS', 'SHiP')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_T9'), (6, 'EAST_T8'), (8, 'EAST_TN'), (10, 'TOF'),
                 (11, 'dG'), (24, 'EAST_T8'), (26, 'TOF'), (27, 'TOF'), (28, 'EAST_T9'), (30, 'TOF'),
                 (31, 'EAST_T8'), (35, 'EAST_TN'), (37, 'EAST_T8')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


def lhc_setup():
    """SPS: 2x SHiP + LHC_pilot_2inj + 2x SHiP + LHC_pilot_2inj."""
    sc = Supercycle('LHC setup', period_bp=46, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SHiP', 1)
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'LHC_pilot_2inj')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'LHC_pilot_2inj')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (8, 'TOF'), (9, 'EAST_T8'), (11, 'dG'),
                 (16, 'EAST_TN'), (18, 'EAST_T9'), (20, 'EAST_T8'), (22, 'TOF'), (25, 'EAST_T8'),
                 (27, 'EAST_T9'), (31, 'TOF'), (32, 'EAST_T8'), (34, 'dG'), (39, 'EAST_TN'),
                 (41, 'EAST_T9'), (43, 'EAST_T8'), (45, 'TOF')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
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
    """SPS: SFTLONG + MD_dedicated + 3x SHiP."""
    sc = Supercycle('Thursday MD (long parallel)', period_bp=51, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTLONG', 1)
    sc.add('SPS', 'MD_dedicated')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'EAST_T9'), (8, 'TOF'), (9, 'EAST_T8'), (11, 'dG'),
                 (24, 'EAST_T8'), (26, 'EAST_TN'), (28, 'EAST_T9'), (30, 'TOF'), (31, 'EAST_T8'),
                 (35, 'TOF'), (36, 'TOF'), (37, 'EAST_T8'), (41, 'EAST_T9'), (43, 'EAST_T8'),
                 (47, 'TOF'), (48, 'TOF'), (49, 'EAST_TN')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


def awake():
    """SPS: SFTLONG + AWAKE + 3x Zero + 2x SHiP + AWAKE."""
    # The sheet has a PSB cycle for the PS at BP 34 that no PS cycle uses:
    # here PSB BP 34 is ISOLDE (one ISOLDE cycle more than the sheet).
    sc = Supercycle('AWAKE', period_bp=40, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTLONG', 1)
    sc.add('SPS', 'AWAKE')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'Zero')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'AWAKE')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'TOF'), (7, 'EAST_T8'), (9, 'EAST_T9'),
                 (11, 'EAST_T8'), (15, 'TOF'), (16, 'MD_short'), (18, 'EAST_T8'), (20, 'EAST_T9'),
                 (24, 'EAST_TN'), (26, 'EAST_TN'), (30, 'ZERO'), (31, 'TOF'), (32, 'EAST_T8'),
                 (36, 'EAST_T9'), (38, 'ZERO'), (39, 'TOF')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 16)
    sc.fill('PSB', 'ISOLDE')
    return sc


def awake_with_parallel_md():
    """SPS: SFTLONG + AWAKE + MD_parallel + 3x SHiP."""
    sc = Supercycle('AWAKE with parallel MD', period_bp=43, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTLONG', 1)
    sc.add('SPS', 'AWAKE')
    sc.add('SPS', 'MD_parallel')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'TOF'), (7, 'EAST_TN'), (9, 'EAST_T9'),
                 (11, 'EAST_T8'), (15, 'TOF'), (16, 'MD_short'), (18, 'TOF'), (21, 'EAST_T8'),
                 (23, 'EAST_TN'), (27, 'EAST_T8'), (29, 'EAST_T9'), (33, 'TOF'), (34, 'ZERO'),
                 (35, 'EAST_T8'), (39, 'EAST_T9'), (41, 'ZERO'), (42, 'TOF')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 16)
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
    """SPS: SFTLONG + Scrubbing + 3x SHiP."""
    sc = Supercycle('Scrubbing', period_bp=51, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTLONG', 1)
    sc.add('SPS', 'Scrubbing')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')
    sc.add('SPS', 'SHiP')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'EAST_T9'), (8, 'TOF'), (9, 'EAST_T8'), (11, 'dG'),
                 (24, 'EAST_T8'), (26, 'EAST_TN'), (28, 'EAST_T9'), (30, 'TOF'), (31, 'EAST_T8'),
                 (35, 'TOF'), (36, 'TOF'), (37, 'EAST_T8'), (41, 'EAST_T9'), (43, 'EAST_T8'),
                 (47, 'TOF'), (48, 'TOF'), (49, 'EAST_TN')]
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
