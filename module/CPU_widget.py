import re
import sys
import CPU
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTextEdit, QGridLayout, QLabel, QTableWidgetItem, QTableWidget, QAbstractItemView,
    QHBoxLayout, QVBoxLayout, QToolButton, QMessageBox)
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QTimer


info = {
    'PID': 0,
    'pageAddress': 1,
    'order': 'A--;',
    'program': 'A=2;A--;A--;A--;A--;A--;A--;end.',
    'tempRes': 'A=-3',
    'time': 10,
    'timeSlice': 5,
    'PSW': '001',
    'PC': '24',
    'ready': [],
    'block': [],
    'memory': [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'device': [[-1, 0], [-1, 0], [-1, 0], [-1, 0], [-1, 0], [-1, 0]]
}


class CPUWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1050, 650)
        self.setContentsMargins(0, 0, 0, 0)
        self.interval = 1000

        self.body = QHBoxLayout()

        self.cpu = CPU.CPU(self)

        self.setTables()

        self.setMiddle()

        self.setRight()

        self.setLayout(self.body)

        self.setMyStyle()

        self.setFunction()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        self.timer.start(self.interval)

    def run(self):
        info = self.cpu.run()
        # print(info)
        self.refresh(info)

    def setTables(self):
        readyLabel = QLabel()
        readyLabel.setText('就绪队列')
        readyLabel.setFixedWidth(250)
        self.ready = ReadyQueue()

        blockLabel = QLabel()
        blockLabel.setText('阻塞队列')
        blockLabel.setFixedWidth(250)
        self.block = BlockQueue()

        answerLabel = QLabel()
        answerLabel.setText('结果')
        answerLabel.setFixedWidth(250)
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
        self.tablesWidget.setFixedWidth(300)
        self.body.addWidget(self.tablesWidget)

    def setMiddle(self):
        self.memory = BlockPainter()

        self.cpuInfo = CPUInfo()

        # 命令显示
        self.orderDisp = OrdersDisplay()

        la = QHBoxLayout()
        la.addWidget(self.cpuInfo)
        la.addWidget(self.orderDisp)

        self.order = QTextEdit()
        self.order.setFixedSize(400, 150)

        self.execute = QToolButton()
        self.execute.setFixedSize(400, 50)
        self.execute.setText('执行程序')
        self.execute.clicked.connect(lambda: self.createProgram(
            self.order.toPlainText().replace('\n', '')))

        self.mLayout = QVBoxLayout()
        self.mLayout.addWidget(self.memory)
        self.mLayout.addLayout(la)
        self.mLayout.addWidget(self.order)
        self.mLayout.addWidget(self.execute)

        self.mWidget = QWidget()
        self.mWidget.setLayout(self.mLayout)
        self.mWidget.setFixedWidth(430)

        self.body.addWidget(self.mWidget)

    def setRight(self):
        self.time = TimeBlock()

        self.device = DeviceStatus()

        self.rLayout = QVBoxLayout()
        self.rLayout.addWidget(self.time)
        self.rLayout.addWidget(self.device)
        self.rLayout.addSpacing(50)
        self.rLayout.setContentsMargins(0, 0, 0, 0)
        self.rWidget = QWidget()
        self.rWidget.setLayout(self.rLayout)
        self.rWidget.setContentsMargins(0, 0, 0, 0)
        self.body.addWidget(self.rWidget)

    def createProgram(self, orders: str):
        if self.order_check(orders):
            if not self.cpu.create(orders.strip(';')):
                self.errorBox('创建失败')
            else:
                msgBox = QMessageBox(
                    QMessageBox.Warning,
                    "提示",
                    "创建成功！",
                    QMessageBox.NoButton,
                    self
                )
                msgBox.addButton("确认", QMessageBox.AcceptRole)
                msgBox.exec_()
                self.refresh(self.cpu.get_info())

    def setFunction(self):
        self.time.stop.clicked.connect(lambda: self.stop(self.time.stop))
        self.time.closeCPU.clicked.connect(
            lambda: self.closeCPU(self.time.closeCPU)
        )
        self.time.restart.clicked.connect(self.restart)
        self.time.nextStep.clicked.connect(self.run)
        self.time.speedUp.clicked.connect(self.speedUp)
        self.cpuInfo.timeSlice.textChanged.connect(
            lambda: self.cpu.setTimeslice(self.cpuInfo.timeSlice.text()))

    def stop(self, btn: QToolButton):
        if self.timer.isActive():
            self.timer.stop()
            self.time.nextStep.setDisabled(False)
            self.time.nextStep.setStyleSheet('''
                *{
                    background-color: #673AB7;
                }
            ''')
            btn.setText('继续')
            btn.setStyleSheet('''
                QToolButton{
                    background-color: #1976D2;
                }
            ''')
        else:
            self.timer.start(self.interval)
            self.time.nextStep.setDisabled(True)
            self.time.nextStep.setStyleSheet('''
                *{
                    background-color: #BDBDBD;
                }
            ''')
            btn.setText('暂停')
            btn.setStyleSheet('''
                QToolButton{
                    background-color: #FF9800;
                }
            ''')

    def closeCPU(self, btn: QToolButton):
        self.time.nextStep.setDisabled(True)
        self.time.nextStep.setStyleSheet('''
            *{
                background-color: #BDBDBD;
            }
        ''')
        if self.timer.isActive():
            self.timer.stop()
            self.cpu.off()
            self.refresh(self.cpu.get_info())
            self.answer.init()

            btn.setText('开机')
            btn.setStyleSheet('''
                QToolButton{
                    background-color: #607D8B;
                }
            ''')
            self.time.stop.setDisabled(True)
            self.time.stop.setText('暂停')
            self.time.stop.setStyleSheet('''
                QToolButton{
                    background-color: #BDBDBD;
                }
            ''')

        else:
            self.timer.start(self.interval)
            self.time.stop.setDisabled(False)
            self.time.stop.setText('暂停')
            self.time.stop.setStyleSheet('''
                QToolButton{
                    background-color: #FF9800;
                }
            ''')
            btn.setText('关机')
            btn.setStyleSheet('''
                QToolButton{
                    background-color: #FF5252;
                }
            ''')

    def restart(self):
        self.cpu.off()
        self.refresh(self.cpu.get_info())
        self.answer.init()

        self.time.stop.setDisabled(False)
        self.time.stop.setText('暂停')
        self.time.stop.setStyleSheet('''
            QToolButton{
                background-color: #FF9800;
            }
        ''')

        self.time.closeCPU.setText('关机')
        self.time.closeCPU.setStyleSheet('''
            QToolButton{
                background-color: #FF5252;
            }
        ''')

        self.time.nextStep.setDisabled(True)
        self.time.nextStep.setStyleSheet('''
            *{
                background-color: #BDBDBD;
            }
        ''')

        if not self.timer.isActive():
            self.timer.start(self.interval)

    def speedUp(self):
        if self.interval == 250:
            self.interval = 1000
            self.time.speedUp.setText('1.0X')
        elif self.interval == 1000:
            self.interval //= 2
            self.time.speedUp.setText('2.0X')
        else:
            self.interval //= 2
            self.time.speedUp.setText('4.0X')
        if self.timer.isActive():
            self.timer.stop()
            self.timer.start(self.interval)

    def order_check(self, orders: str) -> bool:
        """
        首先每一条指令长度只能为4
        初始化指令
        操作指令的第一个字符必须之前使用初始化指令初始化过
        申请设备指令开头指令为ABC选一
        末尾必须为end.
        """
        patterns = [
            r'[a-zA-Z]=\d',
            r'[a-zA-Z](\+\+|\-\-)',
            r'[ABC]\d\d',
            r'end.'
        ]
        if len(orders) > 255:
            self.errorBox('超过程序最大长度255Byte！')
            return False
        if orders.count('end.') > 1:
            self.errorBox('结束语只能有一句！')
            return False
        exists_val = set()
        orders = orders.strip(';').split(';')
        if orders[-1] != 'end.':
            self.errorBox('结尾必须为终止语句!')
            return False
        print(orders)
        for index, order in enumerate(orders):
            if len(order) == 0:
                self.errorBox('未定义的错误！')
                return False
            if re.fullmatch(patterns[0], order):
                exists_val.add(order[0])
                continue
            if re.fullmatch(patterns[1], order):
                if order[0] not in exists_val:
                    self.errorBox('使用未定义的变量: ' + order + ';')
                    return False
                continue
            if re.fullmatch(patterns[2], order):
                if order[0] not in ('A', 'B', 'C'):
                    self.errorBox('不存在设备: ' + order[0])
                    return False
                continue
            if index == len(orders) - 1 and order == 'end.':
                continue
            self.errorBox('未定义的指令: ' + order + ';')
            return False
        return True

    # 错误提示框
    def errorBox(self, mes: str):
        msgBox = QMessageBox(
            QMessageBox.Warning,
            "警告!",
            mes,
            QMessageBox.NoButton,
            self
        )
        msgBox.addButton("确认", QMessageBox.AcceptRole)
        msgBox.exec_()

    def refresh(self, info: dict):
        self.cpuInfo.refresh(info)
        self.memory.refresh(info['memory'], info['pages'])
        self.time.refresh(info['time'])
        self.device.refresh(info['device'])
        self.ready.refresh(info['ready'], info['time'])
        self.block.refresh(info['block'], info['time'])
        self.answer.refresh(info['result'], info['time'])
        self.orderDisp.refresh(info['program'], int(info['PC'])-4)

    def setMyStyle(self):
        self.setStyleSheet('''
            QWidget{
                background-color: white;
                /*border: 1px solid black;*/
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
        self.table = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                      0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.runningBlocks = []
        systemBlocks = QLabel()
        systemBlocks.setText('占用')
        systemBlocks.setFixedSize(50, 70)

        empty = QLabel()
        empty.setText('空闲')
        empty.setFixedSize(50, 70)

        running = QLabel()
        running.setText('运行')
        running.setFixedSize(50, 70)

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

    def refresh(self, table, running):
        self.table = table
        self.runningBlocks = running
        self.update()

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
        self.qp.drawRect(130, 65, 20, 20)
        self.qp.setBrush(QColor('#8bc34a'))
        self.qp.drawRect(240, 65, 20, 20)
        self.qp.setBrush(QColor('#2196F3'))
        self.qp.drawRect(350, 65, 20, 20)
        self.qp.end()


class ReadyQueue(QTableWidget):
    def __init__(self):
        super().__init__(0, 2)
        self.setFixedSize(262, 150)
        self.setHorizontalHeaderLabels(['ID', '等待时间'])
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setShowGrid(False)
        self.setColumnWidth(0, 120)
        self.setColumnWidth(1, 130)
        self.setMyStyle()

    def addPCB(self, _id: int, time: int):
        self.insertRow(self.rowCount())
        _idLabel = QTableWidgetItem(str(_id))
        _idLabel.setTextAlignment(Qt.AlignCenter)

        timeLabel = QTableWidgetItem(str(time))
        timeLabel.setTextAlignment(Qt.AlignCenter)
        self.setItem(self.rowCount()-1, 0, _idLabel)
        self.setItem(self.rowCount()-1, 1, timeLabel)
        self.setAlternatingRowColors(True)

    def refresh(self, queue, time):
        while self.rowCount() != 0:
            self.removeRow(0)
        for pcb in queue:
            self.addPCB(pcb.id, time-pcb.enqueueTime)

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
        self.setAlternatingRowColors(True)
        self.setShowGrid(False)
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 120)
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

    # 每秒跟新一次阻塞队列
    def refresh(self, queue, time):
        # print(queue, time)
        while self.rowCount() != 0:
            self.removeRow(0)
        for pcb in queue:
            cause = ['未阻塞', '未申请到设备: ', '占用设备: ']
            self.addPCB(pcb.id, time-pcb.enqueueTime,
                        cause[pcb.cause] + pcb.device)

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
        self.setAlternatingRowColors(True)
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 80)
        self.setColumnWidth(2, 120)
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

    # 把新的结果插入队列
    def refresh(self, pcb, time):
        if pcb:
            self.addPCB(pcb.id, time-pcb.start-1, str(pcb.varDict))

    # 清空结果队列
    def init(self):
        while self.rowCount() != 0:
            self.removeRow(0)

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
        self.setFixedSize(220, 280)
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
        runningTimeLabel.setText('时间片剩余:')

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

        # 时间片显示以及调整
        self.timeSlice = QLineEdit()
        self.timeSlice.setText('5')
        self.timeSlice.setFixedSize(40, 30)

        self.PSW = QLabel()
        self.PSW.setText('100')

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

    def refresh(self, info: dict):
        self.runningProcess.setText(str(info['PID']))
        self.orderNow.setText(info['order'])
        self.dataNow.setText(info['tempRes'])
        self.runningTime.setText(str(info['remaining']))
        self.timeSlice.setText(str(info['timeSlice']))
        self.PSW.setText(info['PSW'])
        self.PC.setText(info['PC'])

    def setMyStyle(self):
        self.setStyleSheet('''
            QWidget{
                background-color: white;
                /*border: 1px solid black;*/
            }
            QLabel{
                color: #707070;
                font-family: 微软雅黑;
                font-size: 15px;
            }
            QLineEdit{
                border: 1px solid #BDBDBD;
                border-radius: 5px;
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
        self.setFixedSize(250, 170)

        self.title = QLabel()
        self.title.setText('总运行时间')

        self.time = QLabel()
        self.time.setText('00:00:00')

        self.stop = QToolButton()
        self.stop.setText('暂停')
        self.stop.setFixedSize(60, 30)

        self.closeCPU = QToolButton()
        self.closeCPU.setText('关机')
        self.closeCPU.setFixedSize(60, 30)

        self.restart = QToolButton()
        self.restart.setText('重启')
        self.restart.setFixedSize(60, 30)

        self.nextStep = QToolButton()
        self.nextStep.setText('单步运行')
        self.nextStep.setDisabled(True)
        self.nextStep.setFixedSize(140, 30)

        self.speedUp = QToolButton()
        self.speedUp.setText('1.0X')
        self.speedUp.setFixedSize(60, 30)

        self.body = QGridLayout()
        self.body.addWidget(self.title, 0, 0, 1, 3)
        self.body.addWidget(self.time, 1, 0, 1, 3)
        self.body.addWidget(self.stop, 2, 0, 1, 1)
        self.body.addWidget(self.closeCPU, 2, 1, 1, 1)
        self.body.addWidget(self.restart, 2, 2, 1, 1)
        self.body.addWidget(self.nextStep, 3, 0, 1, 2)
        self.body.addWidget(self.speedUp, 3, 2, 1, 1)

        self.setLayout(self.body)
        self.setMystyle()

    def refresh(self, time: int):
        h = time // 3600
        m = (time % 3600) // 60
        s = (time % 3600) % 60
        self.time.setText('{0:02}:{1:02}:{2:02}'.format(h, m, s))

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
        self.speedUp.setStyleSheet('''
            *{
                background-color: #00BCD4;
            }
        ''')
        self.nextStep.setStyleSheet('''
            *{
                background-color: #BDBDBD;
            }
        ''')


class DeviceStatus(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(252, 400)
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

        self.addPCB('A1', 'None', 0)
        self.addPCB('A2', 'None', 0)
        self.addPCB('A3', 'None', 0)
        self.addPCB('B1', 'None', 0)
        self.addPCB('B2', 'None', 0)
        self.addPCB('C', 'None', 0)

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

    def refresh(self, info: list):
        for i in range(6):
            if info[i][0] != -1:
                d = str(info[i][0])
                self.setBackgroundColor(self.devices[i], True)
            else:
                d = 'None'
                self.setBackgroundColor(self.devices[i], False)
            self._ids[i].setText(d)
            self.time[i].setText(str(info[i][1]))

    def setBackgroundColor(self, item, used: bool = False):
        if not used:
            item.setStyleSheet('''
                QWidget{
                    background-color: #009688;
                }
            ''')
        else:
            item.setStyleSheet('''
                QWidget{
                    background-color: #FF5252;
                }
            ''')

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


class OrdersDisplay(QTableWidget):
    def __init__(self):
        super().__init__(0, 1)
        self.setFixedSize(150, 280)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setFocusPolicy(Qt.NoFocus)
        self.setShowGrid(False)
        self.setMyStyle()

    def refresh(self, orders: str, pc: int):
        while self.rowCount() != 0:
            self.removeRow(0)
        if orders == '':
            return
        orders = orders.split(';')
        for index, order in enumerate(orders):
            temp_label = QLabel()
            temp_label.setText(order+';')
            temp_label.setAlignment(Qt.AlignCenter)
            self.insertRow(self.rowCount())
            self.setCellWidget(self.rowCount()-1, 0, temp_label)
            self.setRowHeight(self.rowCount()-1, 25)
            if index < pc // 4:
                temp_label.setStyleSheet('''
                    QLabel{
                        color: #707070;
                    }
                ''')
            elif index == pc // 4:
                temp_label.setStyleSheet('''
                    QLabel{
                        color: #1976D2;
                    }
                ''')
            else:
                temp_label.setStyleSheet('''
                    QLabel{
                        color: #212121;
                    }
                ''')
        self.verticalScrollBar().setSliderPosition(pc // 4 - 4)

    def setMyStyle(self):
        self.setStyleSheet('''
            QTableWidget{
                background-color: white;
                border: 1px solid #BDBDBD;
            }
            QLabel{
                font-family: 微软雅黑;
                font-size: 20px;
            }
        ''')
        self.verticalScrollBar().setStyleSheet('''
            QScrollBar{background:transparent; width: 10px;}
            QScrollBar::handle{background:lightgray; border:2px solid transparent; border-radius:5px;}
            QScrollBar::handle:hover{background:gray;}
            QScrollBar::sub-line{background:transparent;}
            QScrollBar::add-line{background:transparent;}
        ''')


if __name__ == "__main__":
    order = 'A=2;A--;A--;A--;A--;A--;A--;A--;A--;A--;A--;A--;A--;A--;A--;A--;A--;end.'
    app = QApplication(sys.argv)
    text = CPUWidget()
    text.show()
    sys.exit(app.exec_())
