import sys
sys.path.append('../')

import pickle
#import matplotlib
#matplotlib.rcParams['font.sans-serif'] = "Arial"

import pylab as plt
import numpy as np
#from time import sleep
#import matplotlib

import os
simulation = (os.environ["USERNAME"].upper()=="VANVAERE")

if not simulation:
    import serial
    from dpe import DPE
    from lib_data import *
    from lib_nn_dpe import NN_dpe

numCycles = 1
numTrials = 2
startSchmidtVal = -3.0
endSchmidtVal = +1.4

def run_memHNN(numCycles=numCycles,
               numTrials=numTrials,
               startSchmidtVal=startSchmidtVal,
               endSchmidtVal=endSchmidtVal,
               simulation=simulation,
               figure_canvas=None,
               fig=None,
               show_plot=True,
               verbosity=0):
    if verbosity>0.:
        print("Enter run memHNN function.")
        print("This is a"+simulation*" simulation"+(not simulation)*("n experiment"))
    if not simulation:
        dpe_inst = DPE('COM6')
        dpe_inst.set_clock(50)
        dpe_inst.shape

        # fn = "../../20200129-172219-Prober2_HNN_20cyc_1trial_VarSchmidt.pkl"
        fn = "./20200130-120058-memHNN_LinearCorrections.pkl"
        data_lc = None
        with open(fn, "rb") as pkl_file:
            data_lc = pickle.load(pkl_file)
        lin_corrs = data_lc["lin_corrs"]

        import scipy.io as sio
        mat_contents = sio.loadmat('./Exported60Node_GraphNum0.mat')
        CMat = mat_contents['A']

        CMat[0, 33] = 0
        CMat[33, 0] = 0
        CMat[56, 6] = 0
        CMat[6, 56] = 0
        if verbosity>0.:
            print("Experiment: matrix loaded")
    else:
        fn = "./Thomas/20191113-222550-Prober2_HNN_15cyc_100trials_Neg3_0Pos1_4.pkl"

        data = None
        if verbosity>1.:
            print("CWD: {}".format(os.getcwd()))
        with open(fn, "rb") as pkl_file:
            if verbosity > 1.: print("Pkl file opened.")
            data = pickle.load(pkl_file)
            if verbosity>1.: print("Pkl file loaded.")
        CMat = data["CMat"]
        if verbosity>0.:
            print("Simulation: matrix loaded")


    arr = 2
    sizeBatch = 12
    numBatches = 60/sizeBatch
    SchmidtCycleVector = np.linspace(startSchmidtVal, endSchmidtVal, numCycles)
    threshold = 0
    noise = 0
    numCols = 60
    appliedVector1 = np.zeros((64, numTrials))
    appliedVector2 = np.zeros((64, numTrials))
    neuronVectorHistory = np.zeros((60, numTrials, numCycles * numCols + 1))
    neuronVector = np.zeros((60, numTrials))
    columnUpdateHistory = np.zeros((1, numCycles * numCols + 1))
    energyHistory = np.zeros((numCycles * numCols + 1, numTrials))
    num_updates = numCycles * numCols + 1
    time_vector = np.arange(0, num_updates)
    color_idx_array = np.linspace(0, 1.0, numTrials)

    #if not simulation:
    #    lin_corrs = np.zeros_like(appliedVector1)

    # Make the updatable Figure - this code taken from Thomas
    if figure_canvas==None and show_plot:
        plt.ion()
    plt.rcParams['lines.linewidth'] = 2.0  # instead of 1.5
    color_map = 'jet'  # 'cool' #try also 'prism', check here: https://matplotlib.org/examples/color/colormaps_reference.html

    if fig==None:
        fig = plt.figure(0, figsize=[plt.rcParams["figure.figsize"][0] * 2., plt.rcParams["figure.figsize"][1]])
    else:
        fig.clf()
    ax = fig.add_subplot(111)
    color_idx_array = np.linspace(0, 1.0, numTrials)
    ax.set_xlabel("Time", fontsize=15)
    ax.set_ylabel("Energy", fontsize=15)
    ax.set_xlim([time_vector[0], time_vector[-1]])
    ax.set_ylim([-200, 100.])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    trial_index = 0
    energy_vector = np.NaN * np.zeros((num_updates, numTrials))  # NaNs such that it's not plotted

    lines = []
    for tt in np.arange(numTrials):
        lobj = ax.plot(time_vector, energy_vector[:,tt], '-', color=plt.get_cmap(color_map)(color_idx_array[tt]))[0]
        lines.append(lobj)

    # line1, = ax.plot(time_vector, energy_vector[:,0], '-',
    #                 color=plt.get_cmap(color_map)(color_idx_array[trial_index]))  # Returns a tuple of line objects --> line1,
    if verbosity>0.:
        print("Initialize data containers.")
    thisEnergy = np.zeros(numTrials)
    for tt in np.arange(numTrials):
        randomVector = np.random.randint(2, size=(60, 1))
        initVector = randomVector

        # for ss in np.arange(numSchmidt):
        appliedVector1[0:60, tt] = initVector[:, 0]
        appliedVector2[0:60, tt] = 1 - initVector[:, 0]
        neuronVector[0:60, tt] = appliedVector1[0:60, tt] - appliedVector2[0:60, tt]
        neuronVectorHistory[:, tt, 0] = appliedVector1[0:60, tt] - appliedVector2[0:60, tt]
        thisEnergy[tt] = 0.5 * np.dot(neuronVector[:, tt].T, (CMat @ neuronVector[:, tt]))
        energyHistory[0, tt] = thisEnergy[tt]
        energy_vector[0, tt] = thisEnergy[tt]
    if verbosity>0.:
        print("Run experiment.")
    for cc in np.arange(numCycles):
        # print('Cycle number', cc)
        
        randOrderColumnBatches = np.arange(numBatches).astype(int)
        np.random.shuffle(randOrderColumnBatches)

        trackColBatch = 0
        for ii in randOrderColumnBatches:
            if not simulation:
                output1 = dpe_inst.multiply_w_delay(arr, appliedVector1, c_sel=[(ii*sizeBatch), ((ii+1)*sizeBatch)],
                                                    mode=1, debug=False, delay=5)
                output2 = dpe_inst.multiply_w_delay(arr, appliedVector2, c_sel=[(ii*sizeBatch), ((ii+1)*sizeBatch)],
                                                    mode=1, debug=False, delay=5)
                output_corr = noise - dpe_inst.lin_corr(output1, lin_corrs) + dpe_inst.lin_corr(output2, lin_corrs)
            else:
                output_corr = -np.dot(CMat[(ii*sizeBatch):((ii+1)*sizeBatch), :], neuronVector).T
                #output_corr.shape = (-1, 1)
            for tt in np.arange(numTrials):
                threshVector = threshold - SchmidtCycleVector[cc] * neuronVector[ii*sizeBatch:(ii+1)*sizeBatch, tt]
                # if (output_corr2[0,ii] >= threshVector[ii,0]):
                # if (output_corr >= threshVector[ii,0]):
                for columnIndex in np.arange(sizeBatch):
                    actualColumn = ii*sizeBatch + columnIndex
                    if (output_corr[tt, columnIndex] >= threshVector[columnIndex]):
                        appliedVector1[actualColumn, tt] = 1
                        appliedVector2[actualColumn, tt] = 0
                        neuronVector[actualColumn, tt] = 1
                    else:
                        appliedVector1[actualColumn, tt] = 0
                        appliedVector2[actualColumn, tt] = 1
                        neuronVector[actualColumn, tt] = -1
                    #neuronVectorHistory[:, tt, 60 * cc + trackCol + 1] = neuronVector[:, tt]
                    thisEnergy[tt] = 0.5 * np.dot(neuronVector[:, tt].T, (CMat @ neuronVector[:, tt]))
                    # thisEnergy = 0.5*np.dot(neuronVector[:,tt], np.dot(CMat, neuronVector[:,tt]))
                    #energyHistory[60 * cc + trackCol + 1, tt] = thisEnergy[tt]
                    energy_vector[60 * cc + trackColBatch*sizeBatch + columnIndex + 1, tt] = thisEnergy[tt]
                    columnUpdateHistory[0, 60 * cc + trackColBatch*sizeBatch + columnIndex + 1] = actualColumn

                    # line1.set_ydata(energy_vector[:,0])  # wonder whether we can update one point at a time
            for lnum, line in enumerate(lines):
                # line.set_data(xlist[lnum], ylist[lnum]) # set data for each line separately.
                line.set_ydata(energy_vector[:, lnum])  # wonder whether we can update one point at a time
            if show_plot:
                fig.canvas.draw()
                fig.canvas.flush_events()
                if cc==0:
                    legend_list=["Trial {}".format(1+lnum) for lnum,lines in enumerate(lines)]
                    ax.legend(legend_list, bbox_to_anchor=(1.1, 1.1))
            if figure_canvas!=None and show_plot:
                figure_canvas.draw()

            
            trackColBatch = trackColBatch + 1

    return neuronVectorHistory, energyHistory

if (__name__=="__main__"):
    run_memHNN()