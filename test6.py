import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt, QPoint


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(40)

        self.setStyleSheet("""
            background-color: #2b2b2b;
            color: white;
        """)

        # Left title
        self.left_title = QLabel("Main Window")
        self.left_title.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # Center title
        self.center_title = QLabel("Centered Title")
        self.center_title.setAlignment(Qt.AlignCenter)
        self.center_title.setStyleSheet("font-weight: bold;")

        # Close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(parent.close)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                font-size: 14px;
            }
            QPushButton:hover {
                background: red;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addWidget(self.left_title)
        layout.addStretch()
        layout.addWidget(self.center_title)
        layout.addStretch()
        layout.addWidget(self.close_btn)

    # Enable window dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent.move(event.globalPos() - self.drag_pos)
            event.accept()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Remove default title bar
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(600, 400)

        self.title_bar = TitleBar(self)

        content = QLabel("Main Content Area")
        content.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.title_bar)
        layout.addWidget(content)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
