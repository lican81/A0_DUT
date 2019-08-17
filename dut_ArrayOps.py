import drv_gpio as drv

import dut_func as dut
import numpy as np
import matplotlib as plt
from bitstring import BitArray
from misc import *
from np import random
from np.random import Generator
import time

_gain_table = [
    '0b1111100001',
    '0b1111100010',
    '0b1101000100',
    '0b1100001000',
    '0b1100010000',
]

_gain_ratio = [
    1e3,
    5e3,
    30e3,
    200e3,
    1e6
]


def program_matrix_targets(arr, startRow=0, startCol=0, numRows=2, numCols=2, GMin=2e-6, GMax=200e-6):
    # startRow = 0
    # startCol = 0
    # numRows = 2
    # numCols = 2
    # GMin = 2e-6
    # GMax = 200e-6

    targetGVals = np.linspace(GMin, GMax, numRows)
    targetRows = np.arange(startRow, startRow+numRows+1)
    targetCols = np.arange(startCol, startCol+numCols+1)

    vAppliedSet = np.arange(0.4, 4.15, 0.25)
    vAppliedReset = np.arange(0.4, 3.9, 0.25)
    vGateSet = np.arange(0.4, 2.1, 0.1)
    vGateReset = np.arange(5.0, 5.5, 0.5)
    Vread = 0.2
    volts = []
    GHistory = []
    VHistory = []
    for cc in targetCols:
        # for rr in targetRows:
        for i in range(numRows):
            rr = targetRows[i]
            print('Working on array', arr, ', device (row=', rr, 'col=', cc, ')')
            thisGtarget = targetGVals[i]
            thisGHistory = []
            thisVHistory = []
            # Do a first read of this device
            rg = random.randint(GMin, GMax)
            thisGHistory.append(rg)
            print('  Initial G=', rg, 'Target G =', thisGtarget)
            # Now, if device is lower than target, SET it
            if rg < thisGtarget:
                for vgate in vGateSet:
                    for vappset in vAppliedSet:
                        # Apply vappset pulse, then read
                        rg = random.randint(GMin, GMax)
                        thisGHistory.append(rg)
                        thisVHistory.append(vappset)
                        if rg >= thisGtarget:
                            break
                    if rg >= thisGtarget:
                        break
                GHistory.append(thisGHistory)
                VHistory.append(thisVHistory)

            # Else, if device is higher than target, RESET it
            elif rg > thisGtarget:
                for vgate in vGateReset:
                    for vappreset in vAppliedReset:
                        # Apply vappreset pulse, then read
                        rg = random.randint(GMin, GMax)
                        thisGHistory.append(rg)
                        thisVHistory.append(vappreset)
                        if rg <= thisGtarget:
                            break
                    if rg <= thisGtarget:
                        break
                GHistory.append(thisGHistory)
                VHistory.append(thisVHistory)

            fig, ax1 = plt.subplots()
            color = 'tab:red'
            ax1.set_xlabel('Cycles')
            ax1.set_ylabel('Conductance', color=color)
            ax1.plot(thisGHistory, color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            color = 'tab:blue'
            # we already handled the x-label with ax1
            ax2.set_ylabel('Voltage Applied', color=color)
            ax2.plot(thisVHistory, color=color)
            ax2.tick_params(axis='y', labelcolor=color)
            fig.tight_layout()  # otherwise the right y-label is slightly clipped
            plt.show()
            # fig, ax = plt.subplots()
            # ax.plot(thisGHistory)
            # ax.set(xlabel='cycle', ylabel='Conductance', title='Device')
            # ax.grid()
            # plt.show()


def program_matrix_targets2(arr, startRow=0, startCol=0, numRows=2, numCols=2, GMin=2e-6, GMax=200e-6):
    
    from lib_data import *
    save_workspace(vars(), note='SwitchingArray0')
    Imap = a0.pic_read_batch(gain=2, Vread=0.2)
    plt.imshow(Imap[0]*1e6 / 0.2)
    plt.colorbar()

# doing a careful read
arr = 0
rr = 32
cc = 2
vRead = 0.2
vReadGate = 5.0
gains = np.array([4, 3, 2, 1, 0])
maxCurr = np.array([3.2e-3, 650e-6, 110e-6, 14.0e-6, 3.3e-6])
rdCurr = []
for gg in gains:
    rdCurr = a0.read_single(vRead, vReadGate, array=arr, row=rr, col=cc, gain=gg)
    print('Gain=', gg, ', I=', rdCurr)
    if rdCurr < maxCurr[gg]:
        print(maxCurr[gg])
        break
Gmeas = rdCurr/vRead
print(Gmeas*1e6)

#  doing a careful Array read
arr = 0
numRows = 64
numCols = 64
vRead = 0.2
vReadGate = 5.0
gains = np.array([4, 3, 2, 1, 0])
maxCurr = np.array([3.2e-3, 650e-6, 110e-6, 14.0e-6, 3.3e-6])
Gmeas = np.zeros((numRows, numCols))
for rr in range(numRows)
        for cc in range(numCols)
            for gg in gains:
                    rdCurr = a0.read_single(vRead, vReadGate, array=arr, row=rr, col=cc, gain=gg)
                    print('Device Row =', rr, 'Col =', cc, 'Gain=', gg, ', I=', rdCurr)
                    if rdCurr < maxCurr[gg]:
                        print(maxCurr[gg])
                        break
            Gmeas[rr,cc] = 1e6*rdCurr/vRead
            print(Gmeas[rr,cc]*1e6)

plt.imshow(Gmeas)
plt.colorbar()
    

#
# 8/15/19 Array code for the convolutional kernel programming
#

VreadGate = 5.0
vRead = 0.2

arr = 2
startRow = 0
startCol = 0
numRows = 26
numCols = 14
GMin = 1e-6
GMax = 100e-6

#targetGVals = np.linspace(GMax, GMin, numRows)
targetGVals = Gconv/2
targetRows = np.arange(startRow, startRow+numRows)
targetCols = np.arange(startCol, startCol+numCols)

vAppliedSet = np.arange(0.6, 2.3, 0.05)
vAppliedReset = np.arange(0.5, 2.9, 0.05)
vGateSet = np.arange(0.5, 1.6, 0.05)
vGateReset = np.arange(5.0, 5.5, 0.5)

gains = np.array([4, 3, 2, 1, 0])
maxCurr = np.array([3.3e-3, 650e-6, 110e-6, 14.0e-6, 3.3e-6])

GHistory = []
VHistory = []
for j in range(numCols):
    cc = targetCols[j]
    for i in range(numRows):
        rr = targetRows[i]
        print('Working on array', arr, ', device (row=', rr, 'col=', cc, ')')
        thisGtarget = targetGVals[i,j]
        thisGHistory = []
        thisVHistory = []
        thisGainHistory = []
        # Do a first read of this device
        for gg in gains:
            #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
            rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
            if rdCurr < maxCurr[gg]:
                break
        currG = rdCurr/vRead
        thisGHistory.append(currG)
        thisVHistory.append(0)
        print('Initial G=', currG, 'Target G =', thisGtarget)
        # Now, if device is lower than target, SET it
        if currG < thisGtarget:
            for vgate in vGateSet:
                for vappset in vAppliedSet:
                    # Apply vappset pulse, then read
                    a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                    for gg in gains:
                        #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                        rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                        if rdCurr < maxCurr[gg]:
                            break
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(vappset)
                    if currG >= thisGtarget:
                        break
                if currG >= thisGtarget:
                    break
            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

        # Else, if device is higher than target, RESET it, then SET it
        elif currG > thisGtarget:
            for vgate in vGateReset:
                for vappreset in vAppliedReset:
                    # Apply vappreset pulse, then read
                    a0.reset_single_int(vappreset, vgate, array=arr, row=rr, col=cc)
                    for gg in gains:
                        #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                        rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                        if rdCurr < maxCurr[gg]:
                            break
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(-1*vappreset)
                    if currG <= thisGtarget:
                        break
                if currG <= thisGtarget:
                    break

            #Now if it is below Gtarget, then do SET operations; If it is above Gtarget, then Reset failed and device stuck ON
            
            if currG <= thisGtarget:
                for vgate in vGateSet:
                    for vappset in vAppliedSet:
                        # Apply vappset pulse, then read
                        a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                        for gg in gains:
                            #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                            rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                            if rdCurr < maxCurr[gg]:
                                break
                        currG = rdCurr/vRead
                        thisGHistory.append(currG)
                        thisVHistory.append(vappset)
                        if currG >= thisGtarget:
                            break
                    if currG >= thisGtarget:
                        break

            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

        fig, ax1 = plt.subplots()
        color = 'tab:blue'
        ax1.set_xlabel('Cycles')
        ax1.set_ylabel('Conductance (uS)', color=color)
        ax1.plot([i* 1e6 for i in thisGHistory], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:red'
        # we already handled the x-label with ax1
        ax2.set_ylabel('Voltage Applied', color=color)
        ax2.plot(thisVHistory, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.show()
        
#time.sleep(30)
#save_workspace(vars(), note='KernelProgr26x14_ARRAY2')

#
# 8/15/19 Code for array read operation
#
arr = 2
numRows = 64
numCols = 64
vRead = 0.2
vReadGate = 5.0
gains = np.array([4, 3, 2, 1, 0])
maxCurr = np.array([3.2e-3, 650e-6, 110e-6, 14.0e-6, 3.3e-6])
Gmap1post = np.zeros((numRows, numCols))
for rr in range(numRows):
        for cc in range(numCols):
            for gg in gains:
                    #rdCurr = a0.read_single_int(vRead, vReadGate, array=arr, row=rr, col=cc, gain=gg)
                    rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                    if rdCurr < maxCurr[gg]:
                        break
            Gmap1post[rr,cc] = 1e6*rdCurr/vRead
plt.imshow(Gmap1post)
plt.colorbar()


#8/12/19 Array code using slow autogain read for every read
#

VreadGate = 5.0
vRead = 0.2

arr = 0
startRow = 0
startCol = 14
numRows = 64
numCols = 10
GMin = 2e-6
GMax = 200e-6

targetGVals = np.linspace(GMin, GMax, numRows)
targetRows = np.arange(startRow, startRow+numRows)
targetCols = np.arange(startCol, startCol+numCols)

vAppliedSet = np.arange(0.4, 2.5, 0.1)
vAppliedReset = np.arange(0.4, 2.5, 0.1)
vGateSet = np.arange(0.5, 2.2, 0.1)
vGateReset = np.arange(5.0, 5.5, 0.5)

gains = np.array([4, 3, 2, 1, 0])
maxCurr = np.array([3.3e-3, 650e-6, 110e-6, 14.0e-6, 3.3e-6])

GHistory = []
VHistory = []
for j in range(numCols):
    cc = targetCols[j]
    for i in range(numRows):
        rr = targetRows[i]
        print('Working on array', arr, ', device (row=', rr, 'col=', cc, ')')
        thisGtarget = targetGVals[i]
        thisGHistory = []
        thisVHistory = []
        thisGainHistory = []
        # Do a first read of this device
        for gg in gains:
            rdCurr = a0.read_single(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
            if rdCurr < maxCurr[gg]:
                break
        currG = rdCurr/vRead
        thisGHistory.append(currG)
        thisVHistory.append(0)
        print('Initial G=', currG, 'Target G =', thisGtarget)
        # Now, if device is lower than target, SET it
        if currG < thisGtarget:
            for vgate in vGateSet:
                for vappset in vAppliedSet:
                    # Apply vappset pulse, then read
                    a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                    for gg in gains:
                        rdCurr = a0.read_single(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                        if rdCurr < maxCurr[gg]:
                            break
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(vappset)
                    if currG >= thisGtarget:
                        break
                if currG >= thisGtarget:
                    break
            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

        # Else, if device is higher than target, RESET it, then SET it
        elif currG > thisGtarget:
            for vgate in vGateReset:
                for vappreset in vAppliedReset:
                    # Apply vappreset pulse, then read
                    a0.reset_single_int(vappreset, vgate, array=arr, row=rr, col=cc)
                    for gg in gains:
                        rdCurr = a0.read_single(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                        if rdCurr < maxCurr[gg]:
                            break
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(-1*vappreset)
                    if currG <= thisGtarget:
                        break
                if currG <= thisGtarget:
                    break

            #Now if it is below Gtarget, then do SET operations; If it is above Gtarget, then Reset failed and device stuck ON
            
            if currG <= thisGtarget:
                for vgate in vGateSet:
                    for vappset in vAppliedSet:
                        # Apply vappset pulse, then read
                        a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                        for gg in gains:
                            rdCurr = a0.read_single(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                            if rdCurr < maxCurr[gg]:
                                break
                        currG = rdCurr/vRead
                        thisGHistory.append(currG)
                        thisVHistory.append(vappset)
                        if currG >= thisGtarget:
                            break
                    if currG >= thisGtarget:
                        break

            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

        fig, ax1 = plt.subplots()
        color = 'tab:blue'
        ax1.set_xlabel('Cycles')
        ax1.set_ylabel('Conductance (uS)', color=color)
        ax1.plot([i* 1e6 for i in thisGHistory], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:red'
        # we already handled the x-label with ax1
        ax2.set_ylabel('Voltage Applied', color=color)
        ax2.plot(thisVHistory, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.show()
        
        # Vreads = np.arange(0, 0.5, 0.02)
        # Vggate = 5
        # volts = []
        # for vread in Vreads:
        #     volts.append( a0.read_single(vread, Vggate, array=arr, row=rr, col=cc, gain=thisGain) )                
        # plt.plot(Vreads, [i* 1e6 for i in volts], '.-')

        # plt.xlabel('V_device')
        # plt.ylabel('Calculated current (uA)')
        # plt.grid(True, alpha=0.3)
#print('GHistory=', GHistory)
#print('VHistory=', VHistory)

#

gainRes = np.array([1e3, 5e3, 3e4, 2e5, 1e6])
maxGainCurr = 3.5*0.85/gainRes
VreadGate = 5.0

maxGRange = np.array([1e-6, 8e-6, 16e-6, 32e-6, 64e-6, 100e-6, 165e-6, 300e-6, 500e-6])
gainChoice = np.array([4, 4, 4, 4, 4, 3, 3, 3])
minCurrentExp = np.array([1e-6, 1e-6, 1e-6, 1e-6, 1e-6, 1e-6, 1e-6, 1e-6])
readV = np.array([0.4, 0.2, 0.1, 0.05, 0.03, 0.1, 0.05, 0.03])
readV2 = 0.75*readV

arr = 0
startRow = 0
startCol = 13
numRows = 10
numCols = 1
GMin = 4e-6
GMax = 100e-6

targetGVals = np.linspace(GMin, GMax, numRows)
targetRows = np.arange(startRow, startRow+numRows)
targetCols = np.arange(startCol, startCol+numCols)

#gainForTargetG = 4-np.searchsorted(np.flip(maxGainCurr),targetGVals)
targetGIndexSetting = np.searchsorted(maxGRange,targetGVals)

vAppliedSet = np.arange(0.3, 2.6, 0.1)
vAppliedReset = np.arange(0.3, 2.6, 0.1)
vGateSet = np.arange(0.5, 2.2, 0.1)
vGateReset = np.arange(5.0, 5.5, 0.5)
GHistory = []
VHistory = []
for j in range(numCols):
    cc = targetCols[j]
    for i in range(numRows):
        rr = targetRows[i]
        print('Working on array', arr, ', device (row=', rr, 'col=', cc, ')')
        thisGtarget = targetGVals[i]
        #thisGain = gainForTargetG[i]
        thisGain = gainChoice[targetGIndexSetting[i]]
        thisReadV = readV[targetGIndexSetting[i]]
        thisReadV2 = readV2[targetGIndexSetting[i]]
        minCurrExp = minCurrentExp[targetGIndexSetting[i]]
        thisGHistory = []
        thisVHistory = []
        thisGainHistory = []
        # Do a first read of this device
        currI1 = max(a0.read_single_int(thisReadV, VreadGate, array=arr, row=rr, col=cc, gain=thisGain), minCurrExp)
        currI2 = max(a0.read_single_int(thisReadV2, VreadGate, array=arr, row=rr, col=cc, gain=thisGain), minCurrExp)
        currG = (currI1-currI2)/(thisReadV-thisReadV2)
        thisGHistory.append(currG)
        thisVHistory.append(0)
        print('Initial G=', currG, 'Target G =', thisGtarget)
        print('Using Gain=', thisGain, 'Vread=', thisReadV, 'Vread2=', thisReadV2)        
        # Now, if device is lower than target, SET it
        if currG < thisGtarget:
            for vgate in vGateSet:
                for vappset in vAppliedSet:
                    # Apply vappset pulse, then read
                    a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                    currI1 = max(a0.read_single_int(thisReadV, VreadGate, array=arr, row=rr, col=cc, gain=thisGain), minCurrExp)
                    currI2 = max(a0.read_single_int(thisReadV2, VreadGate, array=arr, row=rr, col=cc, gain=thisGain), minCurrExp)
                    #currI1 = a0.read_single_int(thisReadV, VreadGate, array=arr, row=rr, col=cc, gain=thisGain)
                    #currI2 = a0.read_single_int(thisReadV2, VreadGate, array=arr, row=rr, col=cc, gain=thisGain)
                    currG = (currI1-currI2)/(thisReadV-thisReadV2)
                    thisGHistory.append(currG)
                    thisVHistory.append(vappset)
                    if currG >= thisGtarget:
                        break
                if currG >= thisGtarget:
                    break
            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

        # Else, if device is higher than target, RESET it
        elif currG > thisGtarget:
            for vgate in vGateReset:
                for vappreset in vAppliedReset:
                    # Apply vappreset pulse, then read
                    a0.reset_single_int(vappreset, vgate, array=arr, row=rr, col=cc)
                    currI1 = max(a0.read_single_int(thisReadV, VreadGate, array=arr, row=rr, col=cc, gain=thisGain), minCurrExp)
                    currI2 = max(a0.read_single_int(thisReadV2, VreadGate, array=arr, row=rr, col=cc, gain=thisGain), minCurrExp)
                    #currI1 = a0.read_single_int(thisReadV, VreadGate, array=arr, row=rr, col=cc, gain=thisGain)
                    #currI2 = a0.read_single_int(thisReadV2, VreadGate, array=arr, row=rr, col=cc, gain=thisGain)
                    currG = (currI1-currI2)/(thisReadV-thisReadV2)                    
                    thisGHistory.append(currG)
                    thisVHistory.append(-1*vappreset)
                    if currG <= thisGtarget:
                        break
                if currG <= thisGtarget:
                    break
            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

        fig, ax1 = plt.subplots()
        color = 'tab:blue'
        ax1.set_xlabel('Cycles')
        ax1.set_ylabel('Conductance (uS)', color=color)
        ax1.plot([i* 1e6 for i in thisGHistory], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:red'
        # we already handled the x-label with ax1
        ax2.set_ylabel('Voltage Applied', color=color)
        ax2.plot(thisVHistory, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.show()
        
        Vreads = np.arange(0, 0.5, 0.02)
        Vggate = 5
        volts = []
        for vread in Vreads:
            volts.append( a0.read_single(vread, Vggate, array=arr, row=rr, col=cc, gain=thisGain) )                
        plt.plot(Vreads, [i* 1e6 for i in volts], '.-')

        plt.xlabel('V_device')
        plt.ylabel('Calculated current (uA)')
        plt.grid(True, alpha=0.3)

    print('GHistory=', GHistory)
    print('VHistory=', VHistory)

    
    
    gainRes = np.array([1e3, 5e3, 3e4, 2e5, 1e6])
    Vread = 0.2
    maxGainCurr = 3.5*0.85/gainRes
    VreadGate = 5.0

    arr = 1
    startRow = 30
    startCol = 0
    numRows = 2
    numCols = 1
    GMin = 40e-6
    GMax = 80e-6

    targetGVals = np.linspace(GMin, GMax, numRows)
    sampGVals = np.linspace(GMin, GMax, 10*numRows)
    targetRows = np.arange(startRow, startRow+numRows+1)
    targetCols = np.arange(startCol, startCol+numCols+1)

    gainForTargetG = 4-np.searchsorted(np.flip(maxGainCurr),targetGVals)

    vAppliedSet = np.arange(0.4, 4.15, 0.25)
    vAppliedReset = np.arange(0.4, 3.9, 0.25)
    vGateSet = np.arange(0.5, 2.1, 0.1)
    vGateReset = np.arange(5.0, 5.5, 0.5)
    GHistory = []
    VHistory = []
    for j in range(numCols):
        cc = targetCols[j]
        # for rr in targetRows:
        for i in range(numRows):
            rr = targetRows[i]
            print('Working on array', arr, ', device (row=', rr, 'col=', cc, ')')
            thisGtarget = targetGVals[i]
            thisGain = gainForTargetG[i]
            thisGHistory = []
            thisVHistory = []
            thisGainHistory = []
            # Do a first read of this device
            currG = a0.read_single(Vread, VreadGate, array=arr, row=rr, col=cc, gain=thisGain)/Vread
            # rg = sampGVals[random.randint(0, 10*numRows)]
            thisGHistory.append(rg)
            thisVHistory.append(0)
            print('  Initial G=', rg, 'Target G =', thisGtarget)
            # Now, if device is lower than target, SET it
            if currG < thisGtarget:
                for vgate in vGateSet:
                    for vappset in vAppliedSet:
                        # Apply vappset pulse, then read
                        a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                        #rg = sampGVals[random.randint(0, 10*numRows)]
                        currG = a0.read_single(Vread, VreadGate, array=arr, row=rr, col=cc, gain=thisGain)/Vread
                        thisGHistory.append(currG)
                        thisVHistory.append(vappset)
                        if currG >= thisGtarget:
                            break
                    if currG >= thisGtarget:
                        break
                GHistory.append(thisGHistory)
                VHistory.append(thisVHistory)

            # Else, if device is higher than target, RESET it
            elif currG > thisGtarget:
                for vgate in vGateReset:
                    for vappreset in vAppliedReset:
                        # Apply vappreset pulse, then read
                        # a0.reset_single_int(vreset, Vgate, array=ar, row=r, col=c)
                        currG = sampGVals[random.randint(0, 10*numRows)]
                        thisGHistory.append(currG)
                        thisVHistory.append(vappreset)
                        if currG <= thisGtarget:
                            break
                    if currG <= thisGtarget:
                        break
                GHistory.append(thisGHistory)
                VHistory.append(thisVHistory)

            fig, ax1 = plt.subplots()
            color = 'tab:blue'
            ax1.set_xlabel('Cycles')
            ax1.set_ylabel('Conductance', color=color)
            ax1.plot(thisGHistory, color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            color = 'tab:red'
            # we already handled the x-label with ax1
            ax2.set_ylabel('Voltage Applied', color=color)
            ax2.plot(thisVHistory, color=color)
            ax2.tick_params(axis='y', labelcolor=color)
            fig.tight_layout()  # otherwise the right y-label is slightly clipped
            plt.show()
        print('GHistory=', GHistory)
        print('VHistory=', VHistory)


def programConvolLayer(array=0):
#
from lib_data import *
load_workspace(vars(), '20190814-205207-CNN weights')

VreadGate = 5.0
vRead = 0.2

arr = 1
startRow = 0
startCol = 0
numRows = 26
numCols = 14
GMin = 1e-6
GMax = 100e-6

#targetGVals = np.linspace(GMax, GMin, numRows)
targetGVals = Gconv/2
targetRows = np.arange(startRow, startRow+numRows)
targetCols = np.arange(startCol, startCol+numCols)

vAppliedSet = np.arange(0.6, 2.4, 0.05)
vAppliedReset = np.arange(0.5, 3.2, 0.05)
vGateSet = np.arange(0.5, 1.6, 0.05)
vGateReset = np.arange(5.0, 5.5, 0.5)

gains = np.array([4, 3, 2, 1, 0])
maxCurr = np.array([3.3e-3, 650e-6, 110e-6, 14.0e-6, 3.3e-6])

GHistory = []
VHistory = []
for j in range(numCols):
    cc = targetCols[j]
    for i in range(numRows):
        rr = targetRows[i]
        print('Working on array', arr, ', device (row=', rr, 'col=', cc, ')')
        thisGtarget = targetGVals[i,j]
        thisGHistory = []
        thisVHistory = []
        thisGainHistory = []
        # Do a first read of this device
        for gg in gains:
            #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
            rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
            if rdCurr < maxCurr[gg]:
                break
        currG = rdCurr/vRead
        thisGHistory.append(currG)
        thisVHistory.append(0)
        print('Initial G=', currG, 'Target G =', thisGtarget)
        # Now, if device is lower than target, SET it
        if currG < thisGtarget:
            for vgate in vGateSet:
                for vappset in vAppliedSet:
                    # Apply vappset pulse, then read
                    a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                    for gg in gains:
                        #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                        rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                        if rdCurr < maxCurr[gg]:
                            break
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(vappset)
                    if currG >= thisGtarget:
                        break
                if currG >= thisGtarget:
                    break
            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

        # Else, if device is higher than target, RESET it, then SET it
        elif currG > thisGtarget:
            for vgate in vGateReset:
                for vappreset in vAppliedReset:
                    # Apply vappreset pulse, then read
                    a0.reset_single_int(vappreset, vgate, array=arr, row=rr, col=cc)
                    for gg in gains:
                        #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                        rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                        if rdCurr < maxCurr[gg]:
                            break
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(-1*vappreset)
                    if currG <= thisGtarget:
                        break
                if currG <= thisGtarget:
                    break

            #Now if it is below Gtarget, then do SET operations; If it is above Gtarget, then Reset failed and device stuck ON
            
            if currG <= thisGtarget:
                for vgate in vGateSet:
                    for vappset in vAppliedSet:
                        # Apply vappset pulse, then read
                        a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                        for gg in gains:
                            #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                            rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                            if rdCurr < maxCurr[gg]:
                                break
                        currG = rdCurr/vRead
                        thisGHistory.append(currG)
                        thisVHistory.append(vappset)
                        if currG >= thisGtarget:
                            break
                    if currG >= thisGtarget:
                        break

            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

        fig, ax1 = plt.subplots()
        color = 'tab:blue'
        ax1.set_xlabel('Cycles')
        ax1.set_ylabel('Conductance (uS)', color=color)
        ax1.plot([i* 1e6 for i in thisGHistory], color=color)
        ax1.tick_params(axis='y', labelcolor=color)
        ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
        color = 'tab:red'
        # we already handled the x-label with ax1
        ax2.set_ylabel('Voltage Applied', color=color)
        ax2.plot(thisVHistory, color=color)
        ax2.tick_params(axis='y', labelcolor=color)
        fig.tight_layout()  # otherwise the right y-label is slightly clipped
        plt.show()
        
time.sleep(30)
save_workspace(vars(), note='KernelProgr26x14_DPEProber1Arr1')


def programFullConnectedLayer(array=0):
    '''
    Args,

    Returns:
        Gmapping of array
    '''

from lib_data import *
load_workspace(vars(), '20190814-205207-CNN weights')

VreadGate = 5.0
vRead = 0.2
arr = 0
startRow = 0
startCol = 0
numRows = 57
numCols = 40
GMin = 1e-6
GMax = 100e-6
# Scale down Gfc from 0 to 200uS to 100uS
scaledGfc = Gfc/2
# First reshape Gfc to fit within the 64 rows
# reshape from 113x20 to 57x40
newGfc = np.zeros((57,40))+GMin
newGfc[0:57,0:20]=scaledGfc[0:57,0:20]
newGfc[0:56,20:40]=scaledGfc[57:113,0:20]

targetGVals = newGfc
targetRows = np.arange(startRow, startRow+numRows)
targetCols = np.arange(startCol, startCol+numCols)

vAppliedSet = np.arange(0.5, 2.5, 0.05)
vAppliedReset = np.arange(0.5, 3.1, 0.05)
vGateSet = np.arange(0.5, 1.7, 0.05)
vGateReset = np.arange(5.0, 5.5, 0.5)

gains = np.array([4, 3, 2, 1, 0])
maxCurr = np.array([3.3e-3, 650e-6, 110e-6, 14.0e-6, 3.3e-6])
#tmpRows = np.arange(45, 57, 1)
#tmpRows = np.array([34])

GHistory = []
VHistory = []
for j in range(numCols):
    cc = targetCols[j]
    for i in range(numRows):
        rr = targetRows[i]
        print('Working on array', arr, ', device (row=', rr, 'col=', cc, ')')
        thisGtarget = targetGVals[i,j]
        thisGHistory = []
        thisVHistory = []
        thisGainHistory = []
        # Do a first read of this device
        for gg in gains:
            #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
            rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
            if rdCurr < maxCurr[gg]:
                break
        currG = rdCurr/vRead
        thisGHistory.append(currG)
        thisVHistory.append(0)
        print('Initial G=', currG, 'Target G =', thisGtarget)
        # Now, if device is lower than target, SET it
        if currG < thisGtarget:
            for vgate in vGateSet:
                for vappset in vAppliedSet:
                    # Apply vappset pulse, then read
                    a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                    for gg in gains:
                        #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                        rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                        if rdCurr < maxCurr[gg]:
                            break
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(vappset)
                    if currG >= thisGtarget:
                        break
                if currG >= thisGtarget:
                    break
            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

        # Else, if device is higher than target, RESET it, then SET it
        elif currG > thisGtarget:
            for vgate in vGateReset:
                for vappreset in vAppliedReset:
                    # Apply vappreset pulse, then read
                    a0.reset_single_int(vappreset, vgate, array=arr, row=rr, col=cc)
                    for gg in gains:
                        #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                        rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                        if rdCurr < maxCurr[gg]:
                            break
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(-1*vappreset)
                    if currG <= thisGtarget:
                        break
                if currG <= thisGtarget:
                    break

            #Now if it is below Gtarget, then do SET operations; If it is above Gtarget, then Reset failed and device stuck ON
            
            if currG <= thisGtarget and thisGtarget >= 2.5e-6:
                for vgate in vGateSet:
                    for vappset in vAppliedSet:
                        # Apply vappset pulse, then read
                        a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                        for gg in gains:
                            #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                            rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                            if rdCurr < maxCurr[gg]:
                                break
                        currG = rdCurr/vRead
                        thisGHistory.append(currG)
                        thisVHistory.append(vappset)
                        if currG >= thisGtarget:
                            break
                    if currG >= thisGtarget:
                        break

            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

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
        
time.sleep(30)
arr = 0
numRows = 64
numCols = 64
vRead = 0.2
vReadGate = 5.0
gains = np.array([4, 3, 2, 1, 0])
maxCurr = np.array([3.2e-3, 650e-6, 110e-6, 14.0e-6, 3.3e-6])
Gmap0post = np.zeros((numRows, numCols))
for rr in range(numRows):
        for cc in range(numCols):
            for gg in gains:
                    #rdCurr = a0.read_single_int(vRead, vReadGate, array=arr, row=rr, col=cc, gain=gg)
                    rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                    if rdCurr < maxCurr[gg]:
                        break
            Gmap0post[rr,cc] = 1e6*rdCurr/vRead
plt.imshow(Gmap0post)
plt.colorbar()

time.sleep(30)
save_workspace(vars(), note='FullyConnProgr57x40_ARRAY0')

def programFullConnectedLayerContd(array=0):
    '''
    Args,

    Returns:
        Gmapping of array
    '''

from lib_data import *
load_workspace(vars(), '20190814-205207-CNN weights')

VreadGate = 5.0
vRead = 0.2
arr = 0
startRow = 0
startCol = 0
numRows = 57
numCols = 40
GMin = 1e-6
GMax = 100e-6
# Scale down Gfc from 0 to 200uS to 100uS
scaledGfc = Gfc/2
# First reshape Gfc to fit within the 64 rows
# reshape from 113x20 to 57x40
newGfc = np.zeros((57,40))+GMin
newGfc[0:57,0:20]=scaledGfc[0:57,0:20]
newGfc[0:56,20:40]=scaledGfc[57:113,0:20]

targetGVals = newGfc
targetRows = np.arange(startRow, startRow+numRows)
targetCols = np.arange(startCol, startCol+numCols)

vAppliedSet = np.arange(0.5, 2.5, 0.05)
vAppliedReset = np.arange(0.5, 3.1, 0.05)
vGateSet = np.arange(0.5, 1.7, 0.05)
vGateReset = np.arange(5.0, 5.5, 0.5)

gains = np.array([4, 3, 2, 1, 0])
maxCurr = np.array([3.3e-3, 650e-6, 110e-6, 14.0e-6, 3.3e-6])
tmpRows = np.arange(45, 57, 1)
tmpCols = np.array([35, 36, 37, 38, 39])

GHistory = []
VHistory = []
for j in tmpCols:
    cc = targetCols[j]
    for i in range(numRows):
        rr = targetRows[i]
        print('Working on array', arr, ', device (row=', rr, 'col=', cc, ')')
        thisGtarget = targetGVals[i,j]
        thisGHistory = []
        thisVHistory = []
        thisGainHistory = []
        # Do a first read of this device
        for gg in gains:
            #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
            rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
            if rdCurr < maxCurr[gg]:
                break
        currG = rdCurr/vRead
        thisGHistory.append(currG)
        thisVHistory.append(0)
        print('Initial G=', currG, 'Target G =', thisGtarget)
        # Now, if device is lower than target, SET it
        if currG < thisGtarget:
            for vgate in vGateSet:
                for vappset in vAppliedSet:
                    # Apply vappset pulse, then read
                    a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                    for gg in gains:
                        #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                        rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                        if rdCurr < maxCurr[gg]:
                            break
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(vappset)
                    if currG >= thisGtarget:
                        break
                if currG >= thisGtarget:
                    break
            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

        # Else, if device is higher than target, RESET it, then SET it
        elif currG > thisGtarget:
            for vgate in vGateReset:
                for vappreset in vAppliedReset:
                    # Apply vappreset pulse, then read
                    a0.reset_single_int(vappreset, vgate, array=arr, row=rr, col=cc)
                    for gg in gains:
                        #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                        rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                        if rdCurr < maxCurr[gg]:
                            break
                    currG = rdCurr/vRead
                    thisGHistory.append(currG)
                    thisVHistory.append(-1*vappreset)
                    if currG <= thisGtarget:
                        break
                if currG <= thisGtarget:
                    break

            #Now if it is below Gtarget, then do SET operations; If it is above Gtarget, then Reset failed and device stuck ON
            
            if currG <= thisGtarget and thisGtarget >= 2.5e-6:
                for vgate in vGateSet:
                    for vappset in vAppliedSet:
                        # Apply vappset pulse, then read
                        a0.set_single_int(vappset, vgate, array=arr, row=rr, col=cc)
                        for gg in gains:
                            #rdCurr = a0.read_single_int(vRead, VreadGate, array=arr, row=rr, col=cc, gain=gg)
                            rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                            if rdCurr < maxCurr[gg]:
                                break
                        currG = rdCurr/vRead
                        thisGHistory.append(currG)
                        thisVHistory.append(vappset)
                        if currG >= thisGtarget:
                            break
                    if currG >= thisGtarget:
                        break

            GHistory.append(thisGHistory)
            VHistory.append(thisVHistory)

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
        
time.sleep(30)
arr = 0
numRows = 64
numCols = 64
vRead = 0.2
vReadGate = 5.0
gains = np.array([4, 3, 2, 1, 0])
maxCurr = np.array([3.2e-3, 650e-6, 110e-6, 14.0e-6, 3.3e-6])
Gmap0post = np.zeros((numRows, numCols))
for rr in range(numRows):
        for cc in range(numCols):
            for gg in gains:
                    #rdCurr = a0.read_single_int(vRead, vReadGate, array=arr, row=rr, col=cc, gain=gg)
                    rdCurr = a0.pic_read_single(arr, rr, cc, Vread = vRead, skip_conf=False, gain=gg)
                    if rdCurr < maxCurr[gg]:
                        break
            Gmap0post[rr,cc] = 1e6*rdCurr/vRead
plt.imshow(Gmap0post)
plt.colorbar()

time.sleep(30)
save_workspace(vars(), note='FullyConnProgr57x40_ARRAY0_contd')

def read_single_2step():
adc_raw = a0.read_single_int(vread, Vgate, array=ar, row=r, col=c, gain=-1, raw=True)
print(f'{result:013b}')

volt = dut.adc2volt(adc_raw)
print(f'{volt:.4f} V')

gain = adc_raw >> 10
print(f'gain = {gain:d}')

curr = a0.adc2current(adc_raw, 0.5)
print(f'curr = {curr*1e6:.4f} uA')

def read_single_int_array(Vread, Vgate, array=0, row=0, col=0, gain=0, Tsh=0x0c, Vref=0.5):
    '''
    Args,

    Returns:
        The ADC readout voltages
    '''
    VREF_TIA = Vref
    VREF_LO = 0.5

    dut.scan_control(scan_ctrl_bits=bytes([0x10, 0x02, 0x0c, 0x10,
                                           Tsh, 0x01, 0x02]))
    # dut.scan_control(scan_ctrl_bits=bytes([0x10, 0x02, Tsh, 0x10,
    #                                        0x20, 0x01, 0x02]))
    dut.scan_tia(BitArray(_gain_table[gain]*96).bytes)

    # Make sure the VPP is reasonable
    assert VREF_TIA - Vread > -0.2 and VREF_TIA - Vread <= 1

    dut.dac_set('PLANE_VPP', VREF_TIA - Vread)
    dut.dac_set('P_VREF_TIA', VREF_TIA)
    dut.dac_set('P_TVDD', Vgate)

    data_load = dut.data_generate_sparse([row, col])
    dut.load_vectors(array=array, data=data_load)

    dut.pads_defaults()

    dut.reset_dpe()

    drv.gpio_pin_set(*PIC_PINS['DPE_INTERNAL_EN'])
    drv.gpio_pin_set(*PIC_PINS['READ_BIT'])
    drv.gpio_pin_reset(*PIC_PINS['READ_DPE'])

    # drv.gpio_nforce_safe_write(0b100)
    drv.gpio_nforce_safe_write(0b1 << array)
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    time.sleep(2e-7)
    drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])

    [fifo_en, channel] = dut.which_fifo([array, col])

    data = dut.download_fifo(fifo_en)
    volt = dut.adc2volt(data[channel]) - VREF_LO

    return volt / _gain_ratio[gain]


def reset_single_int_array(Vreset, Vgate, array=0, row=0, col=0):
    #     Vreset = 1
    # Vgate = 5
    Twidth = 1e-6

    ar = array
    r = row
    c = col

    dut.scan_control(scan_ctrl_bits=bytes([0xff, 0x01, 0x0c, 0x10,
                                           0x20, 0x01, 0x02]))
    data_load = dut.data_generate_sparse([r, c])
    dut.load_vectors(array=ar, data=data_load)

    dut.pads_defaults()

    drv.gpio_pin_reset(*PIC_PINS['WRITE_ADD_CAP'])
    drv.gpio_pin_set(*PIC_PINS['WRT_INTERNAL_EN'])
    # drv.gpio_pin_set(*PIC_PINS['WRITE_SEL_EXT'])
    dut.reset_dpe()

    dut.dac_set('DAC_VP_PAD', 0)

    drv.gpio_nforce_safe_write(0b1 << ar)

    drv.gpio_pin_set(*PIC_PINS['COL_WRITE_CONNECT'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])
    dut.dac_set('DAC_VP_PAD', Vreset)
    drv.gpio_pin_set(*PIC_PINS['WRT_PULSE'])
    drv.gpio_pin_reset(*PIC_PINS['WRT_PULSE'])

    time.sleep(Twidth)        # delay(as necessary to write)
    dut.dac_set('DAC_VP_PAD', 0)

    drv.gpio_pin_reset(*PIC_PINS['CONNECT_COLUMN_T'])
    drv.gpio_pin_reset(*PIC_PINS['COL_WRITE_CONNECT'])
    drv.gpio_nforce_safe_write(0)


def set_single_int(Vset, Vgate, array=0, row=0, col=0):
    #     Vset = 1
    #     Vgate = 1
    Twidth = 1e-6
    ar = array
    r = row
    c = col
    dut.scan_control(scan_ctrl_bits=bytes([0x80, 0x01, 0x0c, 0x10,
                                           0x20, 0x01, 0x02]))
    data_load = dut.data_generate_sparse([r, c])
    dut.load_vectors(array=ar, data=data_load)

    dut.pads_defaults()
    drv.gpio_pin_set(*PIC_PINS['WRT_INTERNAL_EN'])
    drv.gpio_pin_reset(*PIC_PINS['WRITE_ADD_CAP'])
    # drv.gpio_pin_set(*PIC_PINS['WRITE_SEL_EXT'])

    dut.reset_dpe()

    dut.dac_set('DAC_VP_PAD', 0)

    drv.gpio_pin_set(*PIC_PINS['WRITE_FWD'])

    drv.gpio_nforce_safe_write(0b1 << ar)

    drv.gpio_pin_set(*PIC_PINS['ROW_WRITE_CONNECT'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])
    dut.dac_set('P_TVDD', Vgate)
    dut.dac_set('DAC_VP_PAD', Vset)
    drv.gpio_pin_set(*PIC_PINS['WRT_PULSE'])
    drv.gpio_pin_reset(*PIC_PINS['WRT_PULSE'])

    # time.sleep(Twidth)

    drv.gpio_pin_reset(*PIC_PINS['CONNECT_COLUMN_T'])
    drv.gpio_pin_reset(*PIC_PINS['ROW_WRITE_CONNECT'])
    dut.dac_set('DAC_VP_PAD', 0)
    drv.gpio_nforce_safe_write(0)
