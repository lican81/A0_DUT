import dut_func as dut
import numpy as np
from bitstring import BitArray
from misc import *
import time
import struct

drv = dut.drv

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

_sh_default = [
    # This table assumes the chip runs at 50 MHz
    12,
    12,
    12,
    25,
    100
]


'''
The parameters may be different for each device. You can try and decide which is best for your device. If you don't want to change it,
you can delete or change the decorator above each function.
'''

def read_corr(Vref):
    def middle(func):
        def wrapper(*args,**kwargs):
            raw_adc=func(*args,**kwargs,raw='True')
            g=raw_adc>>10
            VADC_read_first=dut.adc2volt(raw_adc)
            secondVRefHiCmp=4.0+(Vref-VADC_read_first)
            dut.dac_set('DAC_VREF_HI_CMP', secondVRefHiCmp)
            VADC_read_sec = dut.adc2volt(func(*args,**kwargs,raw='True'))
            finalADCOut = VADC_read_sec - (secondVRefHiCmp - 4.0) 
            dut.dac_set('DAC_VREF_HI_CMP', 4.0)
            rdcurr=(finalADCOut-0.5)/_gain_ratio[g]
            return rdcurr
        return wrapper
    return middle


def read_corr_batch(func):
    def wrapper(*args,**kwargs):
        raw_adc=func(*args,**kwargs,raw='True')
        Imap=np.zeros(raw_adc.shape)
        gain=raw_adc>>10
        Ratio=np.zeros(gain.shape)
        for g in range(len(_gain_ratio)):
            Ratio[gain==g]=_gain_ratio[g]
        Vadc_read=dut.adc2volt(raw_adc)
        I=(Vadc_read-0.5)/Ratio
        index4=np.where(np.logical_and(Vadc_read>=2.0,Vadc_read<2.5))
        index3=np.where(np.logical_and(Vadc_read>=1.5,Vadc_read<2.0))
        index2=np.where(np.logical_and(Vadc_read>=1.0,Vadc_read<1.5))
        index1=np.where(np.logical_and(Vadc_read>=0.5,Vadc_read<1.0))
        index5=np.where(np.logical_and(Vadc_read>=2.5,Vadc_read<3.0))
        index6=np.where(np.logical_and(Vadc_read>=3.0,Vadc_read<3.5))
        index7=np.where(np.logical_and(Vadc_read>=3.5,Vadc_read<=4.0))
        Imap[index4]=I[index4]
        VRefHi=[1.0,1.5,2.0,3.0,3.5,4.0]
        Index=[index1,index2,index3,index5,index6,index7]
        for i in range(6):
            dut.dac_set('DAC_VREF_HI_CMP', 4.0+(2.5-VRefHi[i]))
            raw_adc_corr=func(*args,**kwargs,raw='True')
            gain_corr=raw_adc_corr>>10
            ratio=np.zeros(gain_corr.shape)
            for g in range(len(_gain_ratio)):
                ratio[gain==g]=_gain_ratio[g]
                
            I_corr=((dut.adc2volt(raw_adc_corr)-(2.5-VRefHi[i]))-0.5)/ratio
            Imap[Index[i]]=I_corr[Index[i]]
        dut.dac_set('DAC_VREF_HI_CMP',4.0)   
        return Imap
    return wrapper

def adc2current(data, Vref):
    '''
    Converts the RAW adc value to current.

    Args:
        data(uint16): The raw adc data or a data array
        Vref:         The VREF_TIA
    Returns:
        float:        The converted current
    '''
    gain = data >> 10
    return (dut.adc2volt(data) - Vref) / _gain_ratio[gain]


def adc2current_array(data, Vref):
    '''
    Converts the RAW adc values to currents.

    Args:
        data(np.ndarray): The raw adc data or a data array
        Vref:             The VREF_TIA
    Returns:
        np.ndarray:        The converted current
    '''
    gain = data >> 10

    ratio = np.zeros(gain.shape)
    for g in range(len(_gain_ratio)):
        ratio[gain == g] = _gain_ratio[g]

    currents = (dut.adc2volt(data) - Vref) / ratio

    return currents


def pic_read_config(**kwargs):
    '''
    Configure read voltage, timing, gain, etc. 
    They should stay unchanged for the most of the time.
    '''

    Vread = kwargs['Vread'] if 'Vread' in kwargs.keys() else 0.2
    Vgate = kwargs['Vgate'] if 'Vgate' in kwargs.keys() else 5
    gain = kwargs['gain'] if 'gain' in kwargs.keys() else 0
    Tsh = kwargs['Tsh'] if 'Tsh' in kwargs.keys() else _sh_default[gain]
    Vref = kwargs['Vref'] if 'Vref' in kwargs.keys() else 0.425
    Tagc = kwargs['Tagc'] if 'Tagc' in kwargs.keys() else 0x24

    VREF_TIA = Vref

    # print(vars())
    dut.scan_control(scan_ctrl_bits=bytes([0x10, 0x02, Tagc, 0x10,
                                           Tsh, 0x01, 0x02]))

    dut.scan_tia(BitArray(_gain_table[gain]*96).bytes)

    assert VREF_TIA - Vread > -0.2 and VREF_TIA - Vread <= 1

    # print(vars())

    dut.dac_set('PLANE_VPP', VREF_TIA - Vread)
    dut.dac_set('P_VREF_TIA', VREF_TIA)
    dut.dac_set('P_TVDD', Vgate)

    dut.pads_defaults()
    dut.reset_dpe()


@read_corr(2.25)
def pic_read_single(array, row, col, skip_conf=False, raw=False,
                    **kwargs):
    '''
    Read a single device with PIC control
    '''
    gain = kwargs['gain'] if 'gain' in kwargs.keys() else -1
    Vref = kwargs['Vref'] if 'Vref' in kwargs.keys() else 0.5

    # autogain if gain=-1
    mode = 1 if gain == -1 else 0

    if not skip_conf:
        pic_read_config(**kwargs)

    drv.ser.write(f'401,{array},{row},{col},{mode}\0'.encode())
    value = drv.ser.read(2)
    value = struct.unpack('<H', value)[0]

    if raw:
        return value
    else:
        return adc2current(value, Vref)

@read_corr(2.25)
def pic_read_single_test(array, row, col, skip_conf=False, raw=False,
                    **kwargs):
    '''
    Read a single device with PIC control
    '''
    gain = kwargs['gain'] if 'gain' in kwargs.keys() else 0
    Vref = kwargs['Vref'] if 'Vref' in kwargs.keys() else 0.5

    T1 = kwargs['T1'] if 'T1' in kwargs.keys() else 0
    T2 = kwargs['T2'] if 'T2' in kwargs.keys() else 0
    T3 = kwargs['T3'] if 'T3' in kwargs.keys() else 0
    Nt = kwargs['Nt'] if 'Nt' in kwargs.keys() else 1

    # autogain if gain=-1
    mode = 1 if gain == -1 else 0

    if not skip_conf:
        pic_read_config(**kwargs)

    drv.ser.write(f'411,{array},{row},{col},{mode},{T1},{T2},{T3},{Nt}\0'.encode())
    value = drv.ser.read(2)
    value = struct.unpack('<H', value)[0]

    if raw:
        return value
    else:
        return adc2current(value, Vref)

