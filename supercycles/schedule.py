"""
A schedule: how a run is shared between supercycles, and what it delivers over the run.

Model (same as the reference spreadsheet)
-----------------------------------------
* The run lasts ``run_length_hours``; ``time_shares`` gives the % of the run played by each
  supercycle (they sum to 100).
* Downtime is part of the supercycles: a supercycle can contain 'Downtime' cycles (no beam)
  in any machine. E.g. the spreadsheet's 'Downtime' supercycle has the SPS down all the time,
  the PS half and the PSB a quarter of the time. The availability of each machine follows.
* Each supercycle is repeated  run length x share / supercycle length  times.
* Cycles and protons over the run are summed over all supercycles. Averaged fluxes and
  currents leave out the supercycles listed in ``not_in_averages`` (in the spreadsheet:
  'Dedicated MD' and 'Downtime'), and are averaged over the time of the remaining ones.

Example
-------
>>> import scenarios
>>> schedule = Schedule.from_scenario(scenarios.run3)
>>> schedule.availability('PS')     # 0.9 for the spreadsheet scenarios
>>> schedule.supercycle_table()     # share, repetitions, hours per supercycle
>>> schedule.facility_table()       # cycles, protons and average current per facility

Editing, saving, comparing
--------------------------
A Schedule holds everything that defines a scenario, so it is also what is edited and saved:
>>> variant = schedule.copy('run3 with more AWAKE')
>>> variant.supercycles['Physics'].insert('SPS', 'AWAKE')     # lengthens 'Physics' by 6 BP
>>> variant.set_share('AWAKE', 10)
>>> variant.save('run3_more_awake.yaml')                       # Schedule.load(path) reads it back
>>> compare_schedules(schedule, variant)['facilities']         # side by side, with changes
"""
import os
from typing import Optional

import numpy as np
import pandas as pd
import yaml

from supercycles._version import __version__
from supercycles.catalogue import Catalogue, load_catalogue
from supercycles.supercycle import ELEMENTARY_CHARGE, Supercycle


# ---------------------------------------------------------------------------
# YAML layout of the scenario files
# ---------------------------------------------------------------------------
class _OneLine:
    """Marks a dict or list to be written on a single line ({a: 1, b: 2} / [x, y])."""
    def __init__(self, value):
        self.value = value


class _ScenarioDumper(yaml.SafeDumper):
    """Readable scenario files: one-line rows, multi-line text as a block, 12-digit floats."""


def _represent_one_line(dumper, data):
    if isinstance(data.value, dict):
        return dumper.represent_mapping('tag:yaml.org,2002:map', data.value, flow_style=True)
    return dumper.represent_sequence('tag:yaml.org,2002:seq', data.value, flow_style=True)


def _represent_str(dumper, text):
    style = '|' if '\n' in text else None
    return dumper.represent_scalar('tag:yaml.org,2002:str', text, style=style)


def _represent_float(dumper, value):
    text = f'{value:.12g}'
    if 'e' in text and '.' not in text.split('e')[0]:
        text = text.replace('e', '.0e')            # YAML 1.1 needs a dot to read 1e+13 as a float
    elif text.lstrip('-').isdigit():
        text += '.0'
    if value != value:                             # NaN
        text = '.nan'
    return dumper.represent_scalar('tag:yaml.org,2002:float', text)


_ScenarioDumper.add_representer(_OneLine, _represent_one_line)
_ScenarioDumper.add_representer(str, _represent_str)
_ScenarioDumper.add_representer(float, _represent_float)


