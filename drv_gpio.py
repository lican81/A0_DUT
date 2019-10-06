import serial
import struct

import numpy as np
import functools
from misc import *

# LEVEL N functions: lowest level
# TODO: Make serial port not hardcoded
serUSB = 'COM7'
baudrate = 9600  # Does not matter since the transport is through
# USB-CDC

# def with_serial(func):
#     @functools.wraps(func)
#     def wrapper_with_serial(*args, **kwargs):
#         with serial.Serial(serUSB, baudrate, timeout=1) as ser:
#             func(*args, **kwargs)
#     return wrapper_with_serial

ser = None


def connect(new_serial=None):
    global ser

    if new_serial is None:
        ser = serial.Serial(serUSB, baudrate, timeout=1)
        print('Serial port openned.')

    if isinstance(new_serial, serial.Serial):
        ser = new_serial


def disconnect():
    ser.close()
    # print('Serial port disconnected.')


def gpio_port_write(portName, data):
    # portName: e.g. 'A' indicates portA
    # data:     The value to be written

    # Note: pins for the address bits, datain and dataio are hardcoded in firmware, called out via the '202', etc. function numbers
    ser.write(b'201,' +
              portName.encode() + b',' +
              str(data).encode() + b'\0')


def gpio_port_read(portName):
    ser.write(b'202,' +
              portName.encode() + b'\0')

    value = ser.read(4)
    value = struct.unpack('<I', value)

    return value[0]


def gpio_slewrate_select(portName, mask, slewRate):
    # Slewrate 0-3, from the fastest to slowest
    ser.write(b'210,' +
              portName.encode() + b',' +
              str(mask).encode() + b',' +
              str(slewRate).encode() + b'\0')


def gpio_row_col_data_write(data):
    # Writes data to all ROW_COL_DATA<15..0> PIC pins
    ser.write(b'203,' +
              str(data).encode() + b'\0')


def gpio_row_col_bank_write(data):
    # Writes data to all ROW_COL_BANK<3..0> PIC pins
    ser.write(b'204,' +
              str(data).encode() + b'\0')


def gpio_adc_fifo_en_write(data):
    # Writes data to all ACD_FIFO_EN<3..0> PIC pins
    ser.write(b'205,' +
              str(data).encode() + b'\0')

def gpio_array_en_write(data):
    '''
    Write ARRAY_EN<i> pins
    Example: gpio_array_en_write(0b100) makes:
        ARRAY_EN<2:0> = 100
    Only take the lowest three bits in the data
    '''
    for i in range(3):
        if (data & (0b1 <<i)):
            gpio_pin_set(*PIC_PINS[f'ARRAY_EN<{i}>'])
        else:
            gpio_pin_reset(*PIC_PINS[f'ARRAY_EN<{i}>'])

def gpio_nforce_safe_write(data):
    '''
    Write NFORCE_SAFE0i pins
    Example: gpio_nforce_safe_write(0b100) makes:
        NFORCE_SAFE<2:0> = 100
    Only take the lowest three bits in the data
    '''
    for i in range(3):
        if (data & (0b1 <<i)):
            gpio_pin_set(*PIC_PINS[f'NFORCE_SAFE{i}'])
        else:
            gpio_pin_reset(*PIC_PINS[f'NFORCE_SAFE{i}'])
    
# def gpio_dataio_dir_write(regDirectionMask):
#     # regDirectionMask = 0xffff for all input
#     #                    0x0000 for all output

#     ser.write(b'206,'
#               + str(regDirectionMask).encode() + b'\0')


def gpio_adc_read():
    # ADC bus read of ADC_OUT<12..0> from DPE A0
    ser.write(b'207\0')

    value = ser.read(4)
    value = struct.unpack('<I', value)

    return value[0]


def gpio_pin_set(portName, pinPos):
    ser.write(b'211,'
              + portName.encode() + b','
              + str(pinPos).encode() + b'\0')


def gpio_pin_reset(portName, pinPos):
    ser.write(b'212,'
              + portName.encode() + b','
              + str(pinPos).encode() + b'\0')


def gpio_pin_toggle(portName, pinPos):
    ser.write(b'213,'
              + portName.encode() + b','
              + str(pinPos).encode() + b'\0')


def gpio_pin_is_high(portName, pinPos):

    portValue = gpio_port_read(portName)
    # portValue = 0b1010_1111
    return (1 << pinPos) & portValue != 0


def gpio_pin_set_input(portName, pinPos):
    '''
    Set Pin direction as input
    '''
    ser.write(b'230,'
              + portName.encode() + b','
              + str(pinPos).encode() + b'\0')


def gpio_pin_set_output(portName, pinPos):
    '''
    Set Pin direction as output
    '''
    ser.write(b'231,'
              + portName.encode() + b','
              + str(pinPos).encode() + b'\0')