@read_corr_batch
def pic_read_batch(array, raw=False, **kwargs):
    '''
    Read a entire array.

    Args:
        array(int): The array number to read

    Returns:
        np.ndarray: Calcuated current map
    '''
    gain = kwargs['gain'] if 'gain' in kwargs.keys() else 0
    Vref = kwargs['Vref'] if 'Vref' in kwargs.keys() else 0.5
    Tdly = kwargs['Tdly'] if 'Tdly' in kwargs.keys() else 1000

    # autogain if gain=-1
    mode = 1 if gain == -1 else 0

    pic_read_config(**kwargs)

    drv.ser.flushInput()
    drv.ser.write(f'402,{array},{mode},{Tdly}\0'.encode())
    data = []

    r = 0
    while True:
        value = drv.ser.read(2 * 256)
        if len(value) == 0:
            print(f'.', end='')
            continue
        value = struct.unpack('<' + 'H'*256, value)
        data.append(value)

        r += 4
        if r >= 64:
            break

    data = np.array(data).reshape((64, 64))

    if raw:
        return data
    else:
        # return (dut.adc2volt(data) - Vref) / _gain_ratio[gain]
        return adc2current_array(data, Vref)


def pic_dpe_cols(array, col_en=[0xffff, 0xffff, 0xffff, 0xffff]):
    data_load = dut.data_generate_vector(
        [0x0, 0x0, 0x0, 0x0], col_en)
    dut.load_vectors(array=array, data=data_load)


@read_corr_batch
def pic_dpe_batch(array, input, skip_conf=False, raw=False,
                  col_en=[0xffff, 0xffff, 0xffff, 0xffff],
                  **kwargs):
    '''
    Perform DPE (vector-matrix multiplication) operation

    Args:
        array(int): The array number to read
        input(list): Each element is a 64-bit unsigned integer
                     representing a 64-dimensional input vector
        mode(int): 0 -> ground unselected rows and normal gain
                   1 -> float unselected rows and normal gain
                   2 -> ground unselected rows and auto gain
                   3 -> float unselected rows and auto gain

    Returns:
        np.ndarray: The outputs

    Example usage for row at a time read:
        input = [0x1<<i for i in range(64)]
        ts = time.time()
        data = a0.pic_dpe_batch(2, input, gain=3, Vread=0.2, mode=1) / 0.2
        print(time.time()-ts)
        plt.imshow(data * 1e6)
        plt.colorbar()

    '''
    gain = kwargs['gain'] if 'gain' in kwargs.keys() else -1
    Vref = kwargs['Vref'] if 'Vref' in kwargs.keys() else 0.5
    mode = kwargs['mode'] if 'mode' in kwargs.keys() else 1
    Tdly = kwargs['Tdly'] if 'Tdly' in kwargs.keys() else 1000

    if gain == -1:
        mode = mode | 0x2
    else:
        mode = mode & (~0x2)


    if not skip_conf:
        pic_read_config(**kwargs)
        pic_dpe_cols(array, col_en=col_en)

    n_input = len(input)
    data = []

    # Process 60 vectors at a time
    r_start = 0
    while True:
        r_stop = r_start+60 if r_start+60 < n_input else n_input
        r_size = r_stop - r_start

        # print(f'DPE: {r_start}-{r_stop}, len={r_size}')

        cmd = f'403,{array},{r_size},{mode},{Tdly},\1,'.encode()
        cmd += struct.pack('>' + 'Q'*(r_size), *input[r_start:r_stop])
        cmd += b'\0'

        # print(cmd)

        drv.ser.flushInput()
        drv.ser.write(cmd)

        r = 0
        while True:
            value = drv.ser.read(2 * 256)
            if len(value) == 0:
                print(f'.', end='')
                continue
            value = struct.unpack('<' + 'H'*256, value)
            data.append(value)

            r += 4
            if r >= r_size:
                break

        if r_stop == n_input:
            break
        r_start += 60

    data = np.array(data, dtype=np.uint16).reshape((-1, 64))
    # return data[:n_input]
    # return (dut.adc2volt(data[:n_input]) - Vref) / _gain_ratio[gain]

    if raw:
        return data[:n_input]
    else:
        return adc2current_array(data[:n_input], Vref)


def pic_write_single(Vwrite, Vgate, array=0, row=0, col=0, mode=-1):
    ''' 
    Program a device with PIC control

    Args:
        Vwrite(float): Set or Reset voltage
        Vgate(float):  Corresponding gate voltage
        array(int):    The array to program
        row(int):      Row #
        col(int):      col #
        mode(int): 0 -> Reset
                   1 -> Set
                   others -> invalid

    Returns:
        None

    '''
    # Configure timing
    dut.scan_control(scan_ctrl_bits=bytes([0x80, 0x01, 0x0c, 0x10,
                                           0x20, 0x01, 0x02]))

    dut.pads_defaults()

    dut.dac_set('DAC_VP_PAD', 0)

    Vwrite_raw = dut.dac_volt2raw(Vwrite)
    Vgate_raw = dut.dac_volt2raw(Vgate)

    if mode in [0,1]:

        # print(f'404,{array},{row},{col},{mode},{Vwrite_raw},{Vgate_raw}\0'.encode())
        drv.ser.write(f'404,{array},{row},{col},{mode},{Vwrite_raw},{Vgate_raw}\0'.encode())

        # wait for completion
        ret = drv.ser.read(1)

        if ret != b'0':
            print('[ERROR] Single device write return a wrong value')
    else:
        print(F'[ERROR] wrong writing mode = {mode}')

    dut.dac_set('DAC_VP_PAD', 0)

