# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'designer.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(770, 437)
        self.wdt_drawing = QtWidgets.QWidget(Dialog)
        self.wdt_drawing.setGeometry(QtCore.QRect(70, 90, 271, 241))
        self.wdt_drawing.setObjectName("wdt_drawing")
        self.btn_update = QtWidgets.QPushButton(Dialog)
        self.btn_update.setGeometry(QtCore.QRect(40, 360, 113, 32))
        self.btn_update.setObjectName("btn_update")
        self.mpl_img = QtWidgets.QWidget(Dialog)
        self.mpl_img.setGeometry(QtCore.QRect(400, 90, 291, 241))
        self.mpl_img.setObjectName("mpl_img")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "DPE Live Demo"))
        self.btn_update.setText(_translate("Dialog", "Update"))
