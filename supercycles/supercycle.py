import supercycles.acc_constants as cnst
import numpy as np
import warnings

class Supercycle():
    '''
    A simple supercycle representation for a single accelerator.
    Inputs:
        - accelerator [str]: accelerator name
        - name [str]: supercycle name
        - cycles [list]: list of Cycles in the supercycle
    Other class variables:
        - cycle_index [list]: list of cycle indexes in the supercycle
        - cycle_names [list]: list of cycle names in the supercycle
        - bps [int]: number of basic periods of supercycle
        - length [float]: supercycle length [sec]
        - integrated_power [float]: integrated power [MW]
        - average_power [float]: average power [MW]
    Class methods:
        calculate_supercycle_length: calculates supercycle length and bps
        calculate_supercycle_power: calculates supercycle integrated and average power
        allocate_hours: allocates hours to the supercycle assuming a machine availability
            - allocated_hours [int]: allocated hours
            - allocated_seconds [int]: allocated seconds
            - allocated_bps [int]: allocated basic periods
            - number_of_supercycles_played [int]: number of supercycles played in the allocated time
            - number_of_cycles_played [dict]: number of times each cycle is played in the allocated time
        calculate_free_bps: calculates free BPs of the injector
            - free_bps_per_supercycle [int]: free BPs per supercycle
            - free_bps_total [int]: total free BPs

    '''
    def __init__(self, accelerator, name, cycles):
        
        self.accelerator = accelerator
        self.name = name
        self.cycles = cycles

        if len(self.cycles)>0:
            self.cycle_indices = np.arange(len(self.cycles))+1
            self.cycle_names = []
            for cycle in self.cycles:
                self.cycle_names.append(cycle.name)
            self.bps, self.length = self._calculate_supercycle_length()
            self.integrated_power, self.average_power = self._calculate_supercycle_power()


    def _calculate_supercycle_length(self):
        '''
        Calculate super cycle length and bps
        '''
        bps = 0
        length = 0
        for cycle in self.cycles:
            bps += cycle.bps
            length += cycle.length
        if length > cnst.SC_LENGTH_LIMIT:
            #raise ValueError('%s supercycle length: %1.2f seconds - exceeds limit of %1.2f seconds'%(self.name,self.length,cnst.SC_LENGTH_LIMIT))
            #warnings.warn(f'{self.name} supercycle length: {length} seconds - exceeds limit of {cnst.SC_LENGTH_LIMIT} seconds')
            print(f'{self.name} supercycle length: {length} seconds - exceeds limit of {cnst.SC_LENGTH_LIMIT} seconds')
        return bps, length


    def _calculate_supercycle_power(self):
        '''
        Calculate super cycle average power
        '''
        integrated_power = 0
        for cycle in self.cycles:
            integrated_power += cycle.length*cycle.average_power
        average_power = integrated_power/self.length
        if average_power > cnst.AVERAGE_POWER_LIMIT[self.accelerator]:
            #raise ValueError('%s supercycle has an average power of: %1.2f MW exceeds limit of %1.2f MW for %s'%(self.name,average_power,cnst.AVERAGE_POWER_LIMIT[self.accelerator], self.accelerator))
            #warnings.warn(f'{self.name} supercycle has an average power of: {average_power} MW exceeds limit of {cnst.AVERAGE_POWER_LIMIT[self.accelerator]} MW for {self.accelerator}')
            print(f'{self.name} supercycle has an average power of: {average_power} MW exceeds limit of {cnst.AVERAGE_POWER_LIMIT[self.accelerator]} MW for {self.accelerator}')
        return integrated_power, average_power
    

    def add_cycle(self, cycle):
        '''
        Add a cycle to the supercycle
        '''
        self.cycles.append(cycle)
        self.__init__(self.accelerator, self.name, self.cycles)


    def remove_cycle(self, cycle):
        '''
        Delete a cycle from the supercycle
        '''
        self.cycles.remove(cycle) # removes the last occurrence of the cycle
        self.__init__(self.accelerator, self.name, self.cycles)