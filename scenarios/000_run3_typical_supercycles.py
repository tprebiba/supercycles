#%%
from supercycles.database import SPSCYCLES, PSCYCLES, PSBCYCLES
from supercycles.supercycle_grid import SupercycleGrid
from supercycles.vizualizer import GridVisualizer
import pickle


#%%
######################################
# Physics supercycle grid
######################################
physics = SupercycleGrid(nr_of_slots=38, name='Physics')
# SPS
physics.add_cycle('SPS', SPSCYCLES['SFTPRO'], 3)
physics.add_cycle('SPS', SPSCYCLES['deGauss'])
physics.add_cycle('SPS', SPSCYCLES['SFTPRO'])
physics.add_cycle('SPS', SPSCYCLES['deGauss'])
physics.add_cycle('SPS', SPSCYCLES['SFTPRO'])
physics.add_cycle('SPS', SPSCYCLES['deGauss'])
# PS
physics.add_cycle('PS', PSCYCLES['EAST T8'], 4)
physics.add_cycle('PS', PSCYCLES['EAST T9'], 6)
physics.add_cycle('PS', PSCYCLES['EAST TN'], 8)
physics.add_cycle('PS', PSCYCLES['TOF'], 10)
physics.add_cycle('PS', PSCYCLES['ZERO'], 11)
physics.add_cycle('PS', PSCYCLES['ZERO'], 12)
physics.add_cycle('PS', PSCYCLES['ZERO'], 13)
physics.add_cycle('PS', PSCYCLES['EAST T8'], 16)
physics.add_cycle('PS', PSCYCLES['TOF'], 18)
physics.add_cycle('PS', PSCYCLES['EAST TN'], 19)
physics.add_cycle('PS', PSCYCLES['ZERO'], 21)
physics.add_cycle('PS', PSCYCLES['EAST T8'], 22)
physics.add_cycle('PS', PSCYCLES['TOF'], 24)
physics.add_cycle('PS', PSCYCLES['ZERO'], 25)
physics.add_cycle('PS', PSCYCLES['EAST T8'])
physics.add_cycle('PS', PSCYCLES['TOF'])
physics.add_cycle('PS', PSCYCLES['EAST T9'])
physics.add_cycle('PS', PSCYCLES['ZERO'])
physics.add_cycle('PS', PSCYCLES['TOF'])
physics.add_cycle('PS', PSCYCLES['ZERO'])
physics.add_cycle('PS', PSCYCLES['ZERO'])
physics.add_cycle('PS', PSCYCLES['ZERO'])
# PSB
physics.fill_empty_slots_with_cycle('PSB', PSBCYCLES['ISOLDE'])
physics.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 38)
physics.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 37)
# Plot and do some basic calculations
GridVisualizer(physics).display()#save_png_to='../images/supercycle_grid_example.png')
#physics.to_pickle('physics.pkl')
#physics = SupercycleGrid.from_pickle('physics.pkl')
print(physics.sps_supercycle.cycle_counts)
print(physics.ps_supercycle.cycle_counts)
print(physics.psb_supercycle.cycle_counts)
iso_current_uA = physics.psb_supercycle.proton_flux['ISOLDE']*1.6e-19*1e6
east_t8_avgflux = physics.ps_supercycle.proton_flux['EAST T8']*1e-10
east_t9_avgflux = physics.ps_supercycle.proton_flux['EAST T9']*1e-10
east_tn_avgflux = physics.ps_supercycle.proton_flux['EAST TN']*1e-10
print(f'ISOLDE current: {iso_current_uA} uA')
print(f'Average EAST T8 flux: {east_t8_avgflux}e10 protons')
print(f'Average EAST T9 flux: {east_t9_avgflux}e10 protons')
print(f'Average EAST TN flux: {east_tn_avgflux}e10 protons')


