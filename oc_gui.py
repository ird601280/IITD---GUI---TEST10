import sys
import numpy as np
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import OC


class OC_GUI(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        uic.loadUi("oc_controller.ui", self)

        self.oc = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_temperature)

        # Matplotlib Setup
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QtWidgets.QVBoxLayout(self.plot_widget)
        layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)

        # Connect buttons
        self.btn_connect.clicked.connect(self.connect_oc)
        self.btn_set.clicked.connect(self.set_parameters)
        self.btn_enable.clicked.connect(self.enable_oc)
        self.btn_disable.clicked.connect(self.disable_oc)
        self.btn_stability.clicked.connect(self.stability_test)

        self.monitored_temps = []
        self.monitored_times = []

    # -----------------------------
    # Connect to OC
    # -----------------------------
    def connect_oc(self):
        port = self.lineEdit_com.text()
        try:
            self.oc = OC.OC(port)
            self.text_log.append("Connected to OC controller.")
            self.timer.start(1000)
        except Exception as e:
            self.text_log.append(str(e))

    # -----------------------------
    # Set temperature & ramp
    # -----------------------------
    def set_parameters(self):
        temp = self.spin_settemp.value()
        ramp = self.spin_ramp.value()

        self.oc.set_ramp_rate(ramp)
        self.oc.set_temperature(temp)

        self.text_log.append(f"Set Temp: {temp} C | Ramp: {ramp} C/s")

    # -----------------------------
    def enable_oc(self):
        self.oc.enable()
        self.text_log.append("Heater Enabled")

    def disable_oc(self):
        self.oc.disable()
        self.text_log.append("Heater Disabled")

    # -----------------------------
    # Update temperature
    # -----------------------------
    def update_temperature(self):
        if self.oc:
            self.oc.get_status()
            temp = self.oc.temperature[0]
            self.label_temp_value.setText(f"{temp:.3f} C")

            self.monitored_temps.append(temp)
            self.monitored_times.append(datetime.now())

            self.update_plot()

    # -----------------------------
    # Plot
    # -----------------------------
    def update_plot(self):
        if len(self.monitored_times) > 1:
            elapsed = [(t - self.monitored_times[0]).total_seconds()
                       for t in self.monitored_times]

            self.ax.clear()
            self.ax.plot(elapsed, self.monitored_temps)
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel("Temperature (C)")
            self.canvas.draw()

    # -----------------------------
    # Stability Test
    # -----------------------------
    def stability_test(self):

        stability_range = 0.1
        stability_time = 20

        in_range = False
        stable = False

        while not stable:
            self.oc.get_status()
            temp = self.oc.temperature[0]
            setpoint = self.oc.setpoint[0]

            diff = abs(temp - setpoint)

            if diff <= stability_range:
                if not in_range:
                    in_range = True
                    t0 = datetime.now()

                if (datetime.now() - t0).seconds >= stability_time:
                    stable = True
            else:
                in_range = False

            QtWidgets.QApplication.processEvents()

        self.text_log.append("Temperature Stable!")


# -----------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = OC_GUI()
    window.show()
    sys.exit(app.exec_())
