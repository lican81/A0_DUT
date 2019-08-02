    
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
    

def read_single(Vread, Vgate, array=0, row=0, col=0, gain=0):
    '''
    Args,

    Returns:
        The ADC readout voltages
    '''
    VREF_TIA = 0.5

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
    time.sleep(0.01)
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    
    [fifo_en, channel] = dut.which_fifo([array, row, col])

    data = dut.download_fifo( fifo_en )
    volt = dut.adc2volt(data[channel])
    
    return volt