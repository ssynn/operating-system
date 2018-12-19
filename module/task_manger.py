import sys
from PyQt5.QtWidgets import (QApplication, QWidget,
                             QHBoxLayout, QSplitter, QToolButton, QLabel, QVBoxLayout, QGroupBox)
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
import disk as mydisk


class TaskManger(QWidget):

    after_close_signal = pyqtSignal()

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
        # self.device = QToolButton()
        # self.device.setText('设备')
        # self.device.setFixedSize(160, 50)
        # self.device.setIcon(QIcon('icon/device.png'))
        # self.device.setIconSize(QSize(40, 40))
        # self.device.clicked.connect(lambda: self.switch(3, self.device))
        # self.device.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.btnList = [
            self.CPU,
            self.memory,
            self.disk
        ]

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.CPU)
        self.layout.addWidget(self.memory)
        self.layout.addWidget(self.disk)
        # self.layout.addWidget(self.device)
        self.layout.addStretch()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.menu = QGroupBox()
        self.menu.setFixedSize(160, 650)
        self.menu.setLayout(self.layout)
        self.menu.setContentsMargins(0, 0, 0, 0)
        self.body.addWidget(self.menu)

    # 切换视图事件
    def switch(self, index, btn):
        self.focus = index
        self.setClickedStyle(btn)
        self.setContent()

    # 关闭事件
    def closeEvent(self, e):
        self.after_close_signal.emit()

    # 设置右侧信息页
    def setContent(self):
        # print(self.content)
        if self.content is not None:
            self.content.deleteLater()
        # print(self.content)
        if self.focus == 0:
            self.content = QWidget()
            print(self.focus)
        elif self.focus == 1:
            self.content = QWidget()
            print(self.focus)
        elif self.focus == 2:
            self.content = DiskPage()
            print(self.focus)
            print(self.content)
        else:
            # self.content = Detial(self.stu_mes)
            print(self.focus)
        print(self.content)
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

    def setClickedStyle(self, btn):
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


class DiskPage(QWidget):
    def __init__(self):
        super().__init__()
        self.labelList = []
        self.initUI()

    def initUI(self):
        self.title = QLabel()
        self.title.setText('磁盘')

        self.body = QVBoxLayout()
        self.body.addWidget(self.title)

        self.setDiskC()
        self.setDiskD()

        # self.body.addStretch()
        self.setLayout(self.body)
        self.setFixedSize(1100, 650)
        self.setMyStyle()
        self.refresh()
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.refresh)

    def setDiskC(self):
        self.cBlock = BlockPainter('c')

        # 显示磁盘名
        diskTitle = QLabel()
        diskTitle.setText('磁盘名')
        self.diskNameC = QLabel()
        self.diskNameC.setText('C:')
        self.labelList.append(self.diskNameC)
        nameLayout = QVBoxLayout()
        nameLayout.addWidget(diskTitle)
        nameLayout.addWidget(self.diskNameC)

        # 显示总容量
        diskCapacityTitle = QLabel()
        diskCapacityTitle.setText('磁盘容量')
        self.diskCapacityC = QLabel()
        self.diskCapacityC.setText('8192B')
        self.labelList.append(self.diskCapacityC)
        capacityLayout = QVBoxLayout()
        capacityLayout.addWidget(diskCapacityTitle)
        capacityLayout.addWidget(self.diskCapacityC)

        # 显示已用容量
        usedTitle = QLabel()
        usedTitle.setText('已用')
        self.usedC = QLabel()
        self.labelList.append(self.usedC)
        usedLayout = QVBoxLayout()
        usedLayout.addWidget(usedTitle)
        usedLayout.addWidget(self.usedC)

        # 显示剩余容量
        unusedTitle = QLabel()
        unusedTitle.setText('未使用')
        self.unusedC = QLabel()
        self.labelList.append(self.unusedC)
        unusedLayout = QVBoxLayout()
        unusedLayout.addWidget(unusedTitle)
        unusedLayout.addWidget(self.unusedC)

        # 格式化按钮
        self.formatC = QToolButton()
        self.formatC.setText('格式化C盘')
        self.formatC.setFixedSize(120, 50)
        self.formatC.clicked.connect(lambda: mydisk.format_disk('c'))

        # 横向
        info = QHBoxLayout()
        info.addLayout(nameLayout)
        info.addLayout(capacityLayout)
        info.addLayout(usedLayout)
        info.addLayout(unusedLayout)
        info.addWidget(self.formatC)
        infoWidget = QWidget()
        infoWidget.setLayout(info)
        infoWidget.setFixedSize(700, 100)

        self.body.addWidget(self.cBlock)
        self.body.addWidget(infoWidget)
        self.body.addSpacing(50)

    def setDiskD(self):
        self.dBlock = BlockPainter('d')

        # 显示磁盘名
        diskTitle = QLabel()
        diskTitle.setText('磁盘名')
        self.diskNameD = QLabel()
        self.diskNameD.setText('D:')
        self.labelList.append(self.diskNameD)
        nameLayout = QVBoxLayout()
        nameLayout.addWidget(diskTitle)
        nameLayout.addWidget(self.diskNameD)

        # 显示总容量
        diskCapacityTitle = QLabel()
        diskCapacityTitle.setText('磁盘容量')
        self.diskCapacityD = QLabel()
        self.diskCapacityD.setText('8192B')
        self.labelList.append(self.diskCapacityD)
        capacityLayout = QVBoxLayout()
        capacityLayout.addWidget(diskCapacityTitle)
        capacityLayout.addWidget(self.diskCapacityD)

        # 显示已用容量
        usedTitle = QLabel()
        usedTitle.setText('已用')
        self.usedD = QLabel()
        self.labelList.append(self.usedD)
        usedLayout = QVBoxLayout()
        usedLayout.addWidget(usedTitle)
        usedLayout.addWidget(self.usedD)

        # 显示剩余容量
        unusedTitle = QLabel()
        unusedTitle.setText('未使用')
        self.unusedD = QLabel()
        self.labelList.append(self.unusedD)
        unusedLayout = QVBoxLayout()
        unusedLayout.addWidget(unusedTitle)
        unusedLayout.addWidget(self.unusedD)

        # 格式化按钮
        self.formatD = QToolButton()
        self.formatD.setText('格式化D盘')
        self.formatD.setFixedSize(120, 50)
        self.formatD.clicked.connect(lambda: mydisk.format_disk('d'))

        # 横向
        info = QHBoxLayout()
        info.addLayout(nameLayout)
        info.addLayout(capacityLayout)
        info.addLayout(usedLayout)
        info.addLayout(unusedLayout)
        info.addWidget(self.formatD)
        infoWidget = QWidget()
        infoWidget.setLayout(info)
        infoWidget.setFixedSize(700, 100)

        self.body.addWidget(self.dBlock)
        self.body.addWidget(infoWidget)
        self.body.addSpacing(400)

    def refresh(self):
        tableC = mydisk.open_disk('c')[:2]
        tableD = mydisk.open_disk('d')[:2]
        cUnused = tableC[0].count(0) + tableC[1].count(0)
        dUnused = tableD[0].count(0) + tableD[1].count(0)
        self.unusedC.setText(str(cUnused*64)+'B')
        self.usedC.setText(str((128-cUnused)*64)+'B')
        self.cBlock.table = tableC
        self.cBlock.update()
        self.unusedD.setText(str(dUnused*64)+'B')
        self.usedD.setText(str((128-dUnused)*64)+'B')
        self.dBlock.table = tableD
        self.dBlock.update()

    def setMyStyle(self):
        self.setStyleSheet('''
            QWidget{
                background-color: white;
            }
            QLabel{
                color: #707070;
                font-family: 微软雅黑;
                font-size: 20px;
            }
            QToolButton{
                color: white;
                border-radius: 10px;
                background-color: #d32f2f;
                font-family: 微软雅黑;
                font-size: 20px;
            }
        ''')

        self.title.setStyleSheet('''
            QLabel{
                color: black;
                font-size: 40px;
                font-family: 微软雅黑;
            }
        ''')

        for i in self.labelList:
            i.setStyleSheet('''
                QLabel{
                    color: black;
                    font-size: 30px;
                    font-family: 微软雅黑;
                }
            ''')


