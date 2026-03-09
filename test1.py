import sys
import serial.tools.list_ports
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QPushButton, QComboBox,
    QDoubleSpinBox, QVBoxLayout, QHBoxLayout,
    QGroupBox, QMessageBox
)

import pyqtgraph as pg
from datetime import datetime

import sys, os

# import your OC class
#from OC import OC


class OCMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("ABHEY OC Controller")
        self.setGeometry(200, 200, 500, 400)

        self.oc = None

        self.init_ui()

        # timer for live updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout()

        # --------- Connection Group ----------
        conn_group = QGroupBox("Connection")
        conn_layout = QHBoxLayout()

        self.port_combo = QComboBox()
        self.refresh_ports()

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_oc)

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_oc)
        self.disconnect_btn.setEnabled(False)

        conn_layout.addWidget(QLabel("COM Port:"))
        conn_layout.addWidget(self.port_combo)
        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.disconnect_btn)
        conn_group.setLayout(conn_layout)

        # --------- Control Group ----------
        ctrl_group = QGroupBox("Control")
        ctrl_layout = QHBoxLayout()

        self.enable_btn = QPushButton("Enable")
        self.enable_btn.clicked.connect(self.enable_output)
        self.enable_btn.setEnabled(False)

        self.disable_btn = QPushButton("Disable")
        self.disable_btn.clicked.connect(self.disable_output)
        self.disable_btn.setEnabled(False)

        ctrl_layout.addWidget(self.enable_btn)
        ctrl_layout.addWidget(self.disable_btn)
        ctrl_group.setLayout(ctrl_layout)

        # --------- Temperature Group ----------
        temp_group = QGroupBox("Temperature Control")
        temp_layout = QHBoxLayout()

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0, 300)
        self.temp_spin.setSuffix(" °C")

        self.set_temp_btn = QPushButton("Set Temperature")
        self.set_temp_btn.clicked.connect(self.set_temperature)
        self.set_temp_btn.setEnabled(False)

        temp_layout.addWidget(self.temp_spin)
        temp_layout.addWidget(self.set_temp_btn)
        temp_group.setLayout(temp_layout)

        # --------- Ramp Rate Group ----------
        ramp_group = QGroupBox("Ramp Rate")
        ramp_layout = QHBoxLayout()

        self.ramp_spin = QDoubleSpinBox()
        self.ramp_spin.setRange(0.01, 100)
        self.ramp_spin.setSuffix(" °C/s")
        self.ramp_spin.setValue(100)

        self.set_ramp_btn = QPushButton("Set Ramp Rate")
        self.set_ramp_btn.clicked.connect(self.set_ramp)
        self.set_ramp_btn.setEnabled(False)

        ramp_layout.addWidget(self.ramp_spin)
        ramp_layout.addWidget(self.set_ramp_btn)
        ramp_group.setLayout(ramp_layout)

        # --------- Status Group ----------
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()

        self.temp_label = QLabel("Temperature: -- °C")
        self.setpoint_label = QLabel("Setpoint: -- °C")
        self.fault_label = QLabel("Fault: None")

        status_layout.addWidget(self.temp_label)
        status_layout.addWidget(self.setpoint_label)
        status_layout.addWidget(self.fault_label)
        status_group.setLayout(status_layout)

        # --------- Assemble ----------
        main_layout.addWidget(conn_group)
        main_layout.addWidget(ctrl_group)
        main_layout.addWidget(temp_group)
        main_layout.addWidget(ramp_group)
        main_layout.addWidget(status_group)

        central.setLayout(main_layout)

    # ================= Logic =================

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for p in ports:
            self.port_combo.addItem(p.name)

    def connect_oc(self):
        port = self.port_combo.currentText()
        try:
            self.oc = OC(port)
            self.timer.start(1000)

            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.enable_btn.setEnabled(True)
            self.disable_btn.setEnabled(True)
            self.set_temp_btn.setEnabled(True)
            self.set_ramp_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Connection Error", str(e))

    def disconnect_oc(self):
        if self.oc:
            self.timer.stop()
            self.oc.OC_close()
            self.oc = None

        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)

    def enable_output(self):
        if self.oc:
            self.oc.enable()

    def disable_output(self):
        if self.oc:
            self.oc.disable()

    def set_temperature(self):
        if self.oc:
            self.oc.set_temperature(self.temp_spin.value())

    def set_ramp(self):
        if self.oc:
            self.oc.set_ramp_rate(self.ramp_spin.value())

    def update_status(self):
        if not self.oc:
            return

        try:
            temp = self.oc.get_temperature()
            self.temp_label.setText(f"Temperature: {temp:.2f} °C")
            self.setpoint_label.setText(f"Setpoint: {self.oc.setpoint[0]:.2f} °C")

            fault = self.oc.get_faults()
            if fault != 0:
                self.fault_label.setText(f"Fault Code: {fault}")
            else:
                self.fault_label.setText("Fault: None")

        except Exception:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = OCMainWindow()
    win.show()
    sys.exit(app.exec_())