class Schedule:

    def __init__(self, supercycles: dict, time_shares: dict, run_length_hours: float,
                 not_in_averages=(), name: str = '', description: str = '', reference: str = '',
                 catalogue: Optional[Catalogue] = None):
        """
        supercycles      : name -> Supercycle (the order is kept: it is the display order)
        time_shares      : name -> % of the run
        run_length_hours : scheduled length of the run
        not_in_averages  : names of the supercycles left out of the averaged fluxes and currents
        description      : free text (e.g. the docstring of a scenario module)
        reference        : where the scenario comes from (e.g. the sheet of the reference spreadsheet)
        catalogue        : catalogue for new supercycles; default: that of the first supercycle
        """
        mismatch = set(time_shares) ^ set(supercycles)
        if mismatch:
            raise ValueError(f'time shares and supercycles do not match: {sorted(mismatch)}')
        unknown = set(not_in_averages) - set(supercycles)
        if unknown:
            raise ValueError(f'not_in_averages: unknown supercycles {sorted(unknown)}')
        self.name = name
        self.description = description
        self.reference = reference
        self.supercycles = dict(supercycles)         # name -> Supercycle
        self.time_shares = dict(time_shares)         # name -> % of the run
        self.run_length_hours = float(run_length_hours)
        self.not_in_averages = list(not_in_averages)
        if catalogue is None:
            catalogue = next(iter(supercycles.values())).catalogue if supercycles else load_catalogue()
        self.catalogue = catalogue

    @classmethod
    def from_scenario(cls, module) -> 'Schedule':
        """Build a schedule from a module of the scenarios package."""
        return cls(module.supercycles(), module.TIME_SHARES, module.RUN_LENGTH_HOURS,
                   not_in_averages=getattr(module, 'NOT_IN_AVERAGES', ()),
                   name=module.__name__.split('.')[-1],
                   description=(module.__doc__ or '').strip(),
                   reference=getattr(module, 'SHEET', ''),
                   catalogue=getattr(module, 'CATALOGUE', None))

    @classmethod
    def empty(cls, name: str, run_length_hours: float, catalogue: Optional[Catalogue] = None) -> 'Schedule':
        """A scenario without supercycles, to be built from scratch."""
        return cls({}, {}, run_length_hours, name=name, catalogue=catalogue)

    def __repr__(self):
        return (f"Schedule('{self.name}', {len(self.supercycles)} supercycles, "
                f"{self.run_length_hours:g} h, shares sum to {self.total_share:g} %)")

    # ------------------------------------------------------------------ editing
    # The GUI edits a scenario only through these methods (and those of Supercycle).

    def copy(self, name: Optional[str] = None) -> 'Schedule':
        """Independent copy: the supercycles are copied too."""
        return Schedule({n: sc.copy() for n, sc in self.supercycles.items()}, self.time_shares,
                        self.run_length_hours, self.not_in_averages, name=name or self.name,
                        description=self.description, reference=self.reference, catalogue=self.catalogue)

    @property
    def total_share(self) -> float:
        """Sum of the time shares [%] (should be 100)."""
        return sum(self.time_shares.values())

    def add_supercycle(self, sc: Supercycle, share: float = 0.0, in_averages: bool = True) -> None:
        """Add a supercycle (its name must be new) with a share of the run [%]."""
        if sc.name in self.supercycles:
            raise ValueError(f'there is already a supercycle called {sc.name!r}')
        self.supercycles[sc.name] = sc
        self.time_shares[sc.name] = float(share)
        if not in_averages:
            self.not_in_averages.append(sc.name)

    def new_supercycle(self, name: str, period_bp: int, share: float = 0.0) -> Supercycle:
        """Add an empty supercycle that uses the catalogue of the scenario, and return it."""
        sc = Supercycle(name, period_bp, self.catalogue)
        self.add_supercycle(sc, share)
        return sc

    def remove_supercycle(self, name: str) -> None:
        del self.supercycles[name]
        del self.time_shares[name]
        if name in self.not_in_averages:
            self.not_in_averages.remove(name)

    def rename_supercycle(self, old: str, new: str) -> None:
        """Rename a supercycle, keeping its place in the list."""
        if new == old:
            return
        if new in self.supercycles:
            raise ValueError(f'there is already a supercycle called {new!r}')
        self.supercycles = {(new if n == old else n): sc for n, sc in self.supercycles.items()}
        self.time_shares = {(new if n == old else n): v for n, v in self.time_shares.items()}
        self.not_in_averages = [new if n == old else n for n in self.not_in_averages]
        self.supercycles[new].name = new

    def move_supercycle(self, name: str, step: int) -> None:
        """Move a supercycle up (step < 0) or down (step > 0) in the list."""
        names = list(self.supercycles)
        i = names.index(name)
        j = min(max(i + step, 0), len(names) - 1)
        names.insert(j, names.pop(i))
        self.supercycles = {n: self.supercycles[n] for n in names}
        self.time_shares = {n: self.time_shares[n] for n in names}

    def set_share(self, name: str, share: float) -> None:
        """Set the share of the run [%] of one supercycle (the others are not changed)."""
        if name not in self.supercycles:
            raise KeyError(f'no supercycle {name!r}')
        self.time_shares[name] = float(share)

    def set_in_averages(self, name: str, in_averages: bool) -> None:
        if in_averages and name in self.not_in_averages:
            self.not_in_averages.remove(name)
        elif not in_averages and name not in self.not_in_averages:
            self.not_in_averages.append(name)

    def rescale_shares(self, keep=('Downtime',)) -> None:
        """
        Scale the shares of all supercycles except those in ``keep`` so that the total is 100 %
        (their proportions are kept). E.g. after adding a supercycle with 5 %, the others shrink.
        """
        fixed = sum(v for n, v in self.time_shares.items() if n in keep)
        scaled = sum(v for n, v in self.time_shares.items() if n not in keep)
        if scaled <= 0:
            raise ValueError('nothing to rescale: the shares to scale sum to 0')
        factor = (100 - fixed) / scaled
        self.time_shares = {n: (v if n in keep else v * factor) for n, v in self.time_shares.items()}

    # ------------------------------------------------------------------ saving
    def to_dict(self) -> dict:
        """Plain description of the scenario, as written in the YAML files."""
        return {
            'name': self.name,
            'description': self.description,
            'reference': self.reference,
            'run_length_hours': self.run_length_hours,
            'not_in_averages': list(self.not_in_averages),
            'catalogue_changes': self.catalogue.beam_changes(),
            'time_shares': {n: float(v) for n, v in self.time_shares.items()},
            'supercycles': [sc.to_dict() for sc in self.supercycles.values()],
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Schedule':
        """
        Rebuild a scenario from to_dict(). 'catalogue_changes' are applied to the catalogue of the
        files (e.g. {'SPS.SHiP': {'intensity': 5.2e13}}); a supercycle missing from 'time_shares'
        gets 0 %.
        """
        known = {'name', 'description', 'reference', 'run_length_hours', 'not_in_averages',
                 'catalogue_changes', 'time_shares', 'supercycles'}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f'scenario: unknown field(s) {sorted(unknown)}; allowed: {sorted(known)}')
        catalogue = load_catalogue().with_beams(data.get('catalogue_changes') or {})
        supercycles = {}
        for sc_data in data.get('supercycles') or []:
            sc = Supercycle.from_dict(sc_data, catalogue)
            supercycles[sc.name] = sc
        shares = data.get('time_shares') or {}
        extra = set(shares) - set(supercycles)
        if extra:
            raise ValueError(f'time_shares: unknown supercycles {sorted(extra)}')
        return cls(supercycles, {n: float(shares.get(n, 0.0)) for n in supercycles},
                   data['run_length_hours'], data.get('not_in_averages') or (),
                   name=data.get('name', ''), description=data.get('description', ''),
                   reference=data.get('reference', ''), catalogue=catalogue)

    def save(self, path: str) -> None:
        """Write the scenario to a YAML file (one line per placement, numbers to 12 digits)."""
        data = self.to_dict()
        # one line per placement / per changed beam / for the list of names
        for sc in data['supercycles']:
            sc['placements'] = [_OneLine(row) for row in sc['placements']]
        data['catalogue_changes'] = {key: _OneLine(fields) for key, fields in data['catalogue_changes'].items()}
        data['not_in_averages'] = _OneLine(data['not_in_averages'])
        header = (f'# Supercycle scenario, written by supercycles {__version__}.\n'
                  f'# Read it with Schedule.load(path), or open it in the GUI (File > Open).\n'
                  f'# placements: every cycle with its start BP; "parent" = id of the cycle it injects into.\n')
        with open(path, 'w') as f:
            f.write(header)
            yaml.dump(data, f, Dumper=_ScenarioDumper, sort_keys=False, default_flow_style=False,
                      width=110, allow_unicode=True)

    @classmethod
    def load(cls, path: str) -> 'Schedule':
        """Read a scenario written by save() (or written by hand, see Supercycle.from_dict)."""
        with open(path) as f:
            data = yaml.safe_load(f)
        data.setdefault('name', os.path.splitext(os.path.basename(path))[0])
        return cls.from_dict(data)

    # ------------------------------------------------------------------ time
    @property
    def run_length_s(self) -> float:
        return self.run_length_hours * 3600

    @property
    def run_length_days(self) -> float:
        return self.run_length_hours / 24

    def hours(self, name: str) -> float:
        """Time of the run given to a supercycle [h]."""
        return self.run_length_hours * self.time_shares[name] / 100

    def repetitions(self, name: str) -> float:
        """Number of times a supercycle is played over the run."""
        return self.hours(name) * 3600 / self.supercycles[name].length_s

    def availability(self, machine: str) -> float:
        """Fraction of the run in which ``machine`` has beam (1 - share of its downtime BPs)."""
        down = 0.0
        for name, sc in self.supercycles.items():
            down += self.time_shares[name] / 100 * sc.downtime_bps(machine) / sc.period_bp
        return 1 - down

    # ------------------------------------------------------------------ tables
    def supercycle_table(self) -> pd.DataFrame:
        """One row per supercycle: length, share of the run, hours and repetitions."""
        rows = []
        for name, sc in self.supercycles.items():
            rows.append({
                'supercycle': name,
                'period_bp': sc.period_bp,
                'length_s': sc.length_s,
                'share_%': self.time_shares[name],
                'hours': self.hours(name),
                'repetitions': self.repetitions(name),
                'in_averages': name not in self.not_in_averages,
            })
        return pd.DataFrame(rows, columns=['supercycle', 'period_bp', 'length_s', 'share_%', 'hours',
                                           'repetitions', 'in_averages'])

    def availability_table(self) -> pd.DataFrame:
        """One row per machine: availability and downtime over the run."""
        machines = list(self.catalogue.machines)
        rows = [{'machine': machine,
                 'availability_%': 100 * self.availability(machine),
                 'downtime_hours': self.run_length_hours * (1 - self.availability(machine))}
                for machine in machines]
        return pd.DataFrame(rows)

    def cycle_table(self) -> pd.DataFrame:
        """One row per (machine, cycle type): cycles played over the run and per day of run."""
        totals = {}
        for name, sc in self.supercycles.items():
            for machine in sc.machines:
                for key, count in sc.cycle_counts(machine).items():
                    if sc.catalogue.cycle(key).downtime:      # no beam: not a cycle played
                        continue
                    totals[(machine, key)] = totals.get((machine, key), 0) + count * self.repetitions(name)
        rows = [{'machine': machine, 'cycle': key, 'cycles_per_run': n,
                 'cycles_per_day': n / self.run_length_days}
                for (machine, key), n in totals.items()]
        return pd.DataFrame(rows, columns=['machine', 'cycle', 'cycles_per_run', 'cycles_per_day'])

    def facility_table(self) -> pd.DataFrame:
        """
        One row per facility, over the whole run.
        cycles / protons: summed over all supercycles.
        average flux / current: over the time of the supercycles not in ``not_in_averages``.
        """
        totals = {}
        averaged_time_s = sum(self.hours(name) * 3600 for name in self.supercycles
                              if name not in self.not_in_averages)
        for name, sc in self.supercycles.items():
            n = self.repetitions(name)
            for _, row in sc.facility_table().iterrows():
                total = totals.setdefault(row['facility'], {'machine': row['machine'], 'cycles': 0.0,
                                                            'protons': 0.0, 'protons_averaged': 0.0})
                total['cycles'] += row['cycles_per_supercycle'] * n
                total['protons'] += row['protons_per_supercycle'] * n            # NaN if unknown
                if name not in self.not_in_averages:
                    total['protons_averaged'] += row['protons_per_supercycle'] * n

        rows = []
        for facility, total in totals.items():
            flux = total['protons_averaged'] / averaged_time_s if averaged_time_s > 0 else np.nan
            rows.append({'facility': facility, 'machine': total['machine'],
                         'cycles_per_run': total['cycles'],
                         'cycles_per_day': total['cycles'] / self.run_length_days,
                         'protons_per_run': total['protons'],
                         'average_flux_p_per_s': flux,
                         'average_current_uA': flux * ELEMENTARY_CHARGE * 1e6})
        return pd.DataFrame(rows, columns=['facility', 'machine', 'cycles_per_run', 'cycles_per_day',
                                           'protons_per_run', 'average_flux_p_per_s', 'average_current_uA'])

    def per_supercycle_table(self, value: str = 'cycles_per_supercycle') -> pd.DataFrame:
        """
        Supercycles x facilities matrix of one column of Supercycle.facility_table()
        (e.g. 'cycles_per_supercycle', 'current_uA', 'flux_p_per_s'). Missing = 0 cycles / NaN.
        """
        columns = {name: sc.facility_table().set_index('facility')[value]
                   for name, sc in self.supercycles.items()}
        table = pd.DataFrame(columns).T if columns else pd.DataFrame()
        if value == 'cycles_per_supercycle':
            table = table.fillna(0).astype(int)
        table.index.name = 'supercycle'
        return table


