import sys
from PyQt5 import QtCore 
from PyQt5 import QtGui, QtWidgets, uic

from PyQt5.QtWidgets import *

# from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QMainWindow, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QPalette, QPixmap
from PyQt5.QtCore import Qt, QPoint, QSize, pyqtSignal, QObject

import numpy as np
from matplotlib.image import imread
from skimage.transform import resize

import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# import qimage2ndarray

# Load UI Designer File
qtCreatorFile = "MNIST_demo.ui"
Ui_MainWindow, QMainWindow = uic.loadUiType(qtCreatorFile)

# All the widget names are: widget_DrawNumber, widget_ConvertDrawToInput, widget_unrolledinputvector
# widget_ConvLayer, widget_OutputFeatureVectors, widget_FClayer, widget_PlotClassificationResult

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

    def addplot(self,fig):
        self.canvas = FigureCanvas(fig)
        self.canvas.setParent(self.widget_ConvLayer)
        self.canvas.draw()
 
if __name__ == '__main__':
    import sys
    from PyQt5 import QtGui
 
    fig1 = Figure(figsize=(4,3))
    ax1f1 = fig1.add_subplot(111)
    ax1f1.plot(np.random.rand(5))

    app = QApplication(sys.argv)
    main = Main()
    main.addplot(fig1)
    main.show()
    sys.exit(app.exec_())