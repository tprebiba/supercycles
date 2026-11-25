"""
Run 3. No SHiP; SFTPRO with 4.8 s flat top (10.8 s cycle).

Reference: reference_docs/beam_sharing_table_example.xlsx, sheet 'Run 3 (no SHiP, SFTPRO FT=4.8s)'.
Every supercycle below reproduces the sheet BP by BP (checked by the tests), except where a
comment says otherwise.
"""
from supercycles import Supercycle, load_catalogue

SHEET = 'Run 3 (no SHiP, SFTPRO FT=4.8s)'
CATALOGUE = load_catalogue()

RUN_LENGTH_HOURS = 5148        # scheduled run length
SPS_AVAILABILITY = 0.8          # fraction of the run with beam in the SPS

# Share of the run given to each supercycle [%] (sums to 100). As in the sheet: the share of the
# SPS beam time x SPS_AVAILABILITY, and the rest of the run to the 'Downtime' supercycle, in which
# the PS and PSB still run part of the time.
TIME_SHARES = {
    'Physics':                     38.8 * SPS_AVAILABILITY,
    'Physics with parallel MD':    20.3 * SPS_AVAILABILITY,
    'LHC filling':                 14 * SPS_AVAILABILITY,
    'LHC setup':                   5 * SPS_AVAILABILITY,
    'Dedicated MD':                4.4 * SPS_AVAILABILITY,
    'Thursday MD (long parallel)': 2.6 * SPS_AVAILABILITY,
    'AWAKE':                       8 * SPS_AVAILABILITY,
    'AWAKE with parallel MD':      2.9 * SPS_AVAILABILITY,
    'HiRadMat':                    3 * SPS_AVAILABILITY,
    'Scrubbing':                   1 * SPS_AVAILABILITY,
    'Downtime':                    100 * (1 - SPS_AVAILABILITY),
}

# Supercycles left out of the averaged fluxes and currents (as in the sheet)
NOT_IN_AVERAGES = ['Dedicated MD', 'Downtime']


def physics():
    """SPS: SFTPRO + deGauss + SFTPRO + deGauss + SFTPRO + deGauss."""
    sc = Supercycle('Physics', period_bp=36, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('SPS', 'deGauss')
    sc.add('SPS', 'SFTPRO')
    sc.add('SPS', 'deGauss')
    sc.add('SPS', 'SFTPRO')
    sc.add('SPS', 'deGauss')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'EAST_T9'), (8, 'TOF'), (9, 'ZERO'), (10, 'ZERO'),
                 (11, 'ZERO'), (14, 'EAST_T8'), (16, 'TOF'), (17, 'EAST_TN'), (19, 'ZERO'),
                 (20, 'EAST_T8'), (22, 'TOF'), (23, 'ZERO'), (26, 'EAST_T8'), (28, 'TOF'),
                 (29, 'EAST_T9'), (31, 'ZERO'), (32, 'TOF'), (33, 'ZERO'), (34, 'ZERO'), (35, 'ZERO')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


def physics_with_parallel_md():
    """SPS: SFTPRO + MD_parallel + SFTPRO + MD_parallel + SFTPRO + MD_parallel."""
    sc = Supercycle('Physics with parallel MD', period_bp=45, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('SPS', 'MD_parallel')
    sc.add('SPS', 'SFTPRO')
    sc.add('SPS', 'MD_parallel')
    sc.add('SPS', 'SFTPRO')
    sc.add('SPS', 'MD_parallel')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'EAST_T9'), (8, 'TOF'), (11, 'MD'), (14, 'ZERO'),
                 (17, 'TOF'), (18, 'EAST_TN'), (20, 'ZERO'), (21, 'TOF'), (22, 'EAST_T9'),
                 (26, 'EAST_T8'), (28, 'TOF'), (29, 'ZERO'), (32, 'EAST_T8'), (34, 'TOF'),
                 (35, 'EAST_T8'), (37, 'EAST_T9'), (41, 'EAST_T8'), (43, 'EAST_TN')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 12)
    sc.fill('PSB', 'ISOLDE')
    return sc


