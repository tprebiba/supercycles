#%%
from supercycles.database import SPSCYCLES, PSCYCLES, PSBCYCLES
from supercycles.supercycle_grid import SupercycleGrid
from supercycles.vizualizer import GridVisualizer


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


# %%
######################################
# Dedicated MD supercycle grid
######################################


# %%
######################################
# Thursday MD (long parallel) supercycle grid
######################################


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


# %%
######################################
# HiRadMat supercycle grid
######################################


# %%
######################################
# Scrubbing supercycle grid
######################################