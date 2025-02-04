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
viz = SchedulerStatisticsVisualizer(scheduler)

#%%
# Plotting time share of each supercycle
#viz.plot_pie(scheduler.time_share.keys(), scheduler.time_share.values())
#viz.plot_pie(scheduler.effective_time_share.keys(), scheduler.effective_time_share.values())
viz.plot_pie(scheduler.time_share.keys(), scheduler.time_share.values(), show_downtime=True) # same as above

#%%
# Plotting time share of sps, ps and psb cycles
viz.plot_pie(scheduler.sps_total_cycle_times.keys(), scheduler.sps_total_cycle_times.values(), 
             autopct = '%1.1f%%', show_downtime=True)
viz.plot_pie(scheduler.ps_total_cycle_times.keys(), scheduler.ps_total_cycle_times.values(),
             autopct = '%1.1f%%', show_downtime=False)
viz.plot_pie(scheduler.psb_total_cycle_times.keys(), scheduler.psb_total_cycle_times.values(),
             autopct = '%1.1f%%', show_downtime=False)
