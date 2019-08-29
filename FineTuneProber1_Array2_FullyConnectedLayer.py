from lib_data import *
load_workspace(vars(), '20190814-205207-CNN weights')
GMin = 2e-6
GMax = 100e-6
# Scale down Gfc from 0 to 200uS to 100uS
scaledGfc = Gfc/2
# First reshape Gfc to fit within the 64 rows
# reshape from 113x20 to 57x40
#newGfc = np.zeros((57,40))+GMin
newGfc = np.zeros((64,64))+GMin
newGfc[0:57,0:20]=scaledGfc[0:57,0:20]
newGfc[0:56,20:40]=scaledGfc[57:113,0:20]

targetGVals = newGfc

import scipy.io as sio

mat_contents = sio.loadmat('Prober1TargetDevices.mat')
targetRowsPython = mat_contents['targetRowsPython']
targetColsPython = mat_contents['targetColsPython']
actualRows = targetRowsPython[0]
actualCols = targetColsPython[0]
totalDevices = np.size(actualRows)

VreadGate = 5.0
vRead = 0.2
arr = 2
GMin = 2e-6
GMax = 100e-6

targetGThresh = 4e-6

vAppliedSet = np.arange(0.5, 2.7, 0.05)
vAppliedReset = np.arange(0.5, 3.8, 0.1)
vGateSet = np.arange(0.5, 1.7, 0.05)
vGateReset = np.arange(5.0, 5.5, 0.5)

GHistory = []
VHistory = []

Vgate = 5
Vref = 0.5

for jj in range(totalDevices):
    rr = actualRows[jj]
    cc = actualCols[jj]
    thisGtarget = targetGVals[rr,cc]

    thisGHistory = []
    thisVHistory = []
    thisGainHistory = []
    # Do a first read of this device
    rdCurr = a0.read_single_int(vRead, Vgate, array=arr, row=rr, col=cc, gain=-1)             
    currG = rdCurr/vRead
    thisGHistory.append(currG)
    thisVHistory.append(0)
    #print('Initial G=', currG, 'Target G =', thisGtarget)
    initG = currG
    # Now, if device is lower than target, SET it
    if currG < (thisGtarget-targetGThresh):
        for vgate in vGateSet:
            for vappset in vAppliedSet:
                # Apply vappset pulse, then read
                a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)

                rdCurr = a0.read_single_int(vRead, Vgate, array=arr, row=rr, col=cc, gain=-1)
                currG = rdCurr/vRead
                thisGHistory.append(currG)
                thisVHistory.append(vappset)
                if currG >= (thisGtarget-targetGThresh):
                    break
            if currG >= (thisGtarget-targetGThresh):
                break
        GHistory.append(thisGHistory)
        VHistory.append(thisVHistory)

    # Else, if device is higher than target, RESET it, then SET it
    elif currG > (thisGtarget+targetGThresh):
        for vgate in vGateReset:
            for vappreset in vAppliedReset:
                # Apply vappreset pulse, then read
                a0.reset_single_int(vappreset, vgate, array=arr, row=rr, col=cc)

                rdCurr = a0.read_single_int(vRead, Vgate, array=arr, row=rr, col=cc, gain=-1)
                currG = rdCurr/vRead
                thisGHistory.append(currG)
                thisVHistory.append(-1*vappreset)
                if currG <= (thisGtarget+targetGThresh):
                    break
            if currG <= (thisGtarget+targetGThresh):
                break

        #Now if it is below Gtarget, then do SET operations; If it is above Gtarget, then Reset failed and device stuck ON
        
        #if currG <= thisGtarget and thisGtarget >= 2.5e-6:
        if currG <= (thisGtarget-targetGThresh):
            for vgate in vGateSet:
                for vappset in vAppliedSet:
                    # Apply vappset pulse, then read
                    a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)

                    rdCurr = a0.read_single_int(vRead, Vgate, array=arr, row=rr, col=cc, gain=-1)                
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(vappset)
                    if currG >= (thisGtarget-targetGThresh):
                        break
                if currG >= (thisGtarget-targetGThresh):
                    break

    GHistory.append(thisGHistory)
    VHistory.append(thisVHistory)
    print('Array', arr, ', device (row=', rr, 'col=', cc, ') Init G=', initG, ' Target G=', thisGtarget, ' Final G=', currG)

time.sleep(15)
arr = 2
numRows = 64
numCols = 64
vRead = 0.2
vReadGate = 5.0
Gmap2FineTune = np.zeros((numRows, numCols))
for rr in range(numRows):
        for cc in range(numCols):
            rdCurr = a0.read_single_int(vRead, Vgate, array=arr, row=rr, col=cc, gain=-1)
            Gmap2FineTune[rr,cc] = 1e6*rdCurr/vRead
plt.imshow(Gmap2FineTune)
plt.colorbar()

time.sleep(15)
save_workspace(vars(), note='Prober1_FineTuneFCL_ARRAY2')