# ---------------------------------------------------------------------------
# Comparison of two scenarios
# ---------------------------------------------------------------------------
def _side_by_side(table_a: pd.DataFrame, table_b: pd.DataFrame, keys: list, values: list) -> pd.DataFrame:
    """
    Outer join of two tables on ``keys``. For each column of ``values``:
    '<value> A', '<value> B', '<value> change' (B - A) and '<value> change %' (relative to A).
    A row missing from one side counts as 0 there (e.g. a facility that only B delivers to).
    """
    merged = pd.merge(table_a[keys + values], table_b[keys + values], on=keys, how='outer',
                      suffixes=(' A', ' B'), indicator=True)
    # rows in the order of A, then those only in B (pandas sorts the keys of an outer join)
    order_a = {tuple(row): i for i, row in enumerate(table_a[keys].itertuples(index=False))}
    order_b = {tuple(row): i for i, row in enumerate(table_b[keys].itertuples(index=False))}
    merged['_order'] = [order_a.get(tuple(row), len(order_a) + order_b.get(tuple(row), 0))
                        for row in merged[keys].itertuples(index=False)]
    merged = merged.sort_values('_order').reset_index(drop=True)
    only_b, only_a = merged['_merge'] == 'right_only', merged['_merge'] == 'left_only'

    result = merged[keys].copy()
    for value in values:
        # missing row = 0 on that side; NaN inside a table (unknown intensity) stays NaN
        a = merged[f'{value} A'].astype(float).mask(only_b, 0.0)
        b = merged[f'{value} B'].astype(float).mask(only_a, 0.0)
        result[f'{value} A'] = a
        result[f'{value} B'] = b
        result[f'{value} change'] = b - a
        with np.errstate(divide='ignore', invalid='ignore'):
            result[f'{value} change %'] = np.where(a != 0, 100 * (b - a) / a, np.nan)
    return result