#%%
######################################
# Physics with parallel MD supercycle grid
######################################
physics_w_MD = SupercycleGrid(nr_of_slots=47, name='Physics with parallel MD')
# SPS
physics_w_MD.add_cycle('SPS', SPSCYCLES['SFTPRO'], 3)
physics_w_MD.add_cycle('SPS', SPSCYCLES['MD parallel'])
physics_w_MD.add_cycle('SPS', SPSCYCLES['SFTPRO'])
physics_w_MD.add_cycle('SPS', SPSCYCLES['MD parallel'])
physics_w_MD.add_cycle('SPS', SPSCYCLES['SFTPRO'])
physics_w_MD.add_cycle('SPS', SPSCYCLES['MD parallel'])
# PS
physics_w_MD.add_cycle('PS', PSCYCLES['EAST T8'], 4)
physics_w_MD.add_cycle('PS', PSCYCLES['EAST T9'], 6)
physics_w_MD.add_cycle('PS', PSCYCLES['EAST TN'], 8)
physics_w_MD.add_cycle('PS', PSCYCLES['TOF'], 10)
physics_w_MD.add_cycle('PS', PSCYCLES['MD'], 13)
physics_w_MD.add_cycle('PS', PSCYCLES['ZERO'], 16)
physics_w_MD.add_cycle('PS', PSCYCLES['TOF'], 19)
physics_w_MD.add_cycle('PS', PSCYCLES['EAST TN'], 20)
physics_w_MD.add_cycle('PS', PSCYCLES['ZERO'], 22)
physics_w_MD.add_cycle('PS', PSCYCLES['TOF'], 23)
physics_w_MD.add_cycle('PS', PSCYCLES['EAST T9'], 24)
physics_w_MD.add_cycle('PS', PSCYCLES['EAST T8'], 28)
physics_w_MD.add_cycle('PS', PSCYCLES['TOF'], 30)
physics_w_MD.add_cycle('PS', PSCYCLES['ZERO'], 31)
physics_w_MD.add_cycle('PS', PSCYCLES['EAST T8'], 34)
physics_w_MD.add_cycle('PS', PSCYCLES['TOF'], 36)
physics_w_MD.add_cycle('PS', PSCYCLES['EAST T8'], 37)
physics_w_MD.add_cycle('PS', PSCYCLES['EAST T9'], 39)
physics_w_MD.add_cycle('PS', PSCYCLES['EAST T8'], 43)
physics_w_MD.add_cycle('PS', PSCYCLES['EAST TN'], 45)
# PSB
physics_w_MD.add_cycle('PSB', PSBCYCLES['MD'], 14)
physics_w_MD.fill_empty_slots_with_cycle('PSB', PSBCYCLES['ISOLDE'])
physics_w_MD.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 47)
physics_w_MD.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 46)
# Plot and do some basic calculations
GridVisualizer(physics_w_MD, grid_size=(15, 6), dynamic_grid_size=False).display()
print(physics_w_MD.sps_supercycle.cycle_counts)
print(physics_w_MD.ps_supercycle.cycle_counts)
print(physics_w_MD.psb_supercycle.cycle_counts)
iso_current_uA = physics_w_MD.psb_supercycle.proton_flux['ISOLDE']*1.6e-19*1e6
print(f'ISOLDE current: {iso_current_uA} uA')


# %%
######################################
# LHC filling supercycle grid
######################################
lhc_filling = SupercycleGrid(nr_of_slots=34, name='LHC filling')
# SPS
lhc_filling.add_cycle('SPS', SPSCYCLES['SFTPRO'], 3)
lhc_filling.add_cycle('SPS', SPSCYCLES['LHC filling'])
lhc_filling.add_cycle('SPS', SPSCYCLES['deGauss'])
# PS
lhc_filling.add_cycle('PS', PSCYCLES['EAST T9'], 4)
lhc_filling.add_cycle('PS', PSCYCLES['TOF'], 6)
lhc_filling.add_cycle('PS', PSCYCLES['EAST T8'], 7)
lhc_filling.add_cycle('PS', PSCYCLES['ZERO'], 9)
lhc_filling.add_cycle('PS', PSCYCLES['EAST T8'])
lhc_filling.add_cycle('PS', PSCYCLES['EAST TN'])
lhc_filling.add_cycle('PS', PSCYCLES['EAST T9'])
lhc_filling.add_cycle('PS', PSCYCLES['TOF'])
lhc_filling.add_cycle('PS', PSCYCLES['TOF'])
lhc_filling.add_cycle('PS', PSCYCLES['EAST T8'])
lhc_filling.add_cycle('PS', PSCYCLES['EAST TN'])
# PSB
lhc_filling.fill_empty_slots_with_cycle('PSB', PSBCYCLES['ISOLDE'])
lhc_filling.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 34)
lhc_filling.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 33)
# Plot and do some basic calculations
GridVisualizer(lhc_filling).display()
print(lhc_filling.sps_supercycle.cycle_counts)
print(lhc_filling.ps_supercycle.cycle_counts)
print(lhc_filling.psb_supercycle.cycle_counts)
iso_current_uA = lhc_filling.psb_supercycle.proton_flux['ISOLDE']*1.6e-19*1e6
print(f'ISOLDE current: {iso_current_uA} uA')


