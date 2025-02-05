import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QDialog, QFormLayout, QLineEdit, QDialogButtonBox
)
from supercycles.database import SPSCYCLES, PSCYCLES, PSBCYCLES
import sys
from supercycles.supercycle_grid import SupercycleGrid
from supercycles.vizualizer import GridVisualizer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class SupercycleModelingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Supercycle Modelling")
        self.setGeometry(100, 100, 800, 600)

        # Initialize main layout and tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create the main tabs
        self.create_cycles_tab()
        self.create_supercycles_tab()
        self.create_statistics_tab()

    def create_cycles_tab(self):
        """Create the Cycles Database tab with sub-tabs for PSB, PS, and SPS"""
        cycles_tab = QTabWidget()

        # Sub-tabs for PSB, PS, and SPS
        psb_tab = self.create_cycle_list_tab(PSBCYCLES, "PSB")
        ps_tab = self.create_cycle_list_tab(PSCYCLES, "PS")
        sps_tab = self.create_cycle_list_tab(SPSCYCLES, "SPS")

        # Add sub-tabs
        cycles_tab.addTab(psb_tab, "PSB")
        cycles_tab.addTab(ps_tab, "PS")
        cycles_tab.addTab(sps_tab, "SPS")

        self.tabs.addTab(cycles_tab, "Cycles Database")

    def create_cycle_list_tab(self, cycles_dict, title):
        """Create a tab listing cycles with their properties"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create table widget
        table = QTableWidget()
        table.setRowCount(len(cycles_dict))
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Name", "BPs", "Number of Injections", "Coupled Cycle"])

        # Populate table
        for row, (key, cycle) in enumerate(cycles_dict.items()):
            table.setItem(row, 0, QTableWidgetItem(cycle.name))
            table.setItem(row, 1, QTableWidgetItem(str(cycle.bps)))
            table.setItem(row, 2, QTableWidgetItem(str(cycle.number_of_injections)))
            table.setItem(row, 3, QTableWidgetItem(str(cycle.coupled_cycle.name if cycle.coupled_cycle else "")))

        layout.addWidget(table)
        tab.setLayout(layout)
        return tab

    def create_supercycles_tab(self):
        """Create the Supercycles tab"""
        self.supercycles_tab = QTabWidget()
        layout = QVBoxLayout()
        
        # Add "Add new supercycle" button
        add_button = QPushButton("Add new supercycle")
        add_button.clicked.connect(self.add_new_supercycle)
        layout.addWidget(add_button)

        container = QWidget()
        container.setLayout(layout)
        self.supercycles_tab.addTab(container, "Main")
        self.tabs.addTab(self.supercycles_tab, "Supercycles")
    
    def add_new_supercycle(self):
        """Handle adding a new supercycle"""
        dialog = QDialog(self)
        dialog.setWindowTitle("New Supercycle Configuration")

        layout = QFormLayout()
        name_input = QLineEdit()
        bp_input = QLineEdit()
        bp_input.setPlaceholderText("Enter number of BPs")
        layout.addRow("Supercycle Name:", name_input)
        layout.addRow("Number of BPs:", bp_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(lambda: self.create_supercycle_tab(name_input.text(), bp_input.text(), dialog))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)
        dialog.exec_()

    def create_supercycle_tab(self, name, bp_count, dialog):
        """Create a new supercycle grid and display it in a sub-tab"""
        if not name or not bp_count.isdigit():
            return
        
        bp_count = int(bp_count)
        sc_grid = SupercycleGrid(nr_of_slots=bp_count, name=name)

        # Create the visualization
        fig = GridVisualizer(sc_grid).display()

        # Wrap the matplotlib figure in a canvas
        canvas = FigureCanvas(fig)
        tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        tab.setLayout(layout)

        self.supercycles_tab.addTab(tab, name)
        dialog.accept()

    def create_statistics_tab(self):
        """Create the Statistics tab"""
        statistics_tab = QWidget()
        statistics_tab.setLayout(self.simple_tab_layout("Statistics Content"))
        self.tabs.addTab(statistics_tab, "Statistics")

    def simple_tab_layout(self, content_text):
        """Create a simple layout for the tabs with some placeholder content"""
        layout = QVBoxLayout()
        label = QLabel(content_text)
        layout.addWidget(label)
        return layout

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SupercycleModelingApp()
    window.show()
    sys.exit(app.exec_())
