import sys
from PyQt5 import QtCore 
from PyQt5 import QtGui, QtWidgets

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

import qimage2ndarray

class Drawer(QWidget):
    newPoint = pyqtSignal(QPoint)
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.path = QPainterPath()  
        self.pen = QPen(Qt.black, 10, Qt.SolidLine)

        self.clear()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint( QPainter.Antialiasing );

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
        return QSize(280, 280)

    def clear(self):
       
        self.path.clear()
        self.path.addRect(0,0, 280, 280)
        self.update()
        
    def save(self):
        pixmap = QPixmap( 280, 280 )
        pixmap.fill( Qt.white )

        painter = QPainter( pixmap )
        painter.setRenderHint( QPainter.Antialiasing )
        painter.setPen(self.pen)

        painter.drawPath( self.path )
        painter.end()
        pixmap.save( "path.png" )

        self.clear()

    def toArray(self):
        pixmap = QPixmap( 280, 280 )
        pixmap.fill( Qt.white )

        painter = QPainter( pixmap )
        painter.setRenderHint( QPainter.Antialiasing );
        painter.setPen(self.pen)

        painter.drawPath( self.path )
        painter.end()

        arr = qimage2ndarray.rgb_view( pixmap.toImage() )
        return arr

class MatPFC(FigureCanvas):
    def __init__(self, parent=None):
        self.__fig__ = Figure()
        self.axes = self.__fig__.add_subplot(111)
        FigureCanvas.__init__(self, self.__fig__)

        self.setParent(parent)


    def replot(self, img):
        self.axes.cla()
        # self.axes.plot(range(10), np.random.random(10), '.-', alpha=0.75)
        # img = imread('path.png')
        img = np.mean(img, axis=2).astype(np.float) / 255

        padding = 5
        img[np.r_[:padding, img.shape[0]-padding:img.shape[0]]] = 1
        img[:, np.r_[:padding, img.shape[1]-padding:img.shape[1]]] = 1

        img = resize(img, (28,28), anti_aliasing=True)
        im = self.axes.imshow(img, clim=(0,1))
        # self.__fig__.colorbar(im, ax=self.axes)
        
        self.draw()

class MyWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setLayout(QVBoxLayout())
        label = QLabel(self)
        self.drawer = Drawer(self)
        self.drawer.newPoint.connect(lambda p: label.setText('Coordinates: ( %d : %d )' % (p.x(), p.y())))

        btn1 = QPushButton("Clear", self)
        btn1.clicked.connect(self.drawer.clear)

        btn2 = QPushButton("Save", self)
        btn2.clicked.connect(self.drawer.save)
        
        self.layout().addWidget(label)
        self.layout().addWidget(self.drawer)
        self.layout().addWidget(btn1)
        self.layout().addWidget(btn2)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    frm = QWidget()
    # frm.setWindowTitle('NavigationToolbar')
    layout = QHBoxLayout(frm)

    w = MyWidget(frm)
    

    wgtChart = MatPFC(frm)
    # wgtChart.axes.plot(range(10), np.random.random(10), '.-', alpha=0.75)

    def update():
        arr = w.drawer.toArray()
        wgtChart.replot(arr)

    b = QPushButton('Update')
    b.clicked.connect( update )

    layout.addWidget(w)
    layout.addWidget(b)
    layout.addWidget(wgtChart)
    
    frm.show()
    frm.setFocus()
    sys.exit(app.exec_())