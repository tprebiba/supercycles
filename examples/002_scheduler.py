#%%
from supercycles.scheduler import Scheduler
import pickle
from supercycles.vizualizer import SchedulerStatisticsVisualizer


# %%
###############################
# run 3 typical supercycles
###############################
with open('../scenarios/000_run3_typical_supercycles.pkl', 'rb') as file:
    scenario = pickle.load(file)
scheduler = Scheduler(scenario['supercycle_grids'], scenario['time_shares'])


#%%
# make some plots
viz = SchedulerStatisticsVisualizer(scheduler)
viz.plot_pie(scheduler.time_share.keys(), scheduler.time_share.values())
viz.plot_pie(scheduler.effective_time_share.keys(), scheduler.effective_time_share.values())

# %%
