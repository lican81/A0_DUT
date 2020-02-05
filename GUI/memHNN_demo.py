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
    def __init__(self, verbosity=0, simulation=False, save_data=True):
        super(MemHNNMain, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("mem-HNN demo")
        # self.setWindowTitle("mem-HNN demo: analog in-memory optimization of the Max-cut task for a 60 node network.")
        self.setWindowIcon(QtGui.QIcon('labs_logo.png'))
        # self.showFullScreen()
        self.showMaximized()

        # doesn't work:
        # sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        # sizePolicy.setHeightForWidth(True)
        # self.setSizePolicy(sizePolicy)

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
        self.save_data = save_data
        self._experiment_running = False

        self.pushButton_run.clicked.connect(self.run_experiment)
        run_button_pic = QtGui.QIcon('run_button.png')
        self.pushButton_run.setIcon(run_button_pic)
        self.pushButton_run.setIconSize(QtCore.QSize(50, 50))
        # self.mpl_list_figs.itemClicked.connect(self.update_figure)

        self.fig_energy = Figure()  # Figure(figsize=(3,3))
        ax = self.fig_energy.add_subplot(111)
        ax.set_title("Click RUN button to see data for 60 node Max-Cut.", fontsize=15)
        ax.set_xlabel("Time", fontsize=15)
        ax.set_ylabel("Energy", fontsize=15)
        ax.set_xlim([0, 1])
        ax.set_ylim([-200, 100.])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        self.add_mpl(self.fig_energy)

        self.ST_conversion_factor = -10. / 2.0
        self.ST_offset = 0.5
        ST_min = 0.  # -10
        ST_max = 15
        ST_spinbox_list = [self.doubleSpinBox_1_ST_i,
                           self.doubleSpinBox_1_ST_f,
                           self.doubleSpinBox_2_ST_i,
                           self.doubleSpinBox_2_ST_f,
                           self.doubleSpinBox_3_ST_i,
                           self.doubleSpinBox_3_ST_f,
                           # self.doubleSpinBox_4_ST_i,
                           # self.doubleSpinBox_4_ST_f,
                           ]
        ST_init_list = [-1.5, 0.5,
                        0., 0.,
                        -1.5, 0.5,
                        # 0., 0.
                        ]
        ST_mn_mx_list = [(ST_min, ST_max), (ST_min, ST_max),
                         (0., 0.), (0., 0.),
                         (10., 10.), (0., 0.),
                         # 0., 0.
                         ]
        for ST_spinbox, ST_init, (ST_min_l, ST_max_l) in zip(ST_spinbox_list, ST_init_list, ST_mn_mx_list):
            ST_spinbox.setMinimum(ST_min_l)
            ST_spinbox.setMaximum(ST_max_l)
            ST_spinbox.setValue((ST_init - self.ST_offset) * self.ST_conversion_factor)
            ST_spinbox.setSingleStep(0.05)
        self.spinBox_num_trials.setValue(2)
        self.spinBox_num_trials.setMinimum(1)
        self.spinBox_num_trials.setMaximum(10)
        #self.spinBox_num_cycles.setValue(10)
        #self.spinBox_num_cycles.setMinimum(10)
        #self.spinBox_num_cycles.setMaximum(20)
        #self.spinBox_num_cycles.setSingleStep(5)
        # Doesn't work:
        # tmp_index = self.comboBox_num_cycles.findText("10", QtCore.QtMatchFixedString)  # finds the index of the item you want
        self.comboBox_num_cycles.setCurrentIndex(1)
        self.spinBox_batch_size.setValue(12)
        self.spinBox_batch_size.setMinimum(12)
        self.spinBox_batch_size.setMaximum(12)

        # misc about ref solutions:
        self.E_target = -187.
        self.Emin_value_NN = -150.
        self.Emin_value_opt = self.E_target

        self.init_table()

        self.show()

    def init_table(self):
        # self.energy_grid_widget.setParent(None) # hacky to get rid of this - TODO: rewrite code without qtdesigner.
        # self.energy_grid_widget = QtWidgets.QWidget(self.centralwidget)
        # self.energy_grid_widget.setParent(self.centralwidget)
        # self.energy_grid_widget.setGeometry(QtCore.QRect(710, 280, 671, 521))
        # self.energy_grid_widget.setObjectName("energy_table_widget")
        # Create table
        ## self.energy_table_widget = QtWidgets.QTableWidget()
        self.energy_grid_layout = QtWidgets.QGridLayout()
        self.energy_grid_widget.setLayout(self.energy_grid_layout)
        # self.energy_table_widget.setColumnCount(0)
        # self.energy_table_widget.setRowCount(0)
        self.nrow = 3
        self.ncol = 4
        # self.energy_grid_layout.setRowCount(self.nrow)
        # self.energy_grid_layout.setColumnCount(self.ncol)
        self.energy_grid_layout_dct = {}
        for nc in range(self.ncol):
            for nr in range(self.nrow):
                # self.energy_table_widget.setItem(nr, nc, QtWidgets.QTableWidgetItem("Cell ({},{})".format(nr, nc)))
                self.energy_grid_layout_dct[nr, nc] = QtWidgets.QLabel("Cell ({},{})".format(nr, nc))
                self.energy_grid_layout.addWidget(self.energy_grid_layout_dct[nr, nc], nr, nc, )
        # self.energy_table_widget.move(0, 0)
        # self.energy_table_widget.resize()
        # table selection change
        # self.energy_table_widget.doubleClicked.connect(self.on_click)
        self.myFont = QtGui.QFont()
        self.myFont.setBold(True)
        self.energy_grid_layout_dct[0, 0].setText(r"")
        self.energy_grid_layout_dct[0, 1].setText(r"User")
        self.energy_grid_layout_dct[0, 1].setFont(self.myFont)
        self.energy_grid_layout_dct[0, 2].setText(r"No Noise")
        self.energy_grid_layout_dct[0, 2].setFont(self.myFont)
        self.energy_grid_layout_dct[0, 3].setText(r"Optimal")
        self.energy_grid_layout_dct[0, 3].setFont(self.myFont)
        self.energy_grid_layout_dct[1, 0].setText(r"Minimal Energy")
        self.energy_grid_layout_dct[1, 0].setFont(self.myFont)
        self.energy_grid_layout_dct[2, 0].setText(r"Error Percentage")
        self.energy_grid_layout_dct[2, 0].setFont(self.myFont)

        self.energy_grid_layout_dct[1, 1].setText(r"{}".format(0.))
        self.energy_grid_layout_dct[2, 1].setText(r"{0:.1f}".format(100))
        self.energy_grid_layout_dct[1, 2].setText(r"{}".format(self.Emin_value_NN))
        self.energy_grid_layout_dct[2, 2].setText(
            r"{0:.1f}".format(100 * (self.Emin_value_NN - self.E_target) / np.abs(self.E_target)))
        self.energy_grid_layout_dct[1, 3].setText(r"{}".format(self.Emin_value_opt))
        self.energy_grid_layout_dct[2, 3].setText(
            r"{0:.1f}".format(100 * (self.Emin_value_opt - self.E_target) / np.abs(self.E_target)))

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
        numCycles = int(self.comboBox_num_cycles.currentText())#self.spinBox_num_cycles.value()  # 2
        numTrials = self.spinBox_num_trials.value()  # 3
        startSchmidtVal = self.doubleSpinBox_1_ST_i.value() / self.ST_conversion_factor + self.ST_offset  # -3.0
        endSchmidtVal = self.doubleSpinBox_1_ST_f.value() / self.ST_conversion_factor + self.ST_offset  # +1.4
        sizeBatch = self.spinBox_batch_size.value()
        simulation = self.simulation
        if self.verbosity > 0:
            print("Start experiment now:")
        if True:
            self._experiment_running = True
            _, energy_vector, ev_nn, ev_opt = run_memHNN(numCycles=numCycles,
                                                         numTrials=numTrials,
                                                         startSchmidtVal=startSchmidtVal,
                                                         endSchmidtVal=endSchmidtVal,
                                                         sizeBatch=sizeBatch,
                                                         simulation=simulation,
                                                         figure_canvas=self.canvas,  # None,
                                                         fig=self.fig_energy,
                                                         show_plot=True,
                                                         verbosity=self.verbosity)
            if self.save_data:
                np.savetxt("memhnn_data_current.txt", energy_vector)
            self._experiment_running = False
            Emin_value = energy_vector[-1, :].min()
            E_error_fraction = np.abs((Emin_value - self.E_target) / self.E_target)
            self.energy_grid_layout_dct[1, 1].setText(r"{}".format(Emin_value))
            self.energy_grid_layout_dct[2, 1].setText(r"{0:.1f}".format(100 * E_error_fraction))
            Emin_value_nn = ev_nn[~np.isnan(ev_nn)][-1].min()
            E_error_fraction_nn = np.abs((Emin_value_nn - self.E_target) / self.E_target)
            self.energy_grid_layout_dct[1, 2].setText(r"{}".format(Emin_value_nn))
            self.energy_grid_layout_dct[2, 2].setText(r"{0:.1f}".format(100 * E_error_fraction_nn))
            Emin_value_opt = ev_opt[~np.isnan(ev_opt)][-1].min()
            E_error_fraction_opt = np.abs((Emin_value_opt - self.E_target) / self.E_target)
            self.energy_grid_layout_dct[1, 3].setText(r"{}".format(Emin_value_opt))
            self.energy_grid_layout_dct[2, 3].setText(r"{0:.1f}".format(100 * E_error_fraction_opt))
        if self.verbosity > 0:
            print("Finish experiment now")

    def heightForWidth(self, width):
        return width * 0.7559943582510579

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
            # if not self._experiment_running:
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
    if verbosity > 0:
        print("Start application:")
        wdw_width = main.frameGeometry().width()
        wdw_height = main.frameGeometry().height()
        print("Window size is: {}, {}".format(wdw_width, wdw_height))
        print("Aspect ratio {}".format((1.0 * wdw_height) / wdw_width))

    sys.exit(app.exec_())
