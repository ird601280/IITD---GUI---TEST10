import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temp (°C)")
        self.ax.grid(True)

        self.x = list(range(10))
        self.y = [i for i in range(10)]
        self.ax.plot(self.x, self.y)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Temp & Current GUI")
        self.setMinimumSize(1200, 750)

        self.setStyleSheet("""
            QPushButton {
                border-radius: 8px;
                padding: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d6e4ff;
            }
            QFrame {
                border: 1px solid #c5c5c5;
                border-radius: 10px;
            }
        """)

        self.initUI()

    def initUI(self):

        central = QWidget()
        self.setCentralWidget(central)

        mainLayout = QVBoxLayout(central)

        # ================= HEADER =================
        header = QFrame()
        header.setMinimumHeight(70)
        header.setStyleSheet("background-color:#f7c948;")
        headerLayout = QHBoxLayout(header)

        headerLayout.addWidget(QLabel("IITD EQUIP LAB"))
        headerLayout.addStretch()
        title = QLabel("Temp & Current GUI")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        headerLayout.addWidget(title)
        headerLayout.addStretch()
        headerLayout.addWidget(QPushButton("Home"))
        headerLayout.addWidget(QPushButton("X"))

        mainLayout.addWidget(header)

        # ================= BODY =================
        bodyLayout = QHBoxLayout()
        mainLayout.addLayout(bodyLayout)

        # ============ LEFT PANEL ============
        leftPanel = QFrame()
        leftPanel.setMaximumWidth(250)
        leftLayout = QVBoxLayout(leftPanel)

        buttons = [
            "Open Experiment", "New Experiment", "Settings", "File",
            "Details", "Program", "Run & Results", "Analysis"
        ]

        for b in buttons:
            leftLayout.addWidget(QPushButton(b))

        leftLayout.addWidget(QLabel("Module Status"))
        leftLayout.addWidget(QLabel("Case Temp: 21.8°C"))
        leftLayout.addWidget(QLabel("Heat Sink Temp: 25.4°C"))
        leftLayout.addWidget(QLabel("LD Actual Temp: 0.0°C"))
        leftLayout.addWidget(QPushButton("Save Settings"))
        leftLayout.addStretch()

        bodyLayout.addWidget(leftPanel, 2)

        # ============ CENTER PANEL ============
        centerPanel = QFrame()
        centerLayout = QVBoxLayout(centerPanel)

        centerLayout.addWidget(QLabel("Waveform"))

        self.sliderStart = QSlider(Qt.Horizontal)
        self.sliderEnd = QSlider(Qt.Horizontal)
        self.sliderSlope = QSlider(Qt.Horizontal)

        centerLayout.addWidget(self.sliderStart)
        centerLayout.addWidget(self.sliderEnd)
        centerLayout.addWidget(self.sliderSlope)

        centerLayout.addWidget(QPushButton("Save Settings"))

        # Temperature Group
        tempGroup = QGroupBox("Temperature")
        form = QFormLayout()

        self.spinPD = QDoubleSpinBox()
        self.spinSetpoint = QDoubleSpinBox()

        self.radioFast = QRadioButton("Fast")
        self.radioSlow = QRadioButton("Slow")

        form.addRow("PD Current:", self.spinPD)

        hbox = QHBoxLayout()
        hbox.addWidget(self.radioFast)
        hbox.addWidget(self.radioSlow)
        form.addRow("TEC Response:", hbox)

        form.addRow("LD Temp Setpoint:", self.spinSetpoint)

        tempGroup.setLayout(form)

        centerLayout.addWidget(tempGroup)

        bodyLayout.addWidget(centerPanel, 6)

        # ============ RIGHT PANEL ============
        rightPanel = QFrame()
        rightLayout = QVBoxLayout(rightPanel)

        # Serial Group
        serialGroup = QGroupBox("Serial Port Communication")
        form2 = QFormLayout()

        self.comboPort = QComboBox()
        self.comboBaud = QComboBox()
        self.comboData = QComboBox()
        self.comboParity = QComboBox()
        self.comboStop = QComboBox()

        self.comboPort.addItems(["COM1", "COM2", "COM3"])
        self.comboBaud.addItems(["9600", "115200"])
        self.comboData.addItems(["7", "8"])
        self.comboParity.addItems(["None", "Even", "Odd"])
        self.comboStop.addItems(["1", "2"])

        form2.addRow("Port:", self.comboPort)
        form2.addRow("Baud Rate:", self.comboBaud)
        form2.addRow("Data Bits:", self.comboData)
        form2.addRow("Parity:", self.comboParity)
        form2.addRow("Stop Bits:", self.comboStop)

        serialGroup.setLayout(form2)

        rightLayout.addWidget(serialGroup)
        rightLayout.addWidget(QPushButton("Save Settings"))

        # Live Temp Plot
        liveGroup = QGroupBox("Live - Temp")
        liveLayout = QVBoxLayout()

        self.canvas = MplCanvas()
        liveLayout.addWidget(self.canvas)

        liveGroup.setLayout(liveLayout)

        rightLayout.addWidget(liveGroup)

        bodyLayout.addWidget(rightPanel, 3)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())