import sys
from PyQt5.QtWidgets import (QWidget, QToolButton, QApplication,
                             QDesktopWidget, QGridLayout, QSplitter,
                             QTreeWidget, QTreeWidgetItem, QMenu, QAction,
                             QLineEdit, QInputDialog, QMessageBox,
                             QRadioButton, QCheckBox,
                             QPushButton)
from PyQt5.QtGui import QIcon, QFont, QCursor
from PyQt5.QtCore import QSize, Qt, pyqtSignal

# from module import floatlayout as fl
# from module import text_edit as te
import floatlayout as fl
import text_edit as te
import disk as mydisk
import orders


class Explorer(QWidget):
    after_close_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
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
        self.backward.setDisabled(True)

        # 前进按钮
        self.forward = QToolButton()
        self.forward.setIcon(QIcon('icon/right.png'))
        self.forward.setDisabled(True)

        # 返回上一级按钮
        self.upward = QToolButton()
        self.upward.setIcon(QIcon('icon/up.png'))
        self.upward.clicked.connect(self.upwardFunction)

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
        self.rightWidget = FileWidget(self)

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

    # 返回上级方法
    def upwardFunction(self):
        path = mydisk.cut_path(self.addressBar.text())[0]
        self.addressBar.setText(path)
        self.rightWidget.path = path
        self.rightWidget.refresh()

    # 关闭动作
    def closeEvent(self, e):
        self.after_close_signal.emit()

    # 执行语句方法
    def execute(self):
        order = self.rightWidget.path + '>' + self.executeBar.text()
        ans = orders.parser(order)
        if ans[0] == 'path':
            self.rightWidget.path = ans[1]
        self.rightWidget.refresh()
        self.leftTree.refresh()


# 传入explorer类, 用path创建界面中的按钮
class MyTreeView(QTreeWidget):
    def __init__(self, master):
        super().__init__()
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
        self.disk_c.path = 'C:/'

        # D盘
        self.disk_d = QTreeWidgetItem(self.myComputer)
        self.disk_d.setIcon(0, QIcon('icon/disk.ico'))
        self.disk_d.setText(0, '本地磁盘(D:)')
        self.disk_d.path = 'D:/'
        self.clicked.connect(self.leftClicked)

        self.refresh()

    # 树状视图左键方法
    def leftClicked(self, val: object):
        itemNow = self.currentItem()
        if itemNow.text(0) == '我的电脑':
            return
        if itemNow.path in ('C:/', 'D:/'):
            self.refresh()
        self.master.rightWidget.path = itemNow.path
        self.master.rightWidget.refresh()

    # 右键菜单
    def contextMenuEvent(self, e):
        contextMenu = QMenu(self)
        contextMenu.addAction(self.newFile())
        contextMenu.addAction(self.newFolder())
        contextMenu.exec_(e.globalPos())

    # 新建文件
    def newFile(self):
        item = QAction('&新建文件', self)
        item.triggered.connect(self.master.rightWidget.newFileFunction)
        # item.setMenu()
        return item

    # 新建文件夹
    def newFolder(self):
        item = QAction('&新建文件夹', self)
        item.triggered.connect(self.master.rightWidget.newFolderFunction)
        return item

    # 把子元素添加
    def makeChildren(self, parent: QTreeWidgetItem):
        children = mydisk.list_dir(parent.path)
        for child in children:
            if child['attribute'] == 8:
                item = QTreeWidgetItem()
                item.setText(0, child['name'])
                item.path = child['path']
                item.setIcon(0, QIcon('icon/file.ico'))
                parent.addChild(item)
                self.makeChildren(item)

    # 左侧树更新
    def refresh(self):
        '''
        只有添加，删除，修改, 移动, 复制会触发此操作
        '''
        for i in range(self.disk_c.childCount()):
            self.disk_c.removeChild(self.disk_c.child(0))

        self.makeChildren(self.disk_c)

        for i in range(self.disk_d.childCount()):
            self.disk_d.removeChild(self.disk_d.child(0))

        self.makeChildren(self.disk_d)


