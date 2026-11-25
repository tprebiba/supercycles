"""
Catalogue of the injector complex: machines, facilities and cycle types.

Everything is read from the YAML files in ``supercycles/data/catalogue/``; nothing is
hard-coded here. Objects are frozen dataclasses: a catalogue entry describes a
*kind* of cycle and is never modified by a supercycle that uses it.

Naming convention
-----------------
A cycle type is identified by its *key* ``'<MACHINE>.<id>'``, e.g. ``'SPS.SFTPRO'``.
The ``id`` is unique within a machine; the ``name`` is only a display label.

Example
-------
>>> from supercycles import load_catalogue
>>> cat = load_catalogue()
>>> sftpro = cat.cycle('SPS', 'SFTPRO')          # or cat.cycle('SPS.SFTPRO')
>>> sftpro.length_bp, cat.length_s(sftpro)
(9, 10.8)
"""
import copy
import dataclasses
import functools
import os
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
import yaml

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
CATALOGUE_DIR = os.path.join(PACKAGE_DIR, 'data', 'catalogue')
PROFILE_DIR = os.path.join(PACKAGE_DIR, 'data', 'profiles')


class CatalogueError(ValueError):
    """Raised when the catalogue files are inconsistent."""


# ---------------------------------------------------------------------------
# Catalogue entries
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Machine:
    name: str
    upstream: Optional[str]                          # machine injecting into this one
    average_power_limit_MW: Optional[float] = None   # supercycle-averaged power limit


@dataclass(frozen=True)
class Facility:
    id: str
    name: str
    machine: Optional[str]                           # machine delivering the beam (None = any)


@dataclass(frozen=True)
class Beam:
    destination: str                                 # Facility id
    intensity: Optional[float] = None                # protons (or charges) per cycle
    transmission: float = 1.0                        # fraction reaching the destination

    @property
    def delivered(self) -> Optional[float]:
        """Particles per cycle arriving at the destination (None if intensity unknown)."""
        if self.intensity is None:
            return None
        return self.intensity * self.transmission


@dataclass(frozen=True)
class Injection:
    cycle: str        # key of the upstream cycle type, e.g. 'PS.MTE'
    bp_offset: int    # start of the upstream cycle relative to the start of this cycle [BP]


@dataclass(frozen=True)
class CycleType:
    machine: str
    id: str
    name: str
    length_bp: int
    colour: str = 'white'
    user: Optional[str] = None                       # timing user
    average_power_MW: Optional[float] = None
    profile: Optional[str] = None                    # magnet current file in data/profiles/
    beam: Optional[Beam] = None                      # None = internal cycle (feeds the next machine)
    injections: tuple = ()                           # tuple of Injection
    downtime: bool = False                           # True: the machine has no beam during this cycle

    @property
    def key(self) -> str:
        return f'{self.machine}.{self.id}'

    def __repr__(self):
        return f'CycleType({self.key}, {self.length_bp} BP)'


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------
def _read_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def _build(cls, data, where):
    """Instantiate a dataclass from a dict, rejecting unknown keys (catches typos)."""
    allowed = set(cls.__dataclass_fields__)
    unknown = set(data) - allowed
    if unknown:
        raise CatalogueError(f'{where}: unknown field(s) {sorted(unknown)}; allowed: {sorted(allowed)}')
    return cls(**data)


