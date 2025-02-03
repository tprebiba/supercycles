#%%
from supercycles.database import SPSCYCLES, PSCYCLES, PSBCYCLES
from supercycles.supercycle_grid import SupercycleGrid
from supercycles.vizualizer import GridVisualizer

#%%
# Physics supercycle
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
GridVisualizer(physics).display(save_png_to='../images/supercycle_grid_example.png')
physics._count_cycles()
# %%
