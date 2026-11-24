"""
Read a supercycle block of reference/beam_sharing_table_example.xlsx, and express a
Supercycle with the same labels, so that the two can be compared BP by BP.

Sheet layout (all sheets): column G holds the supercycle name on its SPS row; the PS and
PSB rows follow. A header row labelled 'BPs' in column H gives the BP number of each
column; the two columns before BP 1 are BP 0 and BP -1 (previous repetition). Labels are
written in the first BP of each cycle. A cycle feeding the next machine is labelled with
that machine's name ('SPS' in the PS row, 'PS' in the PSB row).
"""
import os

import openpyxl

WORKBOOK = os.path.join(os.path.dirname(__file__), '..', 'reference', 'beam_sharing_table_example.xlsx')

# catalogue key -> label used in the sheet (cycles not feeding another machine)
SHEET_LABELS = {
    'PSB.ISOLDE': 'ISO', 'PSB.MD': 'MD',
    'PS.EAST_T8': 'EAST T8', 'PS.EAST_T9': 'EAST T9', 'PS.EAST_TN': 'EAST TN',
    'PS.TOF': 'TOF', 'PS.ZERO': 'Zero', 'PS.MD': 'MD', 'PS.MD_short': 'MD',
    'SPS.SFTPRO': 'SFTPRO', 'SPS.deGauss': 'deGauss', 'SPS.LHC_filling': 'LHC',
    'SPS.LHC_pilot': 'LHC', 'SPS.AWAKE': 'AWAKE', 'SPS.MD_parallel': 'MD',
    'SPS.MD_dedicated': 'MD', 'SPS.HIRADMT2': 'HiRadMat', 'SPS.SHiP': 'SHiP', 'SPS.Zero': 'Zero',
}
_cache = {}


def _sheet(sheet_name):
    if WORKBOOK not in _cache:
        _cache[WORKBOOK] = openpyxl.load_workbook(WORKBOOK, data_only=True)
    return _cache[WORKBOOK][sheet_name]


def read_block(sheet_name, supercycle_name):
    """
    Return (period_bp, {machine: {bp: label}}) for one supercycle of the sheet,
    with BP 0, -1 wrapped to period, period-1.
    """
    ws = _sheet(sheet_name)
    sps_row = next(r for r in range(1, ws.max_row + 1) if ws.cell(r, 7).value == supercycle_name)
    header_row = max(r for r in range(1, sps_row) if ws.cell(r, 8).value == 'BPs')
    bp1_col = next(c for c in range(1, ws.max_column + 1) if ws.cell(header_row, c).value == 1)
    length_col = next(c for c in range(1, ws.max_column + 1)
                      if ws.cell(header_row - 1, c).value == 'SC length [s]')
    period = round(float(ws.cell(sps_row, length_col).value) / 1.2)

    rows = {}
    for machine, row in [('SPS', sps_row), ('PS', sps_row + 1), ('PSB', sps_row + 2)]:
        labels = {}
        for col in range(bp1_col - 2, bp1_col + period):
            value = ws.cell(row, col).value
            if value is None:
                continue
            bp = (col - bp1_col) % period + 1
            if bp in labels:
                raise ValueError(f'{supercycle_name} {machine}: two labels at BP {bp}')
            labels[bp] = str(value).strip()
        rows[machine] = labels
    return period, rows


def supercycle_labels(sc):
    """{machine: {start_bp: label}} of a Supercycle, using the sheet conventions."""
    rows = {}
    for machine in sc.machines:
        labels = {}
        for p in sc.placements_on(machine):
            if p.parent is not None:
                labels[p.start_bp] = sc.placements[p.parent].machine
            else:
                labels[p.start_bp] = SHEET_LABELS.get(p.cycle.key, p.cycle.key)
        rows[machine] = labels
    return rows
