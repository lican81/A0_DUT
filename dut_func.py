from misc import *
import drv_gpio as drv
import time
import numpy as np




def connect(new_serial=None):
    drv.connect(new_serial)

def disconnect():
    drv.disconnect()

def pads_defaults():
    portName, pinPos = PIC_PINS['CONNECT_COLUMN_T']
    drv.gpio_pin_reset(portName, pinPos)
    # time.sleep(1)
    drv.gpio_row_col_data_write(0x0)  # Writes 0 to ROW_COL_DATA<15..0> pins
    portName, pinPos = PIC_PINS['COL_ROW_SEL']
    drv.gpio_pin_reset(portName, pinPos)
    drv.gpio_row_col_bank_write(0b0000) # Writes 0 to ROW_COL_BANK<3..0> pins
    portName, pinPos = PIC_PINS['LATCH_CLK_DATA']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['ARRAY_EN<0>']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['ARRAY_EN<1>']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['ARRAY_EN<2>']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['NFORCE_SAFE0']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['NFORCE_SAFE1']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['NFORCE_SAFE2']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['READ_BIT']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['READ_DPE']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['COL_WRITE_CONNECT']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['CONNECT_TIA']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['DPE_PULSE']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['AGC_PULSE']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['DPE_INTERNAL_EN']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['AGC_INTERNAL_EN']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['DPE_EXT_OVERRIDE_EN ']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['DPE_EXTERNAL_PULSE']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['DPE_EXT_SH']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['WRITE_FWD']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['WRT_INTERNAL_EN']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['WRT_PULSE']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['WRITE_SEL_EXT']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['WRITE_ADD_CAP']
    drv.gpio_pin_reset(portName, pinPos)
    portName, pinPos = PIC_PINS['ADC_FIFO_ADVANCE']
    drv.gpio_pin_reset(portName, pinPos)
    drv.gpio_adc_fifo_en_write(0b0000) # Writes to ADC_FIFO_EN<3..0> pins
    drv.gpio_pin_reset(*PIC_PINS['ADC_SEL_EXTERNAL'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_BUS_IN'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_CK_IN'])
    drv.gpio_pin_reset(*PIC_PINS['UPDATE_TIA_CONF'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_CHAIN_SEL0'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_CHAIN_SEL1'])

powered_on = 0

def power_on():
    # Refer to Figure 1 for timing diagram
    # Q for Jacqui: Bring up microcontroller power? VDD_ microcontroller = See Table 1
	time.sleep(1) # want to delay 1us
    drv.gpio_pin_reset(*PIC_PINS['NRESET_FULL_CHIP'])
    drv.gpio_pin_reset(*PIC_PINS['NRESET_DPE_ENGINE'])
    pads_defaults()

    # Switch from ground to VDD here after probing to make sure VDD is at the desired value and stable from the DUT

    # Q for Jacqui: VDD_SuperT=See Table 1 -> is this 'Plane VPP'?
    
    while True:
            if P_POWER_GOOD==0: continue
            else:
                time.sleep(100) # want to delay (1ms)
                break

    ALL_VREFS = See Table 1
    dac_set('VREF_ARRAY',0.5)

    # Initialize clocks -> to be written! CK_ARRAY and ADC_CK


    time.sleep(10) # want to delay 10us
    reset_chip()
    time.sleep(1) #delay(1 P_CK_ARRAY clock period)
    scan_control() # Make sure to use the switch in scan_control() to follow during power on specifically
    reset_dpe()

    # Identify globally that chip has been powered on
    global powered_on
    powered_on = 1

def scan_control():
    pass

def power_off():
    pass
    global powered_on
    powered_on = 0

def reset_chip():
	# Resets all scanned in values, TIA enables, and row and column vector registers
	if powered_on == 0:
	    power_on()
    portName, pinPos = PIC_PINS['NRESET_FULL_CHIP']
    drv.gpio_pin_reset(portName, pinPos)
	time.sleep(1) # want to delay 1us
	drv.gpio_pin_set(portName, pinPos)

def reset_dpe():
	# Resets control counters, ADC flip flops, FIFO, and control shadow registers
	if powered_on == 0:
	    power_on()
    portName, pinPos = PIC_PINS['NRESET_DPE_ENGINE']
    drv.gpio_pin_reset(portName, pinPos)
	time.sleep(1) # want to delay 1us
	drv.gpio_pin_set(portName, pinPos)




def dac_init(span=0b010):
    '''
    Span code:
    S2  S1  S0  Span
    ----------------
    0   0   0   0-5 V
    0   0   1   0-10
    0   1   0   -5 ~ +5V
    0   1   1  *-
    1   0   0   -2.5 ~ +2.5

    See DAC_SPAN in misc.py
    '''
    portName, pinPos = PIC_PINS['PIC_LDAC']
    drv.gpio_pin_set(portName, pinPos)

    portName, pinPos = PIC_PINS['PIC_TGP']
    drv.gpio_pin_set(portName, pinPos)

    portName, pinPos = PIC_PINS['PIC_CLR']
    drv.gpio_pin_reset(portName, pinPos)
    # time.sleep(1)
    drv.gpio_pin_set(portName, pinPos)

    cmd = 0b1110
    # address = 0b0000
    # address = DAC_CH[channel]

    data = span | (cmd << 20)
    drv.spi_dac_write(data)
    # print(f'{data:08x}')

    dac_set.is_init = True
    dac_set.span = span

    vlim_lo, vlim_hi = DAC_SPAN[dac_set.span]
    print(f'DAC initialized to a span from {vlim_lo} V to {vlim_hi} V')


def dac_set(channel, voltage):
    # print(f'DAC: setting ch={channel} to vol={voltage}')
    '''
    '''
    if dac_set.is_init == False:
        dac_init(span = 0b010)

    cmd = 0b0011
    # address = 0b0000
    address = DAC_CH[channel]

    # data = int(voltage)
    vlim_lo, vlim_hi = DAC_SPAN[dac_set.span]
    data = int( (voltage - vlim_lo) / (vlim_hi-vlim_lo) * 0xffff  )
    # print(f'{data:08x}')
    data |= (address << 16) | (cmd << 20)
    # print(f'{data:08x}')

    drv.spi_dac_write(data)


