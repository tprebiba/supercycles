import pytest

from supercycles import CatalogueError, load_catalogue


def test_catalogue_loads_and_is_consistent():
    cat = load_catalogue()
    assert set(cat.machines) == {'PSB', 'PS', 'SPS'}
    assert len(cat.cycles) == 50


def test_keys_are_unique_where_old_names_collided():
    cat = load_catalogue()
    degauss = [c for c in cat.cycles.values() if c.name == 'deGauss']
    assert len({c.key for c in degauss}) == 3                 # three different cycles
    assert cat.cycle('PSB', 'HiRadMat').name == 'HiRadMat'    # was 'LHC' in the old database


def test_injections_reference_the_upstream_machine():
    cat = load_catalogue()
    sftpro = cat.cycle('SPS.SFTPRO')
    assert [(i.cycle, i.bp_offset) for i in sftpro.injections] == [('PS.MTE', -1), ('PS.MTE', 0)]
    lhc = cat.cycle('SPS', 'LHC_filling')
    assert [i.bp_offset for i in lhc.injections] == [-2, 1, 4, 7]


def test_numbers_are_floats():
    cat = load_catalogue()
    assert isinstance(cat.cycle('PS.EAST_T8').beam.intensity, float)      # '8e+11' in YAML
    assert cat.cycle('PS.EAST_T8').beam.delivered == pytest.approx(6.4e11)


def test_every_profile_spans_its_cycle_length():
    cat = load_catalogue()
    for cycle in cat.cycles.values():
        if cycle.profile:
            time_s, _ = cat.profile(cycle)
            assert time_s[-1] == pytest.approx(cat.length_s(cycle)), cycle.key


def test_unknown_cycle_gives_helpful_error():
    with pytest.raises(KeyError, match='SPS cycles'):
        load_catalogue().cycle('SPS', 'SFTPROO')


def test_typo_in_yaml_is_rejected(tmp_path):
    import shutil
    from supercycles.catalogue import CATALOGUE_DIR, Catalogue
    for name in ['complex.yaml', 'facilities.yaml', 'psb.yaml', 'ps.yaml', 'sps.yaml']:
        shutil.copy(f'{CATALOGUE_DIR}/{name}', tmp_path / name)
    text = (tmp_path / 'sps.yaml').read_text().replace('length_bp: 9', 'lenght_bp: 9', 1)
    (tmp_path / 'sps.yaml').write_text(text)
    with pytest.raises(CatalogueError, match='lenght_bp'):
        Catalogue(str(tmp_path))
