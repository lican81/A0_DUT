# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MNIST_demo.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1503, 913)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.canvas_digit = QtWidgets.QWidget(self.centralwidget)
        self.canvas_digit.setGeometry(QtCore.QRect(20, 170, 251, 251))
        self.canvas_digit.setObjectName("canvas_digit")
        self.mpl_fc_in = QtWidgets.QWidget(self.centralwidget)
        self.mpl_fc_in.setGeometry(QtCore.QRect(240, 570, 181, 181))
        self.mpl_fc_in.setObjectName("mpl_fc_in")
        self.mpl_conv_input = QtWidgets.QWidget(self.centralwidget)
        self.mpl_conv_input.setGeometry(QtCore.QRect(320, 120, 91, 371))
        self.mpl_conv_input.setObjectName("mpl_conv_input")
        self.btn_classify = QtWidgets.QPushButton(self.centralwidget)
        self.btn_classify.setGeometry(QtCore.QRect(10, 440, 271, 71))
        self.btn_classify.setObjectName("btn_classify")
        self.mpl_conv_weight = QtWidgets.QWidget(self.centralwidget)
        self.mpl_conv_weight.setGeometry(QtCore.QRect(440, 180, 201, 201))
        self.mpl_conv_weight.setObjectName("mpl_conv_weight")
        self.mpl_conv_out = QtWidgets.QWidget(self.centralwidget)
        self.mpl_conv_out.setGeometry(QtCore.QRect(670, 130, 671, 301))
        self.mpl_conv_out.setObjectName("mpl_conv_out")
        self.mpl_fc_weight = QtWidgets.QWidget(self.centralwidget)
        self.mpl_fc_weight.setGeometry(QtCore.QRect(440, 510, 201, 311))
        self.mpl_fc_weight.setObjectName("mpl_fc_weight")
        self.mpl_fc_out = QtWidgets.QWidget(self.centralwidget)
        self.mpl_fc_out.setGeometry(QtCore.QRect(670, 510, 671, 311))
        self.mpl_fc_out.setObjectName("mpl_fc_out")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(80, 140, 131, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(320, 60, 101, 31))
        self.label_2.setObjectName("label_2")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(920, 60, 171, 31))
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(460, 460, 171, 31))
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(930, 470, 201, 21))
        self.label_6.setObjectName("label_6")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(470, 130, 151, 31))
        self.label_3.setObjectName("label_3")
        self.btn_read = QtWidgets.QPushButton(self.centralwidget)
        self.btn_read.setGeometry(QtCore.QRect(460, 830, 141, 61))
        self.btn_read.setObjectName("btn_read")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_classify.setText(_translate("MainWindow", "Classify with Analog DPE Engine"))
        self.label.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">Draw a number</span></p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">Input Vector</span></p></body></html>"))
        self.label_4.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">Output Feature Vectors</span></p></body></html>"))
        self.label_5.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">Fully Connected Layer</span></p></body></html>"))
        self.label_6.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-weight:600;\">Classification Result</span></p></body></html>"))
        self.label_3.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">Convolutional Layer</span></p></body></html>"))
        self.btn_read.setText(_translate("MainWindow", "Read conductance"))
