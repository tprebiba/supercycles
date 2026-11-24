#%%
"""
01 - The catalogue: machines, facilities and cycle types, read from supercycles/data/catalogue/*.yaml
"""
import pandas as pd
from supercycles import load_catalogue

pd.set_option('display.width', 200)
cat = load_catalogue()

#%%
# Global settings and machines (ordered from the first to the last machine of the chain)
print('Basic period:', cat.basic_period_s, 's | max supercycle length:', cat.max_supercycle_length_s, 's')
for machine in cat.machines.values():
    print(machine)

#%%
# Facilities: where the beams go
for facility in cat.facilities.values():
    print(f'{facility.id:10s} {facility.name:22s} delivered by {facility.machine}')

#%%
# Overview of all cycle types
print(cat.to_dataframe()[['key', 'length_bp', 'length_s', 'destination', 'intensity', 'injections']])

#%%
# One cycle type in detail. Keys are 'MACHINE.id'; both spellings work.
sftpro = cat.cycle('SPS', 'SFTPRO')            # same as cat.cycle('SPS.SFTPRO')
print(sftpro)
print('length:', sftpro.length_bp, 'BP =', cat.length_s(sftpro), 's')
print('beam  :', sftpro.beam, '-> delivered per cycle:', f'{sftpro.beam.delivered:.3e}')
print('fed by:', [(inj.cycle, inj.bp_offset) for inj in sftpro.injections])

#%%
# Its magnet current profile
time_s, current_A = cat.profile(sftpro)
print(f'profile: {len(time_s)} points over {time_s[-1]:.1f} s, max current {current_A.max():.0f} A')

#%%
# A typo gives the list of available cycles
try:
    cat.cycle('SPS', 'SFTPRO2')
except KeyError as error:
    print(error)

# %%
