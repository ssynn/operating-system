import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout,
                             QHBoxLayout, QSplitter, QToolButton, QLabel, QVBoxLayout, QGroupBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize


class TaskManger(QWidget):
    def __init__(self):
        super().__init__()
        self.focus = 0
        self.initUI()

    def initUI(self):
        self.body = QSplitter()
        self.setLeftMunu()
        self.content = None
        self.setContent()

        self.bodyLayout = QHBoxLayout()
        self.bodyLayout.addWidget(self.body)
        self.setLayout(self.bodyLayout)
        self.setWindowTitle('资源管理器')
        self.setFixedSize(1280, 720)
        self.setMyStyle()
        self.show()

    # 左侧菜单栏
    def setLeftMunu(self):
        # CPU
        self.CPU = QToolButton()
        self.CPU.setText('CPU')
        self.CPU.setFixedSize(160, 50)
        self.CPU.setIcon(QIcon('icon/cpu.png'))
        self.CPU.setIconSize(QSize(40, 40))
        self.CPU.clicked.connect(
            lambda: self.switch(0, self.CPU))
        self.CPU.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # 内存
        self.memory = QToolButton()
        self.memory.setText('内存')
        self.memory.setFixedSize(160, 50)
        self.memory.setIcon(QIcon('icon/memory.png'))
        self.memory.setIconSize(QSize(40, 40))
        self.memory.clicked.connect(lambda: self.switch(1, self.memory))
        self.memory.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # 磁盘
        self.disk = QToolButton()
        self.disk.setText('磁盘')
        self.disk.setFixedSize(160, 50)
        self.disk.setIcon(QIcon('icon/disk.png'))
        self.disk.setIconSize(QSize(40, 40))
        self.disk.clicked.connect(lambda: self.switch(2, self.disk))
        self.disk.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # 设备
        self.device = QToolButton()
        self.device.setText('设备')
        self.device.setFixedSize(160, 50)
        self.device.setIcon(QIcon('icon/device.png'))
        self.device.setIconSize(QSize(40, 40))
        self.device.clicked.connect(lambda: self.switch(3, self.device))
        self.device.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.btnList = [self.CPU,
                        self.memory, self.disk, self.device]

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.CPU)
        self.layout.addWidget(self.memory)
        self.layout.addWidget(self.disk)
        self.layout.addWidget(self.device)
        self.layout.addStretch()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.menu = QGroupBox()
        self.menu.setFixedSize(160, 650)
        self.menu.setLayout(self.layout)
        self.menu.setContentsMargins(0, 0, 0, 0)
        self.body.addWidget(self.menu)

    def switch(self, index, btn):
        self.focus = index
        for i in self.btnList:
            i.setStyleSheet('''
            *{
                background: white;
            }
            QToolButton:hover{
                background-color: rgba(230, 230, 230, 0.3);
            }
            ''')

        btn.setStyleSheet('''
        QToolButton{
            background-color: rgba(230, 230, 230, 0.7);
        }
        ''')
        self.setContent()

    # 设置右侧信息页
    def setContent(self):
        if self.content is not None:
            self.content.deleteLater()
        if self.focus == 0:
            self.content = QWidget()
            print(self.focus)
        elif self.focus == 1:
            # self.content = BorrowingBooks(self.stu_mes)
            print(self.focus)
        elif self.focus == 2:
            # self.content = History(self.stu_mes)
            print(self.focus)
        else:
            # self.content = Detial(self.stu_mes)
            print(self.focus)
        self.body.addWidget(self.content)

    def setMyStyle(self):
        self.setStyleSheet('''
        QWidget{
            background-color: white;
        }
        ''')
        self.menu.setStyleSheet('''
        QWidget{
            border: 0px;
            border-right: 1px solid rgba(227, 227, 227, 1);
        }
        QToolButton{
            color: rgba(51, 90, 129, 1);
            font-family: 微软雅黑;
            font-size: 25px;
            border-right: 1px solid rgba(227, 227, 227, 1);
        }
        QToolButton:hover{
            background-color: rgba(230, 230, 230, 0.3);
        }
        ''')
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TaskManger()
    # ex.show()
    sys.exit(app.exec_())