def pic_write_batch(Vwrite, Vgate, array=0, mode=-1, P_RESET=0x02):
    ''' 
    Program a device with PIC control.

    If any of Vwrite or Vgate is set to zero, the corresponding device 
    will NOT be programmed during the batch operation.

    Args:
        Vwrite(np.ndarray): Set or Reset voltage
        Vgate(np.ndarray):  Corresponding gate voltage
        array(int):    The array to program
        row(int):      Row #
        col(int):      col #
        mode(int): 0 -> Reset
                   1 -> Set
                   others -> invalid

        P_RESET(int):    The write pulse reset counter for tuneable 
                         pulse widtd, which should be calculated by 
                         ( P_reset - 0x01 ) * (1/CL_ARRAY)
                         So, for a clock of 50 MHz, the time resolution
                         is 20 ns.

    Returns:
        np.ndarray: The outputs

    '''
    assert P_RESET<0xff and P_RESET>0x01
    assert mode==0 or mode ==1

    # Configure timing
    dut.scan_control(scan_ctrl_bits=bytes([0x80, 0x01, 0x0c, 0x10,
                                           0x20, 0x01, P_RESET]))

    dut.pads_defaults()

    dut.dac_set('DAC_VP_PAD', 0)

    Vwrite_raw = dut.dac_volt2raw(Vwrite)
    Vgate_raw = dut.dac_volt2raw(Vgate)

    Vwrite_raw[Vwrite==0] = 0x0
    Vgate_raw[Vgate==0] = 0x0

    for row in range(0,64,2):
        drv.ser.write(f'405,{array},{mode},{row},0,'.encode() 
                    + Vwrite_raw[row:row+2,:].tobytes() + b'\0')

    for row in range(0,64,2):
        drv.ser.write(f'405,{array},{mode},{row+64},0,'.encode() 
                    + Vgate_raw[row:row+2,:].tobytes() + b'\0')

    ret = drv.ser.read(1)
    if ret != b'0':
        print('[ERROR] Single device write return a wrong value')

    dut.dac_set('DAC_VP_PAD', 0)

def pic_write_single_ext(Vwrite, Vgate, array=0, row=0, col=0, mode=-1, Twidth=5):
    ''' 
    Program a device with PIC control

    The pulse is gated through P_CONNECT_COLUMN_T accurately (< +/- 1us).
    But the actual Twidth on VP_PAD is around the 40 us + Twidth

    Args:
        Vwrite(float): Set or Reset voltage
        Vgate(float):  Corresponding gate voltage
        array(int):    The array to program
        row(int):      Row #
        col(int):      col #
        mode(int): 0 -> Reset
                   1 -> Set
                   others -> invalid
        Twidth(int):    Programming pulse width in microseconds

    Returns:
        None

    '''
    # Configure timing
    # dut.scan_control(scan_ctrl_bits=bytes([0x80, 0x01, 0x0c, 0x10,
    #                                        0x20, 0x01, 0x02]))

    dut.pads_defaults()
    #dut.dac_init()
    #dut.dac_set('DAC_VP_PAD', 0)

    Vwrite_raw = dut.dac_volt2raw(Vwrite)
    Vgate_raw = dut.dac_volt2raw(Vgate)
    Vzero_raw = dut.dac_volt2raw(0)

    if mode in [0,1]:

        # print(f'404,{array},{row},{col},{mode},{Vwrite_raw},{Vgate_raw}\0'.encode())
        drv.ser.write(f'406,{array},{row},{col},{mode},{Vwrite_raw},{Vgate_raw},{Vzero_raw},{Twidth}\0'.encode())

        # wait for completion
        ret = drv.ser.read(1)

        if ret != b'0':
            print('[ERROR] Single device write return a wrong value')
    else:
        print(F'[ERROR] wrong writing mode = {mode}')

    #dut.dac_set('DAC_VP_PAD', 0)

def pic_write_batch_ext(Vwrite, Vgate, array=0, mode=-1, Twidth=5):
    ''' 
    Program a device with PIC control.

    If any of Vwrite or Vgate is set to zero, the corresponding device 
    will NOT be programmed during the batch operation.

    Args:
        Vwrite(np.ndarray): Set or Reset voltage
        Vgate(np.ndarray):  Corresponding gate voltage
        array(int):    The array to program
        row(int):      Row #
        col(int):      col #
        mode(int): 0 -> Reset
                   1 -> Set
                   others -> invalid

        Twidth(float):    The programming pulse width in microseconds

    Returns:
        np.ndarray: The outputs

    '''
    assert mode==0 or mode ==1

    # Configure timing
    # dut.scan_control(scan_ctrl_bits=bytes([0x80, 0x01, 0x0c, 0x10,
    #                                        0x20, 0x01, P_RESET]))
    dut.pads_defaults()

    dut.dac_set('DAC_VP_PAD', 0)

    Vwrite_raw = dut.dac_volt2raw(Vwrite)
    Vgate_raw = dut.dac_volt2raw(Vgate)
    Vzero_raw = dut.dac_volt2raw(0)

    Vwrite_raw[Vwrite==0] = 0x0
    Vgate_raw[Vgate==0] = 0x0
    

    for row in range(0,64,2):
        drv.ser.write(f'407,{array},{mode},{Vzero_raw},{Twidth},{row},0,'.encode() 
                    + Vwrite_raw[row:row+2,:].tobytes() + b'\0')

    for row in range(0,64,2):
        drv.ser.write(f'407,{array},{mode},{Vzero_raw},{Twidth},{row+64},0,'.encode() 
                    + Vgate_raw[row:row+2,:].tobytes() + b'\0')

    while True:
        ret = drv.ser.read(1)
        if ret != b'0':
            print('.', end='')
        else:
            break

    dut.dac_set('DAC_VP_PAD', 0)
    
