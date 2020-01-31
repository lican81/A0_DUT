import sys
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

#from experimental_hnn_live_update_final import run_memHNN
from experimental_hnn_live_update_final_batch10 import run_memHNN
from time import sleep

#from skimage.transform import resize

qtCreatorFile = "memHNN_demo.ui"
Ui_MainWindow, QMainWindow = uic.loadUiType(qtCreatorFile)

class MemHNNMain(QMainWindow, Ui_MainWindow):
    def __init__(self, verbosity=0, simulation=False):
        super(MemHNNMain, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("mem-HNN demo")
        self.setWindowIcon(QtGui.QIcon('labs_logo.png'))
        #self.showFullScreen()
        self.setStyleSheet("background-color: white;")
        self.verbosity = verbosity
        self.simulation = simulation
        self._experiment_running = False

        self.pushButton_run.clicked.connect(self.run_experiment)
        #self.mpl_list_figs.itemClicked.connect(self.update_figure)

        self.fig_energy = Figure() #  Figure(figsize=(3,3))
        self.add_mpl(self.fig_energy)

        ST_min = -10
        ST_max = 10
        ST_spinbox_list = [self.doubleSpinBox_1_ST_i,
                           self.doubleSpinBox_1_ST_f,
                           self.doubleSpinBox_2_ST_i,
                           self.doubleSpinBox_2_ST_f,
                           self.doubleSpinBox_3_ST_i,
                           self.doubleSpinBox_3_ST_f,
                           self.doubleSpinBox_4_ST_i,
                           self.doubleSpinBox_4_ST_f,
                           ]
        ST_init_list = [-3.,1.4,
                        0.,0.,
                        0.,0.,
                        0.,0.]
        for ST_spinbox,ST_init in zip(ST_spinbox_list,ST_init_list):
            ST_spinbox.setMinimum(ST_min)
            ST_spinbox.setMaximum(ST_max)
            ST_spinbox.setValue(ST_init)
            ST_spinbox.setSingleStep(0.01)
        self.spinBox_num_trials.setValue(3)
        self.spinBox_num_trials.setMinimum(1)
        self.spinBox_num_trials.setMaximum(10)
        self.spinBox_num_cycles.setValue(2)
        self.spinBox_num_cycles.setMinimum(1)
        self.spinBox_num_cycles.setMaximum(10)
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
        numCycles = self.spinBox_num_cycles.value()#2
        numTrials = self.spinBox_num_trials.value()#3
        startSchmidtVal = self.doubleSpinBox_1_ST_i.value()#-3.0
        endSchmidtVal = self.doubleSpinBox_1_ST_f.value()#+1.4
        simulation = self.simulation
        if self.verbosity>0:
            print("Start experiment now:")
        if True:
            self._experiment_running = True
            run_memHNN(numCycles=numCycles,
                       numTrials=numTrials,
                       startSchmidtVal=startSchmidtVal,
                       endSchmidtVal=endSchmidtVal,
                       simulation=simulation,
                       figure_canvas=self.canvas,#None,
                       fig=self.fig_energy,
                       show_plot=True,
                       verbosity = self.verbosity)
            self._experiment_running = False
        if self.verbosity > 0:
            print("Finish experiment now")

    def keyPressEvent(self, event):
        """Close application from escape key.

        results in QMessageBox dialog from closeEvent, good but how/why?
        """
        if event.key() == QtCore.Qt.Key_Escape:
            if not self._experiment_running:
                self.close()


if __name__ == '__main__':
    import os
    simulation = (os.environ["USERNAME"].upper()=="VANVAERE")
    app = QtWidgets.QApplication(sys.argv)
    verbosity=1
    main = MemHNNMain(verbosity=verbosity,
                      simulation=simulation)
    if verbosity>0: print("Start application:")
    sys.exit(app.exec_())