class Catalogue:
    """
    All machines, facilities and cycle types of the complex.

    Attributes
    ----------
    basic_period_s : float
    max_supercycle_length_s : float
    machines : dict[str, Machine]      ordered from the first to the last machine of the chain
    facilities : dict[str, Facility]
    cycles : dict[str, CycleType]      keyed by 'MACHINE.id'
    """

    def __init__(self, directory=CATALOGUE_DIR, profile_directory=PROFILE_DIR):
        self.directory = directory
        self.profile_directory = profile_directory

        # complex and machines
        complex_data = _read_yaml(os.path.join(directory, 'complex.yaml'))
        self.basic_period_s = float(complex_data['basic_period_s'])
        self.max_supercycle_length_s = float(complex_data['max_supercycle_length_s'])
        self.machines = {}
        for name, data in complex_data['machines'].items():
            self.machines[name] = _build(Machine, dict(name=name, **data), f'machine {name}')

        # facilities
        self.facilities = {}
        for data in _read_yaml(os.path.join(directory, 'facilities.yaml')):
            facility = _build(Facility, data, f'facility {data.get("id")}')
            self.facilities[facility.id] = facility

        # cycle types, one file per machine (psb.yaml, ps.yaml, sps.yaml)
        self.cycles = {}
        for machine in self.machines:
            path = os.path.join(directory, f'{machine.lower()}.yaml')
            if not os.path.exists(path):
                continue
            for data in _read_yaml(path) or []:
                cycle = self._build_cycle(machine, data)
                if cycle.key in self.cycles:
                    raise CatalogueError(f'duplicate cycle id {cycle.key} in {path}')
                self.cycles[cycle.key] = cycle

        self.check()

    def _build_cycle(self, machine, data):
        data = dict(data)
        where = f'{machine} cycle {data.get("id")}'
        # YAML 1.1 reads numbers like 8e+11 (no decimal point) as strings: convert explicitly
        if data.get('average_power_MW') is not None:
            data['average_power_MW'] = float(data['average_power_MW'])
        if data.get('beam') is not None:
            beam = dict(data['beam'])
            for field in ['intensity', 'transmission']:
                if beam.get(field) is not None:
                    beam[field] = float(beam[field])
            data['beam'] = _build(Beam, beam, where + ' beam')
        injections = data.get('injections') or []
        data['injections'] = tuple(_build(Injection, inj, where + ' injection') for inj in injections)
        return _build(CycleType, dict(machine=machine, **data), where)

    # ------------------------------------------------------------------ checks
    def check(self):
        """Verify cross-references; raise CatalogueError listing every problem found."""
        problems = []
        for key, cycle in self.cycles.items():
            if cycle.length_bp < 1:
                problems.append(f'{key}: length_bp must be >= 1')
            if cycle.beam is not None and cycle.beam.destination not in self.facilities:
                problems.append(f'{key}: unknown destination {cycle.beam.destination!r}')
            if cycle.profile is not None and not os.path.exists(
                    os.path.join(self.profile_directory, cycle.profile)):
                problems.append(f'{key}: profile file {cycle.profile!r} not found')
            upstream_machine = self.machines[cycle.machine].upstream
            for injection in cycle.injections:
                if injection.cycle not in self.cycles:
                    problems.append(f'{key}: injection from unknown cycle {injection.cycle!r}')
                elif self.cycles[injection.cycle].machine != upstream_machine:
                    problems.append(f'{key}: injection from {injection.cycle} but the upstream '
                                    f'machine of {cycle.machine} is {upstream_machine}')
        if problems:
            raise CatalogueError('catalogue is inconsistent:\n  ' + '\n  '.join(problems))

    # ------------------------------------------------------------------ access
    def cycle(self, machine_or_key, cycle_id=None) -> CycleType:
        """Get a cycle type: ``cycle('SPS', 'SFTPRO')`` or ``cycle('SPS.SFTPRO')``."""
        key = machine_or_key if cycle_id is None else f'{machine_or_key}.{cycle_id}'
        if key not in self.cycles:
            machine = key.split('.')[0]
            available = [c.id for c in self.cycles.values() if c.machine == machine]
            raise KeyError(f'unknown cycle {key!r}; {machine} cycles: {available}')
        return self.cycles[key]

    def cycles_of(self, machine):
        """List of the cycle types of one machine, in file order."""
        return [c for c in self.cycles.values() if c.machine == machine]

    def length_s(self, cycle: CycleType) -> float:
        return round(cycle.length_bp * self.basic_period_s, 6)

    def profile(self, cycle: CycleType):
        """
        Magnet current profile of a cycle.
        Returns (time [s] from the cycle start, current [A]) as numpy arrays.
        """
        if cycle.profile is None:
            raise KeyError(f'{cycle.key} has no magnet current profile')
        # Two file formats exist: (time, current) with an 'X,Y' units row, and
        # (index, time, current) for the *_ESTIMATED files. In both, time [ms] and
        # current [A] are the last two columns; non-numeric rows are dropped.
        df = pd.read_csv(os.path.join(self.profile_directory, cycle.profile))
        df = df.apply(pd.to_numeric, errors='coerce').dropna()
        time_ms, current_A = df.iloc[:, -2].to_numpy(float), df.iloc[:, -1].to_numpy(float)
        return time_ms / 1e3, current_A

    def with_beam(self, cycle_key: str, intensity: Optional[float] = None,
                  transmission: Optional[float] = None) -> 'Catalogue':
        """
        Copy of the catalogue in which the beam of one cycle type is changed.
        Use it to state a scenario assumption explicitly, e.g.
            cat = load_catalogue().with_beam('SPS.SHiP', intensity=5.2e13)
        The original catalogue is not modified.
        """
        cycle = self.cycle(cycle_key)
        if cycle.beam is None:
            raise ValueError(f'{cycle_key} has no beam to modify')
        changes = {}
        if intensity is not None:
            changes['intensity'] = float(intensity)
        if transmission is not None:
            changes['transmission'] = float(transmission)
        new_cycle = dataclasses.replace(cycle, beam=dataclasses.replace(cycle.beam, **changes))

        new = copy.copy(self)
        new.cycles = dict(self.cycles)
        new.cycles[cycle.key] = new_cycle
        return new

    def to_dataframe(self) -> pd.DataFrame:
        """Overview table of all cycle types."""
        rows = []
        for cycle in self.cycles.values():
            rows.append({
                'key': cycle.key,
                'name': cycle.name,
                'length_bp': cycle.length_bp,
                'length_s': self.length_s(cycle),
                'user': cycle.user,
                'destination': cycle.beam.destination if cycle.beam else None,
                'intensity': cycle.beam.intensity if cycle.beam else None,
                'transmission': cycle.beam.transmission if cycle.beam else None,
                'average_power_MW': cycle.average_power_MW,
                'injections': ', '.join(f'{i.cycle}@{i.bp_offset:+d}' for i in cycle.injections),
                'downtime': cycle.downtime,
            })
        return pd.DataFrame(rows)


@functools.lru_cache(maxsize=None)
def load_catalogue(directory=CATALOGUE_DIR) -> Catalogue:
    """Load (once) and return the catalogue stored in ``directory``."""
    return Catalogue(directory)