# %%
######################################
# LHC setup supercycle grid
######################################
lhc_setup = SupercycleGrid(nr_of_slots=48, name='LHC setup')
# SPS
lhc_setup.add_cycle('SPS', SPSCYCLES['SFTPRO'], 3)
lhc_setup.add_cycle('SPS', SPSCYCLES['LHC pilot'])
lhc_setup.add_cycle('SPS', SPSCYCLES['deGauss'])
lhc_setup.add_cycle('SPS', SPSCYCLES['SFTPRO'])
lhc_setup.add_cycle('SPS', SPSCYCLES['LHC pilot'])
lhc_setup.add_cycle('SPS', SPSCYCLES['deGauss'])
# PS
lhc_setup.add_cycle('PS', PSCYCLES['TOF'], 4)
lhc_setup.add_cycle('PS', PSCYCLES['EAST T8'], 5)
lhc_setup.add_cycle('PS', PSCYCLES['EAST T9'], 7)
lhc_setup.add_cycle('PS', PSCYCLES['TOF'], 9)
lhc_setup.add_cycle('PS', PSCYCLES['ZERO'], 10)
lhc_setup.add_cycle('PS', PSCYCLES['EAST T8'], 13)
lhc_setup.add_cycle('PS', PSCYCLES['ZERO'], 15)
lhc_setup.add_cycle('PS', PSCYCLES['EAST TN'], 16)
lhc_setup.add_cycle('PS', PSCYCLES['ZERO'], 18)
lhc_setup.add_cycle('PS', PSCYCLES['EAST T9'], 19)
lhc_setup.add_cycle('PS', PSCYCLES['MD short'], 21)
lhc_setup.add_cycle('PS', PSCYCLES['EAST T8'], 23)
lhc_setup.add_cycle('PS', PSCYCLES['ZERO'], 27)
lhc_setup.add_cycle('PS', PSCYCLES['EAST TN'], 28)
lhc_setup.add_cycle('PS', PSCYCLES['EAST T8'], 30)
lhc_setup.add_cycle('PS', PSCYCLES['TOF'], 32)
lhc_setup.add_cycle('PS', PSCYCLES['ZERO'], 33)
lhc_setup.add_cycle('PS', PSCYCLES['EAST T8'], 36)
lhc_setup.add_cycle('PS', PSCYCLES['TOF'], 38)
lhc_setup.add_cycle('PS', PSCYCLES['EAST TN'], 39)
lhc_setup.add_cycle('PS', PSCYCLES['TOF'], 41)
lhc_setup.add_cycle('PS', PSCYCLES['EAST T9'], 42)
lhc_setup.add_cycle('PS', PSCYCLES['ZERO'], 44)
lhc_setup.add_cycle('PS', PSCYCLES['ZERO'], 45)
lhc_setup.add_cycle('PS', PSCYCLES['EAST T8'], 46)
# PSB
lhc_setup.add_cycle('PSB', PSBCYCLES['MD'], 21)
lhc_setup.fill_empty_slots_with_cycle('PSB', PSBCYCLES['ISOLDE'])
lhc_setup.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 48)
lhc_setup.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 47)
# Plot and do some basic calculations
GridVisualizer(lhc_setup).display()
iso_current_uA = lhc_setup.psb_supercycle.proton_flux['ISOLDE']*1.6e-19*1e6
print(f'ISOLDE current: {iso_current_uA} uA')


