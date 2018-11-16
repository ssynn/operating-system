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
        # 分割
        # self.body = QSplitter()
        # self.setLeftMunu()
        # self.content = None
        # self.setContent()

        self.bodyLayout = QHBoxLayout()
        # self.bodyLayout.addWidget(self.body)
        self.setLayout(self.bodyLayout)
        self.setFixedSize(1280, 720)
        self.setMyStyle()
        self.show()

    # 左侧菜单栏
    def setLeftMunu(self):
        # 查询按钮
        self.bookSearch = QToolButton()
        self.bookSearch.setText('图书查询')
        self.bookSearch.setFixedSize(160, 50)
        self.bookSearch.setIcon(QIcon('icon/book.png'))
        self.bookSearch.setIconSize(QSize(30, 30))
        self.bookSearch.clicked.connect(
            lambda: self.switch(0, self.bookSearch))
        self.bookSearch.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # 借阅按钮
        self.borrow = QToolButton()
        self.borrow.setText('借阅信息')
        self.borrow.setFixedSize(160, 50)
        self.borrow.setIcon(QIcon('icon/borrowing.png'))
        self.borrow.setIconSize(QSize(30, 30))
        self.borrow.clicked.connect(lambda: self.switch(1, self.borrow))
        self.borrow.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # 借阅历史
        self.history = QToolButton()
        self.history.setText('借阅历史')
        self.history.setFixedSize(160, 50)
        self.history.setIcon(QIcon('icon/history.png'))
        self.history.setIconSize(QSize(30, 30))
        self.history.clicked.connect(lambda: self.switch(2, self.history))
        self.history.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # 个人信息
        self.detial = QToolButton()
        self.detial.setText('个人信息')
        self.detial.setFixedSize(160, 50)
        self.detial.setIcon(QIcon('icon/detial.png'))
        self.detial.setIconSize(QSize(30, 30))
        self.detial.clicked.connect(lambda: self.switch(3, self.detial))
        self.detial.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.btnList = [self.bookSearch,
                        self.borrow, self.history, self.detial]

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.bookSearch)
        self.layout.addWidget(self.borrow)
        self.layout.addWidget(self.history)
        self.layout.addWidget(self.detial)
        self.layout.addStretch()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.menu = QGroupBox()
        self.menu.setFixedSize(160, 500)
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
            # self.content = Books(self.stu_mes)
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
        # self.menu.setStyleSheet('''
        # QWidget{
        #     border: 0px;
        #     border-right: 1px solid rgba(227, 227, 227, 1);
        # }
        # QToolButton{
        #     color: rgba(51, 90, 129, 1);
        #     font-family: 微软雅黑;
        #     font-size: 25px;
        #     border-right: 1px solid rgba(227, 227, 227, 1);
        # }
        # QToolButton:hover{
        #     background-color: rgba(230, 230, 230, 0.3);
        # }
        # ''')
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TaskManger()
    # ex.show()
    sys.exit(app.exec_())
