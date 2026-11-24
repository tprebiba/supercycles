"""
Typical Run 3 supercycles.

Reference: reference/beam_sharing_table_example.xlsx, sheet 'Run 3 (no SHiP, SFTPRO FT=4.8s)'.
BP numbers are those of the sheet (its first SPS cycle starts at BP 1; the sheet's
BP 0 and -1 columns are BP period and period-1 here, thanks to the wrap-around).

Each function returns a new Supercycle, so scenarios can be modified freely.
"""
from supercycles import Supercycle


def physics():
    """Physics: 3x (SFTPRO + deGauss) in the SPS, EAST/TOF in the PS, ISOLDE in the PSB."""
    sc = Supercycle('Physics', period_bp=36)

    # SPS: one after the other, starting at BP 1 (injections are placed automatically)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('SPS', 'deGauss')
    sc.add('SPS', 'SFTPRO')
    sc.add('SPS', 'deGauss')
    sc.add('SPS', 'SFTPRO')
    sc.add('SPS', 'deGauss')

    # PS: the BPs not used by the MTE injections for the SPS
    ps_cycles = [(2, 'EAST_T8'), (4, 'EAST_TN'), (6, 'EAST_T9'), (8, 'TOF'),
                 (9, 'ZERO'), (10, 'ZERO'), (11, 'ZERO'),
                 (14, 'EAST_T8'), (16, 'TOF'), (17, 'EAST_TN'), (19, 'ZERO'),
                 (20, 'EAST_T8'), (22, 'TOF'), (23, 'ZERO'),
                 (26, 'EAST_T8'), (28, 'TOF'), (29, 'EAST_T9'), (31, 'ZERO'),
                 (32, 'TOF'), (33, 'ZERO'), (34, 'ZERO'), (35, 'ZERO')]
    for start_bp, cycle_id in ps_cycles:
        sc.add('PS', cycle_id, start_bp)

    # PSB: every remaining BP goes to ISOLDE
    sc.fill('PSB', 'ISOLDE')
    return sc


if __name__ == '__main__':
    sc = physics()
    print(sc)
    for issue in sc.validate():
        print(issue)
    print(sc.facility_table())
