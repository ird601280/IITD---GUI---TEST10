import sys
import sqlite3
import serial
import serial.tools.list_ports
from datetime import datetime
from time import sleep

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from OC import OC   # import OC controller


# ================= DATABASE =================

def init_db():
    conn = sqlite3.connect("temperature.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS experiments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_temp REAL,
        stability_range REAL,
        stability_time REAL,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


# ================= MATPLOTLIB =================

class MplCanvas(FigureCanvas):

    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        super().__init__(self.fig)

        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Temperature (°C)")
        self.ax.grid(True)

        self.x = []
        self.y = []


# ================= MAIN WINDOW =================

class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        init_db()

        self.oc = None
        self.timer = QTimer()

        self.setWindowTitle("Temperature Stability System")
        self.setMinimumSize(1200, 750)

        self.initUI()

    # ================= UI =================

    def initUI(self):

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

        # ================= LEFT PANEL =================

        left = QFrame()
        leftLayout = QFormLayout(left)

        self.targetTemp = QDoubleSpinBox()
        self.targetTemp.setRange(-100, 300)
        self.targetTemp.setValue(60)

        self.stabilityRange = QDoubleSpinBox()
        self.stabilityRange.setValue(0.1)

        self.stabilityTime = QSpinBox()
        self.stabilityTime.setValue(20)

        leftLayout.addRow("Target Temp (C)", self.targetTemp)
        leftLayout.addRow("Stability Range (C)", self.stabilityRange)
        leftLayout.addRow("Stability Time (s)", self.stabilityTime)

        # SERIAL

        self.portBox = QComboBox()
        self.baudBox = QComboBox()

        ports = serial.tools.list_ports.comports()

        for p in ports:
            self.portBox.addItem(p.device)

        self.baudBox.addItems(["9600", "19200", "115200"])

        leftLayout.addRow("Port", self.portBox)
        leftLayout.addRow("Baud", self.baudBox)

        self.connectBtn = QPushButton("Connect Controller")
        self.connectBtn.clicked.connect(self.connect_controller)

        leftLayout.addRow(self.connectBtn)

        self.startBtn = QPushButton("Start Stability Test")
        self.startBtn.clicked.connect(self.start_test)

        leftLayout.addRow(self.startBtn)

        self.saveBtn = QPushButton("Save Experiment")
        self.saveBtn.clicked.connect(self.save_experiment)

        leftLayout.addRow(self.saveBtn)

        layout.addWidget(left, 2)

        # ================= GRAPH =================

        self.canvas = MplCanvas()

        layout.addWidget(self.canvas, 5)

    # ================= SERIAL CONNECT =================

    def connect_controller(self):

        port = self.portBox.currentText()

        try:

            self.oc = OC(port)

            QMessageBox.information(self, "Connected", "Controller Connected!")

        except Exception as e:

            QMessageBox.critical(self, "Error", str(e))

    # ================= START TEST =================

    def start_test(self):

        if self.oc is None:
            QMessageBox.warning(self, "Error", "Controller not connected")
            return

        self.target = self.targetTemp.value()
        self.range = self.stabilityRange.value()
        self.stable_time = self.stabilityTime.value()

        self.oc.set_temperature(self.target)
        self.oc.enable()

        self.timer.timeout.connect(self.read_temperature)
        self.timer.start(1000)

        self.start_time = datetime.now()
        self.time_in_range = 0

    # ================= READ TEMPERATURE =================

    def read_temperature(self):

        status = self.oc.get_status()

        temp = status.temperature

        now = datetime.now()

        t = (now - self.start_time).seconds

        self.canvas.x.append(t)
        self.canvas.y.append(temp)

        self.canvas.ax.clear()

        self.canvas.ax.plot(self.canvas.x, self.canvas.y)

        self.canvas.draw()

        if abs(temp - self.target) <= self.range:

            self.time_in_range += 1

        else:

            self.time_in_range = 0

        if self.time_in_range >= self.stable_time:

            QMessageBox.information(self, "Stable", "Temperature Stable!")

            self.timer.stop()

    # ================= SAVE EXPERIMENT =================

    def save_experiment(self):

        conn = sqlite3.connect("temperature.db")
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO experiments(target_temp,stability_range,stability_time,timestamp)
        VALUES(?,?,?,?)
        """, (
            self.targetTemp.value(),
            self.stabilityRange.value(),
            self.stabilityTime.value(),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Saved", "Experiment Saved")


# ================= RUN =================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    sys.exit(app.exec_())