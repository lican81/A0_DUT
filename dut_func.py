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
    print('Setting vrefs to default')
                                    #   Norminal    Prober1   Prober2   TP
    dac_set('DAC_VREF_ARRAY', 0.497)#   0.5         0.503               17
    dac_set('P_VREF_TIA', 0.497)    #   0.5         0.503               21
    dac_set('P_VREF_SH', 2.505)     #   2.5         2.495               29
    dac_set('PLANE_VPP', 0.3)       #   0.3         0.304               09
    dac_set('DAC_VP_PAD', 2.507)    #   2.5         2.493               31
    dac_set('P_TVDD', 1)            #   1.0         1.000               33
    dac_set('P_VAGC_0', 1)          #   1.0         1.001               36
    dac_set('P_VAGC_1', 3.9)        #   3.9         3.90_               25
    dac_set('DAC_VREF_HI_CMP', 4)   #   4.0         4.00_               22
    dac_set('P_ADC_EXT_TEST_IN', 1) #   1.0         1.001               32
    # dac_set('P_ADC_EXT_TEST_IN', 0)
    dac_set('P_AMP_VREF', 2.5)      #   2.5         2.500               30
    dac_set('P_AMP_INPUT', 2.5)     #   2.5         2.494               28

    # DAC Schottky, Drive_VN -0.078


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


def scan_control(scan_ctrl_bits=bytes([0x10, 0x02, 0x0c, 0x10,
                                       0x20, 0x01, 0x02])):
    '''
    scan_ctrl_bits: 56 bits, or 7 bytes
        Delay will be (scan value +  2) times CK_ARRAY clock period
        [pulse count start, pulse count reset, SH count start, SH countreset (disabled), 
        AGC frequency counter, write pulse start count, write pulse end count]
    '''
    pads_defaults()
    #    P_SERIAL_BUS_IN data latched in # Refer to Figure 2 for timing diagram and to Table 3 for recommended initial values to use during power on
    # data = bytes([0b000_10000, 0b0000_0010 , 0b0000_1100,0b0001_0000, 0b0010_0000, 0b00000001, 0b00000010])
    drv.spi_serial_write(2, scan_ctrl_bits)


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
    '''
    Reset all scanned in values, TIA enables, and row/column vector registers
    '''
    drv.gpio_pin_reset(*PIC_PINS['NRESET_FULL_CHIP'])
    time.sleep(1e-6)  # want to delay 1us
    drv.gpio_pin_set(*PIC_PINS['NRESET_FULL_CHIP'])


def reset_dpe():
    '''
    Reset control counters, ADC flip flops, FIFO, and control shadow registers
    '''
    drv.gpio_pin_reset(*PIC_PINS['NRESET_DPE_ENGINE'])
    time.sleep(1e-6)  # want to delay 1us
    drv.gpio_pin_set(*PIC_PINS['NRESET_DPE_ENGINE'])
    global dpe_reseted
    dpe_reseted = True


def dac_init(span=0b011):
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
    '''

    '''

    # print(f'DAC: setting ch={channel} to vol={voltage}')
    voltage = voltage - 0.078

    if dac_set.is_init == False:
        dac_init(span=0b011)

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

def dac_volt2raw(voltage):
    if dac_set.is_init == False:
        dac_init(span=0b011)

    vlim_lo, vlim_hi = DAC_SPAN[dac_set.span]

    data = (voltage - vlim_lo) / (vlim_hi-vlim_lo) * 0xffff

    if np.isscalar(voltage):
        data = int(data)
    else:
        data = data.astype(np.uint16)

    return data
    