class BlockPainter(QWidget):

    def __init__(self, driver: str):
        super().__init__()
        self.table = mydisk.open_disk(driver)[:2]
        self.setFixedSize(900, 120)
        self.setStyleSheet('''
            QWidget{
                border: 1px solid black;
            }
        ''')

    def paintEvent(self, a0):
        self.drawRectangles()
        # print('refreshed')

    # 绘制磁盘占用块
    def drawRectangles(self):
        self.qp = QPainter()
        self.qp.begin(self)
        col = QColor(0, 0, 0)
        col.setNamedColor("#d4d4d4")
        self.qp.setPen(col)
        for i in range(128):
            if self.table[i//64][i % 64] == 0:
                self.qp.setBrush(QColor('#8bc34a'))
            else:
                self.qp.setBrush(QColor('#D32F2F'))
            self.qp.drawRect(25*(i % 32)+5, 25*(i//32)+5, 20, 20)
        self.qp.end()


class BlockPainterD(QWidget):
    def __init__(self, diskName: str):
        return super().__init__()
        self.diskName = diskName
        self.setFixedSize(900, 200)
        self.setStyleSheet('''
            QWidget{
                border: 1px solid black;
            }
        ''')
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.update)

    def paintEvent(self, a0):
        self.drawRectangles()

    # 绘制磁盘占用块
    def drawRectangles(self):
        self.qp = QPainter()
        self.qp.begin(self)
        col = QColor(0, 0, 0)
        col.setNamedColor("#d4d4d4")
        self.qp.setPen(col)
        table_c = mydisk.open_disk('d')[:2]
        for i in range(128):
            if table_c[i//64][i % 64] == 0:
                self.qp.setBrush(QColor('#8bc34a'))
            else:
                self.qp.setBrush(QColor('#D32F2F'))
            self.qp.drawRect(20*(i % 32)+5, 20*(i//32)+5, 15, 15)
        self.qp.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TaskManger()
    # ex.show()
    sys.exit(app.exec_())
