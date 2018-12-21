import sys
import CPU
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QGridLayout, QLabel, QTableWidgetItem, QTableWidget, QAbstractItemView,
    QHBoxLayout, QVBoxLayout, QToolButton)
from PyQt5.QtGui import QIcon, QPainter, QColor
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer, Qt


class CPUWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1050, 700)

        self.body = QHBoxLayout()

        self.cpu = CPU.CPU()

        self.setTables()

        self.setMiddle()

        self.setRight()

        self.setLayout(self.body)

        self.setMyStyle()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        self.timer.start(1000)

    def run(self):
        print(123)

    def setTables(self):
        readyLabel = QLabel()
        readyLabel.setText('就绪队列')
        self.ready = ReadyQueue()

        blockLabel = QLabel()
        blockLabel.setText('阻塞队列')
        self.block = BlockQueue()

        answerLabel = QLabel()
        answerLabel.setText('结果')
        self.answer = AnswerQueue()

        self.tables = QVBoxLayout()
        self.tables.addWidget(readyLabel)
        self.tables.addWidget(self.ready)
        self.tables.addWidget(blockLabel)
        self.tables.addWidget(self.block)
        self.tables.addWidget(answerLabel)
        self.tables.addWidget(self.answer)
        self.tablesWidget = QWidget()
        self.tablesWidget.setLayout(self.tables)
        self.body.addWidget(self.tablesWidget)

    def setMiddle(self):
        self.memory = BlockPainter()

        self.cpuInfo = CPUInfo()

        self.order = QTextEdit()
        self.order.setFixedSize(400, 150)

        self.execute = QToolButton()
        self.execute.setFixedSize(400, 50)
        self.execute.setText('执行程序')

        self.mLayout = QVBoxLayout()
        self.mLayout.addWidget(self.memory)
        self.mLayout.addWidget(self.cpuInfo)
        self.mLayout.addWidget(self.order)
        self.mLayout.addWidget(self.execute)

        self.mWidget = QWidget()
        self.mWidget.setLayout(self.mLayout)

        self.body.addWidget(self.mWidget)

    def setRight(self):
        self.time = TimeBlock()

        self.device = DeviceStatus()

        self.rLayout = QVBoxLayout()
        self.rLayout.addWidget(self.time)
        self.rLayout.addWidget(self.device)
        self.rWidget = QWidget()
        self.rWidget.setLayout(self.rLayout)
        self.body.addWidget(self.rWidget)

    def setMyStyle(self):
        self.setStyleSheet('''
            QWidget{
                background-color: white;
            }
            QTextEdit{
                border: 1px solid #BDBDBD;
                border-radius: 10px;
            }
            QToolButton{
            border: 0px;
            background-color:rgba(52, 118, 176, 1);
            color: white;
            font-size: 25px;
            font-family: 微软雅黑;
            border-radius: 20px;
        }
        ''')
        self.tablesWidget.setStyleSheet('''
            QLabel{
                color: #707070;
                font-family: 微软雅黑;
                font-size: 30px;
            }
            QTableWidget{
                border: 1px solid #BDBDBD;
                /*border-radius: 10px;*/
            }
        ''')