def lhc_filling():
    """SPS: SFTPRO + LHC_filling + deGauss."""
    sc = Supercycle('LHC filling', period_bp=32, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('SPS', 'LHC_filling')
    sc.add('SPS', 'deGauss')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T9'), (4, 'TOF'), (5, 'EAST_T8'), (7, 'dG'), (20, 'EAST_T8'),
                 (22, 'EAST_TN'), (24, 'EAST_T9'), (26, 'TOF'), (27, 'TOF'), (28, 'EAST_T8'),
                 (30, 'EAST_TN')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


def lhc_setup():
    """SPS: SFTPRO + LHC_pilot + deGauss + SFTPRO + LHC_pilot + deGauss."""
    sc = Supercycle('LHC setup', period_bp=46, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('SPS', 'LHC_pilot')
    sc.add('SPS', 'deGauss')
    sc.add('SPS', 'SFTPRO')
    sc.add('SPS', 'LHC_pilot')
    sc.add('SPS', 'deGauss')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'TOF'), (3, 'EAST_T8'), (5, 'EAST_T9'), (7, 'TOF'), (8, 'dG'), (11, 'EAST_T8'),
                 (13, 'ZERO'), (14, 'EAST_TN'), (16, 'ZERO'), (17, 'EAST_T9'), (19, 'MD_short'),
                 (21, 'EAST_T8'), (25, 'ZERO'), (26, 'EAST_TN'), (28, 'EAST_T8'), (30, 'TOF'),
                 (31, 'dG'), (34, 'EAST_T8'), (36, 'TOF'), (37, 'EAST_TN'), (39, 'TOF'),
                 (40, 'EAST_T9'), (42, 'ZERO'), (43, 'ZERO'), (44, 'EAST_T8')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 19)
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
    """SPS: SFTPRO + MD_dedicated + deGauss."""
    sc = Supercycle('Thursday MD (long parallel)', period_bp=32, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('SPS', 'MD_dedicated')
    sc.add('SPS', 'deGauss')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T9'), (4, 'TOF'), (5, 'EAST_T8'), (7, 'dG'), (20, 'EAST_T8'),
                 (22, 'EAST_TN'), (24, 'EAST_T9'), (26, 'TOF'), (27, 'TOF'), (28, 'EAST_T8'),
                 (30, 'EAST_TN')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


def awake():
    """SPS: SFTPRO + AWAKE + deGauss + SFTPRO + AWAKE + deGauss."""
    sc = Supercycle('AWAKE', period_bp=36, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('SPS', 'AWAKE')
    sc.add('SPS', 'deGauss')
    sc.add('SPS', 'SFTPRO')
    sc.add('SPS', 'AWAKE')
    sc.add('SPS', 'deGauss')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'TOF'), (3, 'EAST_T9'), (5, 'ZERO'), (6, 'ZERO'), (7, 'EAST_T8'), (11, 'EAST_T8'),
                 (13, 'TOF'), (14, 'ZERO'), (15, 'EAST_TN'), (17, 'TOF'), (20, 'EAST_T8'), (22, 'MD'),
                 (25, 'EAST_T9'), (29, 'EAST_T8'), (31, 'ZERO'), (32, 'TOF'), (33, 'TOF'),
                 (34, 'EAST_TN')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 23)
    sc.fill('PSB', 'ISOLDE')
    return sc


def awake_with_parallel_md():
    """SPS: SFTPRO + AWAKE + MD_parallel + SFTPRO + AWAKE + MD_parallel."""
    sc = Supercycle('AWAKE with parallel MD', period_bp=42, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('SPS', 'AWAKE')
    sc.add('SPS', 'MD_parallel')
    sc.add('SPS', 'SFTPRO')
    sc.add('SPS', 'AWAKE')
    sc.add('SPS', 'MD_parallel')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T9'), (4, 'EAST_TN'), (6, 'TOF'), (7, 'EAST_T8'), (11, 'EAST_T8'),
                 (13, 'TOF'), (14, 'TOF'), (17, 'EAST_TN'), (19, 'TOF'), (20, 'ZERO'), (23, 'EAST_T8'),
                 (25, 'EAST_T9'), (27, 'MD'), (32, 'EAST_T8'), (34, 'EAST_TN'), (38, 'EAST_T9'),
                 (40, 'EAST_T8')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 28)
    sc.fill('PSB', 'ISOLDE')
    return sc


def hiradmat():
    """SPS: SFTPRO + HIRADMT2 + deGauss."""
    sc = Supercycle('HiRadMat', period_bp=32, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('SPS', 'HIRADMT2')
    sc.add('SPS', 'deGauss')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T9'), (4, 'TOF'), (5, 'EAST_T8'), (7, 'dG'), (20, 'EAST_T8'),
                 (22, 'EAST_TN'), (24, 'EAST_T9'), (26, 'TOF'), (27, 'TOF'), (28, 'EAST_T8'),
                 (30, 'EAST_TN')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


def scrubbing():
    """SPS: SFTPRO + Scrubbing + deGauss."""
    sc = Supercycle('Scrubbing', period_bp=32, catalogue=CATALOGUE)

    # SPS (the PS and PSB cycles injecting into them are placed automatically)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('SPS', 'Scrubbing')
    sc.add('SPS', 'deGauss')

    # PS: the BPs not used by the injections for the SPS
    ps_cycles = [(2, 'EAST_T9'), (4, 'TOF'), (5, 'EAST_T8'), (7, 'dG'), (20, 'EAST_T8'),
                 (22, 'EAST_TN'), (24, 'EAST_T9'), (26, 'TOF'), (27, 'TOF'), (28, 'EAST_T8'),
                 (30, 'EAST_TN')]
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
                 (26, 'TOF'), (27, 'EAST_T8'), (29, 'MD'), (32, 'EAST_T8'), (34, 'EAST_T9')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: MD, then every remaining BP to ISOLDE
    sc.add('PSB', 'MD', 11)
    sc.add('PSB', 'MD', 15)
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