def py_logic_analyzer():
    val = drv.gpio_pin_is_high(*PIC_PINS['PWR_GOOD'])
    print(int(val), "\tPWR_GOOD")
    val = drv.gpio_pin_is_high(*PIC_PINS['NRESET_FULL_CHIP'])
    print(int(val), "\tNRESET_FULL_CHIP")
    val = drv.gpio_pin_is_high(*PIC_PINS['NRESET_DPE_ENGINE'])
    print(int(val), "\tNRESET_DPE_ENGINE")
    val = drv.gpio_pin_is_high(*PIC_PINS['ARRAY_EN<0>'])
    print(int(val), "\tARRAY_EN<0>")
    val = drv.gpio_pin_is_high(*PIC_PINS['ARRAY_EN<1>'])
    print(int(val), "\tARRAY_EN<1>")
    val = drv.gpio_pin_is_high(*PIC_PINS['ARRAY_EN<2>'])
    print(int(val), "\tARRAY_EN<2>")
    val = drv.gpio_pin_is_high(*PIC_PINS['NFORCE_SAFE0'])
    print(int(val), "\tNFORCE_SAFE0")
    val = drv.gpio_pin_is_high(*PIC_PINS['NFORCE_SAFE1'])
    print(int(val), "\tNFORCE_SAFE1")
    val = drv.gpio_pin_is_high(*PIC_PINS['NFORCE_SAFE2'])
    print(int(val), "\tNFORCE_SAFE2")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_SEL_EXTERNAL'])
    print(int(val), "\tADC_SEL_EXT")
    val = drv.gpio_pin_is_high(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    print(int(val), "\tDPE_EXT_OVERRIDE_EN")
    val = drv.gpio_pin_is_high(*PIC_PINS['DPE_EXT_SH'])
    print(int(val), "\tDPE_EXT_SH")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_DONE'])
    print(int(val), "\tADC_DONE")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_FIFO_ADVANCE'])
    print(int(val), "\tADC_FIFO_ADVANCE")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_FIFO_EN<0>'])
    print(int(val), "\tADC_FIFO_EN<0>")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_FIFO_EN<1>'])
    print(int(val), "\tADC_FIFO_EN<1>")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_FIFO_EN<2>'])
    print(int(val), "\tADC_FIFO_EN<2>")
    val = drv.gpio_pin_is_high(*PIC_PINS['ADC_FIFO_EN<3>'])
    print(int(val), "\tADC_FIFO_EN<3>")


def scan_tia(data=BitArray('0b1100000100'*96).bytes):
    '''
    960 bit long scan chain for all TIA settings.
    Each tia requries 10 bits configuration, and there are 96 (=32*3) tias for half array

    e.g. data = BitArray('0b1100000100'*96).bytes
    
    bits:
    9       8       7       6       5           4   3    2   1   0 
    --------------------------------------------------------------
    SH      TIA     400f    150f    millercap   1M  200k 30k 5k  1k

    '''
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


def calibrate_adc(voltages, addr_fifo):
    '''
    Use the board DAC output to calibrate the on-chip ADC.
    Input: voltages  An arrange with voltages to be calibrated
           addr_fifo Choose 1 of 12 ADCs
    Output: The raw ADC outputs
    '''
    # Assumes power good, and power_on() procedure completed with control block scan chain loaded
    # example inputs: voltages = np.arange(0.5, 4.5, 0.5) and addr_fifo=0b000
    reset_dpe()

    # Scan in TIA settings: TIA SCAN IN OP AMPS ENABLED, No COMPENSATION, 30k gain
    # Scan chain numbers 1 and 0 must always be enabled during TIA configuration (opamp enable)
    # Last 5 bits represent TIA gain: 10000 - 1M; 00001 - 1k
    # data = BitArray('0b1100000100'*96).bytes
    # scan_tia(data)

    # Select all the arrays
    drv.gpio_array_en_write(0b111)
    drv.gpio_nforce_safe_write(0b111)

    # voltage = 1.5 as an example, I wonder whether we should put it as a parameter of the function
    # dac_set('P_ADC_EXT_TEST_IN', voltages[0])
    # time.sleep(1e-6)        # delay(t_sel_ext or t_ext_inp), min = 2CK
    drv.gpio_pin_set(*PIC_PINS['ADC_SEL_EXTERNAL'])
    # time.sleep(1e-6)       # delay(t_en_overide_sh), min = 0CK
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    time.sleep(1e-6)        # delay(t_fire_sh), min = 3CK
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    # time.sleep(1e-6)        # delay(3 P_ADC_CK periods)
    # drv.gpio_pin_reset(*PIC_PINS['DPE_EXT_SH'])

    # drv.gpio_adc_fifo_en_write(addr_fifo)  # Select which FIFO to download from

    # data = drv.gpio_adc_read()
    # print(f'{data:013b}\t {adc2volt(data):.3f} V')

    adc_output = []

    for V_adc in voltages:
        dac_set('P_ADC_EXT_TEST_IN', V_adc)

        time.sleep(1e-6)
        drv.gpio_pin_reset(*PIC_PINS['DPE_EXT_SH'])
        reset_dpe()
        drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])

        while drv.gpio_pin_is_high(*PIC_PINS['ADC_DONE']) == False:
            pass

        # The result is in the last FIFO, dump the first 15 results
        data_fifo = download_fifo(addr_fifo)
        data = data_fifo[-1]

        adc_output.append(data)

    pads_defaults()
    reset_dpe()
    global adc_calibrated
    adc_calibrated = True

    return adc_output


