#%%
from supercycles.database import SPSCYCLES, PSCYCLES, PSBCYCLES
from supercycles.supercycle_grid import SupercycleGrid
from supercycles.vizualizer import GridVisualizer

#%%
# Interact with grid
sc_grid = SupercycleGrid(nr_of_slots=35, name='LHC filling')
#sc_grid.display_grids()
sc_grid.add_cycle('SPS', SPSCYCLES['SFTPRO'], 2)
sc_grid.add_cycle('SPS', SPSCYCLES['LHC filling'])
sc_grid.add_cycle('SPS', SPSCYCLES['deGauss'])
#sc_grid.remove_cycle('SPS', SPSCYCLES['LHC filling'])
sc_grid.add_cycle('PSB', PSBCYCLES['ISOLDE'], 2)
sc_grid.add_cycle('PS', PSCYCLES['EAST'], 4)
GridVisualizer(sc_grid).display()
#sc_grid.remove_cycle('PSB', PSBCYCLES['ISOLDE'])
#sc_grid.remove_cycle('PSB', PSBCYCLES['ISOLDE'], 2)

sc_grid.add_cycle('PS', PSCYCLES['EAST'], 24)
sc_grid.add_cycle('PS', PSCYCLES['EAST'], 28)
GridVisualizer(sc_grid).display()

sc_grid.remove_cycle('PS', PSCYCLES['EAST'])
GridVisualizer(sc_grid).display()
sc_grid.remove_cycle('PS', PSCYCLES['EAST'])
GridVisualizer(sc_grid).display()

sc_grid.remove_cycle('SPS', SPSCYCLES['LHC filling'])
GridVisualizer(sc_grid).display()

# %%
