import sys
from PyQt5.QtWidgets import QApplication
from module import main_window


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = main_window.MainWindow()
    sys.exit(app.exec_())