def adc2volt(data):
    V_HI = 4.0
    V_LO = 0.5
    value = data & 0x3ff
    voltage = (V_HI-V_LO) * value / 1023 + V_LO
    return voltage


# def download_print_fifo(addr):
#     drv.gpio_adc_fifo_en_write(addr)

#     data = drv.gpio_adc_read()
#     print(f'{data:013b}', end='\t')
#     print(f'{adc2volt(data):.3f} V')

#     StrobeNum = 15
#     for strobe in range(StrobeNum):
#         drv.gpio_pin_set(*PIC_PINS['ADC_FIFO_ADVANCE'])
#         drv.gpio_pin_reset(*PIC_PINS['ADC_FIFO_ADVANCE'])
#         data = drv.gpio_adc_read()
#         print(f'{data:013b}', end='\t')
#         # print(strobe)
#         print(f'{adc2volt(data):.3f} V')
#     print()


def download_fifo( addr ):
    '''
    Download the fifo data

    Args:
        addr (int): The fifo address to be downloaded.

    Returns:
        list: The fifo data
    '''
    FIFO_DEPTH = 16

    data = []

    drv.gpio_adc_fifo_en_write(addr)

    # First fifo data does not require advance
    data.append( drv.gpio_adc_read() )

    for _ in range(FIFO_DEPTH-1):
        drv.gpio_pin_set(*PIC_PINS['ADC_FIFO_ADVANCE'])
        # May need a pulse in C code
        drv.gpio_pin_reset(*PIC_PINS['ADC_FIFO_ADVANCE'])
        data.append( drv.gpio_adc_read() )
    return data


def calibrate_tia():
    if not powered_on:
        power_on()
    if not dpe_reseted:
        reset_dpe()
    if not tia_scanned:
        scan_tia()
    # if not adc_calibrated:
    #     calibrate_adc()
    # pads_defaults()

    load_vectors_rows_to_zero()
    load_vectors_cols_to_zero()
    # LOAD ONE COLUMN ON ONE ARRAY (NOTE: THIS ASSUMES YOU"VE PREVIOUSLY LOADED ALL ZEROS)
    drv.gpio_array_en_write(0b000)  # array enable address
    drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
    drv.gpio_row_col_bank_write(0b0001)
    drv.gpio_row_col_data_write(0b1000_0000_0000_0000)
    time.sleep(1e-5)
    drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    time.sleep(1e-5)
    drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
    reset_dpe()

    drv.gpio_pin_set(*PIC_PINS['WRITE_SEL_EXT'])
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_OVERRIDE_EN'])
    time.sleep(5e-7)        # delay(t_cntl_setup), min = 3TCK
    drv.gpio_nforce_safe_write(0b010)  # select nforce safe
    time.sleep(5e-7)        # delay(t_cal_start), min = 2TCK
    drv.gpio_pin_set(*PIC_PINS['COL_WRITE_CONNECT'])
    time.sleep(5e-7)        # delay(t_opamp), min = 500ns
    drv.gpio_pin_set(*PIC_PINS['CONNECT_TIA'])
    time.sleep(5e-7)
    # ASSUMES EXTERNAL CURRENT SOURCE HOOKED UP
    drv.gpio_pin_set(*PIC_PINS['DPE_EXT_SH'])
    while True:
        if drv.gpio_pin_is_high(*PIC_PINS['ADC_DONE']):
            break

    time.sleep(5e-7)  # delay(t_end_cal), min = 2TCK
    download_print_fifo(0b0000)

    drv.gpio_pin_reset(*PIC_PINS['COL_WRITE_CONNECT'])
    time.sleep(5e-7)  # delay(t_disconnect), min = 2TCK
    drv.gpio_pin_reset(*PIC_PINS['CONNECT_TIA'])
    time.sleep(5e-7)  # delay(t_array_cell), min = 2TCK
    drv.gpio_nforce_safe_write(0b000)  # select nforce safe
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
    drv.i2c_write_pseudo(mux_sel & 0b0100_1100, 1 << mux_addr)


