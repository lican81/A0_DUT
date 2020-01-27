# See here : https://www.learnpyqt.com/apps/simple-sales-tax-calculator/

import sys
# from PyQt4 import QtCore, QtGui, uic
# from PyQt5.QtWidgets import QMainWindow, QApplication
# from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5 import uic, QtCore, QtGui
import os

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# ui_path = os.path.dirname(os.path.abspath(__file__))
# qtCreatorFile = uic.loadUiType(os.path.join(ui_path, "sales_tax_calc_tutorial.ui"))[0]  # Enter file here.

ui_path = os.path.dirname(os.path.abspath(__file__))
print(ui_path)
# qtCreatorFile = uic.loadUiType(os.path.join(ui_path, "sales_tax_calc_tutorial.ui"))[0]
qtCreatorFile = "C:\\microchip\\harmony\\v2_03b\\apps\\mTCAM_DUT\\GUI\\sales_tax_calc_tutorial.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QMainWindow):
    def __init__(self):
        # QtGui.QMainWindow.__init__(self)
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.calc_tax_button.clicked.connect(self.CalculateTax)
    
    def CalculateTax(self):
        price = int(self.ui.price_box.toPlainText())
        tax = (self.ui.tax_rate.value())
        total_price = price = ((tax/100)*price)
        total_price_string = "The total sprice with tax is: " + str(total_price)
        self.ui.results_window.setText(total_price_string)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
sys.exit(app.exec_())

