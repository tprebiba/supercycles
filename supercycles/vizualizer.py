import matplotlib.pyplot as plt
import numpy as np

class GridVisualizer():
    def __init__(self, supercycle_grid, grid_size=(15, 5)):
        """
        Initialize the GridVisualizer.
        :param sps_grid: List representing the SPS grid
        :param ps_grid: List representing the PS grid
        :param psb_grid: List representing the PSB grid
        :param grid_size: Tuple specifying the figure size (width, height)
        """

        self.supercycle_grid = supercycle_grid
        self.sps_grid = supercycle_grid.sps_grid
        self.sps_supercycle = supercycle_grid.sps_supercycle
        self.ps_grid = supercycle_grid.ps_grid
        self.ps_supercycle = supercycle_grid.ps_supercycle
        self.psb_grid = supercycle_grid.psb_grid
        self.psb_supercycle = supercycle_grid.psb_supercycle
        self.grid_size = grid_size


    def _draw_grid(self, ax, grid, y_offset, label, supercycle):
        """
        Draws a single grid row on the axis.
        :param ax: Matplotlib axis
        :param grid: List representing the accelerator grid
        :param y_offset: Vertical offset for grid row
        :param color: Color of the grid cells
        :param label: Label for the row (e.g., SPS, PS)
        """
        num_slots = len(grid)
        for i in range(num_slots):
            cell_cycle = grid[i]
            if cell_cycle is None:
                cell_color = 'white'
            else:
                cell_color = supercycle.cycle_colors[cell_cycle]
            rect = plt.Rectangle((i, y_offset), 1, 1, edgecolor='black', facecolor=cell_color)
            ax.add_patch(rect)
            if cell_cycle:  # Annotate non-empty slots
                #ax.text(i + 0.5, y_offset + 0.5, str(grid[i]), ha='center', va='center', fontsize=8)
                pass
        
        ax.text(-1, y_offset + 0.5, label, ha='right', va='center', fontsize=10, weight='bold')


    def display(self):
        """
        Display the supercycle grids for SPS, PS, and PSB.
        """
        fig, ax = plt.subplots(figsize=self.grid_size)

        # Set axis limits and labels
        total_slots = max(len(self.sps_grid), len(self.ps_grid), len(self.psb_grid))
        ax.set_xlim(0, total_slots)
        ax.set_ylim(-1, 3)
        ax.set_aspect('equal')
        ax.axis('off')

        # Draw grids
        self._draw_grid(ax, self.sps_grid, 2, "SPS", self.sps_supercycle)
        self._draw_grid(ax, self.ps_grid, 1, "PS", self.ps_supercycle)
        self._draw_grid(ax, self.psb_grid, 0, "PSB", self.psb_supercycle)

        plt.title(f'{self.supercycle_grid.name} supercycle')
        plt.show()
