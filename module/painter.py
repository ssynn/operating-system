import sys
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QToolButton
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import QTimer
import disk as mydisk


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
        self.setFixedSize(1000, 690)
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
        print('refreshed')

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = DiskPage()
    ex.show()
    # table = mydisk.open_disk('c')[:2]
    # print(table)
    # ex = BlockPainterC(table)
    # ex.show()
    sys.exit(app.exec_())
