import sys
from PyQt5.QtWidgets import (QWidget, QToolButton, QApplication, QMainWindow,
                             QGridLayout, QSplitter, QVBoxLayout, QHBoxLayout,
                             QFrame)
from PyQt5.QtGui import QPalette, QColor, QBrush, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QDateTime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.body = QSplitter()
        self.body.setOrientation(Qt.Vertical)

        # 设置桌面图标
        self.setDesk()

        # 设置底部菜单栏
        self.setMenuBar()

        # 设置样式
        self.setMyStyle()

        # 时间
        self.time = QTimer()
        self.time.timeout.connect(self.setTime)
        self.time.start(1000)

        # 菜单
        self.startMenuWidget = None

        self.setCentralWidget(self.body)
        self.setGeometry(300, 300, 1280, 720)
        self.setWindowIcon(QIcon('icon/windows.ico'))
        self.setWindowTitle('MyWindows')
        self.show()

    def setDesk(self):
        self.desk = QWidget()
        self.desk.setObjectName('body')
        self.desk.mousePressEvent = self.__deskClicked
        self.body.addWidget(self.desk)

    def __deskClicked(self, e):
        self.startMenuWidget.close()
        print(123)

    def setMenuBar(self):
        self.start = QToolButton()
        self.start.setIcon(QIcon('icon/windows_start.png'))
        self.start.setFixedSize(50, 50)
        self.start.setIconSize(QSize(30, 30))
        self.start.clicked.connect(self.startMenu)

        self.explorerButton = QToolButton()
        self.explorerButton.setIcon(QIcon('icon/explorer.ico'))
        self.explorerButton.setFixedSize(50, 50)
        self.explorerButton.setIconSize(QSize(30, 30))

        self.taskMangerButton = QToolButton()
        self.taskMangerButton.setIcon(QIcon('icon/exe.ico'))
        self.taskMangerButton.setFixedSize(50, 50)
        self.taskMangerButton.setIconSize(QSize(30, 30))

        self.timeDisplay = QToolButton()
        self.timeDisplay.setObjectName('timeDisplay')
        self.timeDisplay.setText(QDateTime.currentDateTime().toString('hh:mm\nyyyy/MM/dd'))
        self.timeDisplay.setFixedSize(QSize(100, 50))

        self.menuBarLayout = QGridLayout()
        self.menuBarLayout.setContentsMargins(0, 0, 0, 0)
        self.menuBarLayout.addWidget(self.start, 0, 0)
        self.menuBarLayout.addWidget(self.explorerButton, 0, 1)
        self.menuBarLayout.addWidget(self.taskMangerButton, 0, 2, 1, 7)
        self.menuBarLayout.addWidget(self.timeDisplay, 0, 10)

        self.menuBar = QWidget()
        self.menuBar.setFixedHeight(50)
        self.menuBar.setLayout(self.menuBarLayout)

        self.body.addWidget(self.menuBar)

    def setTime(self):
        time = QDateTime.currentDateTime().toString('hh:mm\nyyyy/MM/dd')
        self.timeDisplay.setText(time)

    def startMenu(self):
        if self.startMenuWidget is not None:
            self.startMenuWidget.close()
            self.startMenuWidget = None
            return
        deskHeight = self.desk.size().height()
        self.startMenuWidget = QWidget()
        self.startMenuWidget.setParent(self.desk)
        self.startMenuWidget.setGeometry(0, deskHeight-400, 300, 400)
        self.startMenuWidget.setStyleSheet('''
            background-color:rgba(0, 0, 0, 0.3);
        ''')
        self.startMenuWidget.show()

    def setMyStyle(self):
        self.menuBar.setStyleSheet('''
            QWidget{
                background-color: black;
            }
            QToolButton{
                border:0px;
                color:white;
            }
            QToolButton:hover{
                background-color: #414141;
            }
        ''')
        self.body.setStyleSheet('''
            QSplitter::handle{
                width:0;
            }
        ''')

        self.desk.setStyleSheet('''
            QWidget#body{
                border-image: url(icon/desk.jpg);
            }
        ''')


class StartMenu(QWidget):
    def __init__(self, master):
        super().__init__()
        self.master = master
        deskHeight = self.master.desk.size().height()
        self.setGeometry(0, deskHeight-400, 200, 400)
        self.setStyleSheet('''
            background-color:rgba(0, 0, 0, 0.3);
        ''')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
