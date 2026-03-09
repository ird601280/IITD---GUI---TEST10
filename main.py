import sys, os


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QLabel,
    QLineEdit,
    QListWidget, 
    QMainWindow,
    QSlider,
    QSpinBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
    QGroupBox,
    QSlider,
    QRadioButton,
    QSystemTrayIcon,
    QLCDNumber)
 
basedir = os.path.dirname(__file__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IITD EQUIP LAB")
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon("iitdelhilogo.jpg"))

        

        label = QLabel("TEMP & CURRENT MONITORING GUI", self)
        label.setFont(QFont("Arial", 15))
        label.setGeometry(0,0,1000,100)
        label.setStyleSheet("color:pitchblack ;"
                            "background-color:lightgrey;"
                            "font-weight:bold;")
        label.setAlignment(Qt.AlignCenter)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        main_layout.addLayout(self.instrument_bar())
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        content_layout.addWidget(self.temperature_panel(), 1)
        content_layout.addWidget(self.waveform_panel(), 3)
        content_layout.addWidget(self.demodulator_panel(), 1)

        main_layout.addLayout(self.bottom_controls())

 # ---------------- Instrument Bar ----------------
    def instrument_bar(self):
        layout = QHBoxLayout()

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setIcon(QIcon("arrow.png"))
        layout.addWidget(btn_refresh)

        #layout.addWidget(QPushButton("Refresh"))

        
        #self.port_box.setIcon(QIcon("password.png"))
        self.port_box = QComboBox()
        self.port_box.addItems(["COM1", "COM2", "COM3", "COM4"])
        layout.addWidget(self.port_box)


        btn_connect = QPushButton("Connect")
        btn_connect.setIcon(QIcon("plug.png"))
        layout.addWidget(btn_connect)
        layout.addStretch()
        layout.addWidget(QLabel("Disconnected"))

        return layout

    # ---------------- Temperature Panel ----------------
    def temperature_panel(self):
        box = QGroupBox("Temperature")
        layout = QGridLayout()

        labels = [
            "Case Temperature", 
            "LD Actual Temp.",
            "PD current", 
            "TEC Response",
            "LD Temp. Setpoint"
        ]

        for i, text in enumerate(labels):
            layout.addWidget(QLabel(text), i, 0)

        self.case_temp = QLCDNumber()
        self.ld_temp = QLCDNumber()
        self.pd_current = QLCDNumber()

        layout.addWidget(self.case_temp, 0, 1)
        layout.addWidget(self.ld_temp, 1, 1)
        layout.addWidget(self.pd_current, 2, 1)

        self.tec_fast = QRadioButton("Fast")
        self.tec_slow = QRadioButton("Slow")
        self.tec_fast.setChecked(True)

        layout.addWidget(self.tec_fast, 3, 1)
        layout.addWidget(self.tec_slow, 4, 1)

        self.temp_set = QDoubleSpinBox()
        self.temp_set.setRange(0, 100)
        self.temp_set.setValue(25.0)
        self.temp_set.setSuffix(" °C")

        layout.addWidget(self.temp_set, 5, 1)
        layout.addWidget(QPushButton("Set Temperature"), 6, 1)

        box.setLayout(layout)
        return box

    # ---------------- Waveform Panel ----------------
    def waveform_panel(self):
        box = QGroupBox("Waveform")
        layout = QGridLayout()

        layout.addWidget(QLabel("Start (mA)"), 0, 0)
        layout.addWidget(QSlider(Qt.Horizontal), 0, 1)

        layout.addWidget(QLabel("End (mA)"), 1, 0)
        layout.addWidget(QSlider(Qt.Horizontal), 1, 1)

        layout.addWidget(QLabel("Slope"), 2, 0)
        layout.addWidget(QSlider(Qt.Horizontal), 2, 1)

        layout.addWidget(QLabel("Sinewave Frequency"), 3, 0)
        freq = QSpinBox()
        freq.setRange(1, 100000)
        freq.setValue(35000)
        freq.setSuffix(" Hz")
        layout.addWidget(freq, 3, 1)

        layout.addWidget(QLabel("Amplitude (p-p)"), 4, 0)
        layout.addWidget(QSlider(Qt.Horizontal), 4, 1)

        layout.addWidget(QPushButton("Set Parameters"), 5, 1)

        box.setLayout(layout)
        return box

    # ---------------- Demodulator Panel ----------------
    def demodulator_panel(self):
        box = QGroupBox("Demodulator")
        layout = QGridLayout()

        layout.addWidget(QLabel("Output"), 0, 0)
        out = QComboBox()
        out.addItems(["1f", "2f"])
        layout.addWidget(out, 0, 1)

        layout.addWidget(QLabel("Gain"), 1, 0)
        gain = QComboBox()
        gain.addItems(["1X", "10X", "100X"])
        layout.addWidget(gain, 1, 1)

        layout.addWidget(QLabel("2f Phase"), 2, 0)
        phase = QSpinBox()
        phase.setRange(0, 360)
        phase.setSuffix("°")
        layout.addWidget(phase, 2, 1)

        indicator = QLabel("◯")
        indicator.setAlignment(Qt.AlignCenter)
        indicator.setStyleSheet("font-size: 60px;")
        layout.addWidget(indicator, 3, 0, 1, 2)

        layout.addWidget(QPushButton("Set"), 4, 0, 1, 2)

        box.setLayout(layout)
        return box

    # ---------------- Bottom Controls ----------------
    def bottom_controls(self):
        layout = QHBoxLayout()
        layout.addWidget(QPushButton("Run: Slope"))
        layout.addWidget(QPushButton("Run: DC"))
        btn_stop = QPushButton("Stop")
        btn_stop.setIcon(QIcon("stop.png"))
        layout.addWidget(btn_stop)
        layout.addStretch()
        btn_save = QPushButton("Save All Settings")
        btn_save.setIcon(QIcon("save.png"))
        layout.addWidget(btn_save)
        return layout





if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(os.path.join(basedir, "icons", "iitdelhilogo.ico")))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())  # Corrected to sys.exit
    app.exec() 