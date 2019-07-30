from misc import *
import drv_gpio as drv
import time
import numpy as np
from bitstring import BitArray

powered_on = False
dpe_reseted = False
tia_scanned = False
adc_calibrated = False
vectors_loaded = False


def connect(new_serial=None):
    drv.connect(new_serial)


def disconnect():
    drv.disconnect()


def pads_defaults():
    drv.gpio_pin_reset(*PIC_PINS['CONNECT_COLUMN_T'])
    time.sleep(1e-6)
    drv.gpio_row_col_data_write(0x0)  # Writes 0 to ROW_COL_DATA<15..0> pins
    drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
    drv.gpio_row_col_bank_write(0b0000)  # Writes 0 to ROW_COL_BANK<3..0> pins
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
    drv.gpio_adc_fifo_en_write(0b0000)  # Writes to ADC_FIFO_EN<3..0> pins
    drv.gpio_pin_reset(*PIC_PINS['ADC_SEL_EXTERNAL'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_BUS_IN'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_CK_IN'])
    drv.gpio_pin_reset(*PIC_PINS['UPDATE_TIA_CONF'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_CHAIN_SEL0'])
    drv.gpio_pin_reset(*PIC_PINS['SERIAL_CHAIN_SEL1'])

def ground_PIC():
    # Procedure on PIC BEFORE connectinh/powering on A0.
    dac_init()
    vrefs_off()
    pads_defaults()
    drv.clk_stop('ADC_CK')
    drv.clk_stop('CK_ARRAY')
    drv.gpio_pin_reset(*PIC_PINS['NRESET_FULL_CHIP'])
    drv.gpio_pin_reset(*PIC_PINS['NRESET_DPE_ENGINE'])
    drv.gpio_pin_reset(*PIC_PINS['PWR_GOOD'])


def power_on():
    # NOTE: Some physical switches on board are required for power on procedure
    # Refer to Figure 1 of cookbook for timing diagram
    time.sleep(1e-6)  # want to delay 1us
    drv.gpio_pin_reset(*PIC_PINS['NRESET_FULL_CHIP'])
    drv.gpio_pin_reset(*PIC_PINS['NRESET_DPE_ENGINE'])
    pads_defaults()
    # # Switch from ground to VDD here after probing to make sure VDD is at the desired value and stable from the DUT
    drv.gpio_pin_set(*PIC_PINS['PWR_GOOD'])

    # ALL_VREFS = See Table 1 in Cookbook documentation
    vrefs_defaults()
    # Initialize clocks
    drv.clk_start('ADC_CK')
    drv.clk_start('CK_ARRAY')
    time.sleep(1e-5)  # want to delay 10us
    reset_chip()
    time.sleep(2e-8)  # delay(1 P_CK_ARRAY clock period)
    # Make sure to input scan_control() to follow during power on specifically to control block
    scan_control()
    reset_dpe()
    # Identify globally that chip has been powered on
    global powered_on
    powered_on = True


def vrefs_defaults():
    dac_set('DAC_VREF_ARRAY', 0.42)
    dac_set('P_VREF_TIA', 0.42)
    dac_set('P_VREF_SH', 2.42)
    dac_set('PLANE_VPP', 0.22)
    dac_set('DAC_VP_PAD', 2.5)
    dac_set('P_TVDD', 1)
    dac_set('P_VAGC_0', 1)
    dac_set('P_VAGC_1', 3.9)
    dac_set('DAC_VREF_HI_CMP', 3.92)
    dac_set('P_ADC_EXT_TEST_IN', 1)
    dac_set('P_ADC_EXT_TEST_IN', 0)
    dac_set('P_AMP_VREF', 2.5)
    dac_set('P_AMP_INPUT', 2.5)


def vrefs_off():
    dac_set('DAC_VREF_ARRAY', 0)
    dac_set('P_VREF_TIA', 0)
    dac_set('P_VREF_SH', 0)
    dac_set('PLANE_VPP', 0)
    dac_set('DAC_VP_PAD', 0)
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


def scan_control():
    pads_defaults()
    #    P_SERIAL_BUS_IN data latched in # Refer to Figure 2 for timing diagram and to Table 3 for recommended initial values to use during power on
    data = bytes([0b000_10000, 0b0000_0010 , 0b0000_1100,0b0001_0000, 0b0010_0000, 0b00000001, 0b00000010])
    drv.spi_serial_write(2, data)


def power_off():
    vrefs_off()
    pads_defaults()
    drv.clk_stop('CK_ARRAY')
    drv.clk_stop('ADC_CK')
    drv.gpio_pin_reset(*PIC_PINS['NRESET_DPE_ENGINE'])
    time.sleep(2e-8)  # want to delay 1 CK_array CP
    drv.gpio_pin_reset(*PIC_PINS['NRESET_FULL_CHIP'])
    time.sleep(1e-5)  # want to delay 1 CK_array CP
    drv.gpio_pin_reset(*PIC_PINS['PWR_GOOD'])
    global powered_on
    powered_on = False


def reset_chip():
    drv.gpio_pin_reset(*PIC_PINS['NRESET_FULL_CHIP'])
    time.sleep(1e-6)  # want to delay 1us
    drv.gpio_pin_set(*PIC_PINS['NRESET_FULL_CHIP'])


def reset_dpe():
    drv.gpio_pin_reset(*PIC_PINS['NRESET_DPE_ENGINE'])
    time.sleep(1e-6)  # want to delay 1us
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
        dac_init(span=0b010)

    cmd = 0b0011
    # address = 0b0000
    address = DAC_CH[channel]

    # data = int(voltage)
    vlim_lo, vlim_hi = DAC_SPAN[dac_set.span]
    data = int((voltage - vlim_lo) / (vlim_hi-vlim_lo) * 0xffff)
    # print(f'{data:08x}')
    data |= (address << 16) | (cmd << 20)
    # print(f'{data:08x}')

    drv.spi_dac_write(data)
    
dac_set.is_init = False


def py_logic_analyzer():
    val = drv.gpio_pin_is_high(*PIC_PINS['PWR_GOOD'])
    print(int(val),"\tPWR_GOOD")
    val = drv.gpio_pin_is_high(*PIC_PINS['NRESET_FULL_CHIP'])
    print(int(val),"\tNRESET_FULL_CHIP")
    val = drv.gpio_pin_is_high(*PIC_PINS['NRESET_DPE_ENGINE'])
    print(int(val),"\tNRESET_DPE_ENGINE")
    val = drv.gpio_pin_is_high(*PIC_PINS['ARRAY_EN<0>'])
    print(int(val),"\tARRAY_EN<0>")
    val = drv.gpio_pin_is_high(*PIC_PINS['ARRAY_EN<1>'])
    print(int(val),"\tARRAY_EN<1>")
    val = drv.gpio_pin_is_high(*PIC_PINS['ARRAY_EN<2>'])
    print(int(val),"\tARRAY_EN<2>")
    val = drv.gpio_pin_is_high(*PIC_PINS['NFORCE_SAFE0'])
    print(int(val),"\tNFORCE_SAFE0")
    val = drv.gpio_pin_is_high(*PIC_PINS['NFORCE_SAFE1'])
    print(int(val),"\tNFORCE_SAFE1")
    val = drv.gpio_pin_is_high(*PIC_PINS['NFORCE_SAFE2'])
    print(int(val),"\tNFORCE_SAFE2")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_SEL_EXTERNAL'])
    print(int(val),"\tADC_SEL_EXT")
    val = drv.gpio_pin_is_high(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    print(int(val),"\tDPE_EXT_OVERRIDE_EN")
    val = drv.gpio_pin_is_high(*PIC_PINS['DPE_EXT_SH'])
    print(int(val),"\tDPE_EXT_SH")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_DONE'])
    print(int(val),"\tADC_DONE")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_FIFO_ADVANCE'])
    print(int(val),"\tADC_FIFO_ADVANCE")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_FIFO_EN<0>'])
    print(int(val),"\tADC_FIFO_EN<0>")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_FIFO_EN<1>'])
    print(int(val),"\tADC_FIFO_EN<1>")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_FIFO_EN<2>'])
    print(int(val),"\tADC_FIFO_EN<2>")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_FIFO_EN<3>'])
    print(int(val),"\tADC_FIFO_EN<3>")


def scan_tia(data):
    # 960 bit long scan chain for all TIA settings
    # Scan chain numbers 1 and 0 must always be enabled during TIA configuration.
    #data = BitArray('0b1100000100'*96).bytes
    # bits 0-4 are gain control 10000 - 1M; 00001 - 1k
    # bit 5 is Opamp miller compensation
    # bits 6,7 are compensation capacitors
    # bits 8,9 are OpAmp enables

    drv.spi_serial_write(0, data)   # Bottom arrays
    drv.spi_serial_write(1, data)   # Top arrays
    time.sleep(1e-6)
    drv.gpio_pin_set(*PIC_PINS['UPDATE_TIA_CONF'])
    drv.gpio_pin_reset(*PIC_PINS['UPDATE_TIA_CONF'])
    global tia_scanned
    tia_scanned = True


def calibrate_adc(voltages,addr_fifo):
    # Assumes power good, and power_on() procedure completed with control block scan chain loaded
    # example inputs: voltages = np.arange(0.5, 4.5, 0.5) and addr_fifo=0b000
    reset_dpe()

    # Scan in TIA settings: TIA SCAN IN OP AMPS ENABLED, No COMPENSATION, 30k gain
    # Scan chain numbers 1 and 0 must always be enabled during TIA configuration (opamp enable)
    # Last 5 bits represent TIA gain: 10000 - 1M; 00001 - 1k
    data = BitArray('0b1100000100'*96).bytes
    scan_tia(data)

    drv.gpio_array_en_write(0b111)
    drv.gpio_nforce_safe_write(0b111)

    # voltage = 1.5 as an example, I wonder whether we should put it as a parameter of the function
    dac_set('P_ADC_EXT_TEST_IN', voltages[0] )
    time.sleep(1e-6)        # delay(t_sel_ext or t_ext_inp), min = 2CK
    drv.gpio_pin_set(*PIC_PINS['ADC_SEL_EXTERNAL'])
    # time.sleep(1e-6)       # delay(t_en_overide_sh), min = 0CK
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    time.sleep(1e-6)        # delay(t_fire_sh), min = 3CK
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    time.sleep(1e-6)        # delay(3 P_ADC_CK periods)
    drv.gpio_pin_reset(*PIC_PINS['DPE_EXT_SH'])

    while True:
        if drv.gpio_pin_is_high(*PIC_PINS['ADC_DONE']):
            break

    drv.gpio_adc_fifo_en_write(addr_fifo) # Select which FIFO to download from

    data = drv.gpio_adc_read()
    print(f'{data:013b}\t {adc2volt(data):.3f} V')

    for V_adc in voltages:
        dac_set('P_ADC_EXT_TEST_IN', V_adc)    

        time.sleep(1e-6)
        drv.gpio_pin_reset(*PIC_PINS['DPE_EXT_SH'])
        drv.gpio_pin_reset(*PIC_PINS['NRESET_DPE_ENGINE'])
        drv.gpio_pin_set(*PIC_PINS['NRESET_DPE_ENGINE'])
        drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])

        StrobeNum = 15
        for strobe in range(StrobeNum):
            drv.gpio_pin_set(*PIC_PINS['ADC_FIFO_ADVANCE'])
            drv.gpio_pin_reset(*PIC_PINS['ADC_FIFO_ADVANCE'])

        data = drv.gpio_adc_read()
        print(f'{data:013b}\t {adc2volt(data):.3f} V')

    pads_defaults()
    reset_dpe()
    global adc_calibrated
    adc_calibrated = True


def adc2volt(data):
    V_HI = 4.0
    V_LO = 0.5
    value = data & 0x3ff
    voltage = (V_HI-V_LO) * value / 1023 + V_LO
    return voltage


def download_print_fifo(addr):
    drv.gpio_adc_fifo_en_write(addr)

    data = drv.gpio_adc_read()
    print(f'{data:013b}', end='\t')
    print( f'{adc2volt(data):.3f} V' )

    StrobeNum = 15
    for strobe in range(StrobeNum):
        drv.gpio_pin_set(*PIC_PINS['ADC_FIFO_ADVANCE'])
        drv.gpio_pin_reset(*PIC_PINS['ADC_FIFO_ADVANCE'])
        data = drv.gpio_adc_read()
        print(f'{data:013b}', end='\t')
        #print(strobe)
        print( f'{adc2volt(data):.3f} V' )
    print()


def download_fifo():
    drv.gpio_pin_set(*PIC_PINS['ADC_FIFO_ADVANCE'])
    drv.gpio_pin_reset(*PIC_PINS['ADC_FIFO_ADVANCE'])
    data = drv.gpio_adc_read()
    #data2 = adc2volt(data)
    return data




def calibrate_tia():
    if ~powered_on:
        power_on()
    if ~dpe_reseted:
        reset_dpe()
    if ~tia_scanned:
        scan_tia()
    if ~adc_calibrated:
        calibrate_adc()
    pads_defaults()
   
    load_vectors_rows_to_zero()
    load_vectors_cols_to_zero()
    # LOAD ONE COLUMN ON ONE ARRAY (NOTE: THIS ASSUMES YOU"VE PREVIOUSLY LOADED ALL ZEROS)
    drv.gpio_array_en_write(0b000)# array enable address
    drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
    drv.gpio_row_col_bank_write(0b0001)
    drv.gpio_row_col_data_write(0b1000_0000_0000_0000)
    time.sleep(1e-5)
    drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    time.sleep(1e-5)
    drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
    reset_dpe()

    drv.gpio_pin_set(*PIC_PINS['WRITE_SEL_EXT'])
    rv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])   
    time.sleep(5e-7)        # delay(t_cntl_setup), min = 3TCK
    drv.gpio_nforce_safe_write(0b010) # select nforce safe
    time.sleep(5e-7)        # delay(t_cal_start), min = 2TCK
    drv.gpio_pin_set(*PIC_PINS['COL_WRITE_CONNECT'])
    time.sleep(5e-7)        # delay(t_opamp), min = 500ns
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    time.sleep(5e-7)
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH']) # ASSUMES EXTERNAL CURRENT SOURCE HOOKED UP
    while True:
        if drv.gpio_pin_is_high(*PIC_PINS['ADC_DONE']):
            break

    time.sleep(5e-7)  # delay(t_end_cal), min = 2TCK
    download_print_fifo(0b0000)

    drv.gpio_pin_reset(*PIC_PINS['COL_WRITE_CONNECT'])
    time.sleep(5e-7)  # delay(t_disconnect), min = 2TCK
    drv.gpio_pin_reset(*PIC_PINS['CONNECT_TIA'])
    time.sleep(5e-7)  # delay(t_array_cell), min = 2TCK
    drv.gpio_nforce_safe_write(0b000) # select nforce safe
    pads_defaults()
    reset_dpe()


