"""
A supercycle of the whole injector chain (PSB, PS, SPS) on a common time grid.

Model
-----
* A supercycle has a fixed period of ``period_bp`` basic periods (BP), shared by
  all machines. BPs are numbered 1..period_bp.
* The supercycle repeats. A position outside 1..period_bp is wrapped around:
  BP 0 is the last BP of the previous repetition (= period_bp), BP -1 is
  period_bp - 1, and so on. This is how the injections of the first SPS cycle end
  up at the end of the PS and PSB sequences, as in operation.
* The only stored state is the list of *placements*: (cycle type, start BP,
  parent). Timelines, counts, power and fluxes are all computed from it, so
  they can never get out of sync.
* Adding a cycle also places the upstream cycles injecting into it (recursively),
  as described by the ``injections`` of its catalogue entry. These placements
  remember their parent, so removing the parent removes them as well.

Example
-------
>>> sc = Supercycle('Physics', period_bp=36)
>>> sc.add('SPS', 'SFTPRO', 1)        # also places 2x PS.MTE and 2x PSB.MTE
>>> sc.add('SPS', 'deGauss')          # right after the previous SPS cycle
>>> sc.fill('PSB', 'ISOLDE')          # every free PSB BP
>>> print(sc)                         # text view
>>> sc.validate()                     # list of Issue (errors / warnings)
>>> sc.facility_table()               # cycles, protons and flux per facility

Editing an existing supercycle (the period follows; injections keep their offsets):
>>> sc.append('SPS', 'AWAKE')         # after the last SPS cycle, lengthening if there is no room
>>> sc.insert('SPS', 'AWAKE', 10)     # at BP 10, the cycles from there on move later
>>> sc.conflicts('SPS', 'AWAKE', 10)  # what is in the way;  sc.replace(...) removes it and places
>>> sc.insert_bps(13, 2)              # empty BPs;  sc.remove_bps(13, 2) is the inverse
>>> Supercycle.from_dict(sc.to_dict())   # exact copy, through a plain dict (used for the YAML files)
"""
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from supercycles.catalogue import Catalogue, CycleType, load_catalogue

ELEMENTARY_CHARGE = 1.602176634e-19   # [C]


class PlacementError(ValueError):
    """A cycle cannot be placed (overlap, too long, ...). The supercycle is left unchanged."""


@dataclass(frozen=True)
class Placement:
    """One cycle played at a given position of the supercycle."""
    id: int
    cycle: CycleType
    start_bp: int                    # 1..period_bp
    parent: Optional[int] = None     # id of the placement this cycle injects into

    @property
    def machine(self) -> str:
        return self.cycle.machine

    def __repr__(self):
        parent = f', injects into #{self.parent}' if self.parent is not None else ''
        return f'Placement(#{self.id} {self.cycle.key} at BP {self.start_bp}{parent})'


@dataclass(frozen=True)
class Issue:
    """Result of Supercycle.validate()."""
    level: str        # 'error' or 'warning'
    message: str

    def __str__(self):
        return f'[{self.level}] {self.message}'


