import supercycles.acc_constants as cnst
from supercycles.helpers import load_cycle_from_csv
from supercycles.supercycle import Supercycle
import numpy as np
from supercycles.database import SPSCYCLES, PSCYCLES, PSBCYCLES
import copy


class SupercycleGrid():
    def __init__(self, name='Physics', nr_of_slots=50):
        '''
        supercycles [dict]: dictionary of accelerator: SuperCycle
        '''
        self.name = name
        self.nr_of_slots = nr_of_slots

        self.sps_grid = np.full(nr_of_slots, None) # None indicates empty BP slots
        self.ps_grid = np.full(nr_of_slots, None)
        self.psb_grid = np.full(nr_of_slots, None)
        self.sps_supercycle = Supercycle('SPS', name, [])
        self.ps_supercycle = Supercycle('PS', name, [])
        self.psb_supercycle = Supercycle('PSB', name, [])
        self.sps_cycle_counts = {}
        self.ps_cycle_counts = {}
        self.psb_cycle_counts = {}


    def _get_grid(self, accelerator):
        '''
        Get grid for a specific accelerator
        '''
        if accelerator == 'SPS':
            return self.sps_grid, self.sps_supercycle
        elif accelerator == 'PS':
            return self.ps_grid, self.ps_supercycle
        elif accelerator == 'PSB':
            return self.psb_grid, self.psb_supercycle
        else:
            raise ValueError(f"Unknown accelerator: {accelerator}")


    def add_cycle(self, accelerator, cycle, start_slot=None):
        '''
        Adds a cycle to the supercycle grid.
        '''
        try:
             # Save states for rollback
            sps_grid0, sps_supercycle0 = self.sps_grid.copy(), copy.deepcopy(self.sps_supercycle)
            ps_grid0, ps_supercycle0 = self.ps_grid.copy(), copy.deepcopy(self.ps_supercycle)
            psb_grid0, psb_supercycle0 = self.psb_grid.copy(), copy.deepcopy(self.psb_supercycle)

            grid, supercycle = self._get_grid(accelerator)

            # Automatically find the last available slot if not explicitly given
            if start_slot is None:
                # Find the last occupied slot in the grid
                last_occupied_slot = max((i for i, x in enumerate(grid) if x is not None), default=-1)
                start_slot = last_occupied_slot + 1 + 1 # +1 to have it as a slot ID

            # Do some checks before placing the supercycle
            self._validate_placement(cycle, start_slot-1, grid, accelerator) # -1 to convert to 0-based index
            
            # Place the cycle in the primary grid
            for i in range(cycle.bps):
                grid[start_slot -1 + i] = cycle.name # -1 to convert to 0-based index
            #print(f"{cycle.name} added at slot {start_slot} on {accelerator}")
            supercycle.add_cycle(cycle)

            # Handle coupled cycles recursively
            if cycle.coupled_cycle:
                next_start = start_slot - cycle.offset_to_upstream
                for _ in range(cycle.number_of_injections):
                    self.add_cycle(cycle.coupled_cycle.accelerator, cycle.coupled_cycle, next_start)
                    next_start += cycle.coupled_cycle.bps
        except Exception as e:
            # Rollback all states if an error occurs
            self.sps_grid, self.sps_supercycle = sps_grid0, sps_supercycle0
            self.ps_grid, self.ps_supercycle = ps_grid0, ps_supercycle0
            self.psb_grid, self.psb_supercycle = psb_grid0, psb_supercycle0
            raise e


    def _validate_placement(self, cycle, start_slot, grid, accelerator):
        # Ensure cycle fits within grid and slots are available
        if start_slot + cycle.bps > len(grid):
            raise ValueError(f"Error adding cycle {cycle.name} to {accelerator} grid: does not fit within the supercycle grid - make it bigger.")
        if start_slot<0:
            raise ValueError(f"Error adding cycle {cycle.name} to {accelerator} grid: placement goes beyond the start of the supercycle grid.")
        if grid[start_slot] is not None:
            raise ValueError(f"Error adding cycle {cycle.name} to {accelerator} grid: cycle overlaps with {grid[start_slot]} at slot {start_slot}.")


    def remove_cycle(self, accelerator, cycle, start_slot=None):
        '''
        Removes a cycle from the supercycle grid.
        '''
        grid, supercycle = self._get_grid(accelerator)

        # Automatically find the last occurrence if start_slot is None
        if start_slot is None:
            last_occurrence_slot = max((i for i, x in enumerate(grid) if x == cycle.name), default=None)
            if last_occurrence_slot is None:
                print(f"No occurrences of {cycle.name} found on {accelerator}")
                return
            start_slot = last_occurrence_slot - (cycle.bps - 1) + 1 # +1 to have it as a slot ID

        # Ensure the cycle name matches the slot
        if grid[start_slot-1] != cycle.name:
            print(f"No matching cycle found at slot {start_slot} on {accelerator}")
            return

        # Remove all slots occupied by this cycle
        cleared_slots = 0
        for i in range(start_slot-1, start_slot-1 + cycle.bps):
            if grid[i] == cycle.name:
                grid[i] = None
                cleared_slots += 1
        #print(f"Removed {cycle.name} from {accelerator} ({cleared_slots} BP slots cleared)")
        supercycle.remove_cycle(cycle)

        # Handle coupled cycles recursively
        if cycle.coupled_cycle:
            coupled_start_slot = start_slot - cycle.offset_to_upstream
            for _ in range(cycle.number_of_injections):
                self.remove_cycle(cycle.coupled_cycle.accelerator, cycle.coupled_cycle, coupled_start_slot)
                coupled_start_slot += cycle.coupled_cycle.bps


    def display_grids(self):
        print("\nSPS SC:", self.sps_grid)
        print("PS SC: ", self.ps_grid)
        print("PSB SC:", self.psb_grid)


    def fill_empty_slots_with_cycle(self, accelerator, cycle):
        """
        Fill all empty slots in the specified accelerator grid with the given cycle.
        """
        grid, supercycle = self._get_grid(accelerator)

        # Find and fill empty slots
        for i in range(len(grid)):
            if grid[i] is None:
                # Check if the cycle fits from this slot
                if i + cycle.bps <= len(grid) and all(slot is None for slot in grid[i:i + cycle.bps]):
                    for j in range(cycle.bps):
                        grid[i + j] = cycle.name
                    supercycle.add_cycle(cycle)


    def _count_cycles(self):
        for supercycle, counts in zip([self.sps_supercycle, self.ps_supercycle, self.psb_supercycle], [self.sps_cycle_counts, self.ps_cycle_counts, self.psb_cycle_counts]):
            counts = {item: supercycle.cycle_names.count(item) for item in set(supercycle.cycle_names)}
            print(counts)