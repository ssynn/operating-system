import sys
import os
from PyQt5.QtWidgets import (QWidget, QToolButton, QApplication,
                             QDesktopWidget, QGridLayout, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QMenu, QAction,
                             QLineEdit, QInputDialog, QMessageBox)
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtCore import QSize, Qt, pyqtSignal
from model import floatlayout as fl
from model import text_edit as te
# import floatlayout as fl
# import text_edit as te


class Explorer(QWidget):
    after_close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.path = 'C:/'
        self.initUI()

    def initUI(self):
        self.setContent()
        self.setWindowStyle()
        self.show()

    def setWindowStyle(self):
        self.setStyleSheet('''
            QToolButton{
                border:1px solid white;
            }
            Explorer{
                background-color:white;
            }
        ''')
        self.fileView.setStyleSheet('''
            QSplitter::handle{
                width: 0px;
                border: 0px solid gray;
            }
        ''')
        self.setWindowIcon(QIcon('icon/file.ico'))
        self.setWindowTitle('文件管理器')
        self.resize(1280, 800)
        self.center()

    def setContent(self):
        # 主窗体为一个grid控件
        self.mainContent = QGridLayout()

        # 菜单栏
        self.setContentTop()

        # 设置文件浏览部分
        self.setContentBody()

        # 把创建的内容加入
        self.setLayout(self.mainContent)

    # 把主页面居中的方法
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)

    # 设置顶上一排东西
    def setContentTop(self):
        # 后退按钮
        self.backward = QToolButton()
        self.backward.setIcon(QIcon('icon/left.png'))

        # 前进按钮
        self.forward = QToolButton()
        self.forward.setIcon(QIcon('icon/right.png'))
        self.forward.setDisabled(True)

        # 返回上一级按钮
        self.upward = QToolButton()
        self.upward.setIcon(QIcon('icon/up.png'))

        # 地址栏
        self.makeAddressBar()

        # 执行框
        self.makeExecuteBar()

        # 加入按钮到窗体
        self.mainContent.addWidget(self.backward, 0, 0)
        self.mainContent.addWidget(self.forward, 0, 1)
        self.mainContent.addWidget(self.upward, 0, 2)

    # 设置文件浏览部分
    def setContentBody(self):
        # 主题为一个split控件
        self.fileView = QSplitter()

        # 设置左侧树
        self.leftTree = MyTreeView(self)

        # 设置右侧文件浏览
        self.rightWidget = FileWidget()

        # 加入左侧树和右侧文件浏览图标
        self.fileView.addWidget(self.leftTree)
        self.fileView.addWidget(self.rightWidget)

        # 把文件浏览部分加入主体
        self.mainContent.addWidget(self.fileView, 1, 0, 10, 10)

    # 地址栏
    def makeAddressBar(self):
        self.addressBar = QLineEdit()
        fileIcon = QAction(self.addressBar)
        fileIcon.setIcon(QIcon('icon/file.ico'))
        self.addressBar.addAction(fileIcon, QLineEdit.LeadingPosition)
        self.addressBar.setText('C:/')
        self.addressBar.setFont(QFont("Malgun Gothic"))
        self.mainContent.addWidget(self.addressBar, 0, 3, 1, 4)
        self.addressBar.setFocusPolicy(Qt.NoFocus)
        self.addressBar.setStyleSheet('''
            QLineEdit{
                border: 1px solid #d9d9d9;
                height:28px;
            }
        ''')

    # 设置执行框
    def makeExecuteBar(self):
        self.executeBar = QLineEdit()
        executeIcon = QAction(self.executeBar)
        executeIcon.setIcon(QIcon('icon/execute.png'))
        executeIcon.triggered.connect(self.execute)
        self.executeBar.addAction(executeIcon, QLineEdit.TrailingPosition)
        self.executeBar.setText('在此输入执行语句')
        # self.executeBar.editingFinished.connect(self.execute)  # 判断输入完成的方式太奇怪了
        self.executeBar.setFont(QFont("Malgun Gothic"))
        self.executeBar.setClearButtonEnabled(True)
        self.executeBar.setStyleSheet('''
            QLineEdit{
                border: 1px solid #d9d9d9;
                height: 28px;
                color: #85898c;
            }
        ''')
        self.mainContent.addWidget(self.executeBar, 0, 7, 1, 3)

    # 关闭动作
    def closeEvent(self, e):
        self.after_close_signal.emit()

    # 执行语句方法  待完成 -----------------------------------------------
    def execute(self):
        print(self.executeBar.text())