# %%
######################################
# Dedicated MD supercycle grid
######################################
dedicated_md = SupercycleGrid(nr_of_slots=43, name='Dedicated MD')
# SPS
dedicated_md.add_cycle('SPS', SPSCYCLES['MD dedicated'], 4)
dedicated_md.add_cycle('SPS', SPSCYCLES['MD dedicated'])
# PS
dedicated_md.add_cycle('PS', PSCYCLES['MD short'], 14)
dedicated_md.add_cycle('PS', PSCYCLES['TOF'], 16)
dedicated_md.add_cycle('PS', PSCYCLES['EAST T9'], 17)
dedicated_md.add_cycle('PS', PSCYCLES['EAST T8'], 19)
dedicated_md.add_cycle('PS', PSCYCLES['ZERO'], 21)
dedicated_md.add_cycle('PS', PSCYCLES['MD short'], 34)
dedicated_md.add_cycle('PS', PSCYCLES['TOF'], 36)
dedicated_md.add_cycle('PS', PSCYCLES['EAST TN'], 37)
dedicated_md.add_cycle('PS', PSCYCLES['TOF'], 39)
dedicated_md.add_cycle('PS', PSCYCLES['TOF'], 40)
dedicated_md.add_cycle('PS', PSCYCLES['ZERO'], 41)
# PSB
dedicated_md.add_cycle('PSB', PSBCYCLES['MD'], 14)
dedicated_md.add_cycle('PSB', PSBCYCLES['MD'], 34)
dedicated_md.fill_empty_slots_with_cycle('PSB', PSBCYCLES['ISOLDE'])
dedicated_md.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 43)
dedicated_md.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 42)
dedicated_md.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 41)
# Plot and do some basic calculations
GridVisualizer(dedicated_md, grid_size=(15, 8), dynamic_grid_size=False).display()


# %%
######################################
# Thursday MD (long parallel) supercycle grid
######################################
thursday_md = SupercycleGrid(nr_of_slots=34, name='Thursday MD')
# SPS
thursday_md.add_cycle('SPS', SPSCYCLES['SFTPRO'], 3)
thursday_md.add_cycle('SPS', SPSCYCLES['MD dedicated'])
thursday_md.add_cycle('SPS', SPSCYCLES['deGauss'])
# PS
thursday_md.add_cycle('PS', PSCYCLES['EAST T9'], 4)
thursday_md.add_cycle('PS', PSCYCLES['TOF'], 6)
thursday_md.add_cycle('PS', PSCYCLES['EAST T8'], 7)
thursday_md.add_cycle('PS', PSCYCLES['ZERO'], 9)
thursday_md.add_cycle('PS', PSCYCLES['EAST T8'], 22)
thursday_md.add_cycle('PS', PSCYCLES['EAST TN'], 24)
thursday_md.add_cycle('PS', PSCYCLES['EAST T9'], 26)
thursday_md.add_cycle('PS', PSCYCLES['TOF'], 28)
thursday_md.add_cycle('PS', PSCYCLES['TOF'], 29)
thursday_md.add_cycle('PS', PSCYCLES['EAST T8'], 30)
thursday_md.add_cycle('PS', PSCYCLES['EAST T9'], 32)
# PSB
thursday_md.fill_empty_slots_with_cycle('PSB', PSBCYCLES['ISOLDE'])
thursday_md.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 34)
thursday_md.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 33)
# Plot and do some basic calculations
GridVisualizer(thursday_md, grid_size=(12, 8), dynamic_grid_size=False).display()


