#%%
"""
03 - Checking a supercycle and computing what it delivers. Comparing variants.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))   # for scenarios/
import pandas as pd
from supercycles import Supercycle
from scenarios.run3_typical import physics

pd.set_option('display.width', 200)

#%%
# The Run 3 Physics supercycle (reproduces the reference spreadsheet BP by BP)
sc = physics()
print(sc)
print('Issues:', sc.validate())                       # [] = no problem found
print(f"SPS average power: {sc.average_power_MW('SPS'):.2f} MW")
print(sc.facility_table())

#%%
# Counts and time per cycle type, for each machine
for machine in sc.machines:
    print(machine, sc.cycle_counts(machine))

#%%
# Breaking the limits: a single SFTPRO without deGauss exceeds the SPS power limit
bad = Supercycle('SFTPRO only', period_bp=9)
bad.add('SPS', 'SFTPRO', 1)
for issue in bad.validate():
    print(issue)

#%%
# Variants are cheap: copy and edit, then compare what the facilities receive
variant = sc.copy('Physics, PSB MD instead of 2 ISOLDE')
variant.remove_at('PSB', 9)
variant.remove_at('PSB', 10)
variant.add('PSB', 'MD', 9)
variant.add('PSB', 'MD', 10)

comparison = pd.concat({s.name: s.facility_table().set_index('facility')['cycles_per_supercycle']
                        for s in [sc, variant]}, axis=1).fillna(0).astype(int)
print(comparison)
print(f"ISOLDE: {sc.facility_table().set_index('facility').loc['ISOLDE', 'current_uA']:.2f} uA -> "
      f"{variant.facility_table().set_index('facility').loc['ISOLDE', 'current_uA']:.2f} uA")