def load_vectors_rows_to_zero():
    # New code----------
    drv.gpio_array_en_write(0b111)
    drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])

    drv.gpio_row_col_bank_write(0b1111)
    drv.gpio_row_col_data_write(0x0000)
    # time.sleep(1e-7)
    drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    # time.sleep(1e-7)
    drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
    # New code----------

    # roc = [0, 0, 0]
    # # data= 0b1111111111111111
    # data = 0x0000
    # array = [0, 1, 2]

    # N = 3
    # for a in range(0, N):
    #     drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<%d>' % (array[a])])
    #     if roc[a] == 1:
    #         drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
    #     elif roc[a] == 0:
    #         drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
    #     else:
    #         print('error, roc = 0 or 1')

    #     drv.gpio_row_col_bank_write(0b1000)
    #     drv.gpio_row_col_data_write(data)
    #     time.sleep(1e-7)
    #     drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    #     time.sleep(1e-7)
    #     drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

    #     drv.gpio_row_col_bank_write(0b0100)
    #     drv.gpio_row_col_data_write(data)
    #     time.sleep(1e-7)
    #     drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    #     time.sleep(1e-7)
    #     drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

    #     drv.gpio_row_col_bank_write(0b0010)
    #     drv.gpio_row_col_data_write(data)
    #     time.sleep(1e-7)
    #     drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    #     time.sleep(1e-7)
    #     drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

    #     drv.gpio_row_col_bank_write(0b0001)
    #     drv.gpio_row_col_data_write(data)
    #     time.sleep(1e-7)
    #     drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    #     time.sleep(1e-7)
    #     drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

    #     drv.gpio_pin_reset(*PIC_PINS['ARRAY_EN<%d>' % (array[a])])


def load_vectors_cols_to_zero():
    # New code----------
    drv.gpio_array_en_write(0b111)
    drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])

    drv.gpio_row_col_bank_write(0b1111)
    drv.gpio_row_col_data_write(0x0000)
    # time.sleep(1e-7)
    drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    # time.sleep(1e-7)
    drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
    # New code----------


    # roc = [1, 1, 1]
    # data = 0x0000
    # array = [0, 1, 2]
    # N = 3
    # for a in range(0, N):
    #     drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<%d>' % (array[a])])
    #     if roc[a] == 1:
    #         drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
    #     elif roc[a] == 0:
    #         drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
    #     else:
    #         print('error, roc = 0 or 1')

    #     drv.gpio_row_col_bank_write(0b1000)
    #     drv.gpio_row_col_data_write(data)
    #     time.sleep(1e-7)
    #     drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    #     time.sleep(1e-7)
    #     drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

    #     drv.gpio_row_col_bank_write(0b0100)
    #     drv.gpio_row_col_data_write(data)
    #     time.sleep(1e-7)
    #     drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    #     time.sleep(1e-7)
    #     drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

    #     drv.gpio_row_col_bank_write(0b0010)
    #     drv.gpio_row_col_data_write(data)
    #     time.sleep(1e-7)
    #     drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    #     time.sleep(1e-7)
    #     drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

    #     drv.gpio_row_col_bank_write(0b0001)
    #     drv.gpio_row_col_data_write(data)
    #     time.sleep(1e-7)
    #     drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
    #     time.sleep(1e-7)
    #     drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])

    #     drv.gpio_pin_reset(*PIC_PINS['ARRAY_EN<%d>' % (array[a])])