class Supercycle:

    def __init__(self, name: str, period_bp: int, catalogue: Optional[Catalogue] = None):
        self.name = name
        self.period_bp = int(period_bp)
        self.catalogue = catalogue if catalogue is not None else load_catalogue()
        self.placements = {}      # id -> Placement (insertion order is kept)
        self._next_id = 1
        self._cursor = {}         # machine -> BP right after the last cycle added there with add()

    def __repr__(self):
        return (f"Supercycle('{self.name}', {self.period_bp} BP = {self.length_s:.1f} s, "
                f"{len(self.placements)} placements)")

    # ------------------------------------------------------------------ time
    @property
    def length_s(self) -> float:
        return round(self.period_bp * self.catalogue.basic_period_s, 6)

    @property
    def machines(self) -> list:
        return list(self.catalogue.machines)

    def wrap(self, bp: int) -> int:
        """Bring any BP number into 1..period_bp (the supercycle repeats)."""
        return (bp - 1) % self.period_bp + 1

    def occupied_bps(self, placement: Placement) -> list:
        """BPs (1..period_bp) used by a placement, following the wrap-around."""
        return [self.wrap(placement.start_bp + k) for k in range(placement.cycle.length_bp)]

    # ------------------------------------------------------------------ editing
    def add(self, machine: str, cycle_id: str, start_bp: Optional[int] = None,
            with_injections: bool = True) -> Placement:
        """
        Place a cycle and, by default, the upstream cycles that inject into it.

        start_bp : BP where the cycle starts. Values outside 1..period_bp are wrapped.
                   None = right after the last cycle added to this machine with add()
                   (BP 1 for the first one).
        with_injections : False places only this cycle (e.g. to edit injections by hand).

        Either everything is placed, or a PlacementError is raised and nothing changes.
        Returns the placement of the requested cycle.
        """
        cycle = self.catalogue.cycle(machine, cycle_id)
        if start_bp is None:
            start_bp = self._cursor.get(machine, 1)

        planned = []
        self._plan(cycle, start_bp, None, with_injections, planned)
        self._check_free(planned)

        for placement in planned:
            self.placements[placement.id] = placement
        self._next_id += len(planned)
        self._cursor[machine] = self.wrap(start_bp + cycle.length_bp)
        return planned[0]

    def _plan(self, cycle, start_bp, parent_id, with_injections, planned):
        """Recursively list the placements needed for a cycle (nothing is stored here)."""
        if cycle.length_bp > self.period_bp:
            raise PlacementError(f'{cycle.key} ({cycle.length_bp} BP) is longer than the '
                                 f'supercycle ({self.period_bp} BP)')
        placement = Placement(id=self._next_id + len(planned), cycle=cycle,
                              start_bp=self.wrap(start_bp), parent=parent_id)
        planned.append(placement)
        if with_injections:
            for injection in cycle.injections:
                upstream_cycle = self.catalogue.cycle(injection.cycle)
                self._plan(upstream_cycle, start_bp + injection.bp_offset, placement.id,
                           True, planned)

    def _check_free(self, planned):
        """Raise PlacementError if a planned placement overlaps anything (existing or planned)."""
        used = {machine: {} for machine in self.machines}   # machine -> {bp: placement}
        for placement in self.placements.values():
            for bp in self.occupied_bps(placement):
                used[placement.machine][bp] = placement
        planned_by_id = {p.id: p for p in planned}

        for placement in planned:
            for bp in self.occupied_bps(placement):
                other = used[placement.machine].get(bp)
                if other is not None:
                    reason = ''
                    if placement.parent is not None:
                        reason = f' (injection for {planned_by_id[placement.parent].cycle.key})'
                    raise PlacementError(
                        f'cannot place {placement.cycle.key} at BP {placement.start_bp}{reason}: '
                        f'{placement.machine} BP {bp} is already used by {other.cycle.key} '
                        f'(#{other.id}, starting at BP {other.start_bp})')
                used[placement.machine][bp] = placement

    def remove(self, placement) -> None:
        """Remove a placement (object or id) and, recursively, the cycles injecting into it."""
        placement_id = placement.id if isinstance(placement, Placement) else placement
        if placement_id not in self.placements:
            raise KeyError(f'no placement #{placement_id}')
        children = [p.id for p in self.placements.values() if p.parent == placement_id]
        for child_id in children:
            self.remove(child_id)
        del self.placements[placement_id]

    def remove_at(self, machine: str, bp: int) -> None:
        """Remove the cycle of ``machine`` that occupies ``bp`` (with its injections)."""
        placement = self.timeline(machine)[self.wrap(bp) - 1]
        if placement is None:
            raise KeyError(f'{machine} BP {bp} is free')
        self.remove(placement)

    def fill(self, machine: str, cycle_id: str) -> int:
        """
        Place ``cycle_id`` (with its injections) at every free BP of ``machine`` where it fits,
        scanning from BP 1. Returns the number of cycles added.
        """
        cursor = dict(self._cursor)      # filling does not move the add() cursor
        added = 0
        for bp in range(1, self.period_bp + 1):
            if self.timeline(machine)[bp - 1] is not None:
                continue
            try:
                self.add(machine, cycle_id, bp)
                added += 1
            except PlacementError:
                pass
        self._cursor = cursor
        return added

    def copy(self, name: Optional[str] = None) -> 'Supercycle':
        """Independent copy (placements are immutable, so a shallow copy of the dict is enough)."""
        new = Supercycle(name or self.name, self.period_bp, self.catalogue)
        new.placements = dict(self.placements)
        new._next_id = self._next_id
        new._cursor = dict(self._cursor)
        return new

    # ------------------------------------------------------------------ editing: structure
    # These methods change the period of the supercycle. Each cycle keeps its injections at the
    # same offsets (also those wrapped around the end), and every method either succeeds
    # completely or raises PlacementError and changes nothing.

    def root(self, placement) -> Placement:
        """Top-level placement of the tree a placement belongs to (itself if it has no parent)."""
        placement = placement if isinstance(placement, Placement) else self.placements[placement]
        while placement.parent is not None:
            placement = self.placements[placement.parent]
        return placement

    def conflicts(self, machine: str, cycle_id: str, start_bp: int, with_injections: bool = True) -> list:
        """
        Top-level placements that stop ``cycle_id`` (and its injections) from being placed at
        ``start_bp``: the cycles to remove, with their own injections, to make room for it.
        Empty list = it can be placed as is.
        """
        planned = []
        self._plan(self.catalogue.cycle(machine, cycle_id), start_bp, None, with_injections, planned)
        roots = {}
        for placement in planned:
            timeline = self.timeline(placement.machine)
            for bp in self.occupied_bps(placement):
                if timeline[bp - 1] is not None:
                    root = self.root(timeline[bp - 1])
                    roots[root.id] = root
        return list(roots.values())

    def unwrapped_start(self, placement) -> int:
        """
        Start of a placement counted from BP 1 of its own top-level cycle, without wrap-around:
        e.g. 0 or -1 for the injections of a cycle starting at BP 1 (shown at the end of the
        supercycle). Top-level placements return their start_bp.
        """
        placement = placement if isinstance(placement, Placement) else self.placements[placement]
        if placement.parent is None:
            return placement.start_bp
        parent = self.placements[placement.parent]
        return self.unwrapped_start(parent) + self._injection_offset(parent, placement)

    def _injection_offset(self, parent: Placement, child: Placement) -> int:
        """Offset [BP] of an injection relative to the start of the cycle it injects into."""
        # The children of a placement were planned in the order of the catalogue injections.
        children = sorted((p for p in self.placements.values() if p.parent == parent.id), key=lambda p: p.id)
        injections = parent.cycle.injections
        if len(children) == len(injections):
            injection = injections[children.index(child)]
            if self.wrap(parent.start_bp + injection.bp_offset) == child.start_bp:
                return injection.bp_offset
        # injections edited by hand: take the shortest signed distance around the supercycle
        delta = (child.start_bp - parent.start_bp) % self.period_bp
        return delta - self.period_bp if delta > self.period_bp // 2 else delta

    def _shift(self, at_bp: int, shift: int, new_period: int) -> None:
        """
        Move every top-level cycle starting at or after ``at_bp`` by ``shift`` BPs (with its
        injections), and set the period to ``new_period``. Raises PlacementError on overlaps.
        """
        moved = {}
        for placement in self.placements.values():
            root_start = self.root(placement).start_bp
            new_start = self.unwrapped_start(placement) + (shift if root_start >= at_bp else 0)
            moved[placement.id] = (placement, new_start)

        old_period, old_placements = self.period_bp, self.placements
        self.period_bp = new_period
        self.placements = {pid: Placement(p.id, p.cycle, self.wrap(start), p.parent)
                           for pid, (p, start) in moved.items()}
        try:
            self._check_no_overlap()
        except PlacementError:
            self.period_bp, self.placements = old_period, old_placements
            raise
        self._cursor = {machine: self.wrap(bp + shift) if bp >= at_bp else bp
                        for machine, bp in self._cursor.items()}

    def _check_no_overlap(self) -> None:
        """Raise PlacementError if two placements of the same machine share a BP."""
        for machine in self.machines:
            used = {}
            for placement in self.placements_on(machine):
                if placement.cycle.length_bp > self.period_bp:
                    raise PlacementError(f'{placement.cycle.key} ({placement.cycle.length_bp} BP) is '
                                         f'longer than the supercycle ({self.period_bp} BP)')
                for bp in self.occupied_bps(placement):
                    if bp in used:
                        raise PlacementError(f'{machine} BP {bp} would be used by both {used[bp].cycle.key} '
                                             f'(#{used[bp].id}) and {placement.cycle.key} (#{placement.id})')
                    used[bp] = placement

    def insert_bps(self, at_bp: int, n: int = 1) -> None:
        """
        Lengthen the supercycle by ``n`` empty BPs inserted before BP ``at_bp`` (1..period_bp+1).
        Top-level cycles starting at or after ``at_bp`` move ``n`` BPs later, with their
        injections. ``at_bp = period_bp + 1`` adds the BPs at the end, before the injections
        that wrap around to the end (those of a cycle at BP 1).
        """
        if n < 1:
            raise ValueError('n must be >= 1')
        if not 1 <= at_bp <= self.period_bp + 1:
            raise ValueError(f'at_bp must be in 1..{self.period_bp + 1}')
        self._shift(at_bp, n, self.period_bp + n)

    def remove_bps(self, at_bp: int, n: int = 1, remove_cycles: bool = False) -> None:
        """
        Shorten the supercycle by removing BPs ``at_bp`` .. ``at_bp + n - 1`` (the inverse of
        insert_bps). Top-level cycles starting after them move ``n`` BPs earlier, with their
        injections. No top-level cycle may start inside the removed BPs (``remove_cycles=True``
        removes those cycles first, with their injections; see cycles_starting_in()), and nothing
        may end up overlapping; otherwise a PlacementError is raised and nothing changes.
        Because injections come earlier than their cycle, the free BPs of an upstream machine are
        usually a little earlier than those of the SPS: give the BPs of the SPS (or of the machine
        where the gap is) and the upstream gaps follow.
        """
        if n < 1 or not 1 <= at_bp <= self.period_bp - n + 1:
            raise ValueError(f'cannot remove {n} BP(s) from BP {at_bp} of a {self.period_bp} BP supercycle')
        in_the_way = self.cycles_starting_in(at_bp, n)
        if in_the_way and not remove_cycles:
            names = ', '.join(f'{p.cycle.key} at BP {p.start_bp}' for p in in_the_way)
            raise PlacementError(f'cannot remove BP {at_bp}..{at_bp + n - 1}: {names} start(s) there')
        saved = self.copy()
        try:
            for placement in in_the_way:
                self.remove(placement)
            self._shift(at_bp + n, -n, self.period_bp - n)
        except PlacementError:
            self.period_bp, self.placements, self._cursor = saved.period_bp, saved.placements, saved._cursor
            raise

    def cycles_starting_in(self, at_bp: int, n: int = 1) -> list:
        """Top-level placements (any machine) starting in BPs ``at_bp`` .. ``at_bp + n - 1``."""
        return [p for p in self.placements.values() if p.parent is None and at_bp <= p.start_bp < at_bp + n]

    def last_bp(self, machine: str) -> int:
        """
        Last BP used by the cycles of ``machine``, ignoring the injections that wrap around to the
        end of the supercycle (0 if the machine is empty).
        """
        ends = [self.unwrapped_start(p) + p.cycle.length_bp - 1 for p in self.placements_on(machine)
                if self.unwrapped_start(p) >= 1]
        return min(max(ends, default=0), self.period_bp)

    def insert(self, machine: str, cycle_id: str, at_bp: Optional[int] = None,
               replace_conflicts: bool = False) -> Placement:
        """
        Insert a cycle (with its injections) at ``at_bp`` and lengthen the supercycle by its length:
        the cycles from ``at_bp`` on move later. If ``at_bp`` falls inside a cycle of ``machine``,
        the new cycle goes before that cycle. ``at_bp = None`` appends it after the last cycle of
        ``machine``. If its injections still collide with cycles of the upstream machines,
        ``replace_conflicts=True`` removes those cycles (see replace()); otherwise a PlacementError
        is raised. Either everything succeeds or nothing changes.
        """
        cycle = self.catalogue.cycle(machine, cycle_id)
        if at_bp is None:
            at_bp = self.last_bp(machine) + 1
        else:
            occupant = self.timeline(machine)[self.wrap(at_bp) - 1]
            if occupant is not None and self.unwrapped_start(occupant) >= 1:
                at_bp = occupant.start_bp            # before the cycle that is there
        saved = self.copy()
        try:
            self.insert_bps(at_bp, cycle.length_bp)
            if replace_conflicts:
                return self.replace(machine, cycle_id, at_bp)
            return self.add(machine, cycle_id, at_bp)
        except PlacementError:
            self.period_bp, self.placements, self._cursor = saved.period_bp, saved.placements, saved._cursor
            raise

    def end_slot(self, machine: str, cycle_id: str) -> Optional[int]:
        """
        BP right after the last cycle of ``machine`` if ``cycle_id`` fits in the free BPs there
        (without lengthening the supercycle), else None. Only ``machine`` is checked, not the
        upstream machines that its injections need.
        """
        at_bp = self.last_bp(machine) + 1
        length = self.catalogue.cycle(machine, cycle_id).length_bp
        if at_bp + length - 1 > self.period_bp:
            return None
        timeline = self.timeline(machine)
        if any(timeline[bp - 1] is not None for bp in range(at_bp, at_bp + length)):
            return None
        return at_bp

    def append(self, machine: str, cycle_id: str, replace_conflicts: bool = False) -> Placement:
        """
        Place a cycle (with its injections) right after the last cycle of ``machine``: in the free
        BPs there if it fits (see end_slot()), otherwise by lengthening the supercycle (insert()).
        ``replace_conflicts=True`` removes the upstream cycles in the way of its injections.
        """
        at_bp = self.end_slot(machine, cycle_id)
        if at_bp is None:
            return self.insert(machine, cycle_id, None, replace_conflicts)
        if replace_conflicts:
            return self.replace(machine, cycle_id, at_bp)
        return self.add(machine, cycle_id, at_bp)

    def replace(self, machine: str, cycle_id: str, start_bp: int) -> Placement:
        """
        Place a cycle (with its injections), first removing the cycles in its way (with their own
        injections, see conflicts()). Either everything succeeds or nothing changes.
        """
        saved = self.copy()
        try:
            for root in self.conflicts(machine, cycle_id, start_bp):
                self.remove(root)
            return self.add(machine, cycle_id, start_bp)
        except PlacementError:
            self.placements, self._cursor = saved.placements, saved._cursor
            raise

    # ------------------------------------------------------------------ saving
    def to_dict(self) -> dict:
        """
        Plain description of the supercycle (for YAML files). Every placement is listed with its
        id and parent, so that from_dict() rebuilds exactly the same supercycle.
        """
        placements = []
        for p in self.placements.values():
            row = {'id': p.id, 'cycle': p.cycle.key, 'start_bp': p.start_bp}
            if p.parent is not None:
                row['parent'] = p.parent
            placements.append(row)
        return {'name': self.name, 'period_bp': self.period_bp, 'placements': placements}

    @classmethod
    def from_dict(cls, data: dict, catalogue: Optional[Catalogue] = None) -> 'Supercycle':
        """
        Rebuild a supercycle from to_dict(). Also accepts hand-written entries:
          placements without 'id'      ->  added with add() (their injections are placed automatically)
          'fill': ['PSB.ISOLDE', ...]  ->  fill() applied at the end, in order
        """
        known = {'name', 'period_bp', 'placements', 'fill'}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"supercycle {data.get('name')!r}: unknown field(s) {sorted(unknown)}")
        sc = cls(data['name'], data['period_bp'], catalogue)
        rows = data.get('placements') or []

        # exact placements (with id): restored as they are
        exact = [row for row in rows if 'id' in row]
        for row in exact:
            sc.placements[row['id']] = Placement(id=row['id'], cycle=sc.catalogue.cycle(row['cycle']),
                                                 start_bp=sc.wrap(row['start_bp']), parent=row.get('parent'))
        missing_parents = {p.parent for p in sc.placements.values()} - set(sc.placements) - {None}
        if missing_parents:
            raise ValueError(f'supercycle {sc.name!r}: parent id(s) {sorted(missing_parents)} not found')
        sc._check_no_overlap()
        sc._next_id = max(sc.placements, default=0) + 1

        # hand-written placements (no id): placed with their injections
        for row in rows:
            if 'id' not in row:
                machine, cycle_id = row['cycle'].split('.', 1)
                sc.add(machine, cycle_id, row.get('start_bp'))
        for key in data.get('fill') or []:
            machine, cycle_id = key.split('.', 1)
            sc.fill(machine, cycle_id)
        return sc

    # ------------------------------------------------------------------ views
    def placements_on(self, machine: str) -> list:
        """Placements of one machine, ordered by start BP."""
        return sorted((p for p in self.placements.values() if p.machine == machine),
                      key=lambda p: p.start_bp)

    def timeline(self, machine: str) -> list:
        """List of length period_bp: the placement occupying each BP (None = free)."""
        slots = [None] * self.period_bp
        for placement in self.placements_on(machine):
            for bp in self.occupied_bps(placement):
                slots[bp - 1] = placement
        return slots

    def free_bps(self, machine: str) -> list:
        return [bp for bp, p in enumerate(self.timeline(machine), start=1) if p is None]

    def downtime_bps(self, machine: str) -> int:
        """Number of BPs of ``machine`` occupied by downtime cycles (no beam)."""
        return sum(p.cycle.length_bp for p in self.placements_on(machine) if p.cycle.downtime)

    def cycle_counts(self, machine: str) -> dict:
        """Number of times each cycle type (key) is played per supercycle."""
        counts = {}
        for placement in self.placements_on(machine):
            counts[placement.cycle.key] = counts.get(placement.cycle.key, 0) + 1
        return counts

    def cycle_times_s(self, machine: str) -> dict:
        """Time [s] per supercycle spent on each cycle type (key)."""
        return {key: count * self.catalogue.length_s(self.catalogue.cycle(key))
                for key, count in self.cycle_counts(machine).items()}

    def average_power_MW(self, machine: str) -> float:
        """Supercycle-averaged magnet power. Free BPs and cycles without a value count as 0 MW."""
        energy_MJ = 0.0
        for placement in self.placements_on(machine):
            power = placement.cycle.average_power_MW or 0.0
            energy_MJ += power * self.catalogue.length_s(placement.cycle)
        return energy_MJ / self.length_s

    def beam_time_s(self, machine) -> float:
        """Time per repetition [s] in which ``machine`` has beam (its downtime BPs excluded)."""
        if machine is None:
            return self.length_s
        return (self.period_bp - self.downtime_bps(machine)) * self.catalogue.basic_period_s

    def facility_table(self) -> pd.DataFrame:
        """
        Beam delivered per facility, for one repetition of the supercycle.
        protons_per_supercycle is NaN when the intensity of a cycle is not in the catalogue.
        Flux and current are over the time the delivering machine has beam: in a supercycle with
        downtime (e.g. PSB down a quarter of the time) they are the values while the beam is on.
        """
        rows = {}
        for placement in self.placements.values():
            beam = placement.cycle.beam
            if beam is None:
                continue
            row = rows.setdefault(beam.destination, {'cycles_per_supercycle': 0, 'protons': 0.0})
            row['cycles_per_supercycle'] += 1
            row['protons'] = np.nan if beam.delivered is None else row['protons'] + beam.delivered

        table = []
        for facility_id, row in rows.items():
            machine = self.catalogue.facilities[facility_id].machine
            flux = row['protons'] / self.beam_time_s(machine)
            table.append({
                'facility': facility_id,
                'machine': machine,
                'cycles_per_supercycle': row['cycles_per_supercycle'],
                'protons_per_supercycle': row['protons'],
                'flux_p_per_s': flux,
                'current_uA': flux * ELEMENTARY_CHARGE * 1e6,
            })
        return pd.DataFrame(table, columns=['facility', 'machine', 'cycles_per_supercycle',
                                            'protons_per_supercycle', 'flux_p_per_s', 'current_uA'])

    def to_dataframe(self) -> pd.DataFrame:
        """All placements as a table (one row per cycle played)."""
        rows = []
        for machine in self.machines:
            for p in self.placements_on(machine):
                rows.append({'id': p.id, 'machine': machine, 'cycle': p.cycle.key,
                             'start_bp': p.start_bp,
                             'end_bp': self.wrap(p.start_bp + p.cycle.length_bp - 1),
                             'length_bp': p.cycle.length_bp, 'parent': p.parent})
        table = pd.DataFrame(rows)
        if not table.empty:
            table['parent'] = table['parent'].astype('Int64')     # integer ids with <NA> for top-level cycles
        return table

    # ------------------------------------------------------------------ checks
    def validate(self) -> list:
        """Check the supercycle against the limits of the catalogue. Returns a list of Issue."""
        issues = []
        if self.length_s > self.catalogue.max_supercycle_length_s:
            issues.append(Issue('error', f'length {self.length_s:.1f} s exceeds the limit of '
                                         f'{self.catalogue.max_supercycle_length_s:.1f} s'))

        for machine in self.machines:
            limit = self.catalogue.machines[machine].average_power_limit_MW
            if limit is not None:
                power = self.average_power_MW(machine)
                if power > limit:
                    issues.append(Issue('error', f'{machine} average power {power:.2f} MW exceeds '
                                                 f'the limit of {limit:.2f} MW'))
                unknown = sorted({p.cycle.key for p in self.placements_on(machine)
                                  if p.cycle.average_power_MW is None})
                if unknown:
                    issues.append(Issue('warning', f'{machine}: no power value for {unknown} '
                                                   f'(counted as 0 MW)'))
            free = self.free_bps(machine)
            if free:
                issues.append(Issue('warning', f'{machine}: {len(free)} free BP(s): {free}'))

        for placement in self.placements.values():
            expected = len(placement.cycle.injections)
            found = sum(1 for p in self.placements.values() if p.parent == placement.id)
            if found != expected:
                issues.append(Issue('warning', f'{placement.cycle.key} at BP {placement.start_bp} '
                                               f'has {found} of its {expected} injections'))
        return issues

    # ------------------------------------------------------------------ text view
    def show(self, cell_width: int = 4) -> str:
        """
        Text grid: one row per machine (upstream at the bottom), one column per BP.
        Each cycle is drawn as its id written across the BPs it occupies, padded with '-'
        ('.' = free BP). A cycle wrapping around the end is drawn in two pieces.
        """
        w = cell_width
        lines = [f'{self!r}', 'BP   ' + ''.join(f'{bp:<{w}}' for bp in range(1, self.period_bp + 1))]
        for machine in reversed(self.machines):
            row = list(''.join('.'.ljust(w) for _ in range(self.period_bp)))
            for p in self.placements_on(machine):
                first_piece = min(p.cycle.length_bp, self.period_bp - p.start_bp + 1)
                pieces = [(p.start_bp, first_piece)]
                if first_piece < p.cycle.length_bp:
                    pieces.append((1, p.cycle.length_bp - first_piece))
                for start, width in pieces:
                    text = p.cycle.id[:width * w - 1].ljust(width * w - 1, '-') + ' '
                    row[(start - 1) * w:(start - 1 + width) * w] = list(text)
            lines.append(f'{machine:<5}' + ''.join(row))
        return '\n'.join(lines)

    def __str__(self):
        return self.show()

    # ------------------------------------------------------------------ magnet current
    def magnet_current(self, machine: str = 'SPS'):
        """
        Magnet current over one supercycle, built from the catalogue profiles.
        Returns (time [s], current [A]); NaN separates cycles and marks cycles without profile.
        """
        times, currents = [], []
        for placement in self.placements_on(machine):
            t0 = (placement.start_bp - 1) * self.catalogue.basic_period_s
            if placement.cycle.profile is None:
                length = self.catalogue.length_s(placement.cycle)
                t, current = np.array([0.0, length]), np.array([np.nan, np.nan])
            else:
                t, current = self.catalogue.profile(placement.cycle)
            times += [t0 + t, [np.nan]]
            currents += [current, [np.nan]]
        if not times:
            return np.array([]), np.array([])
        return np.concatenate(times), np.concatenate(currents)
