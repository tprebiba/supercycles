#%%
"""
06 - Editing a scenario, saving it and comparing it to the original.
The same operations are available in the GUI (edit mode: Ctrl+E; compare: Ctrl+K).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))   # for scenarios/
import pandas as pd
import scenarios
from supercycles import PlacementError, Schedule, Supercycle, compare_schedules

pd.set_option('display.width', 200)

#%%
# Structural edits of one supercycle: the period follows, injections move with their cycle
sc = scenarios.run3.physics()                  # 36 BP: (SFTPRO + deGauss) x 3
variant = sc.copy('Physics + AWAKE')
variant.append('SPS', 'AWAKE')                 # no free SPS BP at the end: lengthened to 42 BP
print(variant)

try:
    variant.add('SPS', 'deGauss', 10)          # BP 10 is taken
except PlacementError as error:
    print('refused:', error)
print('in the way:', variant.conflicts('SPS', 'deGauss', 10))
variant.replace('PS', 'TOF', 2)                # remove what is in the way, then place
variant.insert_bps(13, 2)                      # 2 empty BPs before BP 13 (cycles from there move later)
variant.remove_bps(13, 2)                      # ... and back

#%%
# Scenario-level edits: the share of the run stays fixed, so a longer supercycle is played fewer times
run3 = Schedule.from_scenario(scenarios.run3)
more_awake = run3.copy('run3 + AWAKE in Physics')
more_awake.supercycles['Physics'].append('SPS', 'AWAKE')
print(run3.repetitions('Physics'), '->', more_awake.repetitions('Physics'))

more_awake.new_supercycle('AWAKE only', period_bp=24, share=2)   # empty; filled below
more_awake.supercycles['AWAKE only'].append('SPS', 'AWAKE')
more_awake.supercycles['AWAKE only'].fill('PSB', 'ISOLDE')
more_awake.rescale_shares(keep=('Downtime',))                     # back to 100 %

#%%
# Save / load (YAML, one line per placement); the GUI opens these files too (File > Open)
more_awake.save('run3_more_awake.yaml')
loaded = Schedule.load('run3_more_awake.yaml')

#%%
# Compare B to A
tables = compare_schedules(run3, loaded)
print(tables['supercycles'][['supercycle', 'share_% A', 'share_% B', 'repetitions A', 'repetitions B']])
print(tables['facilities'][['facility', 'protons_per_run A', 'protons_per_run B', 'protons_per_run change %']])
