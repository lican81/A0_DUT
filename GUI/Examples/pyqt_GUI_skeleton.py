# see https://www.pythonforengineers.com/your-first-gui-app-with-python-and-pyqt/

import sys
# from PyQt4 import QtCore, QtGui, uic
# from PyQt5.QtWidgets import QMainWindow, QApplication
# from PyQt5 import uic
from qtpy.QtWidgets import QMainWindow, QApplication
from qtpy import uic

qtCreatorFile = "sales_tax_calc_tutorial.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QMainWindow):
    # def __init__(self):
    #    QtGui.QMainWindow.__init__(self)
    #    Ui_MainWindow.__init__(self)
    #    self.setupUi(self)
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
sys.exit(app.exec_())