def array_program(targetG, targetTolerance, vSetRamp, vResetRamp, vGateSetRamp, vGateResetRamp, array, maxLoops=5, targetWriteTime=5.12):
#def array_program(targetG, targetTolerance, vSetRamp, vResetRamp, vGateSetRamp, vGateResetRamp, array, maxLoops=5):
    ''' 
    Program an array to a target conductance matrix using batch pic_write and pic_read operations

    Args:
        targetG: matrix of target conductances (Siemens) corresponding to each [row,col]
        targetTolerance: matrix of acceptable tolerances in targetG. Thus, the programming will stop when 
            (targetG-targetTolerance) <= GMatrix <=(targetG+targetTolerance) 
            IF A PARTICULAR CELL [I,J] DOES NOT NEED TO BE PROGRAMMED, SET "targetTolerance[I,J] = inf"
        vSetRamp: a vector providing the sequence of Set voltages to be applied in the inner loop
        vResetRamp: a vector providing the sequence of Reset voltages to be applied in the inner loop
        vGateSetRamp: a vector providing the sequence of Set Gate voltages to be applied in the outer loop
        vGateResetRamp: a vector providing the sequence of Reset Gate voltages to be applied in the outer loop
        array(int):    The array to program
        maxLoops: the maximum number of times the program will run the full inner+outer loop for a Set and Reset sequence before giving up
        row(int):      Row #
        col(int):      col #
        
    Returns:
        np.ndarray: The final read of the array

    '''
    #from dpe import DPE
    # Configure matrices needed
    targetGLow = targetG-targetTolerance
    targetGHigh = targetG+targetTolerance
    currentLoops = 0
    zeroMatrix = np.zeros((64,64))
    Vread=0.2
    changeClock = False
    if (targetWriteTime > 5.12):
        changeClock = True    
        targetClkPeriod = 1e-6*targetWriteTime/250
        targetClkFreq = 1e3*round(1e-3/targetClkPeriod) #Round to the nearest 1kHz
        write_width = hex(255*round(1e-6*targetWriteTime/(255/targetClkFreq))) #Round to the nearest integer 0 to 255 then make Hex
        newDivisor = 100e6/targetClkFreq   
    else:
        #write_width = hex(255*round(1e-6*targetWriteTime/(255/50e6))) #Round to the nearest integer 0 to 255 then make Hex  
        write_width = 0xff

    # Do initial reading
    #GMatrix = pic_read_batch(array, Vread=Vread, gain=-1) / Vread
    input = [0x1<<i for i in range(64)]
    GMatrix = pic_dpe_batch(array, input, gain=-1, Vread=Vread, Tdly=1000) / Vread
    # Now loop as long as any device is out of tolerance for target conductance and we haven't maxed out loops
    while ( (np.any(GMatrix < targetGLow) | np.any(GMatrix > targetGHigh)) & (currentLoops<=maxLoops) ):
        # Do SET operations for any devices too low        
        if np.any(GMatrix < targetGLow):
            print('Now turning ON')
            for vGateSet in vGateSetRamp:
                print('Set, Vgate = ', vGateSet)
                for vSet in vSetRamp:
                    vGateSetMatrix = zeroMatrix + vGateSet * (GMatrix < targetGLow)
                    vWriteSetMatrix = zeroMatrix + vSet * (GMatrix < targetGLow)
                    #print('VWrite:', vWriteSetMatrix[0:3,0:3])
                    #print('VGate:', vGateSetMatrix[0:3,0:3])
                    if changeClock:
                        drv.clk_stop('CK_ARRAY')    
                        drv.clk_config('CK_ARRAY', divisor=newDivisor)    
                        drv.clk_start('CK_ARRAY')
                    pic_write_batch(vWriteSetMatrix, vGateSetMatrix, array=array, mode=1, P_RESET=write_width)
                    #GMatrix = pic_read_batch(array, Vread=Vread, gain=-1) / Vread
                    GMatrix = pic_dpe_batch(array, input, gain=-1, Vread=Vread, Tdly=1000) / Vread
                    if np.all(GMatrix >= targetGLow):
                        break
                if np.all(GMatrix >= targetGLow):
                        break
            currentLoops=currentLoops+1
        # Do RESET operations for any devices too high
        if np.any(GMatrix > targetGHigh):
            print('Now turning OFF')
            for vGateReset in vGateResetRamp:
                print('Reset, Vgate = ', vGateReset)
                for vReset in vResetRamp:
                    vGateResetMatrix = zeroMatrix + vGateReset * (GMatrix > targetGHigh)
                    vWriteResetMatrix = zeroMatrix + vReset * (GMatrix > targetGHigh)
                    pic_write_batch(vWriteResetMatrix, vGateResetMatrix, array=array, mode=0, P_RESET=write_width)
                    #GMatrix = pic_read_batch(array, Vread=Vread, gain=-1) / Vread
                    GMatrix = pic_dpe_batch(array, input, gain=-1, Vread=Vread, Tdly=1000) / Vread
                    if np.all(GMatrix <= targetGHigh):
                        break
                if np.all(GMatrix <= targetGHigh):
                        break
            currentLoops=currentLoops+1

        print('Current loop = ', currentLoops)
    print('Completed with total loops = ', currentLoops)
    return GMatrix    

def cell_program(array, targetRow, targetCol, targetG, targetTolerance, vSetRamp, vResetRamp, vGateSetRamp, vGateResetRamp, maxLoops=5):
    ''' 
    Program a cell to a target conductance

    Args:
        array = targeted array
        [targetRow, targetCol] = targeted cell location

        targetG: target conductances (Siemens)
        targetTolerance: acceptable tolerance in targetG. Thus, the programming will stop when 
            (targetG-targetTolerance) <= G <=(targetG+targetTolerance) 

        vSetRamp: a vector providing the sequence of Set voltages to be applied in the inner loop
        vResetRamp: a vector providing the sequence of Reset voltages to be applied in the inner loop
        vGateSetRamp: a vector providing the sequence of Set Gate voltages to be applied in the outer loop
        vGateResetRamp: a vector providing the sequence of Reset Gate voltages to be applied in the outer loop
        maxLoops: the maximum number of times the program will run the full inner+outer loop for a Set and Reset sequence before giving up
        
    Returns:
        currG: The final read of the device

    '''
    targetGLow = targetG-targetTolerance
    targetGHigh = targetG+targetTolerance
    currentLoops = 0
    vRead=0.2
    Vgate=5.0

    # Do initial reading
    currG = pic_read_single(array, targetRow, targetCol, Vread=vRead, Vgate=Vgate, gain=-1) / vRead
    #currG = read_single_int(vRead, Vgate, array=array, row=targetRow, col=targetCol, gain=-1) / vRead
    initG = currG
    # Now loop as long as the device is out of tolerance for target conductance and we haven't maxed out loops
    while ( ( (currG < targetGLow) | (currG > targetGHigh) ) & (currentLoops < maxLoops) ):
        # Do SET operations if device too low        
        if (currG < targetGLow):
            for vGateSet in vGateSetRamp:
                for vSet in vSetRamp:
                    set_single_int(vSet, vGateSet, array=array, row=targetRow, col=targetCol)
                    currG = pic_read_single(array, targetRow, targetCol, Vread=vRead, Vgate=Vgate, gain=-1) / vRead
                    #currG = read_single_int(vRead, Vgate, array=array, row=targetRow, col=targetCol, gain=-1) / vRead
                    if (currG >= targetGLow):
                        break
                if (currG >= targetGLow):
                        break
            # IF the device did not switch, we may be unformed and do not want to repeat this too many times
            if (currG < targetGLow):
                currentLoops=currentLoops+2
            else:
                currentLoops=currentLoops+1

        # Do RESET operations if device too high
        elif (currG > targetGHigh):
            for vGateReset in vGateResetRamp:
                for vReset in vResetRamp:
                    reset_single_int(vReset, vGateReset, array=array, row=targetRow, col=targetCol)
                    currG = pic_read_single(array, targetRow, targetCol, Vread=vRead, Vgate=Vgate, gain=-1) / vRead
                    #currG = read_single_int(vRead, Vgate, array=array, row=targetRow, col=targetCol, gain=-1) / vRead
                    if (currG <= targetGHigh):
                        break
                if (currG <= targetGHigh):
                        break
            currentLoops=currentLoops+1
            
    #print('InitG=', initG, 'FinalG=', currG, ', Total loops =', currentLoops)
    return currG