# 传入explorer类, 用path创建界面中的按钮
class MyTreeView(QTreeWidget):
    def __init__(self, master, path: str=''):
        super().__init__()
        self.path = path
        self.master = master
        self.setHeaderHidden(True)
        self.setColumnCount(1)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)
        self.setStyleSheet('''
            QTreeWidget{
                border: 0px;
                border-right:1px solid #c3c3c3;
                background-color:white;
            }
        ''')

        self.myComputer = QTreeWidgetItem(self)
        self.myComputer.setIcon(0, QIcon('icon/my_computer.ico'))
        self.myComputer.setText(0, '我的电脑')
        self.myComputer.setExpanded(True)
        # C盘
        self.disk_c = QTreeWidgetItem(self.myComputer)
        self.disk_c.setIcon(0, QIcon('icon/disk_c.ico'))
        self.disk_c.setText(0, '本地磁盘(C:)')
        # D盘
        self.disk_d = QTreeWidgetItem(self.myComputer)
        self.disk_d.setIcon(0, QIcon('icon/disk.ico'))
        self.disk_d.setText(0, '本地磁盘(D:)')

        self.clicked.connect(self.leftClicked)

    # 树状视图左键方法 待完成
    def leftClicked(self, val: object):
        print('clicked')
        # self.master.refresh()

    # 右键菜单
    def contextMenuEvent(self, e):
        contextMenu = QMenu(self)
        contextMenu.addAction(self.newFIle())
        contextMenu.addAction(self.newFolder())
        contextMenu.exec_(e.globalPos())

    # 新建文件
    def newFIle(self):
        item = QAction('&新建文件', self)
        item.triggered.connect(self.master.rightWidget.newFileFunction)
        # item.setMenu()
        return item

    def newFolder(self):
        item = QAction('&新建文件夹', self)
        item.triggered.connect(self.master.rightWidget.newFolderFunction)
        return item


class FileWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.buttonList = []
        self.body = fl.FlowLayout()
        self.setLayout(self.body)
        self.testFunction()

    # 新建文件菜单
    def newFile(self):
        item = QAction('&新建文件', self)
        item.triggered.connect(self.newFileFunction)
        return item

    # 新建文件夹
    def newFolder(self):
        item = QAction('&新建文件夹', self)
        item.triggered.connect(self.newFolderFunction)
        return item

    # 新建文件功能实现 待完成
    def newFileFunction(self):
        self.text_edit = te.TextEdit(self.buttonList)
        self.text_edit.after_close.connect(self.addButton)

    # 创建按钮
    def createButton(self, name: str='', text: str=''):
        button = MyButton(self)
        button.setText(name)
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button.setFont(QFont("Malgun Gothic", 10))
        button.setFixedSize(120, 150)
        button.setIconSize(QSize(120, 120))

        ext = os.path.splitext(name)[1]
        if ext == '.exe':
            button.setIcon(QIcon('icon/exe.ico'))
        elif ext == '.txt':
            button.setIcon(QIcon('icon./text.ico'))
        else:
            button.setIcon(QIcon('icon/empty.ico'))

        return button

    # 创建文件夹按钮
    def createFolderButton(self, name: str):
        button = MyButton(self, 'folder')
        button.setText(name)
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button.setFont(QFont("Malgun Gothic", 10))
        button.setFixedSize(120, 150)
        button.setIconSize(QSize(120, 120))
        button.setIcon(QIcon('icon/file3'))
        return button

    # 把按钮加入界面, 并存入ButtonList数组
    def addButton(self, mes: list):
        btn = self.createButton(mes[0], mes[1])
        self.buttonList.append(btn)
        self.body.addWidget(btn)

    # 左键
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            for i in self.buttonList:
                i.setStyleSheet('''
                QToolButton{
                    background-color:white;
                }
                ''')
        else:
            contextMenu = QMenu(self)
            contextMenu.addAction(self.newFile())
            contextMenu.addAction(self.newFolder())
            contextMenu.exec_(e.globalPos())

    # 新建文件夹 ---------------------------------------------------
    def newFolderFunction(self):
        text, ok = QInputDialog.getText(self, '新的文件夹', '输入文件夹名:')
        for i in self.buttonList:
            if i.text() == text:
                msgBox = QMessageBox(QMessageBox.Warning, "警告!", '文件夹名重复!', QMessageBox.NoButton, self)
                msgBox.addButton("确认", QMessageBox.AcceptRole)
                msgBox.exec_()
                return
        if ok and len(text) != 0:
            btn = self.createFolderButton(text)
            self.buttonList.append(btn)
            self.body.addWidget(btn)

    def testFunction(self):
        self.addButton(['a.exe', 'sadadsad'])
        self.addButton(['b.txt', 'ddddddddd'])


