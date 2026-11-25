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
"""
import pandas as pd

from supercycles.supercycle import ELEMENTARY_CHARGE


class Schedule:

    def __init__(self, supercycles: dict, time_shares: dict, run_length_hours: float,
                 not_in_averages=(), name: str = ''):
        mismatch = set(time_shares) ^ set(supercycles)
        if mismatch:
            raise ValueError(f'time shares and supercycles do not match: {sorted(mismatch)}')
        unknown = set(not_in_averages) - set(supercycles)
        if unknown:
            raise ValueError(f'not_in_averages: unknown supercycles {sorted(unknown)}')
        self.name = name
        self.supercycles = supercycles               # name -> Supercycle
        self.time_shares = time_shares               # name -> % of the run
        self.run_length_hours = float(run_length_hours)
        self.not_in_averages = list(not_in_averages)

    @classmethod
    def from_scenario(cls, module) -> 'Schedule':
        """Build a schedule from a module of the scenarios package."""
        return cls(module.supercycles(), module.TIME_SHARES, module.RUN_LENGTH_HOURS,
                   not_in_averages=getattr(module, 'NOT_IN_AVERAGES', ()),
                   name=module.__name__.split('.')[-1])

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
        return pd.DataFrame(rows)

    def availability_table(self) -> pd.DataFrame:
        """One row per machine: availability and downtime over the run."""
        machines = next(iter(self.supercycles.values())).machines
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
        return pd.DataFrame(rows)

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
            flux = total['protons_averaged'] / averaged_time_s
            rows.append({'facility': facility, 'machine': total['machine'],
                         'cycles_per_run': total['cycles'],
                         'cycles_per_day': total['cycles'] / self.run_length_days,
                         'protons_per_run': total['protons'],
                         'average_flux_p_per_s': flux,
                         'average_current_uA': flux * ELEMENTARY_CHARGE * 1e6})
        return pd.DataFrame(rows)

    def per_supercycle_table(self, value: str = 'cycles_per_supercycle') -> pd.DataFrame:
        """
        Supercycles x facilities matrix of one column of Supercycle.facility_table()
        (e.g. 'cycles_per_supercycle', 'current_uA', 'flux_p_per_s'). Missing = 0 cycles / NaN.
        """
        columns = {name: sc.facility_table().set_index('facility')[value]
                   for name, sc in self.supercycles.items()}
        table = pd.DataFrame(columns).T
        if value == 'cycles_per_supercycle':
            table = table.fillna(0).astype(int)
        table.index.name = 'supercycle'
        return table