def cell_program_with_fb(array, targetRow, targetCol, targetG, targetTolerance, vSetRamp, vResetRamp, vGateSetRamp, vGateResetRamp, maxLoops=5):
    ''' 
    Program a cell to a target conductance

    Args:
        array = targeted array
        [targetRow, targetCol] = targeted cell location

        targetG: target conductances (Siemens)
        targetTolerance: acceptable tolerance in targetG. Thus, the programming will stop when 
            (targetG-targetTolerance) <= G <=(targetG+targetTolerance) 

        vSetRamp: a vector providing the sequence of Set voltages to be applied in the inner loop
        vResetRamp: a vector providing the sequence of Reset voltages to be applied in the inner loop
        vGateSetRamp: a vector providing the sequence of Set Gate voltages to be applied in the outer loop
        vGateResetRamp: a vector providing the sequence of Reset Gate voltages to be applied in the outer loop
        maxLoops: the maximum number of times the program will run the full inner+outer loop for a Set and Reset sequence before giving up
        
    Returns:
        currG: The final read of the device

    '''
    targetGLow = targetG-targetTolerance
    targetGHigh = targetG+targetTolerance
    currentLoops = 0
    vRead=0.2
    Vgate=5.0

    # Do initial reading
    currG = pic_read_single(array, targetRow, targetCol, Vread=vRead, Vgate=Vgate, gain=-1) / vRead
    #currG = read_single_int(vRead, Vgate, array=array, row=targetRow, col=targetCol, gain=-1) / vRead
    initG = currG
    # Now loop as long as the device is out of tolerance for target conductance and we haven't maxed out loops
    while ( ( (currG < targetGLow) | (currG > targetGHigh) ) & (currentLoops < maxLoops) ):
        # Do SET operations if device too low        
        if (currG < targetGLow):
            for vGateSet in vGateSetRamp:
                for vSet in vSetRamp:
                    set_single_int(vSet, vGateSet, array=array, row=targetRow, col=targetCol)
                    currG = pic_read_single(array, targetRow, targetCol, Vread=vRead, Vgate=Vgate, gain=-1) / vRead
                    #currG = read_single_int(vRead, Vgate, array=array, row=targetRow, col=targetCol, gain=-1) / vRead
                    if (currG >= targetGLow):
                        print('Device (row=', targetRow, 'col=', targetCol, ') switched ON at V=', vSet)
                        break
                if (currG >= targetGLow):
                    print('Device (row=', targetRow, 'col=', targetCol, ') switched ON at Vgate=', vGateSet)
                    break
            # IF the device did not switch, we may be unformed and do not want to repeat this too many times
            if (currG < targetGLow):
                print('Device (row=', targetRow, 'col=', targetCol, ') never switched ON sufficiently')
                currentLoops=currentLoops+2
            else:
                currentLoops=currentLoops+1

        # Do RESET operations if device too high
        elif (currG > targetGHigh):
            for vGateReset in vGateResetRamp:
                for vReset in vResetRamp:
                    reset_single_int(vReset, vGateReset, array=array, row=targetRow, col=targetCol)
                    currG = pic_read_single(array, targetRow, targetCol, Vread=vRead, Vgate=Vgate, gain=-1) / vRead
                    #currG = read_single_int(vRead, Vgate, array=array, row=targetRow, col=targetCol, gain=-1) / vRead
                    if (currG <= targetGHigh):
                        print('Device (row=', targetRow, 'col=', targetCol, ') switched OFF at V=', vReset)
                        break
                if (currG <= targetGHigh):
                    print('Device (row=', targetRow, 'col=', targetCol, ') switched OFF at Vgate=', vGateReset)
                    break
            currentLoops=currentLoops+1
            
    #print('InitG=', initG, 'FinalG=', currG, ', Total loops =', currentLoops)
    return currG

def cell_program_with_history(array, targetRow, targetCol, targetG, targetTolerance, vSetRamp, vResetRamp, vGateSetRamp, vGateResetRamp, maxLoops=5):
    ''' 
    Program a cell to a target conductance

    Args:
        array = targeted array
        [targetRow, targetCol] = targeted cell location

        targetG: target conductances (Siemens)
        targetTolerance: acceptable tolerance in targetG. Thus, the programming will stop when 
            (targetG-targetTolerance) <= G <=(targetG+targetTolerance) 

        vSetRamp: a vector providing the sequence of Set voltages to be applied in the inner loop
        vResetRamp: a vector providing the sequence of Reset voltages to be applied in the inner loop
        vGateSetRamp: a vector providing the sequence of Set Gate voltages to be applied in the outer loop
        vGateResetRamp: a vector providing the sequence of Reset Gate voltages to be applied in the outer loop
        maxLoops: the maximum number of times the program will run the full inner+outer loop for a Set and Reset sequence before giving up
        
    Returns:
        currG: The final read of the device

    '''
    targetGLow = targetG-targetTolerance
    targetGHigh = targetG+targetTolerance
    currentLoops = 0
    vRead=0.2
    Vgate=5.0

    # Do initial reading
    currG = pic_read_single(array, targetRow, targetCol, Vread=vRead, Vgate=Vgate, gain=-1) / vRead
    GHistory = []
    VHistory = []
    VGateHistory = []
    GHistory.append(currG)
    VHistory.append(0)
    VGateHistory.append(0)
    #currG = read_single_int(vRead, Vgate, array=array, row=targetRow, col=targetCol, gain=-1) / vRead
    initG = currG
    # Now loop as long as the device is out of tolerance for target conductance and we haven't maxed out loops
    while ( ( (currG < targetGLow) | (currG > targetGHigh) ) & (currentLoops < maxLoops) ):
        # Do SET operations if device too low        
        if (currG < targetGLow):
            for vGateSet in vGateSetRamp:
                for vSet in vSetRamp:
                    set_single_int(vSet, vGateSet, array=array, row=targetRow, col=targetCol)
                    currG = pic_read_single(array, targetRow, targetCol, Vread=vRead, Vgate=Vgate, gain=-1) / vRead
                    #currG = read_single_int(vRead, Vgate, array=array, row=targetRow, col=targetCol, gain=-1) / vRead
                    GHistory.append(currG)
                    VHistory.append(vSet)
                    VGateHistory.append(vGateSet)
                    if (currG >= targetGLow):
                        #print('Device (row=', targetRow, 'col=', targetCol, ') switched ON at V=', vSet)
                        break
                if (currG >= targetGLow):
                    #print('Device (row=', targetRow, 'col=', targetCol, ') switched ON at Vgate=', vGateSet)
                    break
            # IF the device did not switch, we may be unformed and do not want to repeat this too many times
            if (currG < targetGLow):
                #print('Device (row=', targetRow, 'col=', targetCol, ') never switched ON sufficiently')
                currentLoops=currentLoops+2
            else:
                currentLoops=currentLoops+1

        # Do RESET operations if device too high
        elif (currG > targetGHigh):
            for vGateReset in vGateResetRamp:
                for vReset in vResetRamp:
                    reset_single_int(vReset, vGateReset, array=array, row=targetRow, col=targetCol)
                    currG = pic_read_single(array, targetRow, targetCol, Vread=vRead, Vgate=Vgate, gain=-1) / vRead
                    #currG = read_single_int(vRead, Vgate, array=array, row=targetRow, col=targetCol, gain=-1) / vRead
                    GHistory.append(currG)
                    VHistory.append(vReset)
                    VGateHistory.append(vGateReset)
                    if (currG <= targetGHigh):
                        #print('Device (row=', targetRow, 'col=', targetCol, ') switched OFF at V=', vReset)
                        break
                if (currG <= targetGHigh):
                    #print('Device (row=', targetRow, 'col=', targetCol, ') switched OFF at Vgate=', vGateReset)
                    break
            currentLoops=currentLoops+1
            
    #print('InitG=', initG, 'FinalG=', currG, ', Total loops =', currentLoops)
    return currG, GHistory, VHistory, VGateHistory

