import sys
from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout
from PyQt5.QtGui import QPainter, QColor, QBrush


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(700, 400)
        self.setStyleSheet('''
            *{
                background-color: white
            }
        ''')
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawRectangles(qp)
        qp.end()

    def drawRectangles(self, qp):
        col = QColor(0, 0, 0)
        col.setNamedColor("#d4d4d4")
        qp.setPen(col)

        qp.setBrush(QColor(200, 0, 0))

        for i in range(20):
            for j in range(15):
                qp.drawRect(35*i+5, 25*j+5, 30, 20)


if __name__ == "__main__":
    a = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    print(len(a))
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