# %%
######################################
# AWAKE supercycle grid
######################################
awake = SupercycleGrid(nr_of_slots=38, name='AWAKE')
# SPS
awake.add_cycle('SPS', SPSCYCLES['SFTPRO'], 3)
awake.add_cycle('SPS', SPSCYCLES['AWAKE'])
awake.add_cycle('SPS', SPSCYCLES['deGauss'])
awake.add_cycle('SPS', SPSCYCLES['SFTPRO'])
awake.add_cycle('SPS', SPSCYCLES['AWAKE'])
awake.add_cycle('SPS', SPSCYCLES['deGauss'])
# PS
awake.add_cycle('PS', PSCYCLES['TOF'], 4)
awake.add_cycle('PS', PSCYCLES['EAST T9'], 5)
awake.add_cycle('PS', PSCYCLES['ZERO'], 7)
awake.add_cycle('PS', PSCYCLES['ZERO'], 8)
awake.add_cycle('PS', PSCYCLES['EAST T8'], 9)
awake.add_cycle('PS', PSCYCLES['EAST T8'], 13)
awake.add_cycle('PS', PSCYCLES['TOF'], 15)
awake.add_cycle('PS', PSCYCLES['ZERO'], 16)
awake.add_cycle('PS', PSCYCLES['EAST TN'], 17)
awake.add_cycle('PS', PSCYCLES['TOF'], 19)
awake.add_cycle('PS', PSCYCLES['EAST T8'], 22)
awake.add_cycle('PS', PSCYCLES['MD'], 24)
awake.add_cycle('PS', PSCYCLES['EAST T9'], 27)
awake.add_cycle('PS', PSCYCLES['EAST T8'], 31)
awake.add_cycle('PS', PSCYCLES['ZERO'], 33)
awake.add_cycle('PS', PSCYCLES['TOF'], 34)
awake.add_cycle('PS', PSCYCLES['TOF'], 35)
awake.add_cycle('PS', PSCYCLES['EAST TN'], 36)
# PSB
awake.add_cycle('PSB', PSBCYCLES['MD'], 25)
awake.fill_empty_slots_with_cycle('PSB', PSBCYCLES['ISOLDE'])
awake.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 38)
awake.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 37)
# Plot and do some basic calculations
GridVisualizer(awake).display()
print(awake.sps_supercycle.cycle_counts)
print(awake.ps_supercycle.cycle_counts)
print(awake.psb_supercycle.cycle_counts)
iso_current_uA = awake.psb_supercycle.proton_flux['ISOLDE']*1.6e-19*1e6
print(f'ISOLDE current: {iso_current_uA} uA')



# %%
######################################
# AWAKE with parallel MD supercycle grid
######################################
awake_w_MD = SupercycleGrid(nr_of_slots=44, name='AWAKE with parallel MD')
# SPS
awake_w_MD.add_cycle('SPS', SPSCYCLES['SFTPRO'], 3)
awake_w_MD.add_cycle('SPS', SPSCYCLES['AWAKE'])
awake_w_MD.add_cycle('SPS', SPSCYCLES['MD parallel'])
awake_w_MD.add_cycle('SPS', SPSCYCLES['SFTPRO'])
awake_w_MD.add_cycle('SPS', SPSCYCLES['AWAKE'])
awake_w_MD.add_cycle('SPS', SPSCYCLES['MD parallel'])
# PS
awake_w_MD.add_cycle('PS', PSCYCLES['EAST T9'], 4)
awake_w_MD.add_cycle('PS', PSCYCLES['EAST TN'], 6)
awake_w_MD.add_cycle('PS', PSCYCLES['TOF'], 8)
awake_w_MD.add_cycle('PS', PSCYCLES['EAST T8'], 9)
awake_w_MD.add_cycle('PS', PSCYCLES['EAST T8'], 13)
awake_w_MD.add_cycle('PS', PSCYCLES['TOF'], 15)
awake_w_MD.add_cycle('PS', PSCYCLES['TOF'], 16)
awake_w_MD.add_cycle('PS', PSCYCLES['EAST TN'], 19)
awake_w_MD.add_cycle('PS', PSCYCLES['TOF'], 21)
awake_w_MD.add_cycle('PS', PSCYCLES['ZERO'], 22)
awake_w_MD.add_cycle('PS', PSCYCLES['EAST T8'], 25)
awake_w_MD.add_cycle('PS', PSCYCLES['EAST T9'], 27)
awake_w_MD.add_cycle('PS', PSCYCLES['MD'], 29)
awake_w_MD.add_cycle('PS', PSCYCLES['EAST T8'], 34)
awake_w_MD.add_cycle('PS', PSCYCLES['EAST TN'], 36)
awake_w_MD.add_cycle('PS', PSCYCLES['EAST T9'], 40)
awake_w_MD.add_cycle('PS', PSCYCLES['EAST T8'], 42)
# PSB
awake_w_MD.add_cycle('PSB', PSBCYCLES['MD'], 30)
awake_w_MD.fill_empty_slots_with_cycle('PSB', PSBCYCLES['ISOLDE'])
awake_w_MD.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 44)
awake_w_MD.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 43)
# Plot and do some basic calculations
GridVisualizer(awake_w_MD).display()