def load_vectors(array, data):
    '''
    array (int or list): which array(s) you want to load the vector to.
    example: array = 2, or array = [0, 1]
    data: a list which contains at 8 elements, each element is an hex int in the range of [0x0000, 0xffff],\n
        every four elements form a 64-bit vector from left to right, corresponds to bank[0] to bank[3]\n
    '''
    if not powered_on:
        power_on()
    if not dpe_reseted:
        reset_dpe()
    pads_defaults()
    drv.gpio_array_en_write(0)
    if isinstance(array, list):
        for a in array:
            drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<%d>' %(a)])
    else:
        drv.gpio_pin_set(*PIC_PINS['ARRAY_EN<%d>' %(array)])
    drv.gpio_pin_reset(*PIC_PINS['COL_ROW_SEL'])
    addr = 1
    for b in range(0, 4):
        # Rows
        drv.gpio_row_col_bank_write(addr)
        if data == 0:
            drv.gpio_row_col_data_write(0)
        elif data == 1:
            drv.gpio_row_col_data_write(0xffff)
        else:
            drv.gpio_row_col_data_write(data[b])
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
        addr = addr << 1
    drv.gpio_pin_set(*PIC_PINS['COL_ROW_SEL'])
    addr = 1
    for b in range(4, 8):
        # Columns
        drv.gpio_row_col_bank_write(addr)
        if data == 0:
            drv.gpio_row_col_data_write(0)
        elif data == 1:
            drv.gpio_row_col_data_write(0xffff)
        else:
            drv.gpio_row_col_data_write(data[b])
        time.sleep(1e-7)
        drv.gpio_pin_set(*PIC_PINS['LATCH_CLK_DATA'])
        time.sleep(1e-7)
        drv.gpio_pin_reset(*PIC_PINS['LATCH_CLK_DATA'])
        addr = addr << 1
    pads_defaults()
    reset_dpe()

