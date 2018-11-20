import sys
from PyQt5.QtWidgets import QApplication, QTextEdit
from PyQt5.QtGui import QTextCursor, QKeyEvent, QIcon
from PyQt5.QtCore import Qt, QEvent


class Terminal(QTextEdit):
    def __init__(self):
        super().__init__()
        self.headText = r'C:\>'
        self.maxLine = 3
        self.setText('SSYNN Operating System [版本 1.0]\n2018 824063458@qq.com 保留所有权利。\n')
        self.append(self.headText)
        self.toEnd()
        self.installEventFilter(self)
        self.setWindowTitle('命令终端')
        self.setWindowIcon(QIcon('icon/terminal.ico'))
        self.setFixedWidth(800)
        self.resize(800, 700)
        self.setMyStyle()

    def mousePressEvent(self, e):
        pass

    def mouseDoubleClickEvent(self, e):
        pass

    def eventFilter(self, watched, e):
        if e.type() == QEvent.KeyPress:
            keyEvent = QKeyEvent(e)
            # 如果光标位于不可编辑区则必须过滤所有按键操作
            if self.getCursorPosition() < (self.maxLine, len(self.headText)):
                return True
            # 回车
            if keyEvent.key() == Qt.Key_Enter or keyEvent.key() == 16777220:
                self.execute()
                self.append(self.headText)
                self.maxLine += 1
                self.toEnd()
                return True
            # 退格
            if keyEvent.key() == Qt.Key_Backspace:
                if self.getCursorPosition()[1] <= len(self.headText):
                    return True
            # 左键
            if keyEvent.key() == Qt.Key_Left:
                if self.getCursorPosition()[1] <= len(self.headText):
                    return True
            if keyEvent.key() == Qt.Key_Up:
                return True
        return False

    def getCursorPosition(self):
        tc = self.textCursor()
        pLayout = tc.block().layout()
        # 获取光标的列
        nCurpos = tc.position()-tc.block().position()
        # 获取光标的行
        nTextLine = pLayout.lineForTextPosition(
            nCurpos).lineNumber() + tc.block().firstLineNumber()
        return (nTextLine, nCurpos)

    def toEnd(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

    def execute(self):
        temp = self.toPlainText().split('\n')[-1]
        temp = temp.replace(self.headText, '')
        print(temp.split())

    def setMyStyle(self):
        self.setStyleSheet('''
        QTextEdit{
            background-color:black;
            border: 0px;
            color: white;
            font-family: 微软雅黑;
            font-size: 15px;
        }
        ''')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Terminal()
    ex.show()
    sys.exit(app.exec_())
