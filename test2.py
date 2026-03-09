import sys
import serial.tools.list_ports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QPushButton, QComboBox, QDoubleSpinBox,
    QVBoxLayout, QHBoxLayout, QGroupBox,
    QTextEdit
)

import pyqtgraph as pg
from datetime import datetime

from OC import OC


# ---------------- Fault Window ----------------
class FaultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fault History")
        self.resize(400, 300)

        layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setReadOnly(True)

        layout.addWidget(self.text)
        self.setLayout(layout)

    def add_fault(self, msg):
        self.text.append(msg)


# ---------------- Main GUI ----------------
class OCMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ABHEY OC Controller")
        self.resize(900, 600)

        self.oc = None
        self.fault_window = FaultWindow()

        self.temp_history = []
        self.time_history = []

        self.init_ui()
        self.apply_dark_theme()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()

        # -------- LEFT PANEL --------
        left = QVBoxLayout()

        # Connection
        conn = QGroupBox("Connection")
        cl = QHBoxLayout()

        self.port_combo = QComboBox()
        for p in serial.tools.list_ports.comports():
            self.port_combo.addItem(p.name)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_oc)

        cl.addWidget(self.port_combo)
        cl.addWidget(self.connect_btn)
        conn.setLayout(cl)

        # Controls
        ctrl = QGroupBox("Controls")
        ctl = QVBoxLayout()

        self.enable_btn = QPushButton("Enable")
        self.disable_btn = QPushButton("Disable")
        self.enable_btn.clicked.connect(lambda: self.oc.enable())
        self.disable_btn.clicked.connect(lambda: self.oc.disable())

        ctl.addWidget(self.enable_btn)
        ctl.addWidget(self.disable_btn)
        ctrl.setLayout(ctl)

        # Temperature
        temp = QGroupBox("Temperature")
        tl = QVBoxLayout()

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0, 300)
        self.temp_spin.setSuffix(" °C")

        set_temp = QPushButton("Set Temperature")
        set_temp.clicked.connect(
            lambda: self.oc.set_temperature(self.temp_spin.value())
        )

        tl.addWidget(self.temp_spin)
        tl.addWidget(set_temp)
        temp.setLayout(tl)

        # Ramp
        ramp = QGroupBox("Ramp Rate")
        rl = QVBoxLayout()

        self.ramp_spin = QDoubleSpinBox()
        self.ramp_spin.setRange(0.01, 100)
        self.ramp_spin.setValue(100)
        self.ramp_spin.setSuffix(" °C/s")

        set_ramp = QPushButton("Set Ramp")
        set_ramp.clicked.connect(
            lambda: self.oc.set_ramp_rate(self.ramp_spin.value())
        )

        rl.addWidget(self.ramp_spin)
        rl.addWidget(set_ramp)
        ramp.setLayout(rl)

        # Status
        status = QGroupBox("Status")
        sl = QVBoxLayout()

        self.temp_label = QLabel("Temp: --")
        self.setpoint_label = QLabel("Setpoint: --")
        self.fault_btn = QPushButton("View Faults")
        self.fault_btn.clicked.connect(self.fault_window.show)

        sl.addWidget(self.temp_label)
        sl.addWidget(self.setpoint_label)
        sl.addWidget(self.fault_btn)
        status.setLayout(sl)

        left.addWidget(conn)
        left.addWidget(ctrl)
        left.addWidget(temp)
        left.addWidget(ramp)
        left.addWidget(status)

        # -------- RIGHT PANEL (GRAPH) --------
        self.plot = pg.PlotWidget(title="Live Temperature")
        self.plot.setLabel('left', 'Temperature', units='°C')
        self.plot.setLabel('bottom', 'Time', units='s')

        self.temp_curve = self.plot.plot(pen=pg.mkPen('y', width=2))
        self.set_curve = self.plot.plot(pen=pg.mkPen('r', style=pg.QtCore.Qt.DashLine))

        main_layout.addLayout(left, 1)
        main_layout.addWidget(self.plot, 2)

        central.setLayout(main_layout)

    def apply_dark_theme(self):
        self.setStyleSheet("""
        QWidget { background-color: #121212; color: #e0e0e0; }
        QGroupBox { border: 1px solid #444; margin-top: 10px; }
        QPushButton { background-color: #2c2c2c; padding: 6px; }
        QPushButton:hover { background-color: #444; }
        """)

    def connect_oc(self):
        self.oc = OC(self.port_combo.currentText())
        self.timer.start(1000)

    def update_status(self):
        if not self.oc:
            return

        temp = self.oc.get_temperature()
        setp = self.oc.setpoint[0]

        t = len(self.temp_history)
        self.temp_history.append(temp)
        self.time_history.append(t)

        self.temp_curve.setData(self.time_history, self.temp_history)
        self.set_curve.setData(self.time_history, [setp] * len(self.time_history))

        self.temp_label.setText(f"Temp: {temp:.2f} °C")
        self.setpoint_label.setText(f"Setpoint: {setp:.2f} °C")

        fault = self.oc.get_faults()
        if fault != 0:
            msg = f"{datetime.now()} | Fault code: {fault}"
            self.fault_window.add_fault(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = OCMainWindow()
    win.show()
    sys.exit(app.exec_())