class FileWidget(QWidget):
    def __init__(self, master):
        super().__init__()
        self.path = 'C:/'
        self.master = master
        self.buttonList = []
        self.visited = ['C:/']
        self.now = 0
        self.master.backward.clicked.connect(self.back)
        self.master.forward.clicked.connect(self.forward)
        self.clipboard = None
        self.body = fl.FlowLayout()
        self.setLayout(self.body)
        self.refresh()

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

    # 粘贴
    def pasetItem(self):
        item = QAction('&粘贴', self)
        item.triggered.connect(self.pasetFunction)
        return item

    # 弹出文本框
    def newFileFunction(self):
        self.text_edit = te.TextEdit(self.buttonList)
        self.text_edit.after_close.connect(self.createFileOnDisk)

    # 真正再磁盘上建立文件
    def createFileOnDisk(self, info: dict):
        info['path'] = mydisk.format_path(self.path)
        mydisk.create_file(info)
        self.refresh()
        self.master.leftTree.refresh()

    # 创建按钮
    def createButton(self, info: dict):
        button = MyButton(self, info)
        button.setText(mydisk.join_name(info['name'], info['ext']))
        button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        button.setFont(QFont("Malgun Gothic", 10))
        button.setFixedSize(120, 150)
        button.setIconSize(QSize(120, 120))

        ext = info['ext']
        if ext == 'ex':
            button.setIcon(QIcon('icon/exe.ico'))
        elif ext == 'tx':
            button.setIcon(QIcon('icon./text.ico'))
        elif info['attribute'] == 8:
            button.setIcon(QIcon('icon/file3'))
        else:
            button.setIcon(QIcon('icon/empty.ico'))

        return button

    # 把按钮加入界面, 并存入ButtonList数组
    def addButton(self, info: dict):
        '''
        传入新文件信息 {
            'name': str,
            'ext': str,
            'attribute': int,
            'length': int,
            'text': str
        }
        '''
        btn = self.createButton(info)
        self.buttonList.append(btn)
        self.body.addWidget(btn)

    # 按键
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            for i in self.buttonList:
                i.setStyleSheet('''
                QToolButton{
                    background-color:white;
                }
                QToolButton:hover{
                    background-color: #e5f3ff;
                }
                ''')
        else:
            contextMenu = QMenu(self)
            contextMenu.addAction(self.refreshAll())
            contextMenu.addSeparator()
            contextMenu.addAction(self.newFile())
            contextMenu.addAction(self.newFolder())
            paset = self.pasetItem()
            if self.clipboard is None:
                paset.setDisabled(True)
            contextMenu.addAction(paset)
            contextMenu.exec_(e.globalPos())

    # 新建文件夹
    def newFolderFunction(self):
        text, ok = QInputDialog.getText(self, '新的文件夹', '输入文件夹名:')
        if not mydisk.is_dir_name(text):
            self.errorBox('文件夹名不合法!')
            return
        for i in self.buttonList:
            if i.text() == text:
                self.errorBox('文件夹名重复!')
                return
        if ok and len(text) != 0:
            mydisk.create_dir(mydisk.format_path(self.path)+'/'+text)
            self.refresh()
            self.master.leftTree.refresh()

    # 粘贴
    def pasetFunction(self):
        # print('paset', self.clipboard)
        if self.path.find(self.clipboard['path']) == 0:
            self.errorBox('目标文件夹存在于原文件夹内')
            return
        if self.clipboard['operation'] == 'copy':
            mydisk.copy(self.clipboard['path'], self.path)
        else:
            mydisk.move(self.clipboard['path'], self.path)
        self.clipboard = None
        self.refresh()
        self.master.leftTree.refresh()

    # 后退
    def back(self):
        # 后退之后必然可以前进
        self.master.forward.setDisabled(False)
        self.now -= 1
        self.path = self.visited[self.now]
        self.refresh(1)
        if self.now <= 0:
            # 已经不能再后退
            self.master.backward.setDisabled(True)
            return

    # 前进
    def forward(self):
        # 前进之后必然可以后退
        self.master.backward.setDisabled(False)
        self.now += 1
        self.path = self.visited[self.now]
        self.refresh(2)
        if self.now == len(self.visited) - 1:
            # 已经不能再前进
            self.master.forward.setDisabled(True)
            return

    # 全部刷新
    def refreshAll(self):
        item = QAction('刷新', self)
        item.triggered.connect(self.refreshAllFunction)
        return item

    # 全部刷新方法
    def refreshAllFunction(self):
        self.refresh()
        self.master.leftTree.refresh()

    # 刷新
    def refresh(self, op: int = 0):
        if self.path in ('C:', 'c:', 'd:', 'D:'):
            self.path += '/'
        # 普通访问路径
        if op == 0 and self.path != self.visited[self.now]:
            self.now += 1
            self.visited = self.visited[:self.now]
            self.visited.append(self.path)
            # 普通访问路径会导致前进按钮失效
            self.master.forward.setDisabled(True)
            # 已经有可以后退的路径
            if self.now > 0:
                self.master.backward.setDisabled(False)
        self.master.addressBar.setText(self.path)
        for btn in self.buttonList:
            btn.deleteLater()
        self.buttonList = []
        self.file_list = mydisk.list_dir(self.path)
        # print(self.file_list)
        for f in self.file_list:
            self.addButton(f)
        # print(self.now, self.visited)

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


