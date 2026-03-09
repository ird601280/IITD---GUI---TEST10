from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout,  QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IITD EQUIP LAB")
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowIcon(QIcon("iitdelhilogo.jpg")) 
    
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = QMainWindow()
    win.show()
    # win.showFullScreen() # Set the window to full screen
    sys.exit(app.exec_())  # Corrected to sys.exit
    app.exec() 
    