class BlockPainter(QWidget):

    def __init__(self):
        super().__init__()
        self.table = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.table[:3] = [1]*3
        self.runningBlocks = [5, 6, 7]
        systemBlocks = QLabel()
        systemBlocks.setText('系统')

        empty = QLabel()
        empty.setText('空闲')

        running = QLabel()
        running.setText('运行')

        self.body = QGridLayout()
        self.body.addWidget(systemBlocks, 0, 0)
        self.body.addWidget(empty, 0, 1)
        self.body.addWidget(running, 0, 2)
        self.setLayout(self.body)
        self.setFixedSize(410, 100)
        self.setStyleSheet('''
            QLabel{
                font-family: 微软雅黑;
                margin-top: 50px;
                font-size: 20px;
                color: #707070;
            }
        ''')

    def paintEvent(self, a0):
        self.drawRectangles()
        # print(self.size())
        # print('refreshed')

    # 绘制磁盘占用块
    def drawRectangles(self):
        self.qp = QPainter()
        self.qp.begin(self)
        col = QColor(0, 0, 0)
        col.setNamedColor("#d4d4d4")
        self.qp.setPen(col)
        for i in range(32):
            if self.table[i] == 0:
                self.qp.setBrush(QColor('#8bc34a'))
            else:
                self.qp.setBrush(QColor('#D32F2F'))
            self.qp.drawRect(25*(i % 16)+5, 25*(i//16)+5, 20, 20)
        for i in self.runningBlocks:
            self.qp.setBrush(QColor('#2196F3'))
            self.qp.drawRect(25*(i % 16)+5, 25*(i//16)+5, 20, 20)

        self.qp.setBrush(QColor('#D32F2F'))
        self.qp.drawRect(70, 65, 20, 20)
        self.qp.setBrush(QColor('#8bc34a'))
        self.qp.drawRect(200, 65, 20, 20)
        self.qp.setBrush(QColor('#2196F3'))
        self.qp.drawRect(330, 65, 20, 20)
        self.qp.end()


class ReadyQueue(QTableWidget):
    def __init__(self):
        super().__init__(0, 2)
        self.setFixedSize(162, 150)
        self.setHorizontalHeaderLabels(['ID', '等待时间'])
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setShowGrid(False)
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 100)
        self.setMyStyle()

    def addPCB(self, _id: int, time: int):
        self.insertRow(self.rowCount())
        _idLabel = QTableWidgetItem(str(_id))
        _idLabel.setTextAlignment(Qt.AlignCenter)

        timeLabel = QTableWidgetItem(str(time))
        timeLabel.setTextAlignment(Qt.AlignCenter)
        self.setItem(self.rowCount()-1, 0, _idLabel)
        self.setItem(self.rowCount()-1, 1, timeLabel)

    def remove(self, _id: int):
        for i in range(self.rowCount()):
            print(i, self.item(i, 0).text(), _id)
            if self.item(i, 0).text() == str(_id):
                print('removed')
                self.removeRow(i)
                break

    def setMyStyle(self):
        self.verticalScrollBar().setStyleSheet('''
            QScrollBar{background:transparent; width: 10px;}
            QScrollBar::handle{background:lightgray; border:2px solid transparent; border-radius:5px;}
            QScrollBar::handle:hover{background:gray;}
            QScrollBar::sub-line{background:transparent;}
            QScrollBar::add-line{background:transparent;}
        ''')


class BlockQueue(QTableWidget):
    def __init__(self):
        super().__init__(0, 3)
        self.setFixedSize(262, 150)
        self.setHorizontalHeaderLabels(['ID', '等待时间', '阻塞原因'])
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setShowGrid(False)
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 100)
        self.setMyStyle()

    def addPCB(self, _id: int, time: int, cause: str):
        self.insertRow(self.rowCount())
        _idLabel = QTableWidgetItem(str(_id))
        _idLabel.setTextAlignment(Qt.AlignCenter)

        timeLabel = QTableWidgetItem(str(time))
        timeLabel.setTextAlignment(Qt.AlignCenter)

        causeLable = QTableWidgetItem(cause)
        causeLable.setTextAlignment(Qt.AlignCenter)

        self.setItem(self.rowCount()-1, 0, _idLabel)
        self.setItem(self.rowCount()-1, 1, timeLabel)
        self.setItem(self.rowCount()-1, 2, causeLable)

    def remove(self, _id: int):
        for i in range(self.rowCount()):
            print(i, self.item(i, 0).text(), _id)
            if self.item(i, 0).text() == str(_id):
                print('removed')
                self.removeRow(i)
                break

    def setMyStyle(self):
        self.verticalScrollBar().setStyleSheet('''
            QScrollBar{background:transparent; width: 10px;}
            QScrollBar::handle{background:lightgray; border:2px solid transparent; border-radius:5px;}
            QScrollBar::handle:hover{background:gray;}
            QScrollBar::sub-line{background:transparent;}
            QScrollBar::add-line{background:transparent;}
        ''')


class AnswerQueue(QTableWidget):
    def __init__(self):
        super().__init__(0, 3)
        self.setFixedSize(262, 150)
        self.setHorizontalHeaderLabels(['ID', '花费时间', '运行结果'])
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setShowGrid(False)
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 100)
        self.setColumnWidth(2, 100)
        self.setMyStyle()

    def addPCB(self, _id: int, time: int, answer: str):
        self.insertRow(self.rowCount())
        _idLabel = QTableWidgetItem(str(_id))
        _idLabel.setTextAlignment(Qt.AlignCenter)

        timeLabel = QTableWidgetItem(str(time))
        timeLabel.setTextAlignment(Qt.AlignCenter)

        answerLable = QTableWidgetItem(answer)
        answerLable.setTextAlignment(Qt.AlignCenter)

        self.setItem(self.rowCount()-1, 0, _idLabel)
        self.setItem(self.rowCount()-1, 1, timeLabel)
        self.setItem(self.rowCount()-1, 2, answerLable)

    def remove(self, _id: int):
        for i in range(self.rowCount()):
            print(i, self.item(i, 0).text(), _id)
            if self.item(i, 0).text() == str(_id):
                print('removed')
                self.removeRow(i)
                break

    def setMyStyle(self):
        self.verticalScrollBar().setStyleSheet('''
            QScrollBar{background:transparent; width: 10px;}
            QScrollBar::handle{background:lightgray; border:2px solid transparent; border-radius:5px;}
            QScrollBar::handle:hover{background:gray;}
            QScrollBar::sub-line{background:transparent;}
            QScrollBar::add-line{background:transparent;}
        ''')


class CPUInfo(QWidget):
    def __init__(self):
        super().__init__()
        self.body = QHBoxLayout()
        self.setFixedSize(220, 300)
        self.setLabels()
        self.setDataWidget()
        self.setLayout(self.body)
        self.setMyStyle()

    def setLabels(self):
        runningProcessLabel = QLabel()
        runningProcessLabel.setText('当前进程:')

        orderNowLabel = QLabel()
        orderNowLabel.setText('当前指令:')

        dataNowLabel = QLabel()
        dataNowLabel.setText('中间结果:')

        runningTimeLabel = QLabel()
        runningTimeLabel.setText('运行总时间:')

        timeSliceLabel = QLabel()
        timeSliceLabel.setText('时间片长度:')

        PSWLabel = QLabel()
        PSWLabel.setText('PSW:')

        PCLabel = QLabel()
        PCLabel.setText('PC:')

        self.labels = QVBoxLayout()
        self.labels.addWidget(runningProcessLabel)
        self.labels.addWidget(orderNowLabel)
        self.labels.addWidget(dataNowLabel)
        self.labels.addWidget(runningTimeLabel)
        self.labels.addWidget(timeSliceLabel)
        self.labels.addWidget(PSWLabel)
        self.labels.addWidget(PCLabel)
        self.body.addLayout(self.labels)

    def setDataWidget(self):
        self.runningProcess = QLabel()
        self.runningProcess.setText('None')

        self.orderNow = QLabel()
        self.orderNow.setText('NOP')

        self.dataNow = QLabel()
        self.dataNow.setText('None')

        self.runningTime = QLabel()
        self.runningTime.setText('0')

        self.timeSlice = QLabel()
        self.timeSlice.setText('5')

        self.PSW = QLabel()
        self.PSW.setText('000')

        self.PC = QLabel()
        self.PC.setText('0')

        self.dataLayout = QVBoxLayout()
        self.dataLayout.addWidget(self.runningProcess)
        self.dataLayout.addWidget(self.orderNow)
        self.dataLayout.addWidget(self.dataNow)
        self.dataLayout.addWidget(self.runningTime)
        self.dataLayout.addWidget(self.timeSlice)
        self.dataLayout.addWidget(self.PSW)
        self.dataLayout.addWidget(self.PC)
        self.dataLayout.setContentsMargins(0, 0, 0, 0)
        self.dataWidget = QWidget()
        self.dataWidget.setLayout(self.dataLayout)
        self.body.addWidget(self.dataWidget)

    def setMyStyle(self):
        self.setStyleSheet('''
            QWidget{
                background-color: white;
            }
            QLabel{
                color: #707070;
                font-family: 微软雅黑;
                font-size: 15px;
            }
        ''')
        self.dataWidget.setStyleSheet('''
            QLabel{
                color: balck;
            }
        ''')


class TimeBlock(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(250, 150)

        self.title = QLabel()
        self.title.setText('总运行时间')

        self.time = QLabel()
        self.time.setText('00:00:00')

        self.hour = 0
        self.minute = 0
        self.second = 0

        self.stop = QToolButton()
        self.stop.setText('暂停')
        self.stop.setFixedSize(60, 30)

        self.closeCPU = QToolButton()
        self.closeCPU.setText('关机')
        self.closeCPU.setFixedSize(60, 30)

        self.restart = QToolButton()
        self.restart.setText('重启')
        self.restart.setFixedSize(60, 30)

        self.body = QGridLayout()
        self.body.addWidget(self.title, 0, 0, 1, 3)
        self.body.addWidget(self.time, 1, 0, 1, 3)
        self.body.addWidget(self.stop, 2, 0, 1, 1)
        self.body.addWidget(self.closeCPU, 2, 1, 1, 1)
        self.body.addWidget(self.restart, 2, 2, 1, 1)
        self.setLayout(self.body)
        self.setMystyle()

    def setTime(self, hour, minute, second):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.time.setText('{0:2}:{1:2}:{2:2}'.format(
            self.hour, self.minute, self.second))

    def setMystyle(self):
        self.setStyleSheet('''
            QWidget{
                background-color: white;
            }
            QToolButton{
                border: 0px;
                font-family: 微软雅黑;
                font-size: 15px;
                border-radius: 5px;
                color: white;
            }
        ''')
        self.title.setStyleSheet('''
            QLabel{
                color: #707070;
                font-family: 微软雅黑;
                font-size: 15px;
            }
        ''')
        self.time.setStyleSheet('''
            *{
                font-family: 微软雅黑;
                font-size: 50px;
            }
        ''')
        self.stop.setStyleSheet('''
            *{
                background-color: #FF9800;
            }
        ''')
        self.closeCPU.setStyleSheet('''
            *{
                background-color: #FF5252;
            }
        ''')
        self.restart.setStyleSheet('''
            *{
                background-color: #8BC34A;
            }
        ''')


class DeviceStatus(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(252, 430)
        self.body = QVBoxLayout()
        self.body.addSpacing(100)
        self.devices = []
        self._ids = []
        self.time = []

        name = QLabel()
        name.setText('设备名')
        name.setAlignment(Qt.AlignCenter)

        _id = QLabel()
        _id.setText('占用进程')
        _id.setAlignment(Qt.AlignCenter)

        time = QLabel()
        time.setText('剩余时间')
        time.setAlignment(Qt.AlignCenter)

        la = QHBoxLayout()
        la.addWidget(name)
        la.addWidget(_id)
        la.addWidget(time)
        self.title = QWidget()
        self.title.setLayout(la)
        self.title.setFixedHeight(50)
        self.body.addWidget(self.title)

        self.addPCB('A1', '无', 0)
        self.addPCB('A2', '无', 0)
        self.addPCB('A3', '无', 0)
        self.addPCB('B1', '无', 0)
        self.addPCB('B2', '无', 0)
        self.addPCB('C', '无', 0)

        self.setLayout(self.body)
        self.setMyStyle()

    def addPCB(self, pname: str, p_id, ptime: int):
        name = QLabel()
        name.setText(pname)
        name.setAlignment(Qt.AlignCenter)

        _id = QLabel()
        _id.setText(str(p_id))
        _id.setAlignment(Qt.AlignCenter)
        self._ids.append(_id)

        time = QLabel()
        time.setText(str(ptime))
        time.setAlignment(Qt.AlignCenter)
        self.time.append(time)

        la = QHBoxLayout()
        la.addWidget(name)
        la.addWidget(_id)
        la.addWidget(time)
        device = QWidget()
        device.setLayout(la)
        device.setFixedHeight(40)
        self.body.addWidget(device)
        self.devices.append(device)

    def setInfo(self, info: dict):
        pass

    def setMyStyle(self):
        self.setStyleSheet('''
            QWidget{
                background-color: #009688;
                border-radius: 10px;
                color: white;
                font-family: 微软雅黑;
            }
        ''')
        self.title.setStyleSheet('''
            QWidget{
                background-color: #757575;
                font-size: 18px;
            }
        ''')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    text = CPUWidget()
    text.show()
    sys.exit(app.exec_())
