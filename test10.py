import sys, os 

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, 
    QMainWindow, 
    QWidget, 
    QLabel, 
    QPushButton,
    QComboBox, 
    QGroupBox, 
    QGridLayout, 
    QVBoxLayout, 
    QHBoxLayout,
    QSlider, 
    QSpinBox, 
    QDoubleSpinBox, 
    QRadioButton, 
    QLCDNumber
)


from PyQt5.QtCore import Qt

basedir = os.path.dirname(__file__)

# ================= MATPLOTLIB CANVAS =================
class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temp (°C)")
        self.ax.grid(True)

        self.fig.subplots_adjust(left=0.12, right=0.95, top=0.92, bottom=0.15)

        self.x = list(range(10))
        self.y = [i for i in range(10)]
        self.ax.plot(self.x, self.y)


# ================= MAIN WINDOW =================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IITD EQUIP LAB - LMTC GUI")
        self.setWindowIcon(QIcon("OC_Python - Release - Test 10/OC_Python - Release/iitdelhilogo.ico"))
        self.setMinimumSize(1200, 750)
        

        self.setStyleSheet("""
        QFrame {
            border: 1px solid #c5c5c5;
            border-radius: 10px;
        }
        QGroupBox {
            font-weight: bold;
        }
        """)

        self.initUI()

    # ================= BUTTON CREATOR =================
    def create_button(self, text, icon_style, color):
        btn = QPushButton(text)
        btn.setIcon(self.style().standardIcon(icon_style))
        btn.setIconSize(QSize(20, 20))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                text-align: left;
                padding: 8px;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #333333;
            }}
        """)
        return btn

    # ================= UI SETUP =================
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

        title = QLabel("LMTC - GUI")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        headerLayout.addWidget(title)

        headerLayout.addStretch()
        headerLayout.addWidget(QPushButton("Home"))
        headerLayout.addWidget(QPushButton("X"))

        mainLayout.addWidget(header)

        # ================= BODY =================
        bodyLayout = QHBoxLayout()
        mainLayout.addLayout(bodyLayout)

        # ================= LEFT PANEL =================
        leftPanel = QFrame()
        leftPanel.setMaximumWidth(260)
        leftLayout = QVBoxLayout(leftPanel)

        btnOpen = self.create_button("Open Experiment", QStyle.SP_DialogOpenButton, "#3F51B5")
        btnNew = self.create_button("New Experiment", QStyle.SP_FileIcon, "#009688")
        btnSettings = self.create_button("Settings", QStyle.SP_FileDialogDetailedView, "#607D8B")
        btnFile = self.create_button("File Settings", QStyle.SP_DriveHDIcon, "#9C27B0")
        btnDetails = self.create_button("Details", QStyle.SP_MessageBoxInformation, "#795548")
        btnProgram = self.create_button("Program", QStyle.SP_ComputerIcon, "#E91E63")
        btnRun = self.create_button("Run & Results", QStyle.SP_MediaPlay, "#4CAF50")
        btnAnalysis = self.create_button("Analysis", QStyle.SP_DesktopIcon, "#FF5722")

        buttons = [
            btnOpen, btnNew, btnSettings, btnFile,
            btnDetails, btnProgram, btnRun, btnAnalysis
        ]

        for b in buttons:
            leftLayout.addWidget(b)

        leftLayout.addWidget(QLabel("Module Status"))
        leftLayout.addWidget(QLabel("Case Temp: 21.8°C"))
        leftLayout.addWidget(QLabel("Heat Sink Temp: 25.4°C"))
        leftLayout.addWidget(QLabel("LD Actual Temp: 0.0°C"))

        btnSaveLeft = QPushButton("Save Settings")
        btnSaveLeft.setStyleSheet("""
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 6px;
        """)
        leftLayout.addWidget(btnSaveLeft)

        leftLayout.addStretch()
        bodyLayout.addWidget(leftPanel, 2)

        # ================= CENTER PANEL =================
        centerPanel = QFrame()
        centerLayout = QVBoxLayout(centerPanel)

        centerLayout.addWidget(QLabel("Waveform"))

        sliderStart = QSlider(Qt.Horizontal)
        sliderEnd = QSlider(Qt.Horizontal)
        sliderSlope = QSlider(Qt.Horizontal)

        centerLayout.addWidget(sliderStart)
        centerLayout.addWidget(sliderEnd)
        centerLayout.addWidget(sliderSlope)

        btnSaveWave = QPushButton("Save Settings")
        btnSaveWave.setStyleSheet("""
            background-color: #2196F3;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 6px;
        """)
        centerLayout.addWidget(btnSaveWave)

        # Temperature Group
        tempGroup = QGroupBox("Temperature")
        form = QFormLayout()

        spinPD = QDoubleSpinBox()
        spinSetpoint = QDoubleSpinBox()

        radioFast = QRadioButton("Fast")
        radioSlow = QRadioButton("Slow")

        form.addRow("PD Current:", spinPD)

        hbox = QHBoxLayout()
        hbox.addWidget(radioFast)
        hbox.addWidget(radioSlow)
        form.addRow("TEC Response:", hbox)

        form.addRow("LD Temp Setpoint:", spinSetpoint)

        tempGroup.setLayout(form)
        centerLayout.addWidget(tempGroup)

        bodyLayout.addWidget(centerPanel, 6)

        # ================= RIGHT PANEL =================
        rightPanel = QFrame()
        rightLayout = QVBoxLayout(rightPanel)

        serialGroup = QGroupBox("Serial Port Communication")
        form2 = QFormLayout()

        comboPort = QComboBox()
        comboBaud = QComboBox()
        comboData = QComboBox()
        comboParity = QComboBox()
        comboStop = QComboBox()

        comboPort.addItems(["COM1", "COM2", "COM3"])
        comboBaud.addItems(["9600", "115200"])
        comboData.addItems(["7", "8"])
        comboParity.addItems(["None", "Even", "Odd"])
        comboStop.addItems(["1", "2"])

        form2.addRow("Port:", comboPort)
        form2.addRow("Baud Rate:", comboBaud)
        form2.addRow("Data Bits:", comboData)
        form2.addRow("Parity:", comboParity)
        form2.addRow("Stop Bits:", comboStop)

        serialGroup.setLayout(form2)
        rightLayout.addWidget(serialGroup)

        btnSaveSerial = QPushButton("Save Settings")
        btnSaveSerial.setStyleSheet("""
            background-color: #FF9800;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 6px;
        """)
        rightLayout.addWidget(btnSaveSerial)

        liveGroup = QGroupBox("Live - Temp")
        liveLayout = QVBoxLayout()

        canvas = MplCanvas()
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        liveLayout.addWidget(canvas)
        liveGroup.setLayout(liveLayout)

        rightLayout.addWidget(liveGroup)

        rightLayout.setStretch(0, 0)
        rightLayout.setStretch(1, 0)
        rightLayout.setStretch(2, 1)

        bodyLayout.addWidget(rightPanel, 3)


# ================= RUN =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(basedir, "icons", "iitdelhilogo.ico")))
    app.setWindowIcon(QtGui.QIcon("iitdelhilogo.ico"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())