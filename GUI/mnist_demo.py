

from PyQt5 import QtCore
from PyQt5 import QtGui, QtWidgets, uic
import qimage2ndarray

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import numpy as np
from skimage.transform import resize

qtCreatorFile = "MNIST_demo.ui"
Ui_MainWindow, QMainWindow = uic.loadUiType(qtCreatorFile)


class DrawingWidget(QtWidgets.QWidget):
    newPoint = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.path = QtGui.QPainterPath()
        self.pen = QtGui.QPen(QtCore.Qt.black, 20, QtCore.Qt.SolidLine)

        self.clear()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(self.pen)

        painter.drawPath(self.path)

    def mousePressEvent(self, event):
        self.path.moveTo(event.pos())
        self.update()

    def mouseMoveEvent(self, event):
        self.path.lineTo(event.pos())
        self.newPoint.emit(event.pos())
        self.update()

    def sizeHint(self):
        return QtCore.QSize(280, 280)

    def clear(self):
        self.path.clear()
        self.path.addRect(0, 0, 280, 280)
        self.update()

    # def save(self):
    #     pixmap = QtGui.QPixmap(280, 280)
    #     pixmap.fill(Qt.white)

    #     painter = QtGui.QPainter(pixmap)
    #     painter.setRenderHint(QtGui.QPainter.Antialiasing)
    #     painter.setPen(self.pen)

    #     painter.drawPath(self.path)
    #     painter.end()
    #     pixmap.save("path.png")

    #     self.clear()

    def toArray(self):
        pixmap = QtGui.QPixmap(280, 280)
        pixmap.fill(QtCore.Qt.white)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(self.pen)

        painter.drawPath(self.path)
        painter.end()

        arr = qimage2ndarray.rgb_view(pixmap.toImage())
        return arr


class MnistMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(MnistMainWindow, self).__init__()
        self.setupUi(self)

        self.drawing = DrawingWidget(parent=self.drawing_digit)
        self.btn_clear.clicked.connect(self.drawing.clear)

        # Setup the digit panel
        self.fig_digit = Figure(figsize=(3,3))
        # self.ax_digit = self.fig_digit.add_subplot(111)
        self.ax_digit = self.fig_digit.add_axes((0,0,1,1))
        self.ax_digit.get_xaxis().set_visible(False)
        self.ax_digit.get_yaxis().set_visible(False)

        self.canvas_digit = FigureCanvas(self.fig_digit)
        self.canvas_digit.setParent(self.mpl_digit)
        
        self.btn_classify.clicked.connect(self.classify)


        

    def classify(self):
        img = self.drawing.toArray()
        img = self._pre_process(img)
        
        self.ax_digit.imshow( img )
        self.canvas_digit.draw()

        img_in = img[..., np.newaxis]

    def _pre_process(img):
        padding = 10

        img = np.mean(img, axis=2).astype(np.float) / 255
        img = img[padding:-padding, padding:-padding]

        img = resize(img, (24, 24), anti_aliasing=True)
        img = 1-img

        return img


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '..')

    from lib_data import *
    from lib_nn_dpe import NN_dpe
    from dpe import DPE

    app = QtWidgets.QApplication(sys.argv)
    main = MnistMainWindow()


    main.show()
    sys.exit(app.exec_())