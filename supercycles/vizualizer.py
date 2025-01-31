import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

class SupercyclePlotter:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 4))
        self.color_map = {}  # Optional: store colors for destinations

    def plot_supercycle(self, supercycle):
        """
        Plot a single supercycle using rectangles for each cycle.
        """
        self.ax.clear()  # Clear any previous plots
        current_x = 0

        for cycle in supercycle.cycles:
            color = self._get_cycle_color(cycle.destination)
            rect = Rectangle((current_x, 0), cycle.length, 1, edgecolor='black', facecolor=color)
            self.ax.add_patch(rect)
            self.ax.text(current_x + cycle.length / 2, 0.5, cycle.name,
                          ha='center', va='center', fontsize=10)
            current_x += cycle.length

        self.ax.set_xlim(0, supercycle.length)
        self.ax.set_ylim(0, 1.5)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_title(f"Supercycle for {supercycle.accelerator}")
        plt.show()

    def plot_coupled_supercycles(self, coupled_supercycle):
        """
        Plot coupled supercycles for multiple accelerators.
        """
        self.ax.clear()
        y_position = len(coupled_supercycle.supercycles)

        for acc, supercycle in coupled_supercycle.supercycles.items():
            current_x = 0
            for cycle in supercycle.cycles:
                color = self._get_cycle_color(cycle.destination)
                rect = Rectangle((current_x, y_position - 0.5), cycle.length, 0.8,
                                  edgecolor='black', facecolor=color)
                self.ax.add_patch(rect)
                self.ax.text(current_x + cycle.length / 2, y_position - 0.1, cycle.name,
                              ha='center', va='center', fontsize=8)
                current_x += cycle.length

            y_position -= 1

        self.ax.set_xlim(0, max(sc.length for sc in coupled_supercycle.supercycles.values()))
        self.ax.set_ylim(0, len(coupled_supercycle.supercycles) + 1)
        self.ax.set_xlabel("Time (s)")
        self.ax.set_yticks(range(1, len(coupled_supercycle.supercycles) + 1))
        self.ax.set_yticklabels(coupled_supercycle.supercycles.keys())
        self.ax.set_title("Coupled Supercycles Visualization")
        plt.show()

    def _get_cycle_color(self, destination):
        """
        Return a color for the given destination. Assigns new colors as needed.
        """
        if destination not in self.color_map:
            # Assign a random color for new destinations
            import random
            self.color_map[destination] = (random.random(), random.random(), random.random())
        return self.color_map[destination]
