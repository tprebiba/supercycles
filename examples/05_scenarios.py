#%%
"""
05 - Scenarios: the supercycles of the reference spreadsheet, one module per sheet.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))   # for scenarios/
import matplotlib.pyplot as plt
import pandas as pd
import scenarios
from supercycles.plotting import plot_supercycle

pd.set_option('display.width', 200)

#%%
# One scenario: its settings, time shares and supercycles
run3 = scenarios.run3
print(run3.__doc__)
print('Run length:', run3.RUN_LENGTH_HOURS, 'h | SPS availability:', run3.SPS_AVAILABILITY)
for name, sc in run3.supercycles().items():
    print(f'{run3.TIME_SHARES[name]:5.1f} %  {sc!r}')

#%%
# What each supercycle delivers, for every scenario (per repetition of the supercycle)
rows = []
for scenario_name, module in scenarios.ALL.items():
    for name, sc in module.supercycles().items():
        table = sc.facility_table().set_index('facility')['cycles_per_supercycle']
        rows.append({'scenario': scenario_name, 'supercycle': name, 'length_s': sc.length_s,
                     'share_%': module.TIME_SHARES[name], **table.to_dict()})
overview = pd.DataFrame(rows).fillna(0)
print(overview[['scenario', 'supercycle', 'length_s', 'share_%', 'NorthArea', 'SHiP', 'ISOLDE', 'nTOF', 'EAST_T8']])

#%%
# All supercycles of one scenario, one below the other
supercycles = scenarios.run4_ship_ft9p6.supercycles()
fig, axs = plt.subplots(len(supercycles), 1, figsize=(16, 2.2 * len(supercycles)))
for ax, sc in zip(axs, supercycles.values()):
    plot_supercycle(sc, ax=ax, fontsize=7)
fig.tight_layout()
plt.show()
