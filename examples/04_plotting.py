#%%
"""
04 - Plotting a supercycle and the SPS magnet current.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))   # for scenarios/
import matplotlib.pyplot as plt
from supercycles.plotting import plot_supercycle, plot_magnet_current
from scenarios.run3_typical import physics

sc = physics()

#%%
fig, axs = plt.subplots(2, 1, figsize=(14, 5.5), gridspec_kw={'height_ratios': [1.2, 1]})
plot_supercycle(sc, ax=axs[0])                 # injected cycles are drawn slightly lighter
plot_magnet_current(sc, 'SPS', ax=axs[1])
fig.tight_layout()
plt.show()

#%%
# BP numbers instead of time on the x axis
plot_supercycle(sc, show_time=False)
plt.show()