def load_vectors(array, roc, data):
    # array: a list which contains the arrays you want to enable, i.e. [0, 1]: enable array0 and 1
    # roc: a list which choose colume or row for the corresponding array, 0: row, 1: colume
    # the sizes of 'array' and 'roc' must be the same
    # data:
    if ~powered_on:
        power_on()
    if ~dpe_reseted:
        reset_dpe()
    pads_defaults()
    N = len(array)
    for a in range(0, N-1):
        drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<%d>' % (array[a])])
        if roc[a] == 1:
            drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
        elif roc[a] == 0:
            drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
        else:
            print('error, roc = 0 or 1')
            return
        drv.gpio_row_col_bank_write(0b1000)
        drv.gpio_row_col_data_write(hex(data[N*a]))
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_row_col_bank_write(0b0100)
        drv.gpio_row_col_data_write(hex(data[N*a+1]))
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_row_col_bank_write(0b0010)
        drv.gpio_row_col_data_write(hex(data[N*a+2]))
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_row_col_bank_write(0b0001)
        drv.gpio_row_col_data_write(hex(data[N*a+3]))
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_pin_reset(*PIC_PINS['ARRAY_EN<%d>' % (array[a])])
    pads_defaults()
    reset_dpe()


def cal_mux_sel(mux_sel, mux_addr):
    '''
    Select the path with calibrication muxes
    mux_sel is used to choose between four muxes, value can be 0,1,2,3
    mux_addr is the address within the mux, it is converted to a one-hot 
        vector to chose only one output. 
        But does not have to be in case we will want to select multiple 
        outputs at the same time.
    '''

    # Clear all muxes
    drv.gpio_pin_reset(*PIC_PINS['PICI2C_RESET'])
    drv.gpio_pin_set(*PIC_PINS['PICI2C_RESET'])

    # Send I2C commands
    assert mux_sel >= 0 and mux_sel < 4
    drv.i2c_write_pseudo(mux_sel & 0b0100_1100, 1<<mux_addr)

