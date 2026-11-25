"""Plots of a Supercycle. Plotting only reads the supercycle; it never modifies it."""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def plot_supercycle(sc, ax=None, fontsize=8, show_time=True):
    """One row per machine (upstream at the bottom); one box per cycle, split where it wraps."""
    if ax is None:
        _, ax = plt.subplots(figsize=(max(8, sc.period_bp * 0.35), 2.2))
    for row, machine in enumerate(sc.machines):
        for p in sc.placements_on(machine):
            pieces = [(p.start_bp, min(p.cycle.length_bp, sc.period_bp - p.start_bp + 1))]
            if pieces[0][1] < p.cycle.length_bp:                       # wraps around the end
                pieces.append((1, p.cycle.length_bp - pieces[0][1]))
            for start, width in pieces:
                ax.add_patch(Rectangle((start - 1, row), width, 1, facecolor=p.cycle.colour,
                                       edgecolor='k', lw=0.6, alpha=0.6 if p.parent else 1,
                                       hatch='//' if p.cycle.downtime else None))
                if not p.cycle.downtime:
                    ax.text(start - 1 + width / 2, row + 0.5, p.cycle.id, ha='center', va='center',
                            fontsize=fontsize, rotation=0 if width >= 4 else 90)
        down = [bp for bp, p in enumerate(sc.timeline(machine), start=1) if p is not None and p.cycle.downtime]
        if down:                                        # one label, on the longest run of downtime BPs
            runs = [[down[0]]]
            for bp in down[1:]:
                runs[-1].append(bp) if bp == runs[-1][-1] + 1 else runs.append([bp])
            longest = max(runs, key=len)
            ax.text((longest[0] - 1 + longest[-1]) / 2, row + 0.5, 'Downtime', ha='center', va='center',
                    fontsize=fontsize + 1, bbox=dict(facecolor='white', edgecolor='none', pad=1))
        free = sc.free_bps(machine)
        for bp in free:
            ax.add_patch(Rectangle((bp - 1, row), 1, 1, facecolor='none', edgecolor='lightgrey', lw=0.5))
    ax.set(xlim=(0, sc.period_bp), ylim=(0, len(sc.machines)), yticks=[r + 0.5 for r in range(len(sc.machines))],
           yticklabels=sc.machines, title=f'{sc.name}  ({sc.period_bp} BP = {sc.length_s:.1f} s)')
    step = next(n for n in [1, 2, 5, 10, 20, 50] if sc.period_bp / n <= 20)   # at most ~20 ticks
    ticks = range(0, sc.period_bp + 1, step)
    ax.set_xticks(list(ticks))
    ax.set_xticklabels([f'{t * sc.catalogue.basic_period_s:.1f}' if show_time else t for t in ticks], fontsize=fontsize)
    ax.set_xlabel('time [s]' if show_time else 'BP')
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    return ax


def plot_magnet_current(sc, machine='SPS', ax=None):
    """Magnet current over one supercycle, from the catalogue profiles."""
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 3))
    t, current = sc.magnet_current(machine)
    ax.plot(t, current / 1e3, color='k', lw=1)
    ax.set(xlim=(0, sc.length_s), xlabel='time [s]', ylabel=r'$I_\mathrm{mains}$ [kA]',
           title=f'{sc.name}: {machine} magnet current, average power {sc.average_power_MW(machine):.1f} MW')
    return ax
