    
import drv_gpio as drv

import dut_func as dut
import numpy as np
from bitstring import BitArray
from misc import *
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
    dut.scan_tia( BitArray(_gain_table[gain]*96).bytes )
    
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
    drv.gpio_nforce_safe_write( 0b1 << array )
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    # drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    
    [fifo_en, channel] = dut.which_fifo([array, col])

    data = dut.download_fifo( fifo_en )
    volt = dut.adc2volt(data[channel]) - VREF_LO
    
    return volt / _gain_ratio[gain]

def read_single_int(Vread, Vgate, array=0, row=0, col=0, gain=0, Tsh=0x0c, Vref=0.5):
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
    dut.scan_tia( BitArray(_gain_table[gain]*96).bytes )
    
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
    drv.gpio_nforce_safe_write( 0b1 << array )
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    time.sleep(2e-7)
    drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    
    [fifo_en, channel] = dut.which_fifo([array, col])

    data = dut.download_fifo( fifo_en )
    volt = dut.adc2volt(data[channel]) - VREF_LO
    
    return volt / _gain_ratio[gain]

def reset_single(Vreset, Vgate, array=0, row=0, col=0):
#     Vreset = 1
    # Vgate = 5
    Twidth = 1e-6

    ar=array
    r=row
    c=col

    data_load = dut.data_generate_sparse([r, c])
    dut.load_vectors(array=ar, data=data_load)

    dut.pads_defaults()
#     drv.gpio_pin_set(*PIC_PINS['WRT_INTERNAL_EN'])

    drv.gpio_pin_reset(*PIC_PINS['WRITE_ADD_CAP'])
    drv.gpio_pin_set(*PIC_PINS['WRITE_SEL_EXT'])
    dut.reset_dpe()

    dut.dac_set('DAC_VP_PAD', 0)
    

    drv.gpio_nforce_safe_write(0b1<<ar)

    drv.gpio_pin_set(*PIC_PINS['COL_WRITE_CONNECT'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])


    dut.dac_set('DAC_VP_PAD', Vreset)
    time.sleep(Twidth)        # delay(as necessary to write)
    dut.dac_set('DAC_VP_PAD', 0)

    drv.gpio_pin_reset(*PIC_PINS['CONNECT_COLUMN_T'])
    drv.gpio_pin_reset(*PIC_PINS['COL_WRITE_CONNECT'])
    drv.gpio_nforce_safe_write(0)


def set_single(Vset, Vgate, array=0, row=0, col=0):
#     Vset = 1
#     Vgate = 1
    Twidth = 1e-6
    ar=array
    r=row
    c=col

    data_load = dut.data_generate_sparse([r, c])
    dut.load_vectors(array=ar, data=data_load)

    dut.pads_defaults()
#     drv.gpio_pin_set(*PIC_PINS['WRT_INTERNAL_EN'])
    drv.gpio_pin_reset(*PIC_PINS['WRITE_ADD_CAP'])
    drv.gpio_pin_set(*PIC_PINS['WRITE_SEL_EXT'])

    dut.reset_dpe()

    dut.dac_set('DAC_VP_PAD', 0)

    drv.gpio_pin_set(*PIC_PINS['WRITE_FWD'])

    drv.gpio_nforce_safe_write(0b1<<ar)

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

    ar=array
    r=row
    c=col

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
    

    drv.gpio_nforce_safe_write(0b1<<ar)

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
    ar=array
    r=row
    c=col
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

    drv.gpio_nforce_safe_write(0b1<<ar)

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
    dut.scan_tia( BitArray(_gain_table[gain]*96).bytes )
    
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
    drv.gpio_nforce_safe_write( 0b1 << array )
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    time.sleep(2e-7)
    drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    
    [fifo_en, channel] = dut.which_fifo([array, col])

    data = dut.download_fifo( fifo_en )
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
    dut.scan_tia( BitArray(_gain_table[gain]*96).bytes )
    
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
    drv.gpio_nforce_safe_write( 0b1 << array )
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    # drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    
    [fifo_en, channel] = dut.which_fifo([array, col])

    data = dut.download_fifo( fifo_en )
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
    dut.scan_tia( BitArray(_gain_table[gain]*96).bytes )
    
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
    drv.gpio_nforce_safe_write( 0b1 << array )
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    
    [fifo_en, channel] = dut.which_fifo([array, col])

    data = dut.download_fifo( fifo_en )
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
    dut.scan_tia( BitArray(_gain_table[gain]*96).bytes )
    
    # Make sure the VPP is reasonable
    assert VREF_TIA - Vread > -0.2 and VREF_TIA - Vread < 1

    dut.dac_set('PLANE_VPP', VREF_TIA - Vread)
    dut.dac_set('P_VREF_TIA', VREF_TIA)
    dut.dac_set('P_TVDD', Vgate)

    data_load = dut.data_generate_vector(row_vector, [0xffff,0xffff,0xffff,0xffff])
    dut.load_vectors(array=array, data=data_load)

    dut.pads_defaults()

    dut.reset_dpe()

    drv.gpio_pin_set(*PIC_PINS['DPE_INTERNAL_EN'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    drv.gpio_pin_set(*PIC_PINS['READ_BIT'])
    drv.gpio_pin_reset(*PIC_PINS['READ_DPE'])

    # drv.gpio_nforce_safe_write(0b100)
    drv.gpio_nforce_safe_write( 0b1 << array )
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])

    drv.gpio_pin_set(*PIC_PINS['DPE_PULSE'])
    drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])

    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_PULSE'])
    # time.sleep(1e-6)
    # drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    
    volt = []
    fifo_en = [(2-array)*2, (2-array)*2+6, (2-array)*2+1, (2-array)*2+7]
    data1 = dut.download_fifo( fifo_en[0] )
    data2 = dut.download_fifo( fifo_en[1] )
    for b in range(0, 32, 2):
        channel = (b//16)*8 + (7-b%16//2)
        volt.append((dut.adc2volt(data1[channel]) - VREF_LO) / _gain_ratio[gain])
        volt.append((dut.adc2volt(data2[channel]) - VREF_LO) / _gain_ratio[gain])
    data3 = dut.download_fifo( fifo_en[2] )
    data4 = dut.download_fifo( fifo_en[3] )
    for b in range(32, 64, 2):
        channel = (3-b//16)*8 + b%16//2
        volt.append((dut.adc2volt(data3[channel]) - VREF_LO) / _gain_ratio[gain])
        volt.append((dut.adc2volt(data4[channel]) - VREF_LO) / _gain_ratio[gain])
    
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