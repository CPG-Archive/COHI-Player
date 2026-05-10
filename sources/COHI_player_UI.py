import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication
from PyQt5.QtCore import Qt


class Ui_MainWindow(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(480, 320)
        MainWindow.setMaximumSize(QtCore.QSize(480, 320))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        MainWindow.setPalette(palette)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        MainWindow.setFont(font)
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.title = QtWidgets.QLabel(self.centralwidget)
        self.title.setGeometry(QtCore.QRect(17, 9, 445, 60))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.title.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(38)
        font.setBold(True)
        font.setWeight(75)
        self.title.setFont(font)
        self.title.setObjectName("title")

        self.playing_wav = QtWidgets.QLabel(self.centralwidget)
        self.playing_wav.setGeometry(QtCore.QRect(20, 78, 441, 20))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.playing_wav.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(75)
        self.playing_wav.setFont(font)
        self.playing_wav.setObjectName("playing_wav")


        self.play_time = QtWidgets.QLabel(self.centralwidget)
        self.play_time.setGeometry(QtCore.QRect(20, 158, 220, 14))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.play_time.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(75)
        self.play_time.setFont(font)
        self.play_time.setObjectName("play_time")

        self.play_total = QtWidgets.QLabel(self.centralwidget)
        self.play_total.setGeometry(QtCore.QRect(240, 158, 221, 14))
        self.play_total.setAlignment(Qt.AlignRight)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.play_total.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(75)
        self.play_total.setFont(font)
        self.play_total.setObjectName("play_total")


        self.ScrollBar_playtime = QtWidgets.QScrollBar(self.centralwidget)
        self.ScrollBar_playtime.setFont(font)
        self.ScrollBar_playtime.setGeometry(10, 115, 460, 30)     #QtCore.QRect(00, 00, 220, 1))
        self.ScrollBar_playtime.setMinimum(0)
        self.ScrollBar_playtime.setMaximum(1000)
        self.ScrollBar_playtime.setPageStep(1)
        self.ScrollBar_playtime.setProperty("value", 0)
        self.ScrollBar_playtime.setOrientation(QtCore.Qt.Horizontal)
        self.ScrollBar_playtime.setObjectName("ScrollBar_playtime")


        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(-10, 170, 501, 110))
        self.widget.setObjectName("widget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")


        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(20, -1, 20, -1)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.pushButton_prev = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_prev.setFont(font)
        self.pushButton_prev.setObjectName("pushButton_prev")
        self.pushButton_prev.setShortcut('p')
        #self.pushButton_prev.pressed.connect(self.previous_pressed)
        self.horizontalLayout.addWidget(self.pushButton_prev)

        self.pushButton_restart = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_restart.setFont(font)
        self.pushButton_restart.setObjectName("pushButton_restart")
        #self.pushButton_restart.setShortcut('r')
        #self.pushButton_restart.pressed.connect(self.restart_pressed)
        self.horizontalLayout.addWidget(self.pushButton_restart)

        self.pushButton_next = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_next.setFont(font)
        self.pushButton_next.setObjectName("pushButton_next")
        #self.pushButton_next.setShortcut('n')
        #self.pushButton_next.pressed.connect(self.next_pressed)
        self.horizontalLayout.addWidget(self.pushButton_next)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(20, -1, 20, -1)
        self.horizontalLayout_2.setSpacing(20)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.pushButton_pause = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_pause.setFont(font)
        self.pushButton_pause.setObjectName("pushButton_pause")
        #self.pushButton_pause.setShortcut('x')
        #self.pushButton_pause.pressed.connect(self.pause_pressed)
        self.horizontalLayout_2.addWidget(self.pushButton_pause)

        self.pushButton_cont = QtWidgets.QPushButton(self.widget)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_cont.setFont(font)
        self.pushButton_cont.setObjectName("pushButton_cont")
        #self.pushButton_cont.setShortcut('c')
        #self.pushButton_cont.pressed.connect(self.continue_pressed)
        self.horizontalLayout_2.addWidget(self.pushButton_cont)

        self.pushButton_shutdown = QtWidgets.QPushButton(self.widget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        self.pushButton_shutdown.setPalette(palette)
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_shutdown.setFont(font)
        self.pushButton_shutdown.setFlat(False)
        self.pushButton_shutdown.setObjectName("pushButton_shutdown")
        #self.pushButton_shutdown.setShortcut('S')
        #self.pushButton_shutdown.pressed.connect(self.shutdown_pressed)
        self.horizontalLayout_2.addWidget(self.pushButton_shutdown)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)



    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.title.setText(_translate("MainWindow", "COHI-Player mini"))
        self.playing_wav.setText(_translate("MainWindow", "playing WAV file: "))
        self.play_time.setText(_translate("MainWindow", "actual playing time: "))
        self.play_total.setText(_translate("MainWindow", "total playing time: "))

        self.pushButton_prev.setText(_translate("MainWindow", "Previous WAV"))
        self.pushButton_restart.setText(_translate("MainWindow", "Restart"))
        self.pushButton_next.setText(_translate("MainWindow", "Next WAV"))
        self.pushButton_pause.setText(_translate("MainWindow", "Pause"))
        self.pushButton_cont.setText(_translate("MainWindow", "Continue"))
        self.pushButton_shutdown.setText(_translate("MainWindow", "Shutdown"))


class Color(QWidget):

    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class Window(QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setupUi(self)


if __name__ == "__main__":

    app = QApplication(sys.argv)

    win = Window()

    win.show()



    sys.exit(app.exec())