from misc import *
import drv_gpio as drv
import time
import numpy as np

powered_on = False
dpe_reseted = False
tia_scanned = False
control_scanned = False
adc_calibrated = False
tia_calibrated = False

def connect(new_serial=None):
    drv.connect(new_serial)

def disconnect():
    drv.disconnect()

def pads_defaults():
    drv.gpio_pin_reset(*PIC_PINS['CONNECT_COLUMN_T'])
    time.sleep(1e-6)
    drv.gpio_row_col_data_write(0x0)  # Writes 0 to ROW_COL_DATA<15..0> pins
    drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
    drv.gpio_row_col_bank_write(0b0000) # Writes 0 to ROW_COL_BANK<3..0> pins
    drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
    drv.gpio_pin_reset(*PIC_PINS['ARRAY_EN<0>'])
    drv.gpio_pin_reset(*PIC_PINS['ARRAY_EN<1>'])
    drv.gpio_pin_reset(*PIC_PINS['ARRAY_EN<2>'])
    drv.gpio_pin_reset(*PIC_PINS['NFORCE_SAFE0'])
    drv.gpio_pin_reset(*PIC_PINS['NFORCE_SAFE1'])
    drv.gpio_pin_reset(*PIC_PINS['NFORCE_SAFE2'])
    drv.gpio_pin_reset(*PIC_PINS['READ_BIT'])
    drv.gpio_pin_reset(*PIC_PINS['READ_DPE'])
    drv.gpio_pin_reset(*PIC_PINS['COL_WRITE_CONNECT'])
    drv.gpio_pin_reset(*PIC_PINS['CONNECT_TIA'])
    drv.gpio_pin_reset(*PIC_PINS['DPE_PULSE'])
    drv.gpio_pin_reset(*PIC_PINS['AGC_PULSE'])
    drv.gpio_pin_reset(*PIC_PINS['DPE_INTERNAL_EN'])
    drv.gpio_pin_reset(*PIC_PINS['AGC_INTERNAL_EN'])
    drv.gpio_pin_reset(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    drv.gpio_pin_reset(*PIC_PINS['DPE_EXT_PULSE'])
    drv.gpio_pin_reset(*PIC_PINS['DPE_EXT_SH'])
    drv.gpio_pin_reset(*PIC_PINS['WRITE_FWD'])
    drv.gpio_pin_reset(*PIC_PINS['WRT_INTERNAL_EN'])
    drv.gpio_pin_reset(*PIC_PINS['WRT_PULSE'])
    drv.gpio_pin_reset(*PIC_PINS['WRITE_SEL_EXT'])
    drv.gpio_pin_reset(*PIC_PINS['WRITE_ADD_CAP'])
    drv.gpio_pin_reset(*PIC_PINS['ADC_FIFO_ADVANCE'])
    drv.gpio_adc_fifo_en_write(0b0000) # Writes to ADC_FIFO_EN<3..0> pins
    drv.gpio_pin_reset(*PIC_PINS['ADC_SEL_EXTERNAL'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_BUS_IN'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_CK_IN'])
    drv.gpio_pin_reset(*PIC_PINS['UPDATE_TIA_CONF'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_CHAIN_SEL0'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_CHAIN_SEL1'])

def power_on():
    # this function is for documentation ONLY right now! 
    # Some physical switches on board are required for power on procedure
    
    # Refer to Figure 1 for timing diagram
    # Q for Jacqui: Bring up microcontroller power? VDD_ microcontroller = See Table 1
    time.sleep(1e-6) # want to delay 1us
    drv.gpio_pin_reset(*PIC_PINS['NRESET_FULL_CHIP'])
    drv.gpio_pin_reset(*PIC_PINS['NRESET_DPE_ENGINE'])
    pads_defaults()

    # # Switch from ground to VDD here after probing to make sure VDD is at the desired value and stable from the DUT

    # Q for Jacqui: VDD_SuperT=See Table 1 -> is this 'Plane VPP'? NOPE: this is the switch on the board!!
    
    while True:
        powergoodhigh = drv.gpio_pin_is_high(*PIC_PINS['PWR_GOOD'])
        if powergoodhigh:
            time.sleep(1e-3) # want to delay (1ms)
            break

    # ALL_VREFS = See Table 1 in Cookbook documentation
    vrefs_defaults()

    # Initialize clocks -> TO BE WRITTEN! CK_ARRAY and ADC_CK
    drv.clk_start('ADC_CLK')
    drv.clk_start('CK_ARRAY')
    
    time.sleep(1e-5) # want to delay 10us
    reset_chip()
    time.sleep(2e-8) #delay(1 P_CK_ARRAY clock period)
    poweron_scan_control() # Make sure to use the switch in scan_control() to follow during power on specifically
    reset_dpe()

    # Identify globally that chip has been powered on
    global powered_on
    powered_on = True

def vrefs_defaults():
    dac_set('DAC_VREF_ARRAY',0.5)
    dac_set('P_VREF_TIA',0.5)
    dac_set('P_VREF_SH',2.5)
    dac_set('PLANE_VPP',0.3)
    dac_set('DAC_VP_PAD',0)
    dac_set('P_TVDD', 5)
    dac_set('P_VAGC_0', 1)
    dac_set('P_VAGC_1', 4)
    dac_set('DAC_VREF_HI_CMP', 4)
    dac_set('P_ADC_EXT_TEST_IN', 0)
    
def vrefs_off():
    dac_set('DAC_VREF_ARRAY',0)
    dac_set('P_VREF_TIA',0)
    dac_set('P_VREF_SH',0)
    dac_set('PLANE_VPP',0)
    dac_set('DAC_VP_PAD',0)
    dac_set('P_TVDD', 0)
    dac_set('P_VAGC_0', 0)
    dac_set('P_VAGC_1', 0)
    dac_set('DAC_VREF_HI_CMP', 0)
    dac_set('P_ADC_EXT_TEST_IN', 0)
    dac_set('P_AMP_VREF', 0)
    dac_set('P_AMP_INPUT', 0)
    dac_set('DAC_SPARE1', 0)
    dac_set('DAC_SPARE2', 0)    
    dac_set('DAC_DRIVE_VN', 0)
    dac_set('DAC_SCHOTTKY', 0)

def poweron_scan_control():
    pads_defaults()
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_CK_IN'])
    
    # P_SERIAL_CK_IN number of clock pulses = number of bits read in using P_SERIAL_BUS_IN # Number of clock pulses must exactly equal the number of scan bits being read in 
	#for pulse in P_SERIAL_CK_IN clock pulses:
    #    P_SERIAL_BUS_IN data latched in # Refer to Figure 2 for timing diagram and to Table 3 for recommended initial values to use during power on
    data = bytes([0b01000000, 0b10000000, 0b00000100, 0b00000000, 0b00110000, 0b01000000,0b00001000])
    drv.spi_serial_write(1, data) # addr 1 here means SERIAL_CHAIN_SEL0 is 1 and _SEL1 is 0
    

def power_off():
    drv.gpio_pin_reset(*PIC_PINS['NRESET_DPE_ENGINE'])
    time.sleep(2e-8) # want to delay 1 CK_array CP
    drv.gpio_pin_reset(*PIC_PINS['NRESET_FULL_CHIP'])
    time.sleep(1e-5)# want to delay 10us  
    
    # STILL TO BE WRITTEN in drv_gpio
    drv.clk_stop('ADC_CK')
    drv.clk_stop('CK_ARRAY')        
    vrefs_off()
    global powered_on
    powered_on = False

def reset_chip():
    # Resets all scanned in values, TIA enables, and row and column vector registers
    if ~powered_on:
        power_on()
        
    drv.gpio_pin_reset(*PIC_PINS['NRESET_FULL_CHIP'])
    time.sleep(1e-6) # want to delay 1us
    drv.gpio_pin_set(*PIC_PINS['NRESET_FULL_CHIP'])

def reset_dpe():
    # Resets control counters, ADC flip flops, FIFO, and control shadow registers
    if ~powered_on:
        power_on()
    drv.gpio_pin_reset(*PIC_PINS['NRESET_DPE_ENGINE'])
    time.sleep(1e-6) # want to delay 1us
    drv.gpio_pin_set(*PIC_PINS['NRESET_DPE_ENGINE'])
    global dpe_reseted
    dpe_reseted = True

def dac_init(span=0b010):
    '''
    Span code:
    S2  S1  S0  Span
    ----------------
    0   0   0   0-5 V
    0   0   1   0-10
    0   1   0   -5 ~ +5V
    0   1   1   -10 ~ + 10
    1   0   0   -2.5 ~ +2.5

    See DAC_SPAN in misc.py
    '''
    drv.gpio_pin_set(*PIC_PINS['PIC_LDAC'])

    drv.gpio_pin_set(*PIC_PINS['PIC_TGP'])

    drv.gpio_pin_reset(*PIC_PINS['PIC_CLR'])
    # time.sleep(1)
    drv.gpio_pin_set(*PIC_PINS['PIC_CLR'])

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

dac_set.is_init = False

# def scan_control():
#     if ~powered_on:
#         power_on()
#         reset_dpe()
#     pads_defaults()

def calibrate_adc():
    if ~powered_on:
        power_on()
    if ~dpe_reseted:
        reset_dpe()
    pads_defaults()
    drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE2'])
    drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE1'])
    drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE0'])
    dac_set('P_ADC_EXT_TEST_IN', 1.5)       # voltage = 1.5 as an example, I wonder whether we should put it as a parameter of the function
    time.sleep(1e-6)        # delay(t_sel_ext or t_ext_inp), min = 2CK
    drv.gpio_pin_set(*PIC_PINS['ADC_SEL_EXTERNAL'])
    #time.sleep(1e-6)       # delay(t_en_overide_sh), min = 0CK
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERIDE_EN'])
    time.sleep(1e-6)        # delay(t_fire_sh), min = 3CK
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    time.sleep(1e-6)        # delay(3 P_ADC_CK periods)
    drv.gpio_pin_reset(*PIC_PINS['DPE_EXT_SH'])
    while True:
        if drv.gpio_pin_is_high(*PIC_PINS['ADC_DONE']):
            break
    download_fifo()
    pads_defaults()
    reset_dpe()

def calibrate_tia():
    if ~powered_on:
        power_on()
    if ~dpe_reseted:
        reset_dpe()
    if ~tia_scanned:
        scan_tia()
    if ~adc_calibrated:
        calibrate_adc()
    #if ~vectors_loaded:
        #load_vectors()
    pads_defaults()
    #VP_PAD
    drv.gpio_pin_set(*PIC_PINS['WRITE_SEL_EXT'])
    time.sleep(5e-7)        # delay(t_cntl_setup), min = 3TCK
    drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE2'])
    drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE1'])
    drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE0'])
    time.sleep(5e-7)        # delay(t_cal_start), min = 2TCK
    drv.gpio_pin_set(*PIC_PINS['COL_WRITE_CONNECT'])
    time.sleep(5e-7)        # delay(t_opamp), min = 500ns
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    while True:
        if drv.gpio_pin_is_high(*PIC_PINS['ADC_DONE']):
            break
    time.sleep(5e-7)        #delay(t_end_cal), min = 2TCK
    download_fifo()
    drv.gpio_pin_reset(*PIC_PINS['COL_WRITE_CONNECT'])
    time.sleep(5e-7)        #delay(t_disconnect), min = 2TCK
    drv.gpio_pin_reset(*PIC_PINS['CONNECT_TIA'])
    time.sleep(5e-7)        #delay(t_array_cell), min = 2TCK
    drv.gpio_pin_reset(*PIC_PINS['NFORCE_SAFE2'])
    drv.gpio_pin_reset(*PIC_PINS['NFORCE_SAFE1'])
    drv.gpio_pin_reset(*PIC_PINS['NFORCE_SAFE0'])
    pads_defaults()
    reset_dpe()

def load_vectors(array, data):
    # array: a list or an int which contains the arrays you want to enable, i.e. [0, 1]: enable array0 and 1; 0: enable array0; 3: enable all arrays
    # data: a list which contains at (8, 16, 24) elements, each element is an hex int in the range of [0x0000, 0xffff], every four elements form a 64-bit vector...
    # every eight elements form the vectors for an array, the first four form row vector, second four form colume vector.
    # from left to right
    if ~powered_on:
        power_on()
    if ~dpe_reseted:
        reset_dpe()
    pads_defaults()
    if isinstance(array, list):
        N = len(array)
        for a in range(0, N):
            drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<%d>' %(array[a])])
            drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
            for b in range(0, 4):
                addr = bin(1)
                drv.gpio_row_col_bank_write(addr)
                drv.gpio_row_col_data_write(data[N*a+b])
                time.sleep(1e-7)
                drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
                time.sleep(1e-7)
                drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
                addr = addr << 1
            drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
            for b in range(4, 8):
                addr = bin(1)
                drv.gpio_row_col_bank_write(addr)
                drv.gpio_row_col_data_write(data[N*a+b])
                time.sleep(1e-7)
                drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
                time.sleep(1e-7)
                drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
                addr = addr << 1
            drv.gpio_pin_reset(*PIC_PINS['ARRAY_EN<%d>' %(array[a])])
    elif array == 3:
        drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<0>'])
        drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<1>'])
        drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<2>'])
        drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
        for b in range(0, 4):
            addr = bin(1)
            drv.gpio_row_col_bank_write(addr)
            drv.gpio_row_col_data_write(data[b])
            time.sleep(1e-7)
            drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
            time.sleep(1e-7)
            drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
            addr = addr << 1
        drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
        for b in range(4, 8):
            addr = bin(1)
            drv.gpio_row_col_bank_write(addr)
            drv.gpio_row_col_data_write(data[b])
            time.sleep(1e-7)
            drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
            time.sleep(1e-7)
            drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
            addr = addr << 1
    elif (array == 0) or (array == 1) or (array == 2):
        drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<%d>' %(array)])
        drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
        for b in range(0, 4):
            addr = bin(1)
            drv.gpio_row_col_bank_write(addr)
            drv.gpio_row_col_data_write(data[b])
            time.sleep(1e-7)
            drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
            time.sleep(1e-7)
            drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
            addr = addr << 1
        drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
        for b in range(4, 8):
            addr = bin(1)
            drv.gpio_row_col_bank_write(addr)
            drv.gpio_row_col_data_write(data[b])
            time.sleep(1e-7)
            drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
            time.sleep(1e-7)
            drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
            addr = addr << 1
    else:
        print("Input error, please see the instruction")
        return
    pads_defaults()
    reset_dpe()

def data_generate(index):
    # index: a list, which contains the row and colume you want to write. If index = 1, the output is all 1
    # i.e. For the same array: [0, 2]: row 0 and col 2, [0, 2, 3, 6]: row 0 and col2, row 3 and col 6
    # for different array: [[0, 2], [3, 6]]
    if index == 1:
        data = [0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff]
        return data
    elif isinstance(index, list):
        if isinstance(index[0], list):
            N = len(index)
            data = []
            for a in range(0, N):
                data = data+[0, 0, 0, 0, 0, 0, 0, 0]
            for a in range(0, N):
                M = len(index[a])//2
                for b in range(0, M):
                    # row data
                    row_dic = {0: 2, 1: 0, 2: 1, 3: 3}
                    bank_row = row_dic[index[a][2*b]//16]
                    if index[a][2*b]%2 == 1 and  index[a][2*b] < 32:
                        bit = index[a][2*b]%16//2
                        if data[8*a+bank_row] >> (bit + 8) == 0:
                            data[8*a+bank_row] = data[8*a+bank_row] + (1 << (bit + 8))
                    elif index[a][2*b]%2 == 0 and  index[a][2*b] < 32:
                        bit = index[a][2*b]%16//2
                        if data[8*a+bank_row] >> bit == 0:
                            data[8*a+bank_row] = data[8*a+bank_row] + (1 << bit)
                    elif index[a][2*b]%2 == 1 and  index[a][2*b] >= 32:
                        bit = index[a][2*b]%16//2
                        if data[8*a+bank_row] >> (15-bit) == 0:
                            data[8*a+bank_row] = data[8*a+bank_row] + (1 << (15 - bit))
                    elif index[a][2*b]%2 == 0 and  index[a][2*b] >= 32:
                        bit = index[a][2*b]%16//2
                        if data[8*a+bank_row] >> (7-bit) == 0:
                            data[8*a+bank_row] = data[8*a+bank_row] + (1 << (7 - bit))
                    # colume data
                    bank_col = 2*(index[a][2*b+1]//32) + (index[a][2*b+1]%2)
                    if index[a][2*b+1] < 32:
                        bit = 15 - (index[a][2*b+1]//2)
                        if data[8*a+bank_col+4] >> bit == 0:
                            data[8*a+bank_col+4] = data[8*a+bank_col+4] + (1 << bit)
                    elif index[a][2*b+1] >= 32:
                        bit = (index[a][2*b+1]-32)//2
                        if data[8*a+bank_col+4] >> bit == 0:
                            data[8*a+bank_col+4] = data[8*a+bank_col+4] + (1 << bit)
            return data
        elif isinstance(index[0], int):
            data = [0, 0, 0, 0, 0, 0, 0, 0]
            M = len(index)//2
            for b in range(0, M):
                # row data
                row_dic = {0: 2, 1: 0, 2: 1, 3: 3}
                bank_row = row_dic[index[2*b]//16]
                if index[2*b]%2 == 1 and  index[2*b] < 32:
                    bit = index[2*b]%16//2
                    if data[bank_row] >> (bit + 8) == 0:
                        data[bank_row] = data[bank_row] + (1 << (bit + 8))
                elif index[2*b]%2 == 0 and  index[2*b] < 32:
                    bit = index[2*b]%16//2
                    if data[bank_row] >> bit == 0:
                        data[bank_row] = data[bank_row] + (1 << bit)
                elif index[2*b]%2 == 1 and  index[2*b] >= 32:
                    bit = index[2*b]%16//2
                    if data[bank_row] >> (15-bit) == 0:
                        data[bank_row] = data[bank_row] + (1 << (15 - bit))
                elif index[2*b]%2 == 0 and  index[2*b] >= 32:
                    bit = index[2*b]%16//2
                    if data[bank_row] >> (7-bit) == 0:
                        data[bank_row] = data[bank_row] + (1 << (7 - bit))
                # colume data
                bank_col = 2*(index[2*b+1]//32) + (index[2*b+1]%2)
                if index[2*b+1] < 32:
                    bit = 15 - (index[2*b+1]//2)
                    if data[bank_col+4] >> bit == 0:
                        data[bank_col+4] = data[bank_col+4] + (1 << bit)
                elif index[2*b+1] >= 32:
                    bit = (index[2*b+1]-32)//2
                    if data[bank_col+4] >> bit == 0:
                        data[bank_col+4] = data[bank_col+4] + (1 << bit)
            return data

def download_fifo(fifo_en):
    # fifo: an int ([0, 11]) which indicates which fifo you want to download. If you want to download all of them, fifo = 12
    pads_defaults()
    if fifo_en < 12:
        drv.gpio_adc_fifo_en_write(bin(11-fifo_en))
        time.sleep(2e-7)        # delay(2 P_ADC_CK periods)
        array_num = (fifo_en % 6)//2
        drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE%d' %(array_num)])
        for b in range(15, -1, -1):
            time.sleep(2e-7)        # delay(2 P_ADC_CK periods)
            drv.gpio_pin_set(*PIC_PINS['ADC_FIFO_ADVANCE'])
            time.sleep(2e-7)        # delay(2 P_ADC_CK periods)
            drv.gpio_pin_reset(*PIC_PINS['ADC_FIFO_ADVANCE'])
            time.sleep(2e-7)        # delay(2 P_ADC_CK periods)
    elif fifo_en == 12:
        for a in range(0, 12):
            drv.gpio_adc_fifo_en_write(bin(11-a))
            time.sleep(2e-7)        # delay(2 P_ADC_CK periods)
            array_num = (a % 6)//2
            drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE%d' %(array_num)])
            for b in range(15, -1, -1):
                time.sleep(2e-7)        # delay(2 P_ADC_CK periods)
                drv.gpio_pin_set(*PIC_PINS['ADC_FIFO_ADVANCE'])
                time.sleep(2e-7)        # delay(2 P_ADC_CK periods)
                drv.gpio_pin_reset(*PIC_PINS['ADC_FIFO_ADVANCE'])
                time.sleep(2e-7)        # delay(2 P_ADC_CK periods)
    else:
        print("Input error, fifo must be an int in the range [0, 12]")
        return
    pads_defaults()
    reset_dpe()

def read(array, index):
    if ~powered_on:
        power_on()
    if ~control_scanned:
        scan_control()
    if ~tia_scanned:
        scan_tia()
    if ~adc_calibrated:
        calibrate_adc()
    if ~tia_calibrated:
        calibrate_tia()
    data = data_generate(index)
    load_vectors(array, data)
    time.sleep(2e-7)
    drv.gpio_pin_set(*PIC_PINS['DPE_INTERNAL_EN'])
    