import pylab as plt
import pickle
import numpy as np
from time import sleep
import matplotlib

simulation = True

if not simulation:
    import dpe
    from lib_data import *

# matplotlib.use('Qt5Agg')

numCycles = 2
numTrials = 3
startSchmidtVal = -3.0
endSchmidtVal = +1.4

if not simulation:
    #import dpe
    import scipy.io as sio
    mat_contents = sio.loadmat('Exported60Node_GraphNum0.mat')
    CMat = mat_contents['A']
else:
    fn = "./20191113-222550-Prober2_HNN_15cyc_100trials_Neg3_0Pos1_4.pkl"

    data = None
    with open(fn, "rb") as pkl_file:
        data = pickle.load(pkl_file)
    CMat = data["CMat"]


CMat[0, 33] = 0
CMat[33, 0] = 0
CMat[56, 6] = 0
CMat[6, 56] = 0

arr = 2
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

if not simulation:
    noise = 0.
    lin_corrs = np.zeros_like(appliedVector1)

# Make the updatable Figure - this code taken from Thomas

plt.ion()
plt.rcParams['lines.linewidth'] = 2.0  # instead of 1.5
color_map = 'jet'  # 'cool' #try also 'prism', check here: https://matplotlib.org/examples/color/colormaps_reference.html

fig = plt.figure(0, figsize=[plt.rcParams["figure.figsize"][0] * 2., plt.rcParams["figure.figsize"][1]])
ax = fig.add_subplot(121)
color_idx_array = np.linspace(0, 1.0, numTrials)
ax.set_xlabel("Time", fontsize=15)
ax.set_ylabel("Energy", fontsize=15)
ax.set_xlim([time_vector[0], time_vector[-1]])
ax.set_ylim([-200, 300.])

trial_index = 0
energy_vector = np.NaN * np.zeros((num_updates, numTrials))  # NaNs such that it's not plotted

lines = []
for tt in np.arange(numTrials):
    lobj = ax.plot(time_vector, energy_vector, '-', color=plt.get_cmap(color_map)(color_idx_array[tt]))[0]
    lines.append(lobj)

# line1, = ax.plot(time_vector, energy_vector[:,0], '-',
#                 color=plt.get_cmap(color_map)(color_idx_array[trial_index]))  # Returns a tuple of line objects --> line1,

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

for cc in np.arange(numCycles):
    # print('Cycle number', cc)
    randOrderColumns = np.arange(60)
    np.random.shuffle(randOrderColumns)

    trackCol = 0
    for ii in randOrderColumns:
        if not simulation:
            output1 = dpe.multiply_w_delay(arr, appliedVector1, c_sel=[ii, ii + 1], mode=1, debug=False, delay=5)
            output2 = dpe.multiply_w_delay(arr, appliedVector2, c_sel=[ii, ii + 1], mode=1, debug=False, delay=5)
            output_corr = noise - dpe.lin_corr(output1, lin_corrs) + dpe.lin_corr(output2, lin_corrs)
        else:
            output_corr = np.dot(-CMat[ii,:], neuronVector)
            output_corr.shape = (-1, 1)
        for tt in np.arange(numTrials):
            threshVector = threshold - SchmidtCycleVector[cc] * neuronVector[ii, tt]
            # if (output_corr2[0,ii] >= threshVector[ii,0]):
            # if (output_corr >= threshVector[ii,0]):
            if (output_corr[tt, 0] >= threshVector):
                appliedVector1[ii, tt] = 1
                appliedVector2[ii, tt] = 0
                neuronVector[ii, tt] = 1
            else:
                appliedVector1[ii, tt] = 0
                appliedVector2[ii, tt] = 1
                neuronVector[ii, tt] = -1
            neuronVectorHistory[:, tt, 60 * cc + trackCol + 1] = neuronVector[:, tt]
            thisEnergy[tt] = 0.5 * np.dot(neuronVector[:, tt].T, (CMat @ neuronVector[:, tt]))
            # thisEnergy = 0.5*np.dot(neuronVector[:,tt], np.dot(CMat, neuronVector[:,tt]))
            energyHistory[60 * cc + trackCol + 1, tt] = thisEnergy[tt]
            energy_vector[60 * cc + trackCol + 1, tt] = thisEnergy[tt]

            # line1.set_ydata(energy_vector[:,0])  # wonder whether we can update one point at a time
        for lnum, line in enumerate(lines):
            # line.set_data(xlist[lnum], ylist[lnum]) # set data for each line separately.
            line.set_ydata(energy_vector[:, lnum])  # wonder whether we can update one point at a time
            fig.canvas.draw()
            fig.canvas.flush_events()

        columnUpdateHistory[0, 60 * cc + trackCol + 1] = ii
        trackCol = trackCol + 1