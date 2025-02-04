import pickle
import pandas as pd
from collections import Counter


class Scheduler:
    def __init__(self, scenario={}, time_share={},
                 run_duration_days=214.5, machine_availability=0.8):
        """
        Initialize the Scheduler with optional scenario data.
        """
        self.scenario = scenario
        self.machine_availability = machine_availability
        self._set_time_share(time_share)
        self._set_run_duration(run_duration_days)
        self._calculate_supercycle_counts()
        self._calculate_cycle_counts()
        self._calculate_cycle_time()

    def _scenario_from_pickle(self, filename):
        """
        Load a SupercycleGrid object from a pickle file.
        """
        with open(filename, 'rb') as file:
            scenario = pickle.load(file)
        print(f"SupercycleGrid loaded from {filename}")
        self.scenario = scenario

    def _set_time_share(self, time_share):
        """
        Set the time share of each supercycle in the schedule.
        """
        self.time_share = time_share
        self.effective_time_share = {key: value * self.machine_availability for key, value in time_share.items()}
        self.effective_time_share['Downtime'] = (1-self.machine_availability)*100

    def _set_run_duration(self, days=214.5):
        """
        Set the duration of the scenario in days and the machine availability.
        """
        self.run_duration_weeks = days / 7
        self.run_duration_days = days
        self.run_duration_hours = days * 24
        self.run_duration_seconds = days * 24 * 3600

        self.run_duration_effective_weeks = self.run_duration_weeks * self.machine_availability
        self.run_duration_effective_days = self.run_duration_days * self.machine_availability
        self.run_duration_effective_hours = self.run_duration_hours * self.machine_availability
        self.run_duration_effective_seconds = self.run_duration_seconds * self.machine_availability

    def _calculate_supercycle_counts(self):
        """
        Calculate the number of supercycles for each scenario.
        """
        self.supercycle_counts = {key: round(self.run_duration_effective_seconds*self.time_share[key]/100/supercycle.sps_supercycle.length,0) for key, supercycle in self.scenario.items()}

    def _calculate_cycle_counts(self):
        """
        Calculate the number of cycles for each scenario.
        """
        self.sps_total_cycle_counts = Counter()
        self.ps_total_cycle_counts = Counter()
        self.psb_total_cycle_counts = Counter()
        for supercyclename,supercycle in self.scenario.items():
            total_cycle_counts_of_supercycle = {key: value*self.supercycle_counts[supercyclename] for key, value in supercycle.sps_supercycle.cycle_counts.items()}
            self.sps_total_cycle_counts.update(total_cycle_counts_of_supercycle)
            total_cycle_counts_of_supercycle = {key: value*self.supercycle_counts[supercyclename] for key, value in supercycle.ps_supercycle.cycle_counts.items()}
            self.ps_total_cycle_counts.update(total_cycle_counts_of_supercycle)
            total_cycle_counts_of_supercycle = {key: value*self.supercycle_counts[supercyclename] for key, value in supercycle.psb_supercycle.cycle_counts.items()}
            self.psb_total_cycle_counts.update(total_cycle_counts_of_supercycle)
    
    def _calculate_cycle_time(self):
        """
        Calculate the time spent on each cycle for each scenario.
        """
        self.sps_total_cycle_times = Counter()
        self.ps_total_cycle_times = Counter()
        self.psb_total_cycle_times = Counter()
        for supercyclename, supercycle in self.scenario.items():
            total_cycle_times_of_supercycle = {key: value*self.supercycle_counts[supercyclename] for key, value in supercycle.sps_supercycle.cycle_times.items()}
            self.sps_total_cycle_times.update(total_cycle_times_of_supercycle)
            total_cycle_times_of_supercycle = {key: value*self.supercycle_counts[supercyclename] for key, value in supercycle.ps_supercycle.cycle_times.items()}
            self.ps_total_cycle_times.update(total_cycle_times_of_supercycle)
            total_cycle_times_of_supercycle = {key: value*self.supercycle_counts[supercyclename] for key, value in supercycle.psb_supercycle.cycle_times.items()}
            self.psb_total_cycle_times.update(total_cycle_times_of_supercycle)