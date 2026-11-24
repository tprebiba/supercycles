# Supercycles Modeling and Beam Sharing in the CERN Injectors

A Python package for modeling the supercycles of the CERN proton injector complex (PSB, PS and SPS):
how the basic periods are shared between cycles, and what each facility receives.

<br/><img src='images/run3_physics_new_core.png' width='850'>

**Contact for corrections & suggestions**: [tirsi.prebibaj@cern.ch](mailto:tirsi.prebibaj@cern.ch)


## Installation

```
pip install git+https://github.com/tprebiba/supercycles.git
```

Requirements: Python ≥ 3.8, `numpy`, `scipy`, `pandas`, `matplotlib`, `pyyaml` (and `openpyxl` for the tests).


## Structure

```
supercycles/
    catalogue.py               Catalogue, CycleType, Beam, Injection, Facility, Machine
    supercycle.py              Supercycle, Placement, Issue, PlacementError
    plotting.py                plot_supercycle, plot_magnet_current
    data/catalogue/*.yaml      machines & limits, facilities, cycle types of PSB / PS / SPS
    data/profiles/*.csv        SPS magnet current profiles
scenarios/run3_typical.py      Run 3 supercycles
examples/                      01_catalogue, 02_build_supercycle, 03_checks_and_deliverables, 04_plotting
reference/                     beam_sharing_table_example.xlsx (the spreadsheet model used as reference)
tests/                         pytest suite, incl. a BP-by-BP comparison with the reference spreadsheet
```

### Catalogue
All data lives in YAML files, not in the code. Every cycle type has a unique key `MACHINE.id`
(e.g. `SPS.SFTPRO`), a length in basic periods (1 BP = 1.2 s), its beam (destination facility,
intensity, transmission) and an explicit list of the upstream cycles injecting into it:

```yaml
- id: SFTPRO
  length_bp: 9
  average_power_MW: 52.83
  profile: SFTPRO1_10point8.csv
  beam: {destination: NorthArea, intensity: 4.2e+13, transmission: 0.92169}
  injections:
    - {cycle: PS.MTE, bp_offset: -1}     # relative to the start of the SFTPRO cycle
    - {cycle: PS.MTE, bp_offset: 0}
```

Unknown fields (typos), unknown destinations, missing profile files and injections from the wrong
machine are rejected when the catalogue is loaded.

### Supercycle
- Fixed period in BP, common to all machines. The supercycle repeats: BP 0 is the last BP of the
  previous repetition (wrap-around), so the injections of the first SPS cycle sit at the end of the
  PS and PSB sequences, as in operation.
- The only stored state is the list of placements (cycle type, start BP, parent). Timelines, counts,
  power and fluxes are computed from it.
- `add()` places the injections recursively and either succeeds completely or changes nothing.
  `remove()` takes the injections along.
- `validate()` returns the problems found: length limit, SPS power limit, free BPs, missing injections.

```python
from supercycles import Supercycle

sc = Supercycle('Physics', period_bp=36)
sc.add('SPS', 'SFTPRO', 1)      # + 2x PS.MTE (BP 36, 1) + 2x PSB.MTE (BP 35, 36)
sc.add('SPS', 'deGauss')        # right after the previous SPS cycle
sc.fill('PSB', 'ISOLDE')        # every free PSB BP
print(sc)                       # text grid
sc.validate()                   # [] if everything is fine
sc.facility_table()             # cycles, protons, flux and current per facility
```

Run the tests with `python -m pytest tests`.


## Relevant presentations and notes

- **SPS Operation and Future Proton Sharing Scenarios for the ECN3 facility**
  [CERN-PBC-NOTE 2023001](https://cds.cern.ch/record/2848908/files/CERN-PBC-Notes-2023-001.pdf)

- **Proton sharing in the injector complex post LS3**, Chamonix Workshop 2025
  [Online access (restricted)](https://indi.to/RT4HJ)
