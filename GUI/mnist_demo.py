

from PyQt5 import QtCore
from PyQt5 import QtGui, QtWidgets, uic
import qimage2ndarray

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
matplotlib.rcParams['font.sans-serif'] = "Arial"

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

        # Setup convolution weight panel
        self.fig_conv_weight = Figure(figsize=(2,3))
        # self.ax_conv_weight = self.fig_conv_weight.add_axes((0,0,1,1))
        # self.ax_conv_weight.get_xaxis().set_visible(False)
        # self.ax_conv_weight.get_yaxis().set_visible(False)
        self.canvas_conv_weight = FigureCanvas(self.fig_conv_weight)
        self.canvas_conv_weight.setParent(self.mpl_conv_weight)

        # Setup FC weight panel
        self.fig_fc_weight = Figure(figsize=(2,4))
        # self.ax_fc_weight = self.fig_fc_weight.add_axes((0,0,1,1))
        # self.ax_fc_weight.get_xaxis().set_visible(False)
        # self.ax_fc_weight.get_yaxis().set_visible(False)
        self.canvas_fc_weight = FigureCanvas(self.fig_fc_weight)
        self.canvas_fc_weight.setParent(self.mpl_fc_weight)

        # Setup conv input panel
        self.fig_conv_in = Figure(figsize=(3,4))
        # self.ax_conv_in = self.fig_conv_in.add_axes((0,0,1,1))
        # self.ax_conv_in.get_xaxis().set_visible(False)
        # self.ax_conv_in.get_yaxis().set_visible(False)
        self.canvas_conv_in = FigureCanvas(self.fig_conv_in)
        self.canvas_conv_in.setParent(self.mpl_conv_in)

        # Setup conv output panel
        self.fig_conv_out = Figure(figsize=(6,3))
        self.ax_conv_outs = [None] * 7
        for i in range(7):
            self.ax_conv_outs[i] = self.fig_conv_out.add_subplot(2,4,i+1)
            self.ax_conv_outs[i].get_xaxis().set_visible(False)
            self.ax_conv_outs[i].get_yaxis().set_visible(False)

        self.canvas_conv_out = FigureCanvas(self.fig_conv_out)
        self.canvas_conv_out.setParent(self.mpl_conv_out)
        self.fig_conv_out.tight_layout()


        # Setup FC output panel
        self.fig_fc_out = Figure(figsize=(6,3))
        # self.ax_fc_out = self.fig_fc_out.add_axes((0,0,1,1))
        self.ax_fc_out = self.fig_fc_out.add_subplot(111)
        self.canvas_fc_out = FigureCanvas(self.fig_fc_out)
        self.canvas_fc_out.setParent(self.mpl_fc_out)
        self.fig_fc_out.tight_layout()



        # Connect button click signals
        self.btn_classify.clicked.connect(self.classify)
        self.btn_read.clicked.connect(self.read_conductance)

        self._init_dpe()

    def _init_dpe(self):
        self._conf = {
            'r_conv':   20,
            'c_conv':   20,
            'arr_conv': 0,
            'r_fc':     0,
            'c_fc':     0,
            'arr_fc': 1,
        }

        self.dpe = DPE('COM3')
        self.dpe.set_clock(50)

        load_workspace(self._conf, '../20200130-100802-mnist_config')

        # load_workspace(self._conf, '../20200130-105530-mnist_config_prober1')
        # print(self._conf['arr_conv'])
    
        self.nn = NN_dpe(self._conf['weights'])


    def read_conductance(self):
        self.statusbar.showMessage('Reading conductance...')
        self.repaint()

        g_conv = self.dpe.read(self._conf['arr_conv'], method='fast')
        g_conv = g_conv[self._conf['r_conv']:self._conf['r_conv']+26,
                        self._conf['c_conv']:self._conf['c_conv']+14, ]

        self.fig_conv_weight.clf()
        # self.ax_conv_weight = self.fig_conv_weight.add_axes((0,0,1,1))
        self.ax_conv_weight = self.fig_conv_weight.add_subplot(111)
        self.ax_conv_weight.get_xaxis().set_visible(False)
        self.ax_conv_weight.get_yaxis().set_visible(False)
        self.ax_conv_weight.set_title('Conductance ($\mu$S)')
        im_conv = self.ax_conv_weight.imshow(g_conv * 1e6)
        self.ax_conv_weight.set_aspect('auto')
        self.fig_conv_weight.colorbar(im_conv, ax=self.ax_conv_weight)
        self.fig_conv_weight.tight_layout()
        self.canvas_conv_weight.draw()

        g_fc = self.dpe.read(self._conf['arr_fc'], method='fast')
        g_fc1 = g_fc[self._conf['r_fc']:self._conf['r_fc']+57,
                     self._conf['c_fc']:self._conf['c_fc']+20, ]

        g_fc2 = g_fc[self._conf['r_fc']:self._conf['r_fc']+56,
                     self._conf['c_fc']+20:self._conf['c_fc']+40, ]

        g_fc = np.concatenate((g_fc1, g_fc2), axis=0)

        self.fig_fc_weight.clf()
        self.ax_fc_weight = self.fig_fc_weight.add_subplot(111)
        self.ax_fc_weight.get_xaxis().set_visible(False)
        self.ax_fc_weight.get_yaxis().set_visible(False)
        self.ax_fc_weight.set_title('Conductance( $\mu$S)')
        im_fc = self.ax_fc_weight.imshow(g_fc * 1e6)
        self.ax_fc_weight.set_aspect('auto')
        self.fig_fc_weight.colorbar(im_fc, ax=self.ax_fc_weight)
        self.fig_fc_weight.tight_layout()
        self.canvas_fc_weight.draw()

        self.statusbar.showMessage('Conductance read completed.')


    def classify(self):
        for i in range(7):
            self.ax_conv_outs[i].cla()
        self.canvas_conv_out.draw()
        self.ax_fc_out.cla()
        self.canvas_fc_out.draw()

        img = self.drawing.toArray()
        img = self._pre_process(img)
        
        self.ax_digit.imshow( img )
        self.canvas_digit.draw()
        self.repaint()

        ## Convolution layer
        image = img[..., np.newaxis]
        vectors = self.nn._conv_flattern(image)

        self._disp_conv_in(vectors)

        print('Convolving image...')

        output = self.dpe.multiply(
            self._conf['arr_conv'], 
            vectors, 
            c_sel=[self._conf['c_conv'], self._conf['c_conv']+14], 
            r_start=self._conf['r_conv'], mode=0, Tdly=500) / (self.nn.Gratio/2)

        output_cor = self.dpe.lin_corr(output, self._conf['lin_cor_conv'])
        x = output_cor[:, ::2] - output_cor[:, 1::2]
        x = x.reshape(20, 20, -1)

        self._disp_conv_out(x)
        self.repaint()

        print('Convolution completed, start fully connected layer...')

        ## Fully connected layer
        x1 = self.nn.relu(x)
        x1 = self.nn.max_pooling(x1)
        x1 = self.nn.flattern(x1)

        x = x1
        x1 = x[:57].T
        x2 = x[57:].T

        sc1 = x1.max()
        sc2 = x2.max()

        # Gfc1 = nn.Gfc[:57]
        # Gfc2 = nn.Gfc[57:]

        x1 = x1 / sc1
        x2 = x2 / sc2

        output1 = self.dpe.multiply(self._conf['arr_fc'], np.array([x1]).T, c_sel=[
                            0, 20], mode=0, Tdly=500)
        output1 = self.dpe.lin_corr(output1, self._conf['new_lin_cor_fc1']) * sc1

        output2 = self.dpe.multiply(self._conf['arr_fc'], np.array([x2]).T, c_sel=[
                            20, 40], mode=0, Tdly=500)
        output2 = self.dpe.lin_corr(output2, self._conf['new_lin_cor_fc2']) * sc2

        outputs = output1 + output2

        y = outputs[:, ::2] - outputs[:, 1::2]
        
        self._plot_result(y)

        print(f'Classfied digit {y.argmax()}.')

    def _disp_conv_in(self, img):
        self.fig_conv_in.clf()
        self.ax_conv_in = self.fig_conv_in.add_subplot(111)

        self.ax_conv_in.set_title('Voltage (V)')
        self.ax_conv_in.get_xaxis().set_visible(False)
        self.ax_conv_in.get_yaxis().set_visible(False)
        im_conv_in = self.ax_conv_in.imshow(img.T* 0.2)
        self.ax_conv_in.set_aspect('auto')
        self.fig_conv_in.colorbar(im_conv_in, ax=self.ax_conv_in)
        self.fig_conv_in.tight_layout()

        self.canvas_conv_in.draw()
        self.repaint()

        # self.ax_conv_in.imshow(img.T)
        # self.canvas_conv_in.draw()
        # self.repaint()



    def _disp_conv_out(self, x):
        for i in range(7):
            self.ax_conv_outs[i].imshow(x[:,:,i])
        self.canvas_conv_out.draw()

    def _plot_result(self, y):
        self.ax_fc_out.cla()
        self.ax_fc_out.bar(range(10), y.reshape(-1) / 256 * 1e6)
        self.ax_fc_out.set_ylabel('Average current ($\mu$A)')
        self.ax_fc_out.set_title(f'Recognized {y.argmax()}')
        self.ax_fc_out.set_xticks(np.arange(0,10,1))
        self.ax_fc_out.grid(True, alpha=0.3)
        self.fig_fc_out.tight_layout()
        self.canvas_fc_out.draw()
        self.repaint()

    def _pre_process(self, img):
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