# %%
######################################
# HiRadMat supercycle grid
######################################
hiradmat = SupercycleGrid(nr_of_slots=34, name='HiRadMat')
# SPS
hiradmat.add_cycle('SPS', SPSCYCLES['SFTPRO'], 3)
hiradmat.add_cycle('SPS', SPSCYCLES['HiRadMat'])
hiradmat.add_cycle('SPS', SPSCYCLES['deGauss'])
# PS
hiradmat.add_cycle('PS', PSCYCLES['EAST T9'], 4)
hiradmat.add_cycle('PS', PSCYCLES['TOF'], 6)
hiradmat.add_cycle('PS', PSCYCLES['EAST T8'], 7)
hiradmat.add_cycle('PS', PSCYCLES['ZERO'], 9)
hiradmat.add_cycle('PS', PSCYCLES['EAST T8'], 22)
hiradmat.add_cycle('PS', PSCYCLES['EAST TN'], 24)
hiradmat.add_cycle('PS', PSCYCLES['EAST T9'], 26)
hiradmat.add_cycle('PS', PSCYCLES['TOF'], 28)
hiradmat.add_cycle('PS', PSCYCLES['TOF'], 29)
hiradmat.add_cycle('PS', PSCYCLES['EAST T8'], 30)
hiradmat.add_cycle('PS', PSCYCLES['EAST T9'], 32)
# PSB
hiradmat.fill_empty_slots_with_cycle('PSB', PSBCYCLES['ISOLDE'])
hiradmat.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 34)
hiradmat.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 33)
# Plot and do some basic calculations
GridVisualizer(hiradmat).display()


# %%
######################################
# Scrubbing supercycle grid
######################################
scrubbing = SupercycleGrid(nr_of_slots=34, name='Scrubbing')
# SPS
scrubbing.add_cycle('SPS', SPSCYCLES['SFTPRO'], 3)
scrubbing.add_cycle('SPS', SPSCYCLES['Scrubbing'])
scrubbing.add_cycle('SPS', SPSCYCLES['deGauss'])
# PS
scrubbing.add_cycle('PS', PSCYCLES['EAST T9'], 4)
scrubbing.add_cycle('PS', PSCYCLES['TOF'], 6)
scrubbing.add_cycle('PS', PSCYCLES['EAST T8'], 7)
scrubbing.add_cycle('PS', PSCYCLES['ZERO'], 9)
scrubbing.add_cycle('PS', PSCYCLES['EAST T8'], 22)
scrubbing.add_cycle('PS', PSCYCLES['EAST TN'], 24)
scrubbing.add_cycle('PS', PSCYCLES['EAST T9'], 26)
scrubbing.add_cycle('PS', PSCYCLES['TOF'], 28)
scrubbing.add_cycle('PS', PSCYCLES['TOF'], 29)
scrubbing.add_cycle('PS', PSCYCLES['EAST T8'], 30)
scrubbing.add_cycle('PS', PSCYCLES['EAST T9'], 32)
# PSB
scrubbing.fill_empty_slots_with_cycle('PSB', PSBCYCLES['ISOLDE'])
scrubbing.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 34)
scrubbing.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 33)
# Plot and do some basic calculations
GridVisualizer(scrubbing).display()


#%%
######################################
# Save scenario
######################################
supercycle_grids = {
    physics.name: physics,
    physics_w_MD.name: physics_w_MD,
    lhc_filling.name: lhc_filling,
    lhc_setup.name: lhc_setup,
    dedicated_md.name: dedicated_md,
    thursday_md.name: thursday_md,
    awake.name: awake,
    awake_w_MD.name: awake_w_MD,
    hiradmat.name: hiradmat,
    scrubbing.name: scrubbing,
}
time_shares = {
    physics.name: 38.8,
    physics_w_MD.name: 20.3,
    lhc_filling.name: 14,
    lhc_setup.name: 5,
    dedicated_md.name: 4.4,
    thursday_md.name: 2.6,
    awake.name: 8,
    awake_w_MD.name: 2.9,
    hiradmat.name: 3,
    scrubbing.name: 1,
}
# verify that time shares add up to 100
assert sum(time_shares.values()) == 100
# save scenario
scenario = {
    'supercycle_grids': supercycle_grids,
    'time_shares': time_shares,
}
with open('000_run3_typical_supercycles.pkl', 'wb') as file:
    pickle.dump(scenario, file)