def pic_dac_init(span=0):
    ser.write(f'304,{span}\0'.encode())

def pic_dac_set(raw=0):
    ser.write(f'302,{raw}\0'.encode())

# def register_write(addr, data):
#     gpio_addr_write(addr)  # safer to write register bits first incase dataio is being pointed to -> PIC_STROBE_REG_N is always propogating through the address decoder circuit so good practice to change 'path' before changing signal

#     portName, pinPos = PIC_PINS['PIC_STROBE_REG_N']
#     gpio_pin_reset(portName, pinPos)

#     gpio_datain_write(data)
#     gpio_pin_set(portName, pinPos)


# def register_read(addr):
#     portName, pinPos = PIC_PINS['PIC_STROBE_REG_N']

#     # For the register read operation, since the read is active during low, we should probably assert the register address  before the strobe reg pin is brought low to make sure we latch/point to the correct register. This is different than register write, which is active on the rising edge. Read is instead simply active low (level vs. edge sensitive).
#     gpio_addr_write(addr)
#     gpio_dataio_dir_write(0xffff)  # set all the dataio pins as input

#     gpio_pin_reset(portName, pinPos)
#     data = gpio_dataio_read()

#     gpio_pin_set(portName, pinPos)

#     return data


def spi_dac_write(data):
    '''
    DAC spi channel=1
    '''
    data = struct.pack('<I', data)
    data = struct.unpack('>I', data)[0]

    ser.write(b'214,' +
              str(data).encode() + b'\0')


def spi_serial_write(addr, data):
    # if 0, SERIAL_CHAIN_SEL0 and SEL1 are 0 # Bottom TIA scan chain
    # if 1, SERIAL_CHAIN_SEL0 is 1 and SEL1 is 0 # TIA settings (top TIA scan chain)
    # if 2, SERIAL_CHAIN_SEL0 is 0 and SEL1 is 1 # Control block
    # if 3, SERIAL_CHAIN_SEL0 is 1 and SEL1 is 1 # No scan chain (empty)
    # DEFAULt IS SERIAL_CHAIN_SEL0 and 1 are low when not explicitly addressed

    # ser.write(b'215,' +
    #           str(addr).encode() + b',' +
    #           str(len(data)).encode() + b',\1' +
    #           data + b'\0')

    ser.write(b'303,' +
                  str(addr).encode() + b',' +
                  str(len(data)).encode() + b',\1,' +
                  data + b'\0')

    ret = ser.read(1)

    if ret != b'0':
        print('[ERROR] SPI return wrong value')

    return ret



def spi_serial_write_and_read(addr, data):
    # if 0, SERIAL_CHAIN_SEL0 and SEL1 are 0
    # if 1, SERIAL_CHAIN_SEL0 is 1 and SEL1 is 0
    # if 2, SERIAL_CHAIN_SEL0 is 0 and SEL1 is 1
    # if 3, SERIAL_CHAIN_SEL0 is 1 and SEL1 is 1
    # DEFAULt IS SERIAL_CHAIN_SEL0 and 1 are low when not explicitly addressed

    # print(b'215,' +
    #       str(addr).encode() + b',' +
    #       str(len(data)).encode() + b',' +
    #       data + b'\0')

    sz_data = len(data)

    ser.write(b'219,' +
              str(addr).encode() + b',' +
              str(sz_data).encode() + b',\1' +
              data + b'\0,')

    line = ser.read(4 * sz_data)

    # values = np.array(struct.unpack('<' + 'I' * sz_data, line))
    return line


def pic_adc_read():
    ser.write(b'216' + b'\0')
    line = ser.read(4 * 5)

    value = np.array(struct.unpack('<' + 'I' * 5, line))
    voltages = value * 3.3 / 0x0fff

    # for voltage in voltages:
    #     print(f'voltage = {voltage:.2f}V')

    return voltages


def clk_start(channel):
    '''
    Start the REFCLKOx
    Example: clk_start('ADC_CK')
    '''
    ch = REFCLKO[channel]
    ser.write(b'217,' +
              str(ch).encode() + b'\0')


def clk_stop(channel):
    '''
    Stop the REFCLKOx
    Example: clk_stop('ADC_CK')
    '''
    ch = REFCLKO[channel]
    ser.write(b'218,' +
              str(ch).encode() + b'\0')


def clk_config(channel, base=0, divisor=20):
    '''
    Change the clock frequency
    '''
    freq = 200000.0 / (2 * (divisor + base / 512.0))
    print(f'Setting {channel} freq={freq}kHz')

    ch = REFCLKO[channel]
    ser.write(b'220,' +
              str(ch).encode() + b',' +
              str(base).encode() + b',' +
              str(divisor).encode() + b'\0')


def i2c_write_pseudo(addr, data):
    ser.write(b'221,' +
              str(addr).encode() + b',' +
              str(data).encode() + b'\0')