class MyButton(QToolButton):
    def __init__(self, master, buttonType: str='file'):
        super().__init__()
        self.master = master
        self.buttonType = buttonType
        self.setStyleSheet('''
            QToolButton:hover{
                background-color: #e5f3ff;
            }
        ''')

    # 双击
    def mouseDoubleClickEvent(self, e):
        if self.buttonType == 'file':
            self.editMenuFunction()
        # 文件夹双击方法 未完成----------------------------
        else:
            print('fold')

    # 单击
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.leftClicked()
        else:
            self.buttonContext()

    # 文件右键菜单
    def buttonContext(self):
        print(self.buttonType)
        menu = QMenu()
        if self.buttonType == 'file':
            menu.addAction(self.editMenu())
            menu.addAction(self.cutMenu())
            menu.addAction(self.copyMenu())
            menu.addSeparator()
            menu.addAction(self.deleteMenu())
            menu.addAction(self.renameMenu())
            menu.addSeparator()
            menu.addAction(self.attributeMenu())
        else:
            menu.addAction(self.editMenu())
            print('foldRightClick')
        menu.exec_(QCursor.pos())

    # 左键选中
    def leftClicked(self):
        for i in self.master.buttonList:
            i.setStyleSheet('''
            QToolButton{
                background-color:white;
                border: 1px solid white;
            }
            QToolButton:hover{
                background-color: #e5f3ff;
            }
            ''')
        self.setStyleSheet('''
            QToolButton{
                background-color:#e5f3ff;
                border: 1px solid #99d1ff;
            }
            QToolButton:hover{
                background-color: #e5f3ff;
            }
        ''')

    # 以下功能全部没有做完 ########################################
    # 编辑
    def editMenu(self):
        item = QAction('&修改(E)', self)
        item.triggered.connect(self.editMenuFunction)
        return item

    def editMenuFunction(self):
        content = 'asddsad'  # 这里应该是一个获取文本内容的方法 未完成
        self.text_edit = te.TextEdit(self.master.buttonList, [self.text(), content])
        # self.text_edit.after_close.connect() # 这里是一个保存文件的方法 未完成

    # 剪切
    def cutMenu(self):
        item = QAction('&剪切(X)', self)
        return item

    # 复制
    def copyMenu(self):
        item = QAction('&复制(C)', self)
        return item

    # 删除
    def deleteMenu(self):
        item = QAction('&删除(D)', self)
        return item

    # 重命名
    def renameMenu(self):
        item = QAction('&重命名(M)', self)
        return item

    # 属性
    def attributeMenu(self):
        item = QAction('&属性(R)', self)
        return item


def main():
    app = QApplication(sys.argv)
    ex = Explorer()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