def hybrid_array_program(targetG, targetTolerance, vSetRamp, vResetRamp, vGateSetRamp, vGateResetRamp, array, maxLoops=5):
    ''' 
    Hybrid scheme until batch reads work.
    Programs an array to a target conductance matrix using single cell reads with batch pic_write operations

    Args:
        targetG: matrix of target conductances (Siemens) corresponding to each [row,col]
        targetTolerance: matrix of acceptable tolerances in targetG. Thus, the programming will stop when 
            (targetG-targetTolerance) <= GMatrix <=(targetG+targetTolerance) 
            IF A PARTICULAR CELL [I,J] DOES NOT NEED TO BE PROGRAMMED, SET "targetTolerance[I,J] = inf"
        vSetRamp: a vector providing the sequence of Set voltages to be applied in the inner loop
        vResetRamp: a vector providing the sequence of Reset voltages to be applied in the inner loop
        vGateSetRamp: a vector providing the sequence of Set Gate voltages to be applied in the outer loop
        vGateResetRamp: a vector providing the sequence of Reset Gate voltages to be applied in the outer loop
        array(int):    The array to program
        maxLoops: the maximum number of times the program will run the full inner+outer loop for a Set and Reset sequence before giving up
        row(int):      Row #
        col(int):      col #
        
    Returns:
        np.ndarray: The final read of the array

    '''
    #from dpe import DPE
    # Configure matrices needed
    targetGLow = targetG-targetTolerance
    targetGHigh = targetG+targetTolerance
    currentLoops = 0
    zeroMatrix = np.zeros((64,64))
    GMatrix = zeroMatrix
    vRead=0.2
    Vgate = 5
    numRows = 64
    numCols = 64
    # Do initial reading
    #GMatrix = pic_read_batch(array, Vread=Vread, gain=-1) / Vread
    for rr in range(numRows):
        for cc in range(numCols):
            GMatrix[rr,cc] = pic_read_single(array, rr, cc, Vread=vRead, Vgate=Vgate, gain=-1) / vRead
    # Now loop as long as any device is out of tolerance for target conductance and we haven't maxed out loops
    while ( (np.any(GMatrix < targetGLow) | np.any(GMatrix > targetGHigh)) & (currentLoops<maxLoops) ):
        # Do SET operations for any devices too low        
        if np.any(GMatrix < targetGLow):
            print('Now turning ON')
            for vGateSet in vGateSetRamp:
                print('Set, Vgate = ', vGateSet)
                for vSet in vSetRamp:
                    vGateSetMatrix = zeroMatrix + vGateSet * (GMatrix < targetGLow)
                    vWriteSetMatrix = zeroMatrix + vSet * (GMatrix < targetGLow)
                    print(np.sum(GMatrix < targetGLow), ' are still too far below target Conductance')
                    #print('VWrite:', vWriteSetMatrix[0:3,0:3])
                    #print('VGate:', vGateSetMatrix[0:3,0:3])
                    pic_write_batch(vWriteSetMatrix, vGateSetMatrix, array=array, mode=1)
                    #GMatrix = pic_read_batch(array, Vread=Vread, gain=-1) / Vread
                    rowscols=np.nonzero(GMatrix < targetGLow)
                    testRows = rowscols[0]
                    testCols = rowscols[1]
                    for ii in range(np.size(testRows)):
                        GMatrix[testRows[ii],testCols[ii]] = pic_read_single(array, testRows[ii], testCols[ii], Vread=vRead, Vgate=Vgate, gain=-1) / vRead

                    if np.all(GMatrix >= targetGLow):
                        break
                if np.all(GMatrix >= targetGLow):
                        break
            currentLoops=currentLoops+1
        #Do a full array read before starting Reset operations    
        for rr in range(numRows):
            for cc in range(numCols):
                GMatrix[rr,cc] = pic_read_single(array, rr, cc, Vread=vRead, Vgate=Vgate, gain=-1) / vRead

        # Do RESET operations for any devices too high
        if np.any(GMatrix > targetGHigh):
            print('Now turning OFF')
            for vGateReset in vGateResetRamp:
                print('Reset, Vgate = ', vGateReset)
                for vReset in vResetRamp:
                    vGateResetMatrix = zeroMatrix + vGateReset * (GMatrix > targetGHigh)
                    vWriteResetMatrix = zeroMatrix + vReset * (GMatrix > targetGHigh)
                    print(np.sum(GMatrix > targetGHigh), ' are still too far above target Conductance')
                    pic_write_batch(vWriteResetMatrix, vGateResetMatrix, array=array, mode=0)
                    #GMatrix = pic_read_batch(array, Vread=Vread, gain=-1) / Vread
                    rowscols=np.nonzero(GMatrix > targetGHigh)
                    testRows = rowscols[0]
                    testCols = rowscols[1]
                    for ii in range(np.size(testRows)):
                        GMatrix[testRows[ii],testCols[ii]] = pic_read_single(array, testRows[ii], testCols[ii], Vread=vRead, Vgate=Vgate, gain=-1) / vRead
                    if np.all(GMatrix <= targetGHigh):
                        break
                if np.all(GMatrix <= targetGHigh):
                        break
            currentLoops=currentLoops+1
        #currentLoops=currentLoops+1
        print('Current loop = ', currentLoops)
    print('Completed with total loops = ', currentLoops)
    return GMatrix    

def read_single(Vread, Vgate, array=0, row=0, col=0, gain=0):
    '''
    Args,

    Returns:
        The ADC readout voltages
    '''
    VREF_TIA = 0.5
    VREF_LO = 0.5

    dut.scan_control(scan_ctrl_bits=bytes([0x10, 0x02, 0x0c, 0x10,
                                           0x20, 0x01, 0x02]))
    dut.scan_tia(BitArray(_gain_table[gain]*96).bytes)

    # Make sure the VPP is reasonable
    assert VREF_TIA - Vread > -0.2 and VREF_TIA - Vread < 1

    dut.dac_set('PLANE_VPP', VREF_TIA - Vread)
    dut.dac_set('P_VREF_TIA', VREF_TIA)
    dut.dac_set('P_TVDD', Vgate)

    data_load = dut.data_generate_sparse([row, col])
    dut.load_vectors(array=array, data=data_load)

    dut.pads_defaults()

    dut.reset_dpe()

    # drv.gpio_pin_set(*PIC_PINS['DPE_INTERNAL_EN'])

    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    drv.gpio_pin_set(*PIC_PINS['READ_BIT'])
    drv.gpio_pin_reset(*PIC_PINS['READ_DPE'])

    # drv.gpio_nforce_safe_write(0b100)
    drv.gpio_nforce_safe_write(0b1 << array)
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    # drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])

    [fifo_en, channel] = dut.which_fifo([array, col])

    data = dut.download_fifo(fifo_en)
    volt = dut.adc2volt(data[channel]) - VREF_LO

    return volt / _gain_ratio[gain]


