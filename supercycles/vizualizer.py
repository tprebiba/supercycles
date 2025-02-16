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
        return fig


class SchedulerStatisticsVisualizer():
    def __init__(self, scheduler):
        """
        Initialize the SchedulerStatisticsVisualizer.
            scheduler: Scheduler object
        """
        self.scheduler = scheduler
    
    def plot_pie(self, labels, sizes, show_downtime=False,
                 figsize=(8,8), 
                 autopct='%1.1f%%', fontsize=12, rotation=90, _colors=None):
        """
        Plot a pie chart of the supercycle counts.
        """
        labels = list(labels)
        sizes = list(sizes)
        total_time = sum(sizes)
        if show_downtime:
            downtime = 100*(1 - self.scheduler.machine_availability)
            for i in range(len(sizes)):
                sizes[i] = sizes[i]*(100-downtime)/100
            labels.append('Downtime')
            sizes.append(downtime*total_time/100)
        
        fig, ax = plt.subplots(figsize=figsize, facecolor='white')
        fontsize=fontsize
        wedges, texts, autotexts = ax.pie(
            sizes, labels=labels, autopct=autopct,
            colors=_colors,startangle=rotation,textprops=dict(color="black", size=fontsize)  # Adjust the text properties
        )
        # Adjust the labels to be inside the pie chart
        for text, autotext in zip(texts, autotexts):
            text.set(size=fontsize)
            autotext.set(size=fontsize)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        fig.tight_layout()
        return fig
        