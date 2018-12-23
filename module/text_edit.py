import sys
from PyQt5.QtWidgets import QWidget, QTextEdit, QGridLayout, QLineEdit, QApplication, QLabel, QToolButton, QMessageBox, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
import disk


class TextEdit(QWidget):

    after_close = pyqtSignal(dict)

    def __init__(self, existList: list = [], mes: list = None, op: str = 'new'):
        '''
        existList为当前目录的文件
        mes[0] 为文件名
        mes[1] 为文本内容
        '''
        super().__init__()
        self.existList = existList
        self.op = op
        self.setWindowIcon(QIcon('icon/text.ico'))
        self.setWindowTitle('文本编辑器')
        self.resize(600, 300)
        self.setContentsMargins(0, 0, 0, 0)

        self.line = QLineEdit()
        self.line.setFixedSize(200, 30)

        self.title = QLabel()
        self.title.setText('文件名')

        top = QHBoxLayout()
        top.addWidget(self.title)
        top.addWidget(self.line)
        top.addStretch()

        self.textArea = QTextEdit()
        self.textArea.textChanged.connect(self.showTextLength)

        self.textLength = QLabel()
        self.textLength.setText('0 Byte')

        self.confirm = QToolButton()
        self.confirm.setText('确认')
        self.confirm.setFixedSize(80, 30)
        self.confirm.clicked.connect(self.confirmFunction)

        self.cancel = QToolButton()
        self.cancel.setText('取消')
        self.cancel.setFixedSize(80, 30)
        self.cancel.clicked.connect(self.close)

        bottom = QHBoxLayout()
        bottom.addWidget(self.textLength)
        bottom.addStretch()
        bottom.addWidget(self.confirm)
        bottom.addWidget(self.cancel)

        self.body = QVBoxLayout()
        self.body.setContentsMargins(0, 0, 0, 5)
        self.body.addLayout(top)
        self.body.addWidget(self.textArea)
        self.body.addLayout(bottom)

        self.setLayout(self.body)

        if mes is not None:
            self.line.setText(mes[0])
            self.textArea.setText(mes[1])
            if mes[2] & 1 != 0:
                self.textArea.setDisabled(True)

        self.setMyStyle()
        self.show()

    def showTextLength(self):
        length = len(self.textArea.toPlainText().encode())
        self.textLength.setText(str(length) + ' Byte')

    def confirmFunction(self):
        if self.op == 'new':
            for i in self.existList:
                if i.text() == self.line.text():
                    self.errorBox('文件名重复!')
                    return

        if len(self.textArea.toPlainText().encode()) > 255:
            self.errorBox('文件内容超过最大长度!')
            return

        if not disk.is_file_name(self.line.text()):
            self.errorBox('文件名不符合规范!')
            return

        name, ext = disk.file_name_split(self.line.text())
        ans = {
            'name': name,
            'ext': ext,
            'attribute': 4,
            'length': len(self.textArea.toPlainText().encode()),
            'text': self.textArea.toPlainText()
        }
        self.close()
        self.after_close.emit(ans)

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

    def setMyStyle(self):
        self.setStyleSheet('''
            QWidget{
                background-color: white;
            }
            QTextEdit{
                border-top:1px solid #ECECEC;
                border-bottom: 1px solid #ECECEC;
            }
            QToolButton{
                border: 0px;
                font-family: 微软雅黑;
                font-size: 15px;
                border-radius: 5px;
                color: white;
            }
            QLineEdit{
                border-radius: 5px;
                border: 1px solid #9E9E9E;
            }
        ''')
        self.title.setStyleSheet('''
            *{
                font-family: 微软雅黑;
                font-size: 20px;
                border: 0px;
                margin-left: 5px;
            }
        ''')
        self.textLength.setStyleSheet('''
            *{
                border: 0px;
                font-family: 微软雅黑;
                font-size: 20px;
                margin-left: 5px;
            }
        ''')
        self.confirm.setStyleSheet('''
            *{
                background: #448AFF;
            }
        ''')
        self.cancel.setStyleSheet('''
            *{
                background: #D32F2F;
                margin-right: 5px;
            }
        ''')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TextEdit()
    sys.exit(app.exec_())
