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

    if new_serial == None:
        ser = serial.Serial(serUSB, baudrate, timeout=1)
        print('Serial port openned.')

    if isinstance(new_serial, serial.Serial):
        ser = new_serial


def disconnect():
    ser.close()
    print('Serial port disconnected.')


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
    ser.write(b'203,' +
              str(data).encode() + b'\0')


def gpio_row_col_bank_write(data):
    ser.write(b'204,' +
              str(data).encode() + b'\0')


def gpio_adc_fifo_en_write(data):
    ser.write(b'205,' +
              str(data).encode() + b'\0')


# def gpio_dataio_dir_write(regDirectionMask):
#     # regDirectionMask = 0xffff for all input
#     #                    0x0000 for all output

#     ser.write(b'206,'
#               + str(regDirectionMask).encode() + b'\0')


def gpio_adc_read():
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
    print(b'215,' +
          str(addr).encode() + b',' +
          str(len(data)).encode() + b',' +
          data + b'\0')

    ser.write(b'215,' +
              str(addr).encode() + b',' +
              str(len(data)).encode() + b',' +
              data + b'\0')

# def spi_read(channel, data):
#     pass


# def pwm_start(channel, width, period):
#     '''
#     There are 3 PWM channels, with ch0 and ch1 sharing timer TMR1, and ch2 using TMR2
#     ch0->OC2, ch1->OC6, ch2-> OC8

#     06/13/19: currently pins are setup so that
#     PIC_READ is CH0 (OC2)
#     PIC_START_SEARCH is CH1 (OC6)
#     PIC_PULSE is CH2 (OC8)

#     PIC_READ is continuous pulse, so setting the width = 0 stops the PWM.

#     The unit for the period and width parameter is 10 ns.
#     The maximum value for both is 0xffff (16-bit timer) for now, i.e. 655,350 ns.
#     '''
#     ser.write(b'209,' +
#               str(channel).encode() + b',' +
#               str(width).encode() + b',' +
#               str(period).encode() + b'\0')

# def mcu_reset():
#     ser.write(b'999,')


# def adc_read():
#     ser.write(b'214\0')

#     value = ser.read(2 * 8)
#     value = struct.unpack('<' + 'H'*8, value)
#     return value

# async def adc_int_read(channel):
#     # Use interupt in the microcontroller
#     pass