class MyButton(QToolButton):
    def __init__(self, master, info: dict):
        super().__init__()
        self.master = master
        self.info = info
        self.buttonType = ''
        self.isFocused = False
        if info['attribute'] == 8:
            self.buttonType = 'folder'
        elif info['ext'] == 'tx':
            self.buttonType = 'file'
        elif info['ext'] == 'ex':
            self.buttonType = 'exe'
        self.setMyStyle()

    # TODO 双击
    def mouseDoubleClickEvent(self, e):
        # print(self.buttonType, self.info)
        # TODO 可执行文件双击方法, 运行程序
        if self.buttonType == 'exe':
            # print('EXECUTE', self.info['name']+'.'+self.info['ext'])
            return
        # 文件夹双击方法, 进入此文件夹
        if self.buttonType == 'folder':
            if mydisk.get_block(self.info['path'])[0] == -1:
                return
            self.master.path = self.info['path']
            self.master.refresh()
            return
        # 文件双击方法，打开文件
        # print('Edit', self.info['path'])
        self.editMenuDialog()

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
        if self.buttonType != 'folder':
            menu.addAction(self.editMenu())
            menu.addAction(self.cutMenu())
            menu.addAction(self.copyMenu())
            menu.addSeparator()
            menu.addAction(self.deleteMenu())
            menu.addSeparator()
            menu.addAction(self.attributeMenu())
        else:
            menu.addAction(self.cutMenu())
            menu.addAction(self.copyMenu())
            menu.addAction(self.renameMenu())
            menu.addAction(self.deleteMenu())
        menu.exec_(QCursor.pos())

    # 编辑
    def editMenu(self):
        item = QAction('&编辑(E)', self)
        item.triggered.connect(self.editMenuDialog)
        return item

    # 弹出编辑框
    def editMenuDialog(self):
        _file = mydisk.open_file(self.info['path'])
        if not _file:
            return
        self.text_edit = te.TextEdit(
            self.master.buttonList,
            [mydisk.join_name(_file['name'], _file['ext']), _file['text'], self.info['attribute']],
            'edit'
        )
        self.text_edit.after_close.connect(self.editMenuFunction)

    # 把编辑完的结果写入磁盘
    def editMenuFunction(self, info: dict):
        mydisk.modify_file(self.info['path'], info)
        self.master.refresh()
        self.master.master.leftTree.refresh()

    # 剪切
    def cutMenu(self):
        item = QAction('&剪切(X)', self)
        item.triggered.connect(self.cutFunction)
        return item

    # 复制
    def copyMenu(self):
        item = QAction('&复制(C)', self)
        # item.setShortcut(QKeySequence(QKeySequence.Copy))
        # item.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        item.triggered.connect(self.copyFunction)
        return item

    # 复制方法
    def copyFunction(self):
        self.info['operation'] = 'copy'
        self.master.clipboard = self.info

    # 剪切方法
    def cutFunction(self):
        self.info['operation'] = 'cut'
        self.master.clipboard = self.info

    # 删除
    def deleteMenu(self):
        item = QAction('&删除(D)', self)
        item.triggered.connect(self.deleteFunction)
        return item

    # 文件夹重命名
    def renameMenu(self):
        item = QAction('&重命名(M)', self)
        item.triggered.connect(self.renameFunction)
        return item

    # 给文件夹重命名的方法
    def renameFunction(self):
        text, ok = QInputDialog.getText(self, '重命名文件夹', '输入文件夹名:')
        if not mydisk.is_dir_name(text):
            self.errorBox('文件夹名不合法!')
            return
        for i in self.master.buttonList:
            if i.text() == text:
                self.errorBox('文件夹名重复!')
                return
        if ok and len(text) != 0:
            mydisk.modify_dir(self.info['path'], text)
            self.master.refresh()
            self.master.master.leftTree.refresh()

    # 属性
    def attributeMenu(self):
        item = QAction('&属性(R)', self)
        item.triggered.connect(self.attributeDialog)
        return item

    # 属性对话框
    def attributeDialog(self):
        self.attr = AttributeBox(self.info['attribute'])
        self.attr.show()
        self.attr.after_close.connect(self.attributeChange)

    # 修改磁盘中的数据
    def attributeChange(self, attr: int):
        print(mydisk.change(self.info['path'], attr))
        self.master.refresh()

    # 左键选中
    def leftClicked(self):
        for i in self.master.buttonList:
            i.isFocused = False
            i.setStyleSheet('''
            QToolButton{
                background-color:white;
                border: 1px solid white;
            }
            QToolButton:hover{
                background-color: #e5f3ff;
            }
            ''')
        self.isFocused = True
        self.setStyleSheet('''
            QToolButton{
                background-color:#e5f3ff;
                border: 1px solid #99d1ff;
            }
            QToolButton:hover{
                background-color: #e5f3ff;
            }
        ''')

    # 删除方法
    def deleteFunction(self):
        if self.info['attribute'] == 8:
            mydisk.delete_dir(self.info['path'])
        else:
            # 不能删除系统文件
            if self.info['attribute'] & 2 == 0:
                mydisk.delete_file(self.info['path'])
            else:
                self.errorBox('系统文件不能删除！')
        self.master.refresh()
        self.master.master.leftTree.refresh()

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
            QToolButton:hover{
                background-color: #e5f3ff;
            }
        ''')


class AttributeBox(QWidget):

    after_close = pyqtSignal(int)

    def __init__(self, attribute: int = 0):
        super().__init__()

        self.readOnlyBox = QCheckBox('只读')
        self.systemBox = QRadioButton('系统文件')
        self.fileBox = QRadioButton('普通文件')

        self.confimButton = QPushButton()
        self.confimButton.setText('确认')
        self.confimButton.clicked.connect(self.confimFunction)

        self.cancelButton = QPushButton('取消')
        self.cancelButton.setText('取消')
        self.cancelButton.clicked.connect(self.close)

        ly = QGridLayout()
        ly.addWidget(self.readOnlyBox, 0, 0)
        ly.addWidget(self.systemBox, 0, 1)
        ly.addWidget(self.fileBox, 0, 2)
        ly.addWidget(self.confimButton, 1, 1)
        ly.addWidget(self.cancelButton, 1, 2)

        self.setLayout(ly)
        if attribute & 1 != 0:
            self.readOnlyBox.setChecked(True)
        if attribute & 2 != 0:
            self.systemBox.setChecked(True)
        if attribute & 4 != 0:
            self.fileBox.setChecked(True)

    def confimFunction(self):
        if self.systemBox.isChecked():
            ans = 2
        else:
            ans = 4
        if self.readOnlyBox.isChecked():
            ans += 1
        self.after_close.emit(ans)
        self.close()


def main():
    app = QApplication(sys.argv)
    ex = Explorer()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