def load_vectors_rows_to_zero():
    roc = [0 ,0, 0]
    # data= 0b1111111111111111
    data= 0x0000
    array= [0, 1, 2]
    N = 3
    for a in range(0, N-1):
        drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<%d>' %(array[a])])
        if roc[a] == 1:
            drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
        elif roc[a] == 0:
            drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
        else:
            print('error, roc = 0 or 1')
            
        drv.gpio_row_col_bank_write(0b1000)
        drv.gpio_row_col_data_write(data)
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_row_col_bank_write(0b0100)
        drv.gpio_row_col_data_write(data)
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_row_col_bank_write(0b0010)
        drv.gpio_row_col_data_write(data)
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_row_col_bank_write(0b0001)
        drv.gpio_row_col_data_write(data)
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_pin_reset(*PIC_PINS['ARRAY_EN<%d>' %(array[a])])

def load_vectors_cols_to_zero():
    roc = [1 ,1, 1]
    data= 0x0000
    array= [0, 1, 2]
    N = 3
    for a in range(0, N-1):
        drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<%d>' %(array[a])])
        if roc[a] == 1:
            drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
        elif roc[a] == 0:
            drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
        else:
            print('error, roc = 0 or 1')
            
        drv.gpio_row_col_bank_write(0b1000)
        drv.gpio_row_col_data_write(data)
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_row_col_bank_write(0b0100)
        drv.gpio_row_col_data_write(data)
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_row_col_bank_write(0b0010)
        drv.gpio_row_col_data_write(data)
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_row_col_bank_write(0b0001)
        drv.gpio_row_col_data_write(data)
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

        drv.gpio_pin_reset(*PIC_PINS['ARRAY_EN<%d>' %(array[a])])