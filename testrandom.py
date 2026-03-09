import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel,
    QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QMessageBox
)
from PyQt5.QtCore import QTimer


class LDPDController(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LD-PD Control System")
        self.setGeometry(200, 200, 500, 300)

        self.serial_port = None

        self.initUI()

        # Timer for periodic PD reading
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_pd)

    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Port Selection
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()

        refresh_btn = QPushButton("Refresh Ports")
        refresh_btn.clicked.connect(self.refresh_ports)

        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_serial)

        port_layout.addWidget(QLabel("COM Port:"))
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(refresh_btn)
        port_layout.addWidget(connect_btn)

        # Laser Current Control
        current_layout = QHBoxLayout()
        self.current_input = QLineEdit()
        self.current_input.setPlaceholderText("Enter Current (mA)")

        set_current_btn = QPushButton("Set Current")
        set_current_btn.clicked.connect(self.set_current)

        current_layout.addWidget(QLabel("Laser Current:"))
        current_layout.addWidget(self.current_input)
        current_layout.addWidget(set_current_btn)

        # Photodiode Display
        self.pd_label = QLabel("PD Voltage: --- V")

        read_pd_btn = QPushButton("Read PD")
        read_pd_btn.clicked.connect(self.read_pd)

        start_auto_btn = QPushButton("Start Auto Read")
        start_auto_btn.clicked.connect(self.start_auto_read)

        stop_auto_btn = QPushButton("Stop Auto Read")
        stop_auto_btn.clicked.connect(self.stop_auto_read)

        # Stop Laser
        stop_btn = QPushButton("STOP LASER")
        stop_btn.clicked.connect(self.stop_laser)

        # Add to layout
        layout.addLayout(port_layout)
        layout.addLayout(current_layout)
        layout.addWidget(self.pd_label)
        layout.addWidget(read_pd_btn)
        layout.addWidget(start_auto_btn)
        layout.addWidget(stop_auto_btn)
        layout.addWidget(stop_btn)

        central_widget.setLayout(layout)

    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)

    def connect_serial(self):
        try:
            port = self.port_combo.currentText()
            self.serial_port = serial.Serial(port, 9600, timeout=1)
            QMessageBox.information(self, "Success", "Connected Successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def set_current(self):
        if self.serial_port:
            value = self.current_input.text()
            command = f"SETI {value}\n"
            self.serial_port.write(command.encode())

    def read_pd(self):
        if self.serial_port:
            try:
                self.serial_port.write(b"READPD\n")
                response = self.serial_port.readline().decode().strip()
                self.pd_label.setText(f"PD Voltage: {response} V")
            except:
                pass

    def start_auto_read(self):
        self.timer.start(1000)

    def stop_auto_read(self):
        self.timer.stop()

    def stop_laser(self):
        if self.serial_port:
            self.serial_port.write(b"STOP\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LDPDController()
    window.show()
    sys.exit(app.exec_())
