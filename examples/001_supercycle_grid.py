#%%
from supercycles.database import SPSCYCLES, PSCYCLES, PSBCYCLES
from supercycles.supercycle_grid import SupercycleGrid
from supercycles.vizualizer import GridVisualizer

#%%
# Make and display a supercycle grid
sc_grid = SupercycleGrid(nr_of_slots=35, name='LHC filling')
#sc_grid = SupercycleGrid(nr_of_slots=10, name='LHC filling')
sc_grid.display_grids()
GridVisualizer(sc_grid).display()

#%%
# Add some cycles in the SPS and their injections
sc_grid.add_cycle('SPS', SPSCYCLES['SFTPRO'], 3) # add at a specific slot ID
sc_grid.add_cycle('SPS', SPSCYCLES['LHC filling']) # add at the last available ID
sc_grid.add_cycle('SPS', SPSCYCLES['deGauss']) # add at the last available ID
GridVisualizer(sc_grid).display()

#%%
# Add some cycles in the PSB and PS
sc_grid.add_cycle('PSB', PSBCYCLES['ISOLDE'], 3)
sc_grid.add_cycle('PS', PSCYCLES['EAST'], 5)
sc_grid.add_cycle('PS', PSCYCLES['EAST'], 24)
sc_grid.add_cycle('PS', PSCYCLES['EAST'], 28)
sc_grid.add_cycle('PS', PSCYCLES['TOF'], 30)
sc_grid.add_cycle('PS', PSCYCLES['TOF'], 31)
GridVisualizer(sc_grid).display()

#%%
# Remove some cycles
sc_grid.remove_cycle('PS', PSCYCLES['EAST']) # removes the last occurrence of the cycle
GridVisualizer(sc_grid).display()
sc_grid.remove_cycle('PS', PSCYCLES['EAST']) # removes the last occurrence of the cycle
GridVisualizer(sc_grid).display()
sc_grid.remove_cycle('SPS', SPSCYCLES['LHC filling'])
GridVisualizer(sc_grid).display()

#%% Try to add a cycle that overlaps with an existing cycle
sc_grid.add_cycle('SPS', SPSCYCLES['LHC filling'], 4)