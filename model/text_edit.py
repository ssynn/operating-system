import sys
from PyQt5.QtWidgets import QWidget, QTextEdit, QGridLayout, QLineEdit, QApplication, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal


class TextEdit(QWidget):
    after_close = pyqtSignal(list)

    def __init__(self, existList: list, mes: list=None):
        super().__init__()
        self.existList = existList
        self.setWindowIcon(QIcon('icon/text.ico'))
        self.setWindowTitle('文本编辑器')
        self.resize(600, 300)
        self.body = QGridLayout()
        self.line = QLineEdit()
        self.textArea = QTextEdit()
        self.title = QLabel()
        self.title.setText('文件名')
        self.body.addWidget(self.line, 0, 1, 1, 5)
        self.body.addWidget(self.title, 0, 0)
        self.body.addWidget(self.textArea, 1, 0, 1, 6)

        self.confirm = QPushButton()
        self.confirm.setText('确认')
        self.confirm.clicked.connect(self.confirmFunction)
        self.cancel = QPushButton()
        self.cancel.setText('取消')
        self.cancel.clicked.connect(self.close)

        self.body.addWidget(self.confirm, 2, 4)
        self.body.addWidget(self.cancel, 2, 5)
        self.setLayout(self.body)
        if mes is not None:
            self.line.setText(mes[0])
            self.textArea.setText(mes[1])
        self.show()

    def confirmFunction(self):
        for i in self.existList:
            if i.text() == self.line.text():
                msgBox = QMessageBox(QMessageBox.Warning, "警告!", '文件名重复!', QMessageBox.NoButton, self)
                msgBox.addButton("确认", QMessageBox.AcceptRole)
                msgBox.exec_()
                return
        ans = [self.line.text(), self.textArea.toPlainText()]
        self.close()
        self.after_close.emit(ans)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TextEdit()
    sys.exit(app.exec_())
