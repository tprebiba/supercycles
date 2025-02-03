import matplotlib.pyplot as plt
import numpy as np


class GridVisualizer():
    def __init__(self, supercycle_grid, grid_size=(15, 5),
                 dynamic_grid_size=True):
        """
        Initialize the GridVisualizer.
            supercycle_grid: SupercycleGrid object
            grid_size: Tuple specifying the figure size (width, height)
        """

        self.supercycle_grid = supercycle_grid
        self.grid_size = grid_size

        self.sps_grid = supercycle_grid.sps_grid
        self.sps_supercycle = supercycle_grid.sps_supercycle
        self.ps_grid = supercycle_grid.ps_grid
        self.ps_supercycle = supercycle_grid.ps_supercycle
        self.psb_grid = supercycle_grid.psb_grid
        self.psb_supercycle = supercycle_grid.psb_supercycle
        self.total_slots = self.supercycle_grid.nr_of_slots
        if dynamic_grid_size:
            self.grid_size = (self.total_slots*15/35, 5)

    def _draw_grid(self, ax, grid, y_offset, label, supercycle,
                   fontsize):
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
                ax.text(i + 0.5, y_offset + 0.5, str(grid[i]), ha='center', va='center', fontsize=fontsize-3, rotation=90)
                pass
        
        ax.text(-0.5, y_offset + 0.5, label, ha='right', va='center', fontsize=fontsize, weight='bold')


    def display(self, fontsize=12, 
                save_png_to=None):
        """
        Display the supercycle grids with Slot ID and Time rows.
        """
        fig, ax = plt.subplots(figsize=self.grid_size)

        # Set axis limits and labels
        ax.set_xlim(0, self.total_slots)
        ax.set_ylim(-2, 4)  # Adjust for additional rows
        #ax.set_aspect('equal')
        ax.set_aspect('auto')
        ax.axis('off')

        # Draw Slot ID row above the SPS grid
        for i in range(self.total_slots):
            ax.text(i + 0.5, 3.2, str(i+1), ha='center', va='center', fontsize=fontsize-3, color='black')

        # Draw Time row below the PSB grid (Slot ID * 1.2 seconds)
        for i in range(self.total_slots):
            time_value = round((i+1) * 1.2, 1)
            ax.text(i + 0.5, -.3, f"{time_value}s", ha='center', va='center', fontsize=fontsize-3, color='darkblue')

        # Draw grids
        self._draw_grid(ax, self.sps_grid, 2, "SPS", self.sps_supercycle, fontsize)
        self._draw_grid(ax, self.ps_grid, 1, "PS", self.ps_supercycle, fontsize)
        self._draw_grid(ax, self.psb_grid, 0, "PSB", self.psb_supercycle, fontsize)

        plt.title(f'{self.supercycle_grid.name} supercycle', fontsize=fontsize+2)
        plt.show()
        if save_png_to:
            fig.savefig(save_png_to, dpi=400)

