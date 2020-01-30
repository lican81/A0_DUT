import sys
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from Thomas.experimental_hnn_live_update_simulation import run_memHNN

from skimage.transform import resize

qtCreatorFile = "memHNN_demo.ui"
Ui_MainWindow, QMainWindow = uic.loadUiType(qtCreatorFile)

class MemHNNMain(QMainWindow, Ui_MainWindow):
    def __init__(self, verbosity=0):
        super(MemHNNMain, self).__init__()
        self.setupUi(self)
        self.fig_dict = {}

        self.verbosity = verbosity

        self.pushButton_run.clicked.connect(self.run_experiment)
        #self.mpl_list_figs.itemClicked.connect(self.update_figure)

        self.fig_energy = Figure() #  Figure(figsize=(3,3))
        self.add_mpl(self.fig_energy)

        # Setup the digit panel
        # self.ax_digit = self.fig_energy.add_subplot(111)
        # self.ax_energy = self.fig_energy.add_axes((0,0,1,1))
        # self.ax_energy.get_xaxis().set_visible(False)
        # self.ax_energy.get_yaxis().set_visible(False)

        # self.canvas_energy = FigureCanvas(self.fig_digit)
        # self.canvas_energy.setParent(self.mpl_energy)

        self.show()

    def add_mpl(self, fig):
        self.canvas = FigureCanvas(fig)
        self.mpl_vl.addWidget(self.canvas)
        self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,
                                         self.mpl_energy, coordinates=True)
        self.mpl_vl.addWidget(self.toolbar)


    def remove_mpl(self, ):
        self.mpl_vl.removeWidget(self.canvas)
        self.canvas.close()
        self.mpl_vl.removeWidget(self.toolbar)
        self.toolbar.close()

    def run_experiment(self,):
        numCycles = 2
        numTrials = 3
        startSchmidtVal = -3.0
        endSchmidtVal = +1.4
        simulation = True
        if self.verbosity>0:
            print("start experiment now")
        if True:
            run_memHNN(numCycles=numCycles,
                       numTrials=numTrials,
                       startSchmidtVal=startSchmidtVal,
                       endSchmidtVal=endSchmidtVal,
                       simulation=simulation,
                       figure_canvas=self.canvas,#None,
                       fig=self.fig_energy,
                       show_plot=True,
                       verbosity = self.verbosity)
        if self.verbosity > 0:
            print("finish experiment now")


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    main = MemHNNMain(verbosity=1)

    sys.exit(app.exec_())

