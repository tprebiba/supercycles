import pytest

from supercycles import PlacementError, Supercycle


def test_injections_are_placed_with_wrap_around():
    sc = Supercycle('t', 36)
    sc.add('SPS', 'SFTPRO', 1)
    assert [p.start_bp for p in sc.placements_on('PS')] == [1, 36]      # BP 0 -> 36
    assert [p.start_bp for p in sc.placements_on('PSB')] == [35, 36]    # BP -1, 0 -> 35, 36


def test_add_without_start_appends_after_previous_cycle():
    sc = Supercycle('t', 36)
    sc.add('SPS', 'SFTPRO', 1)
    assert sc.add('SPS', 'deGauss').start_bp == 10
    assert sc.add('SPS', 'SFTPRO').start_bp == 13


def test_overlap_raises_and_changes_nothing():
    sc = Supercycle('t', 36)
    sc.add('SPS', 'SFTPRO', 1)
    sc.add('PS', 'EAST_T8', 12)                  # blocks the PS MTE needed by an SFTPRO at 13
    before = dict(sc.placements)
    with pytest.raises(PlacementError, match='injection for SPS.SFTPRO'):
        sc.add('SPS', 'SFTPRO', 13)
    assert sc.placements == before


def test_remove_takes_injections_along():
    sc = Supercycle('t', 36)
    sftpro = sc.add('SPS', 'SFTPRO', 1)
    assert len(sc.placements) == 5               # SFTPRO + 2 PS MTE + 2 PSB MTE
    sc.remove(sftpro)
    assert sc.placements == {}


def test_cycle_longer_than_period_is_refused():
    with pytest.raises(PlacementError, match='longer than the supercycle'):
        Supercycle('t', 10).add('SPS', 'LHC_filling', 1)


def test_validate_reports_power_limit_and_free_bps():
    sc = Supercycle('t', 9)
    sc.add('SPS', 'SFTPRO', 1)                   # 52.8 MW alone > 41.1 MW
    messages = [str(i) for i in sc.validate()]
    assert any('[error] SPS average power' in m for m in messages)
    assert any('PSB: 7 free BP(s)' in m for m in messages)


def test_copy_is_independent():
    sc = Supercycle('t', 36)
    sc.add('SPS', 'SFTPRO', 1)
    variant = sc.copy('variant')
    variant.add('SPS', 'deGauss')
    assert len(sc.placements) == 5 and len(variant.placements) == 6
