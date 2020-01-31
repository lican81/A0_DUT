import sys
from PyQt5 import QtGui, QtCore, QtWidgets, uic
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# from experimental_hnn_live_update_final import run_memHNN
from experimental_hnn_live_update_final_batch10 import run_memHNN
from time import sleep

# from skimage.transform import resize

qtCreatorFile = "memHNN_demo.ui"
Ui_MainWindow, QMainWindow = uic.loadUiType(qtCreatorFile)


class MemHNNMain(QMainWindow, Ui_MainWindow):
    def __init__(self, verbosity=0, simulation=False):
        super(MemHNNMain, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("mem-HNN demo")
        self.setWindowIcon(QtGui.QIcon('labs_logo.png'))
        # self.showFullScreen()
        bg_style = "background-color: white; "
        style_str = """
QMainWindow { background-color: white; }
QPushButton {
    border-width: 4px;
    border-image: url(button.png) 4 4 4 4 stretch stretch;
}
        """
        self.setStyleSheet(style_str)
        # self.setStyleSheet("")

        self.verbosity = verbosity
        self.simulation = simulation
        self._experiment_running = False

        self.pushButton_run.clicked.connect(self.run_experiment)
        run_button_pic = QtGui.QIcon('run_button.png')
        self.pushButton_run.setIcon(run_button_pic)
        self.pushButton_run.setIconSize(QtCore.QSize(50, 50))
        # self.mpl_list_figs.itemClicked.connect(self.update_figure)

        self.fig_energy = Figure()  # Figure(figsize=(3,3))
        ax = self.fig_energy.add_subplot(111)
        ax.set_title("Click RUN to see data.")
        ax.set_xlabel("Time", fontsize=15)
        ax.set_ylabel("Energy", fontsize=15)
        ax.set_xlim([0, 1])
        ax.set_ylim([-200, 100.])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
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
        ST_init_list = [-3., 1.4,
                        0., 0.,
                        0., 0.,
                        0., 0.]
        for ST_spinbox, ST_init in zip(ST_spinbox_list, ST_init_list):
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

    def run_experiment(self, ):
        numCycles = self.spinBox_num_cycles.value()  # 2
        numTrials = self.spinBox_num_trials.value()  # 3
        startSchmidtVal = self.doubleSpinBox_1_ST_i.value()  # -3.0
        endSchmidtVal = self.doubleSpinBox_1_ST_f.value()  # +1.4
        simulation = self.simulation
        if self.verbosity > 0:
            print("Start experiment now:")
        if True:
            self._experiment_running = True
            _, energyHistory = run_memHNN(numCycles=numCycles,
                                          numTrials=numTrials,
                                          startSchmidtVal=startSchmidtVal,
                                          endSchmidtVal=endSchmidtVal,
                                          simulation=simulation,
                                          figure_canvas=self.canvas,  # None,
                                          fig=self.fig_energy,
                                          show_plot=True,
                                          verbosity=self.verbosity)
            self._experiment_running = False
            Emin_value = energyHistory.min()
        if self.verbosity > 0:
            print("Finish experiment now")

    def closeEvent(self, event):
        """Generate 'question' dialog on clicking 'X' button in title bar.

        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Save, Close, Cancel buttons
        """
        if self._experiment_running:
            reply = QtWidgets.QMessageBox.question(
                self, "Message",
                "Are you sure you want to quit? The experiment is still running, closing the window might be unsafe.",
                QtWidgets.QMessageBox.Close | QtWidgets.QMessageBox.Cancel)

            if (reply == QtWidgets.QMessageBox.Close):
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def keyPressEvent(self, event):
        """Close application from escape key.

        results in QMessageBox dialog from closeEvent, good but how/why?
        """
        if event.key() == QtCore.Qt.Key_Escape:
            #if not self._experiment_running:
            self.close()
            # else:
            #     print("You can only close after finishing the experiment.")


if __name__ == '__main__':
    import os

    simulation = (os.environ["USERNAME"].upper() == "VANVAERE")
    app = QtWidgets.QApplication(sys.argv)
    verbosity = 1
    main = MemHNNMain(verbosity=verbosity,
                      simulation=simulation)
    if verbosity > 0: print("Start application:")
    sys.exit(app.exec_())