@read_corr(2.25)
def read_single_int(Vread, Vgate, array=0, row=0, col=0, 
                    gain=0, Tsh=-1, Vref=0.5,
                    raw=False):
    '''
    Args,
        gain(int): If -1, then auto_gain

    Returns:
        The ADC readout voltages
    '''
    VREF_TIA = Vref
    VREF_LO = 0.5

    if Tsh<0:
        Tsh = _sh_default[gain]

    dut.scan_control(scan_ctrl_bits=bytes([0x10, 0x02, 0x0c*3, 0x10,
                                           Tsh, 0x01, 0x02]))

    if gain >= 0 and gain <= 4:
        AGC = False
        dut.scan_tia(BitArray(_gain_table[gain]*96).bytes)
        time.sleep(5e-3)
    else:
        AGC = True
        


    # Make sure the VPP is reasonable
    assert VREF_TIA - Vread > -0.2 and VREF_TIA - Vread <= 1

    dut.dac_set('PLANE_VPP', VREF_TIA - Vread)
    dut.dac_set('P_VREF_TIA', VREF_TIA)
    dut.dac_set('P_TVDD', Vgate)

    data_load = dut.data_generate_sparse([row, col])
    dut.load_vectors(array=array, data=data_load)

    dut.pads_defaults()

    dut.reset_dpe()

    if AGC:
        drv.gpio_pin_set(*PIC_PINS['AGC_INTERNAL_EN'])
    else:
        drv.gpio_pin_set(*PIC_PINS['DPE_INTERNAL_EN'])

    drv.gpio_pin_set(*PIC_PINS['READ_BIT'])
    drv.gpio_pin_reset(*PIC_PINS['READ_DPE'])

    drv.gpio_nforce_safe_write(0b1 << array)
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    if AGC:
        drv.gpio_pin_set(*PIC_PINS['AGC_PULSE'])
        time.sleep(2e-7)
        drv.gpio_pin_reset(*PIC_PINS['AGC_PULSE'])
    else:
        drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
        time.sleep(2e-7)
        drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    [fifo_en, channel] = dut.which_fifo([array, col])

    data = dut.download_fifo(fifo_en)

    # volt = dut.adc2volt(data[channel]) - VREF_LO

    if raw:
        return data[channel]
    else:
        return adc2current(data[channel], VREF_LO)
    # volt / _gain_ratio[gain]


def reset_single(Vreset, Vgate, array=0, row=0, col=0, Twidth=1e-6):
    '''
    Reset a single device with PIC timing control

    Args,
        Twidth(int):    The pulse width in seconds.
    '''
    ar = array
    r = row
    c = col

    data_load = dut.data_generate_sparse([r, c])
    dut.load_vectors(array=ar, data=data_load)

    dut.pads_defaults()
