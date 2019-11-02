from lib_data import *
import scipy.io as sio

actualRows = np.array([0,10])
actualCols = np.array([0,10])
totalDevices = np.size(actualRows)

VreadGate = 5.0
vRead = 0.2
arr = 0

vAppliedSet = np.arange(0.1, 3.1, 0.1)
vAppliedReset = np.arange(0.1, 3.1, 0.1)
vGateSet = np.arange(0.1, 1.9, 0.1)
vGateReset = np.arange(5.0, 5.5, 0.5)

AllDevicesGHistory = []
AllDevicesVHistory = []
AllDevicesVGateHistory = []

Vref = 0.5
maxGProtect = 500e-6
GTargetOFF = 2e-6
numRepeats = 3

for jj in range(totalDevices):
    rr = actualRows[jj]
    cc = actualCols[jj]
    GHistory = []
    VHistory = []
    VGateHistory = []

    for nn in range(numRepeats):
        thisGHistory = []
        thisVHistory = []
        thisVGateHistory = []
        # Do a first read of this device
        rdCurr = a0.pic_read_single(arr, rr, cc, Vread=vRead, Vgate=VreadGate, gain=-1)
        #rdCurr = a0.read_single_int(vRead, Vgate, array=arr, row=rr, col=cc, gain=-1)             
        currG = rdCurr/vRead
        thisGHistory.append(currG)
        thisVHistory.append(0)
        thisVGateHistory.append(0)
        #print('Initial G=', currG, 'Target G =', thisGtarget)
        initG = currG
        
        for vgate in vGateSet:
            for vappset in vAppliedSet:
                # Apply vappset pulse, then read
                a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)

                #rdCurr = a0.read_single_int(vRead, Vgate, array=arr, row=rr, col=cc, gain=-1)
                rdCurr = a0.pic_read_single(arr, rr, cc, Vread=vRead, Vgate=VreadGate, gain=-1)
                currG = rdCurr/vRead
                thisGHistory.append(currG)
                thisVHistory.append(vappset)
                thisVGateHistory.append(vgate)
                if currG >= maxGProtect:
                    break
            if currG >= maxGProtect:
                break
        if currG >= maxGProtect:
                break
        
        print('SET: Array', arr, ', device (row=', rr, 'col=', cc, ') Repeat=', nn,' Init G=', initG, ' Final G=', currG)
        beforeRESETG = currG
        # Now try to reset the device to repeat the SET switching again
        for vgate in vGateReset:
            for vappreset in vAppliedReset:
                # Apply vappreset pulse, then read
                a0.reset_single_int(vappreset, vgate, array=arr, row=rr, col=cc)
                rdCurr = a0.pic_read_single(arr, rr, cc, Vread=vRead, Vgate=VreadGate, gain=-1)
                currG = rdCurr/vRead
                thisGHistory.append(currG)
                thisVHistory.append(-1*vappreset)
                thisVGateHistory.append(vgate)
                if currG <= GTargetOFF:
                    break
            if currG <= GTargetOFF:
                break

        GHistory.append(thisGHistory)
        VHistory.append(thisVHistory)
        VGateHistory.append(thisVGateHistory)
        print('RESET: Array', arr, ', device (row=', rr, 'col=', cc, ') Repeat=', nn,' Init G=', beforeRESETG, ' Final G=', currG)
        
        fig, ax1 = plt.subplots()
        color = 'tab:blue'
        ax1.set_xlabel('Cycles')
        ax1.set_ylabel('Conductance (uS)', color=color)
        ax1.plot([i* 1e6 for i in thisGHistory], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax2 = ax1.twinx()  
        color = 'tab:red'
        ax2.set_ylabel('Voltage Applied', color=color)
        ax2.plot(thisVHistory, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        fig.tight_layout()  
        plt.show()

    AllDevicesGHistory.append(GHistory)
    AllDevicesVHistory.append(VHistory)
    AllDevicesVGateHistory.append(VGateHistory)

save_workspace(vars(), note='RCLab1_Array0_SwitchONTests1')