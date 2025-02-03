import supercycles.acc_constants as cnst
from supercycles.helpers import load_cycle_from_csv


class Cycle():
    '''
    A simple cycle representation.
    Inputs:
        - accelerator [str]: accelerator name
        - name [str]: cycle name
        - bps [int]: number of basic periods in the cycle
    Optional inputs:
        - destination [str]: cycle destination
        - lsa_cycle [str]: LSA cycle name
        - timing_user [str]: TGM user
        - coupled_cycle [Cycle]: coupled cycle in upstream accelerator
        - number_of_injections [int]: number of injections
        - offset_to_upstream [int]: number of BPs before the coupled cycle starts relative to the upstream cycle
        - cycle_profile_file [str]: csv file name with cycle profile
        - average_power [float]: average cycle power [MW]
        - color [str]: cycle color
    Other class variables:
        - length [float]: cycle length [sec]
        - cycle_profile_x [np.array]: cycle profile in x axis [ms]
        - cycle_profile_y [np.array]: cycle profile in y axis [A]
    '''
    def __init__(self,
                 accelerator, name, bps, 
                 destination='', lsa_cycle = '', timing_user='',
                 coupled_cycle=None, number_of_injections=1, offset_to_upstream=0,
                 cycle_profile_file = None, average_power=0,
                 total_intensity_per_cycle_e10 = 0, transmission_to_destination=1,
                 color='white'
                 ):
        
        self.accelerator = accelerator 
        self.name = name
        self.bps = bps
        self.destination = destination
        self.lsa_cycle = lsa_cycle
        self.timing_user = timing_user
        self.coupled_cycle = coupled_cycle
        self.number_of_injections = number_of_injections
        self.offset_to_upstream = offset_to_upstream
        self.average_power = average_power # [MW]
        self.total_intensity_per_cycle_e10 = total_intensity_per_cycle_e10 # [e10]
        self.transmission_to_destination = transmission_to_destination
        self.color = color

        self.length = self.bps*cnst.BASIC_PERIOD # [sec]        
        self.cycle_profile_x = None
        self.cycle_profile_y = None
        if cycle_profile_file:
            self.cycle_profile_x, self.cycle_profile_y = load_cycle_from_csv(cycle_profile_file)
