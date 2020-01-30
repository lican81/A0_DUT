import sys
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from skimage.transform import resize

qtCreatorFile = "memHNN_demo.ui"
Ui_MainWindow, QMainWindow = uic.loadUiType(qtCreatorFile)

class MemHNNMain(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(MemHNNMain, self).__init__()
        self.setupUi(self)
        self.fig_dict = {}

        #self.pushButton_run.clicked.connect(self.update_figure)
        self.mpl_list_figs.itemClicked.connect(self.update_figure)

        self.fig_energy = Figure() #  Figure(figsize=(3,3))
        self.add_mpl(self.fig_energy)

        # Setup the digit panel
        # self.ax_digit = self.fig_energy.add_subplot(111)
        # self.ax_energy = self.fig_energy.add_axes((0,0,1,1))
        # self.ax_energy.get_xaxis().set_visible(False)
        # self.ax_energy.get_yaxis().set_visible(False)

        # self.canvas_energy = FigureCanvas(self.fig_digit)
        # self.canvas_energy.setParent(self.mpl_energy)

    def update_figure(self, item):
        text = item.text()
        self.remove_mpl()
        self.add_mpl(self.fig_dict[text])

    def add_figure(self, name, fig):
        self.fig_dict[name] = fig
        self.mpl_list_figs.addItem(name)

    def add_mpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mpl_vl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                                         self.mpl_energy, coordinates=True)
        self.mpl_vl.addWidget(self.toolbar)

    # This is the alternate toolbar placement. Susbstitute the three lines above
    # for these lines to see the different look.
    #        self.toolbar = NavigationToolbar(self.canvas,
    #                self, coordinates=True)
    #        self.addToolBar(self.toolbar)

    def remove_mpl(self, ):
        self.mpl_vl.removeWidget(self.canvas)
        self.canvas.close()
        self.mpl_vl.removeWidget(self.toolbar)
        self.toolbar.close()


if __name__ == '__main__':

    fig1 = Figure()
    ax1f1 = fig1.add_subplot(111)
    ax1f1.plot(np.random.rand(5))

    fig2 = Figure()
    ax1f2 = fig2.add_subplot(121)
    ax1f2.plot(np.random.rand(5))
    ax2f2 = fig2.add_subplot(122)
    ax2f2.plot(np.random.rand(10))

    fig3 = Figure()
    ax1f3 = fig3.add_subplot(111)
    ax1f3.pcolormesh(np.random.rand(20, 20))

    app = QtWidgets.QApplication(sys.argv)
    main = MemHNNMain()
    main.add_figure('One plot', fig1)
    main.add_figure('Two plots', fig2)
    main.add_figure('Pcolormesh', fig3)


    main.show()
    sys.exit(app.exec_())

