import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QToolButton)


class TaskManger(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 1000, 700)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TaskManger()
    sys.exit(app.exec_())