def compare_schedules(a: Schedule, b: Schedule) -> dict:
    """
    Compare scenario B to scenario A. Returns a dict of DataFrames (see _side_by_side for the columns):
        'run'          run length and availability of each machine
        'supercycles'  share of the run, length, repetitions and hours of each supercycle
        'cycles'       cycles played per run, per cycle type
        'facilities'   cycles, protons, average flux and current per facility
    """
    run_a = pd.concat([pd.DataFrame([{'quantity': 'run length [h]', 'value': a.run_length_hours}]),
                       a.availability_table().assign(quantity=lambda t: t['machine'] + ' availability [%]')
                       .rename(columns={'availability_%': 'value'})[['quantity', 'value']]])
    run_b = pd.concat([pd.DataFrame([{'quantity': 'run length [h]', 'value': b.run_length_hours}]),
                       b.availability_table().assign(quantity=lambda t: t['machine'] + ' availability [%]')
                       .rename(columns={'availability_%': 'value'})[['quantity', 'value']]])
    return {
        'run': _side_by_side(run_a, run_b, ['quantity'], ['value']),
        'supercycles': _side_by_side(a.supercycle_table(), b.supercycle_table(), ['supercycle'],
                                     ['share_%', 'length_s', 'repetitions', 'hours']),
        'cycles': _side_by_side(a.cycle_table(), b.cycle_table(), ['machine', 'cycle'], ['cycles_per_run']),
        'facilities': _side_by_side(a.facility_table(), b.facility_table(), ['facility', 'machine'],
                                    ['cycles_per_run', 'protons_per_run', 'average_flux_p_per_s',
                                     'average_current_uA']),
    }
