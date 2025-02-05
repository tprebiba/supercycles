import pickle
import pandas as pd
from collections import Counter


class Scheduler():
    def __init__(self, scenario={}, time_share={}, scenario_title=None,
                 run_duration_days=214.5, machine_availability=0.8):
        """
        Initialize the Scheduler with optional scenario data.
        """
        self.scenario = scenario
        self.machine_availability = machine_availability
        self.scenario_title = scenario_title
        self._set_time_share(time_share)
        self._set_run_duration(run_duration_days)
        self._calculate_supercycle_counts()
        self._calculate_cycle_counts()
        self._calculate_cycle_time()
        self._calculate_proton_flux()

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

    def _calculate_proton_flux(self):
        """
        Calculate the proton flux for each scenario.
        """
        self.sps_mean_proton_flux = Counter()
        self.ps_mean_proton_flux = Counter()
        self.psb_mean_proton_flux = Counter()
        for supercyclename, supercycle in self.scenario.items():
            mean_proton_flux_of_supercycle = {key: value*self.effective_time_share[supercyclename] for key, value in supercycle.sps_supercycle.proton_flux.items()}
            self.sps_mean_proton_flux.update(mean_proton_flux_of_supercycle)
            mean_proton_flux_of_supercycle = {key: value*self.effective_time_share[supercyclename] for key, value in supercycle.ps_supercycle.proton_flux.items()}
            self.ps_mean_proton_flux.update(mean_proton_flux_of_supercycle)
            mean_proton_flux_of_supercycle = {key: value*self.effective_time_share[supercyclename] for key, value in supercycle.psb_supercycle.proton_flux.items()}
            self.psb_mean_proton_flux.update(mean_proton_flux_of_supercycle)
        self.sps_mean_proton_flux = {key: value/(sum(self.effective_time_share.values())-self.effective_time_share['Downtime']) for key, value in self.sps_mean_proton_flux.items()}
        self.ps_mean_proton_flux = {key: value/(sum(self.effective_time_share.values())-self.effective_time_share['Downtime']) for key, value in self.ps_mean_proton_flux.items()}
        self.psb_mean_proton_flux = {key: value/(sum(self.effective_time_share.values())-self.effective_time_share['Downtime']) for key, value in self.psb_mean_proton_flux.items()}

    def summary_table(self):
        """
        Create a summary table of the supercycle scenario using Pandas.
        """

        data = {
            "Accelerator": [],
            "Cycle": [],
            "Cycles/year [1e6]": [],
            "Cycles/week [1e3]": [],
            "Cycles/day [1e3]": [],
            "Average proton flux (incl. transm.) [1e10 p/s]": []
        }
        for accelerator_counts, accelerator in zip([self.sps_total_cycle_counts, self.ps_total_cycle_counts, self.psb_total_cycle_counts],
                                                   ["SPS", "PS", "PSB"]):
            for cycle, cycle_count in accelerator_counts.items():
                data["Accelerator"].append(accelerator)
                data["Cycle"].append(cycle)
                data["Cycles/year [1e6]"].append(cycle_count / 1e6)
                data["Cycles/week [1e3]"].append(cycle_count / self.run_duration_weeks / 1e3)
                data["Cycles/day [1e3]"].append(cycle_count / self.run_duration_days / 1e3)
                if accelerator == "SPS":
                    data["Average proton flux (incl. transm.) [1e10 p/s]"].append(self.sps_mean_proton_flux[cycle] / 1e10)
                elif accelerator == "PS":
                    data["Average proton flux (incl. transm.) [1e10 p/s]"].append(self.ps_mean_proton_flux[cycle] / 1e10)
                elif accelerator == "PSB":
                    data["Average proton flux (incl. transm.) [1e10 p/s]"].append(self.psb_mean_proton_flux[cycle] / 1e10)

        df = pd.DataFrame(data)

        # metadata = pd.DataFrame({
        #     "Accelerator": ["Summary Table", "", "", ""],
        #     "Cycle": [f"Run duration: {self.run_duration_days} days", "", "", ""],
        #     "Cycles/year [1e6]": [f"SPS availability: {self.machine_availability * 100} %", "", "", ""],
        #     "Cycles/week [1e3]": ["", "", "", ""],
        #     "Cycles/day [1e3]": ["", "", "", ""]
        # })
        # df = pd.concat([metadata, df], ignore_index=True)

        return df