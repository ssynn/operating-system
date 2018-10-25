import sys
from model import explorer
from PyQt5.QtWidgets import (QWidget, QToolButton, QApplication, QMainWindow,
                             QGridLayout, QSplitter)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QDateTime


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.startMenuWidget = None
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

        self.setCentralWidget(self.body)
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowIcon(QIcon('icon/windows.ico'))
        self.setWindowTitle('MyWindows')
        self.show()
        # 菜单
        self.setMenuWidget()

    def setDesk(self):
        self.desk = QWidget()
        self.desk.setObjectName('body')
        self.desk.mousePressEvent = self.__deskClicked
        self.body.addWidget(self.desk)

    def __deskClicked(self, e):
        self.startMenuWidget.hide()

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
        self.explorerButton.clicked.connect(self.explorerStart)

        self.taskMangerButton = QToolButton()
        self.taskMangerButton.setIcon(QIcon('icon/task.ico'))
        self.taskMangerButton.setFixedSize(50, 50)
        self.taskMangerButton.setIconSize(QSize(50, 50))
        self.taskMangerButton.clicked.connect(self.taskMangerStart)

        self.timeDisplay = QToolButton()
        self.timeDisplay.setObjectName('timeDisplay')
        self.timeDisplay.setText(QDateTime.currentDateTime().toString('hh:mm\nyyyy/MM/dd'))
        self.timeDisplay.setFixedSize(QSize(100, 50))
        self.timeDisplay.clicked.connect(self.timeWidget)

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
        deskHeight = self.desk.size().height()
        self.startMenuWidget.setGeometry(0, deskHeight-400, 300, 400)
        self.startMenuWidget.setHidden(not self.startMenuWidget.isHidden())

    # 设置菜单
    def setMenuWidget(self):
        self.startMenuWidget = QWidget()
        self.startMenuWidget.setParent(self)

        blank = QWidget()

        offButton = QToolButton()
        offButton.setIcon(QIcon('icon/off.png'))
        offButton.setIconSize(QSize(40, 40))
        offButton.clicked.connect(self.close)

        explorerMenuButton = QToolButton()
        explorerMenuButton.setIcon(QIcon('icon/explorer.ico'))
        explorerMenuButton.setText(' 文件管理器')
        explorerMenuButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        explorerMenuButton.setIconSize(QSize(40, 40))
        explorerMenuButton.setFixedSize(250, 50)
        explorerMenuButton.clicked.connect(self.explorerStart)

        taskMangerMenuButton = QToolButton()
        taskMangerMenuButton.setIcon(QIcon('icon/task.ico'))
        taskMangerMenuButton.setText(' 资源管理器')
        taskMangerMenuButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        taskMangerMenuButton.setIconSize(QSize(40, 40))
        taskMangerMenuButton.setFixedSize(250, 50)
        taskMangerMenuButton.clicked.connect(self.taskMangerStart)

        self.startMenuWidgetLayout = QGridLayout()
        self.startMenuWidgetLayout.setContentsMargins(0, 0, 0, 0)
        self.startMenuWidgetLayout.addWidget(blank, 0, 0, 5, 1)
        self.startMenuWidgetLayout.addWidget(offButton, 6, 0)
        self.startMenuWidgetLayout.addWidget(explorerMenuButton, 0, 1, 1, 3)
        self.startMenuWidgetLayout.addWidget(taskMangerMenuButton, 1, 1, 1, 3)
        self.startMenuWidget.setLayout(self.startMenuWidgetLayout)
        self.startMenuWidget.setStyleSheet('''
            QWidget{
                background-color: rgba(0, 0, 0, 0.5);
            }
            QToolButton{
                background-color: rgba(0, 0, 0, 0);
                color:white;
                font-family: 微软雅黑;
            }
            QToolButton:hover{
                background-color: rgba(255, 255, 255, 0.1);
            }
        ''')

    # 改变窗体大小时触发
    def resizeEvent(self, e):
        if self.startMenuWidget is None:
            return
        deskHeight = self.desk.size().height()
        self.startMenuWidget.setGeometry(0, deskHeight-400, 400, 400)

    # 文件管理器关闭
    def explorerCloseEvent(self):
        self.explorerButton.setStyleSheet('''''')

    # 开启任务管理器 ------------------
    def taskMangerStart(self):
        print('task')

    # 开启文件管理器 ------------------
    def explorerStart(self):
        self.explorerButton.setStyleSheet('''
            QToolButton{
                border-bottom:3px solid #76b9ed;
            }
        ''')
        exp = explorer.Explorer()
        exp.after_close_signal.connect(self.explorerCloseEvent)

    # 时间详情 -----------------------
    def timeWidget(self):
        print('time')

    def setMyStyle(self):
        self.menuBar.setStyleSheet('''
            QWidget{
                background-color: black;
            }
            QToolButton{
                border:0px;
                color:white;
                border-bottom:3px solid black;
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