def which_fifo(index):
    '''
    Return: fifo # and channel # in the form [fifo#, channel#] \n
    Input: [array#, col#]
    '''
    if index[1] < 32:
        if index[1]%2 == 0:
            fifo_en = (2-index[0])*2
        else:
            fifo_en = (2-index[0])*2+6
    else:
        if index[1]%2 == 0:
            fifo_en = (2-index[0])*2+1
        else:
            fifo_en = (2-index[0])*2+7
    
    if index[1] < 32:
        channel = (index[1]//16)*8 + (7-index[1]%16//2)
    else:
        channel = (3-index[1]//16)*8 + index[1]%16//2
    return [fifo_en, channel]

def data_generate_sparse(index):
    '''
    index: a list, which contains the row and colume you want to write. Every two elements represent one device.\n
        i.e. [0, 2]: row0 and col2, [0, 2, 3, 6]: row0 and col2, row3 and col6
    '''
    data = [0, 0, 0, 0, 0, 0, 0, 0]
    M = len(index)//2
    for b in range(0, M):
        # row data
        row_dic = {0: 2, 1: 0, 2: 1, 3: 3}
        bank_row = row_dic[index[2*b]//16]
        if index[2*b]%2 == 1 and  index[2*b] < 32:
            bit = index[2*b]%16//2
            if (data[bank_row] >> (bit + 8))&1 == 0:
                data[bank_row] = data[bank_row] + (1 << (bit + 8))
        elif index[2*b]%2 == 0 and  index[2*b] < 32:
            bit = index[2*b]%16//2
            if (data[bank_row] >> bit)&1 == 0:
                data[bank_row] = data[bank_row] + (1 << bit)
        elif index[2*b]%2 == 1 and  index[2*b] >= 32:
            bit = index[2*b]%16//2
            if (data[bank_row] >> (15-bit))&1 == 0:
                data[bank_row] = data[bank_row] + (1 << (15 - bit))
        elif index[2*b]%2 == 0 and  index[2*b] >= 32:
            bit = index[2*b]%16//2
            if (data[bank_row] >> (7-bit))&1 == 0:
                data[bank_row] = data[bank_row] + (1 << (7 - bit))
        # colume data
        bank_col = 2*(index[2*b+1]//32) + (index[2*b+1]%2)
        if index[2*b+1] < 32:
            bit = 15 - (index[2*b+1]//2)
            if (data[bank_col+4] >> bit)&1 == 0:
                data[bank_col+4] = data[bank_col+4] + (1 << bit)
        elif index[2*b+1] >= 32:
            bit = (index[2*b+1]-32)//2
            if (data[bank_col+4] >> bit)&1 == 0:
                data[bank_col+4] = data[bank_col+4] + (1 << bit)
    return data
   
def data_generate_vector(row_vector, col_vector):
    '''
    row_vector and col_vector in the form of [0x****, 0x****, 0x****, 0x****],\n
    left to right: higher bit to lower bit
    '''
    data = [0, 0, 0, 0, 0, 0, 0, 0]
    # row vector
    row_dic = {0: 2, 1: 0, 2: 1, 3: 3}
    for a in range(0, 2):
        for b in range(0, 8):
            bank_row = row_dic[a]
            if (row_vector[3-a] >> 2*b)&1 == 1:
                data[bank_row] = data[bank_row] + (1 << b)
            if (row_vector[3-a] >> 2*b+1)&1 == 1:
                data[bank_row] = data[bank_row] + (1 << b+8)
    for a in range(2, 4):
        for b in range(0, 8):
            bank_row = row_dic[a]
            if (row_vector[3-a] >> 2*b)&1 == 1:
                data[bank_row] = data[bank_row] + (1 << 7-b)
            if (row_vector[3-a] >> 2*b+1)&1 == 1:
                data[bank_row] = data[bank_row] + (1 << 15-b)
    # col vector
    for a in range(0, 2):
        for b in range(0, 8):
            if (col_vector[3-a] >> 2*b)&1 == 1:
                data[4]= data[4] + (1 << 15-b-8*a)
            if (col_vector[3-a] >> 2*b+1)&1 == 1:
                data[5]= data[5] + (1 << 15-b-8*a)
    for a in range(2, 4):
        for b in range(0, 8):
            if (col_vector[3-a] >> 2*b)&1 == 1:
                data[6]= data[6] + (1 << b+8*(a-2))
            if (col_vector[3-a] >> 2*b+1)&1 == 1:
                data[7]= data[7] + (1 << b+8*(a-2))
    return data


# def write_forward_external(array, index, voltage, write_all=False, add_cap=False):
#     # supposed to be a SET operation
#     if not powered_on:
#         power_on()
#     if ~control_scanned:
#         scan_control()
#     if ~tia_scanned:
#         scan_tia()
#     if ~adc_calibrated():
#         calibrate_adc()
#     if ~tia_calibrated:
#         calibrate_tia()
#     if ~write_all:
#         data = data_generate_sparse(index)
#         load_vectors(array, data)
#     else:
#         print('Please make sure you have loaded desired vectors before excuting write process')
#     pads_defaults()
#     drv.gpio_pin_set(*PIC_PINS['WRT_INTERNAL_EN'])
#     if add_cap:
#         drv.gpio_pin_set(*PIC_PINS['WRITE_ADD_CAP'])
#     else:
#         drv.gpio_pin_reset(*PIC_PINS['WRITE_ADD_CAP'])
#     reset_dpe()
#     time.sleep(2e-7)        # delay(del2)
#     dac_set('DAC_VP_PAD', 0)
#     time.sleep(2e-7)        # delay(del2)
#     drv.gpio_pin_set(*PIC_PINS['WRITE_FWD'])
#     time.sleep(2e-7)        # delay(del2)
#     if array == 0 or array == 1 or array == 2:
#         drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE%d' %(array)])
#     elif array == 3:
#         drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE0'])
#         drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE1'])
#         drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE2'])
#     elif isinstance(array, list):
#         for a in array:
#             drv.gpio_pin_set(*PIC_PINS['NFORCE_SAFE%d' %(a)])
#     time.sleep(2e-7)        # delay(del2)
#     drv.gpio_pin_set(*PIC_PINS['ROW_WRITE_CONNECT'])
#     time.sleep(2e-7)        # delay(del2)
#     drv.gpio_pin_set(*PIC_PINS['CONNECT_COLUMN_T'])
#     time.sleep(2e-7)        # delay(del2)
#     dac_set('DAC_VP_PAD', voltage)
#     time.sleep(1e-3)        # delay(as necessary to write)
#     dac_set('DAC_VP_PAD', 0)
#     time.sleep(2e-6)        # delay(write pulse width + del1), how to determin 'write pulse widt'?
#     drv.gpio_pin_reset(*PIC_PINS['CONNECT_COLUMN_T'])
#     time.sleep(2e-7)        # delay(del2)
#     drv.gpio_pin_reset(*PIC_PINS['ROW_WRITE_CONNECT'])
#     time.sleep(2e-7)        # delay(del2)
#     drv.gpio_pin_reset(*PIC_PINS['NFORCE_SAFE0'])
#     drv.gpio_pin_reset(*PIC_PINS['NFORCE_SAFE1'])
#     drv.gpio_pin_reset(*PIC_PINS['NFORCE_SAFE2'])
#     pads_defaults()
#     reset_dpe()