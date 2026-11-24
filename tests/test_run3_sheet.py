"""Regression: the model reproduces the Run 3 sheet of reference/beam_sharing_table_example.xlsx."""
import pytest

from scenarios import run3_typical
from tests.sheet_reader import read_block, supercycle_labels

SHEET = 'Run 3 (no SHiP, SFTPRO FT=4.8s)'


def test_physics_matches_sheet_bp_by_bp():
    sc = run3_typical.physics()
    period, sheet = read_block(SHEET, 'Physics')
    assert sc.period_bp == period == 36
    ours = supercycle_labels(sc)
    for machine in ['SPS', 'PS', 'PSB']:
        assert ours[machine] == sheet[machine], machine


def test_physics_is_valid():
    assert run3_typical.physics().validate() == []


def test_physics_deliverables_match_sheet():
    table = run3_typical.physics().facility_table().set_index('facility')
    # sheet: 17 ISOLDE cycles x 3.2e13 / 43.2 s, converted with e = 1.6e-19 -> 2.0148 uA
    assert table.loc['ISOLDE', 'cycles_per_supercycle'] == 17
    assert table.loc['ISOLDE', 'current_uA'] == pytest.approx(2.014815 * 1.602176634 / 1.6)
    # sheet formula (cells BK32..BM32): n_cycles * intensity * 0.8 / 43.2 s, intensity in p
    assert table.loc['EAST_T8', 'flux_p_per_s'] == pytest.approx(4 * 0.08e13 * 0.8 / 43.2)
    assert table.loc['EAST_T9', 'flux_p_per_s'] == pytest.approx(2 * 0.03e13 * 0.8 / 43.2)
    assert table.loc['EAST_TN', 'flux_p_per_s'] == pytest.approx(2 * 0.03e13 * 0.8 / 43.2)
    assert table.loc['NorthArea', 'cycles_per_supercycle'] == 3


def test_physics_sps_power_just_below_limit():
    power = run3_typical.physics().average_power_MW('SPS')
    assert power == pytest.approx((3 * 10.8 * 52.83 + 3 * 3.6 * 4.77) / 43.2)
    assert power < 41.1
