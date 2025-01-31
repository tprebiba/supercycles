#%%
from supercycles.database import SPSCYCLES, PSCYCLES, PSBCYCLES
from supercycles.supercycle_grid import SupercycleGrid

# %%
supercycle = SupercycleGrid(nr_of_slots=40)
supercycle.add_cycle('SPS', SPSCYCLES['SFTPRO'], 2)
supercycle.display_grids()
supercycle.remove_cycle('SPS', SPSCYCLES['SFTPRO'])
supercycle.display_grids()

#supercycle.add_cycle('SPS', SPSCYCLES['deGauss'])
#supercycle.display_grids()
#supercycle.remove_cycle('SPS', SPSCYCLES['SFTPRO'])
#supercycle.add_cycle('SPS', SPSCYCLES['LHC filling'])
#supercycle.display_grids()
# %%