#     drv.gpio_pin_set(*PIC_PINS['WRT_INTERNAL_EN'])

    drv.gpio_pin_reset(*PIC_PINS['WRITE_ADD_CAP'])
    drv.gpio_pin_set(*PIC_PINS['WRITE_SEL_EXT'])
    dut.reset_dpe()

    dut.dac_set('DAC_VP_PAD', 0)

    drv.gpio_nforce_safe_write(0b1 << ar)

    drv.gpio_pin_set(*PIC_PINS['COL_WRITE_CONNECT'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    dut.dac_set('DAC_VP_PAD', Vreset)
    time.sleep(Twidth)        # delay(as necessary to write)
    dut.dac_set('DAC_VP_PAD', 0)

    drv.gpio_pin_reset(*PIC_PINS['CONNECT_COLUMN_T'])
    drv.gpio_pin_reset(*PIC_PINS['COL_WRITE_CONNECT'])
    drv.gpio_nforce_safe_write(0)


def set_single(Vset, Vgate, array=0, row=0, col=0, Twidth=1e-6):
    '''
    Set a single device with PIC timing control

    Args,
        Twidth(int):    The pulse width in seconds.\
    '''

    ar = array
    r = row
    c = col

    data_load = dut.data_generate_sparse([r, c])
    dut.load_vectors(array=ar, data=data_load)

    dut.pads_defaults()
#     drv.gpio_pin_set(*PIC_PINS['WRT_INTERNAL_EN'])
    drv.gpio_pin_reset(*PIC_PINS['WRITE_ADD_CAP'])
    drv.gpio_pin_set(*PIC_PINS['WRITE_SEL_EXT'])

    dut.reset_dpe()

    dut.dac_set('DAC_VP_PAD', 0)

    drv.gpio_pin_set(*PIC_PINS['WRITE_FWD'])

    drv.gpio_nforce_safe_write(0b1 << ar)

    drv.gpio_pin_set(*PIC_PINS['ROW_WRITE_CONNECT'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    dut.dac_set('P_TVDD', Vgate)
    dut.dac_set('DAC_VP_PAD', Vset)
    time.sleep(Twidth)
    dut.dac_set('DAC_VP_PAD', 0)

    drv.gpio_pin_reset(*PIC_PINS['CONNECT_COLUMN_T'])
    drv.gpio_pin_reset(*PIC_PINS['ROW_WRITE_CONNECT'])
    drv.gpio_nforce_safe_write(0)


def reset_single_int(Vreset, Vgate, array=0, row=0, col=0):
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


def read_dpe_single_int(Vread, Vgate, array=0, row=0, col=0, gain=0, Tsh=0x0c, Vref=0.5):
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
    drv.gpio_pin_set(*PIC_PINS['READ_DPE'])

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


def read_dpe_single(Vread, Vgate, array=0, row=0, col=0, gain=0):
    '''
    Args,

    Returns:
        The ADC readout voltages
    '''
    VREF_TIA = 0.5
    VREF_LO = 0.5

    dut.scan_control(scan_ctrl_bits=bytes([0x10, 0x02, 0x0c, 0x10,
                                           0x20, 0x01, 0x02]))
    dut.scan_tia(BitArray(_gain_table[gain]*96).bytes)

    # Make sure the VPP is reasonable
    assert VREF_TIA - Vread > -0.2 and VREF_TIA - Vread < 1

    dut.dac_set('PLANE_VPP', VREF_TIA - Vread)
    dut.dac_set('P_VREF_TIA', VREF_TIA)
    dut.dac_set('P_TVDD', Vgate)

    data_load = dut.data_generate_sparse([row, col])
    dut.load_vectors(array=array, data=data_load)

    dut.pads_defaults()

    dut.reset_dpe()

    # drv.gpio_pin_set(*PIC_PINS['DPE_INTERNAL_EN'])

    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    drv.gpio_pin_set(*PIC_PINS['READ_BIT'])
    drv.gpio_pin_set(*PIC_PINS['READ_DPE'])

    # drv.gpio_nforce_safe_write(0b100)
    drv.gpio_nforce_safe_write(0b1 << array)
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    # drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])

    [fifo_en, channel] = dut.which_fifo([array, col])

    data = dut.download_fifo(fifo_en)
    volt = dut.adc2volt(data[channel]) - VREF_LO

    return volt / _gain_ratio[gain]


def read_dpe_col_int(Vread, Vgate, row, array=0, col=0, gain=0, Vref=0.5):
    '''
    Args,

    Returns:
        The ADC readout voltages
    '''
    VREF_TIA = Vref
    VREF_LO = 0.5

    dut.scan_control(scan_ctrl_bits=bytes([0x10, 0x02, 0x0c, 0x10,
                                           0x0c, 0x01, 0x02]))
    dut.scan_tia(BitArray(_gain_table[gain]*96).bytes)

    # Make sure the VPP is reasonable
    assert VREF_TIA - Vread > -0.2 and VREF_TIA - Vread < 1

    dut.dac_set('PLANE_VPP', VREF_TIA - Vread)
    dut.dac_set('P_VREF_TIA', VREF_TIA)
    dut.dac_set('P_TVDD', Vgate)

    index = []
    for r in row:
        index.append(r)
        index.append(col)

    data_load = dut.data_generate_sparse(index)
    dut.load_vectors(array=array, data=data_load)

    dut.pads_defaults()

    dut.reset_dpe()

    drv.gpio_pin_set(*PIC_PINS['DPE_INTERNAL_EN'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    drv.gpio_pin_set(*PIC_PINS['READ_BIT'])
    drv.gpio_pin_set(*PIC_PINS['READ_DPE'])

    # drv.gpio_nforce_safe_write(0b100)
    drv.gpio_nforce_safe_write(0b1 << array)
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])

    [fifo_en, channel] = dut.which_fifo([array, col])

    data = dut.download_fifo(fifo_en)
    volt = dut.adc2volt(data[channel]) - VREF_LO

    return volt / _gain_ratio[gain]


def read_dpe_int(Vread, Vgate, row_vector, array=0, gain=0, Vref=0.5):
    '''
    Args,

    Returns:
        The ADC readout voltages
    '''
    VREF_TIA = Vref
    VREF_LO = 0.5

    dut.scan_control(scan_ctrl_bits=bytes([0x10, 0x02, 0x0c, 0x10,
                                           0x0c, 0x01, 0x02]))
    dut.scan_tia(BitArray(_gain_table[gain]*96).bytes)

    # Make sure the VPP is reasonable
    assert VREF_TIA - Vread > -0.2 and VREF_TIA - Vread < 1

    dut.dac_set('PLANE_VPP', VREF_TIA - Vread)
    dut.dac_set('P_VREF_TIA', VREF_TIA)
    dut.dac_set('P_TVDD', Vgate)

    data_load = dut.data_generate_vector(
        row_vector, [0xffff, 0xffff, 0xffff, 0xffff])
    dut.load_vectors(array=array, data=data_load)

    dut.pads_defaults()

    dut.reset_dpe()

    drv.gpio_pin_set(*PIC_PINS['DPE_INTERNAL_EN'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    drv.gpio_pin_set(*PIC_PINS['READ_BIT'])
    drv.gpio_pin_reset(*PIC_PINS['READ_DPE'])

    # drv.gpio_nforce_safe_write(0b100)
    drv.gpio_nforce_safe_write(0b1 << array)
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])

    volt = []
    fifo_en = [(2-array)*2, (2-array)*2+6, (2-array)*2+1, (2-array)*2+7]
    data1 = dut.download_fifo(fifo_en[0])
    data2 = dut.download_fifo(fifo_en[1])
    for b in range(0, 32, 2):
        channel = (b//16)*8 + (7-b % 16//2)
        volt.append(
            (dut.adc2volt(data1[channel]) - VREF_LO) / _gain_ratio[gain])
        volt.append(
            (dut.adc2volt(data2[channel]) - VREF_LO) / _gain_ratio[gain])
    data3 = dut.download_fifo(fifo_en[2])
    data4 = dut.download_fifo(fifo_en[3])
    for b in range(32, 64, 2):
        channel = (3-b//16)*8 + b % 16//2
        volt.append(
            (dut.adc2volt(data3[channel]) - VREF_LO) / _gain_ratio[gain])
        volt.append(
            (dut.adc2volt(data4[channel]) - VREF_LO) / _gain_ratio[gain])

    # [fifo_en, channel] = dut.which_fifo([array, 3])
    # data = dut.download_fifo( fifo_en )
    # volt = dut.adc2volt(data[channel]) - VREF_LO

    return volt

# def read_dpe_allarray_int(Vread, Vgate, row_vector, gain=0, Vref=0.5):
#     '''
#     Args,

#     Returns:
#         The ADC readout voltages
#     '''
#     VREF_TIA = Vref
#     VREF_LO = 0.5

#     dut.scan_control(scan_ctrl_bits=bytes([0x10, 0x02, 0x0c, 0x10,
#                                            0x20, 0x01, 0x02]))
#     dut.scan_tia( BitArray(_gain_table[gain]*96).bytes )

#     # Make sure the VPP is reasonable
#     assert VREF_TIA - Vread > -0.2 and VREF_TIA - Vread < 1

#     dut.dac_set('PLANE_VPP', VREF_TIA - Vread)
#     dut.dac_set('P_VREF_TIA', VREF_TIA)
#     dut.dac_set('P_TVDD', Vgate)

#     data_load = dut.data_generate_vector(row_vector, [0xffff,0xffff,0xffff,0xffff])
#     dut.load_vectors(array=array, data=data_load)

#     dut.pads_defaults()

#     dut.reset_dpe()

#     # drv.gpio_pin_set(*PIC_PINS['DPE_INTERNAL_EN'])

#     drv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
#     drv.gpio_pin_set(*PIC_PINS['READ_BIT'])
#     drv.gpio_pin_set(*PIC_PINS['READ_DPE'])

#     # drv.gpio_nforce_safe_write(0b100)
#     drv.gpio_nforce_safe_write( 0b111 )
#     drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
#     drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

#     # drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
#     # drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

#     drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
#     # time.sleep(1e-6)
#     drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])

#     [fifo_en, channel] = dut.which_fifo([array, col])

#     data = dut.download_fifo( fifo_en )
#     volt = dut.adc2volt(data[channel]) - VREF_LO

#     return volt / _gain_ratio[gain]
