'''
COPYRIGHT Hewlett Packard Labs

Created by Can Li, can.li@hpe.com

'''


import dut_a0 as a0
import numpy as np
import serial
import time
from IPython import display

dut = a0.dut
drv = dut.drv


def with_ser(func):
    '''
    A decorator handles all the functions require a serial communication
    '''
    def wrapper_with_ser(*args, **kwargs):
        #print(f'Running {func} with serial')
        with serial.Serial(args[0].ser_name, 9600, timeout=1) as ser:
            dut.connect(ser)

            ts = time.time()
            result = func(*args, **kwargs)
            #print(f'[INFO] Elapsed time = {time.time()-ts:.2f}s')

        #print('Serial disconnected')
        return result
    return wrapper_with_ser

class DPE:
    ser_name = None
    N_BIT = 8
    clk_adc = 5
    clk_array = 5

    shape = [64, 64]

    def __init__(self, ser_name='COM6'):
        self.ser_name = ser_name
        self.a0 = a0
        self.init_dut()

    @with_ser
    def init_dut(self):
        '''
        Initialize the DUT
        '''
        dut.reset_chip()
        dut.reset_dpe()
        dut.ground_PIC()
        dut.power_on()

    @with_ser
    def power_off(self):
        '''
        Manually turn off the power
        '''
        dut.power_off()

    @with_ser
    def set_clock(self, Mhz):
        '''
        Set clock frequency

        Args:
            Mhz(int): Frequency to set in MHz
        '''
        drv.clk_stop('ADC_CK')
        drv.clk_stop('CK_ARRAY')
        drv.clk_config('ADC_CK', divisor=100//Mhz)
        drv.clk_config('CK_ARRAY', divisor=100//Mhz)
        drv.clk_start('ADC_CK')
        drv.clk_start('CK_ARRAY')

        self.clk_adc = Mhz
        self.clk_array = Mhz

    @with_ser
    def read(self, array, Vread=0.2, gain=-1, method='slow', numReads=1, **kwargs):
        '''
        Read the array conductance

        Args:
            array(int): The array #
        Returns:
            numpy.ndarray: The conductance map
        '''
        Gmaps = []

        for _ in range(numReads):
            if method == 'slow':
                Gmap = a0.pic_read_batch(array, Vread=Vread, gain=gain, **kwargs) / Vread
            elif method == 'fast':
                input = [0x1 << i for i in range(self.shape[0])]
                Gmap = a0.pic_dpe_batch(array, input, gain=gain, Vread=Vread, **kwargs) / Vread
            elif method == 'single':
                Gmap = self._read_single(array, Vread=Vread, gain=gain, **kwargs) / Vread
            else:
                print('[ERROR] invalid mode..')
                Gmap = 0
                break

            Gmaps.append(Gmap)

        Gmap = np.mean(np.array(Gmaps), axis=0)

        if not np.isscalar(Gmap):
            self.shape = Gmap.shape

        return Gmap

    def _read_single(self, array, Vread=0.2, gain=-1, **kwargs):
        '''
        Read the conductance one-by-one.

        This method is extremely slow, but appears to be more stable for now.

        Args:
            Msel(np.ndarray):   The mask for devices to read.
        Returns:
            numpy.ndarray:      The current map
        '''
        Msel = kwargs['Msel'] if 'Msel' in kwargs.keys() else np.zeros(self.shape)
        Imap = np.zeros(self.shape)

        n_sel = Msel.reshape(-1).sum()
        if n_sel == 0:
            print('Select zero device, skip reading..')
        elif n_sel > 10:
            print(f'[WARINING] read {int(n_sel)} devices with single mode, expect' + \
                  f' very long reading time')

        for r in range(self.shape[0]):
            for c in range(self.shape[1]):
                if Msel[r, c] == 1:
                    Imap[r, c] = a0.pic_read_single(Vread=Vread, array=array, row=r, col=c, gain=gain)

        return Imap

    @with_ser
    def set(self, array, Vset, Vgate, mask=1, Twidth=20e-9, 
            verbose=False, **kwargs):
        '''
        Batch set function

        Args:
            array(int):      The array number, 0|1|2 for superT A0
            Vset(int|np.array)  The set voltage(s). If it is a scalar
                                value, all set voltages are set to the same value.
                                Otherwise it is a set voltage matrix with
                                each element corresponding to one device.
            Vgate(int|np.array) The corresponding gate voltage during the 
                                set programming operation.
            mask(int|np.array)  If it is a scalar, then it will effectively 
                                a scaling factor, with 1 enabling all.
                                If it is an arary, element 1 indicates enable 
                                for the corresponding device while 0 disable.
            Twidth(float)       The programming pulse width in seconds
            Verbose(bool)       Print detailed information for debug purpose.
        '''

        if np.isscalar(Vset):
            Vset = np.ones(self.shape) * Vset
        

        if np.isscalar(Vgate):
            Vgate = np.ones(self.shape) * Vgate
        
        Vset *= mask
        Vgate *= mask

        if verbose:
            print(f'Setting {sum((Vset*Vgate).reshape(-1)!=0)} devices...')

        P_RESET = 0x01 + int(Twidth * self.clk_array*1e6)

        if P_RESET <= 0x01:
            print(f'The pulse width {Twidth*1e9} ns is too small, skip..')
        elif P_RESET <0Xff:
            if verbose:
                print(f'Programming with internal timing P_RESET={P_RESET}')
            a0.pic_write_batch(Vset, Vgate, array, mode=1, P_RESET=P_RESET, 
                               **kwargs)
        else:
            if verbose:
                print(f'Programming with external timing Twidth={Twidth/1e-6:.3f} us')
            a0.pic_write_batch_ext(Vset, Vgate, array, mode=1, Twidth=Twidth/1e-6, 
                                   **kwargs)

    @with_ser
    def reset(self, array, Vreset, Vgate, mask=1, Twidth=20e-9,
              verbose=False, **kwargs):
        '''
        Batch set function

        Args:
            array(int):      The array number, 0|1|2 for superT A0
            Vset(int|np.array)  The reset voltage(s). If it is a scalar
                                value, all set voltages are set to the same value.
                                Otherwise it is a set voltage matrix with
                                each element corresponding to one device.
            Vgate(int|np.array) The corresponding gate voltage during the 
                                set programming operation.
            mask(int|np.array)  If it is a scalar, then it will effectively 
                                a scaling factor, with 1 enabling all.
                                If it is an arary, element 1 indicates enable 
                                for the corresponding device while 0 disable.
            Twidth(float)       The programming pulse width in seconds
            Verbose(bool)       Print detailed information for debug purpose.
        '''

        if np.isscalar(Vreset):
            Vreset = np.ones(self.shape) * Vreset

        if np.isscalar(Vgate):
            Vgate = np.ones(self.shape) * Vgate 

        Vreset *= mask
        Vgate *= mask

        if verbose:
            print(f'Resetting {sum((Vreset*Vgate).reshape(-1)!=0)} devices...')

        P_RESET = 0x01 + int(Twidth * self.clk_array*1e6)

        if P_RESET <= 0x01:
            print(f'The pulse width {Twidth*1e9:.1f} ns is too small, skip..')
        elif P_RESET <0Xff:
            if verbose:
                print(f'Programming with internal timing P_RESET={P_RESET}')
            a0.pic_write_batch(Vreset, Vgate, array, mode=0, P_RESET=P_RESET, 
                               **kwargs)
        else:
            if verbose:
                print(f'Programming with external timing Twidth={Twidth/1e-6:.3f} us')
            a0.pic_write_batch_ext(Vreset, Vgate, array, mode=0, Twidth=Twidth/1e-6, 
                                   **kwargs)

    def tune_conductance(self, array, Gtarget, **kwargs):
        '''
        Tune the conductance with an iterative approach

        Args:
            array(int):                 The array number to program
            Gtarget(np.array):          The target conductance matrix
            Msel(np.array(np.bool)):    Mask for selected devices to program

        '''
        vSetRamp = kwargs['vSetRamp'] if 'vSetRamp' in kwargs.keys() else [1, 3.5, 1]
        vGateSetRamp = kwargs['vGateSetRamp'] if 'vGateSetRamp' in kwargs.keys() else [0.5, 1.4, 0.05]
        vResetRamp = kwargs['vResetRamp'] if 'vResetRamp' in kwargs.keys() else [0.3, 1.5, 0.05]
        vGateResetRamp = kwargs['vGateResetRamp'] if 'vGateResetRamp' in kwargs.keys() else [5.0, 5.5, 0.5]
        numReads = kwargs['numReads'] if 'numReads' in kwargs.keys() else 1
        
        maxSteps = kwargs['maxSteps'] if 'maxSteps' in kwargs.keys() else 200

        GtolType = kwargs['GtolType'] if 'GtolType' in kwargs.keys() else 'abs'
        Gtol = kwargs['Gtol'] if 'Gtol' in kwargs.keys() else 4e-6
        Gtol_in = kwargs['Gtol_in'] if 'Gtol_in' in kwargs.keys() else Gtol
        Gtol_out = kwargs['Gtol_out'] if 'Gtol_out' in kwargs.keys() else Gtol

        Msel = kwargs['Msel'] if 'Msel' in kwargs.keys() else np.ones(self.shape)

        saveHistory = kwargs['saveHistory'] if 'saveHistory' in kwargs.keys() else False
        maxRetry = kwargs['maxRetry'] if 'maxRetry' in kwargs.keys() else 5

        Tdly = kwargs['Tdly'] if 'Tdly' in kwargs.keys() else 500
        method = kwargs['method'] if 'method' in kwargs.keys() else 'slow'

        Twidth = kwargs['Twidth'] if 'Twidth' in kwargs.keys() else 20e-9
        TwidthSet = kwargs['TwidthSet'] if 'TwidthSet' in kwargs.keys() else Twidth
        TwidthReset = kwargs['TwidthReset'] if 'TwidthReset' in kwargs.keys() else Twidth


        #If 'relative' tolerance type is used, compute Gtol matrix
        if GtolType == 'rel':
            RelTolIn = Gtol_in; 
            RelTolOut = Gtol_out; 

            Gtol_out = Gtarget * RelTolOut; 
            Gtol_in = Gtarget * RelTolIn; 

            print(f'Tolerance type set to relative');
            idxMsel = np.array(Msel,dtype=bool); 
            print(f'Gtol_in: MIN {np.min(Gtol_in[idxMsel])} MAX {np.max(Gtol_in[idxMsel])}');
            print(f'Gtol_out: MIN {np.min(Gtol_out[idxMsel])} MAX {np.max(Gtol_out[idxMsel])}');   

            time.sleep(5); 

        def default_callback(data):
            display.clear_output(wait=True)

        plot_callback = kwargs['plot_callback'] if 'plot_callback' in kwargs.keys() else default_callback

        assert array in [0,1,2]

        if saveHistory: 
            hist_data = {
                'Ghist': [],
                'vSetHist': [],
                'vGateSetHist': [],
                'vResetHist': [],
                'vGateResetHist': []
            }

        vSet = np.zeros(self.shape) 
        vGateSet = np.zeros(self.shape)
        vReset = np.zeros(self.shape)
        vGateReset = np.zeros(self.shape)

        Mbound = np.zeros(self.shape)
        Mset = np.ones(self.shape, dtype=np.bool)
        Mreset = np.ones(self.shape, dtype=np.bool)

        # Main programming cycle
        for s in range(maxSteps):
            # Read conductance and take average
            Gread = self.read(array, Tdly=Tdly, method=method, numReads=numReads, 
                              Msel=Msel)  # Msel parameter only applies to single read

            # Determine the devices to be programmed..
            # Mset = ((Gread - Gtarget) < -Gtol) * Msel
            # Mreset = ((Gread - Gtarget) > Gtol) * Msel
            Mset = np.logical_or(Mset, (Gread - Gtarget) < (-Gtol_out))
            Mset = np.logical_and(Mset, (Gread - Gtarget) < (-Gtol_in))
            Mset = Mset * Msel

            Mreset = np.logical_or( Mreset, (Gread - Gtarget) > (Gtol_out) )
            Mreset = np.logical_and( Mreset, (Gread - Gtarget) > (Gtol_in) )
            Mreset = Mreset * Msel

            numLeft = sum(Mreset.reshape(-1)) + sum(Mset.reshape(-1)) - sum((Mbound>=maxRetry).reshape(-1))
            
            if numLeft == 0:
                print('-'*30)
                print('Programming completed.')
                break
            
            # Reset parameters for all devices meet the tolerance requirement
            vSet = vSet * Mset
            vGateSet = vGateSet * Mset
            vReset = vReset * Mreset
            vGateReset = vGateReset * Mreset

        #     Pover
                # Adjust programming parameters
            for i in range(self.shape[0]):
                for j in range(self.shape[1]):

                    if Mset[i,j] == 1:
                        if vSet[i,j] == 0 or vGateSet[i,j] == 0:
                            # Initiate
                            vSet[i,j] = vSetRamp[0]
                            vGateSet[i,j] = vGateSetRamp[0]
                            Mbound[i,j] = 0
                        else:
                            vSet[i,j] += vSetRamp[-1]

                            if vSet[i,j] > vSetRamp[1]:
                                vGateSet[i,j] += vGateSetRamp[-1]

                                if vGateSet[i,j] > vGateSetRamp[1]:
                                    vGateSet[i,j] = vGateSetRamp[1]
                                    vSet[i,j] = vSetRamp[1]
                                    Mbound[i,j] += 1
                                else:
                                    vSet[i,j] = vSetRamp[0]


                    if Mreset[i,j] == 1:
                        if vReset[i,j] == 0 or vGateReset[i,j] == 0:
                            # Initiate
                            vReset[i,j] = vResetRamp[0]
                            vGateReset[i,j] = vGateResetRamp[0]
                            Mbound[i,j] = 0
                        else:
                            vReset[i,j] += vResetRamp[-1]

                            if vReset[i,j] > vResetRamp[1]:
                                vGateReset[i,j] += vGateResetRamp[-1]

                                if vGateReset[i,j] > vGateResetRamp[1]:
                                    vGateReset[i,j] = vGateResetRamp[1]
                                    vReset[i,j] = vResetRamp[1]
                                    Mbound[i,j] += 1
                                else:
                                    vReset[i,j] = vSetRamp[0]

            if saveHistory:
                hist_data['Ghist'].append(Gread)           
                hist_data['vSetHist'].append(vSet)
                hist_data['vGateSetHist'].append(vGateSet * (Mbound<=maxRetry))
                hist_data['vResetHist'].append(vReset)
                hist_data['vGateResetHist'].append(vGateReset * (Mbound<=maxRetry))
            
                plot_callback(hist_data)

            print(f'Start programming, step={s}, maxBound={sum((Mbound>=maxRetry).reshape(-1))} ' +
                f'yield= {sum( ((np.abs(Gread-Gtarget)<Gtol_in) * Msel).reshape(-1)) / sum(Msel.reshape(-1))*100:.2f}% - ' + 
                       f'{sum( ((np.abs(Gread-Gtarget)<Gtol_out) * Msel).reshape(-1)) / sum(Msel.reshape(-1))*100:.2f}%')

            print(f'{numLeft} devices to be programmed...reset {sum(Mreset.reshape(-1))}, set {sum(Mset.reshape(-1))}')
            # Start programming
            self.set(array, vSet, vGateSet * (Mbound<=maxRetry), verbose=True, Twidth=TwidthSet)
            self.reset(array, vReset, vGateReset * (Mbound<=maxRetry), verbose=True, Twidth=TwidthReset)

        # return hist_data
        return vars()
    # def tune_conductance_old(self, array, Gtarget, **kwargs):
    #     '''
    #     Tune the conductance with an iterative approach

    #     Args:
    #         array(int):                 The array number to program
    #         Gtarget(np.array):          The target conductance matrix
    #         Msel(np.array(np.bool)):    Mask for selected devices to program

    #     '''
    #     vSetRamp = kwargs['vSetRamp'] if 'vSetRamp' in kwargs.keys() else [1, 3.5, 1]
    #     vGateSetRamp = kwargs['vGateSetRamp'] if 'vGateSetRamp' in kwargs.keys() else [0.5, 1.4, 0.05]
    #     vResetRamp = kwargs['vResetRamp'] if 'vResetRamp' in kwargs.keys() else [0.3, 1.5, 0.05]
    #     vGateResetRamp = kwargs['vGateResetRamp'] if 'vGateResetRamp' in kwargs.keys() else [5.0, 5.5, 0.5]
    #     numReads = kwargs['numReads'] if 'numReads' in kwargs.keys() else 1
        
    #     maxSteps = kwargs['maxSteps'] if 'maxSteps' in kwargs.keys() else 200
    #     Gtol = kwargs['Gtol'] if 'Gtol' in kwargs.keys() else 4e-6
    #     Gtol_in = kwargs['Gtol_in'] if 'Gtol_in' in kwargs.keys() else Gtol
    #     Gtol_out = kwargs['Gtol_out'] if 'Gtol_out' in kwargs.keys() else Gtol

    #     Msel = kwargs['Msel'] if 'Msel' in kwargs.keys() else np.ones(self.shape)

    #     saveHistory = kwargs['saveHistory'] if 'saveHistory' in kwargs.keys() else False
    #     maxRetry = kwargs['maxRetry'] if 'maxRetry' in kwargs.keys() else 5

    #     Tdly = kwargs['Tdly'] if 'Tdly' in kwargs.keys() else 500
    #     method = kwargs['method'] if 'method' in kwargs.keys() else 'slow'

    #     Twidth = kwargs['Twidth'] if 'Twidth' in kwargs.keys() else 20e-9
    #     TwidthSet = kwargs['TwidthSet'] if 'TwidthSet' in kwargs.keys() else Twidth
    #     TwidthReset = kwargs['TwidthReset'] if 'TwidthReset' in kwargs.keys() else Twidth

    #     def default_callback(data):
    #         display.clear_output(wait=True)

    #     plot_callback = kwargs['plot_callback'] if 'plot_callback' in kwargs.keys() else default_callback

    #     assert array in [0,1,2]

    #     if saveHistory:
    #         hist_data = {
    #             'Ghist': [],
    #             'vSetHist': [],
    #             'vGateSetHist': [],
    #             'vResetHist': [],
    #             'vGateResetHist': []
    #         }

    #     vSet = np.zeros(self.shape) 
    #     vGateSet = np.zeros(self.shape)
    #     vReset = np.zeros(self.shape)
    #     vGateReset = np.zeros(self.shape)

    #     Mbound = np.zeros(self.shape)
    #     Mset = np.ones(self.shape, dtype=np.bool)
    #     Mreset = np.ones(self.shape, dtype=np.bool)

    #     # Main programming cycle
    #     for s in range(maxSteps):
    #         # Read conductance and take average
    #         Gread = self.read(array, Tdly=Tdly, method=method, numReads=numReads)

    #         # Determine the devices to be programmed..
    #         Mset = ((Gread - Gtarget) < -Gtol) * Msel
    #         Mreset = ((Gread - Gtarget) > Gtol) * Msel
    #         #Mset = Mset | ((Gread - Gtarget) < (-Gtol_out))
    #         #Mset = Mset & ((Gread - Gtarget) < (-Gtol_in))
    #         #Mset = Mset * Msel

    #         #Mreset = Mreset | ((Gread - Gtarget) > (Gtol_out))
    #         #Mreset = Mreset & ((Gread - Gtarget) > (Gtol_in))
    #         #Mreset = Mreset * Msel

    #         numLeft = sum(Mreset.reshape(-1)) + sum(Mset.reshape(-1)) - sum((Mbound>=maxRetry).reshape(-1))
            
    #         if numLeft == 0:
    #             print('-'*30)
    #             print('Programming completed.')
    #             break
            
    #         # Reset parameters for all devices meet the tolerance requirement
    #         vSet = vSet * Mset
    #         vGateSet = vGateSet * Mset
    #         vReset = vReset * Mreset
    #         vGateReset = vGateReset * Mreset

    #     #     Pover
    #             # Adjust programming parameters
    #         for i in range(self.shape[0]):
    #             for j in range(self.shape[1]):

    #                 if Mset[i,j] == 1:
    #                     if vSet[i,j] == 0 or vGateSet[i,j] == 0:
    #                         # Initiate
    #                         vSet[i,j] = vSetRamp[0]
    #                         vGateSet[i,j] = vGateSetRamp[0]
    #                         Mbound[i,j] = 0
    #                     else:
    #                         vSet[i,j] += vSetRamp[-1]

    #                         if vSet[i,j] > vSetRamp[1]:
    #                             vGateSet[i,j] += vGateSetRamp[-1]

    #                             if vGateSet[i,j] > vGateSetRamp[1]:
    #                                 vGateSet[i,j] = vGateSetRamp[1]
    #                                 vSet[i,j] = vSetRamp[1]
    #                                 Mbound[i,j] += 1
    #                             else:
    #                                 vSet[i,j] = vSetRamp[0]


    #                 if Mreset[i,j] == 1:
    #                     if vReset[i,j] == 0 or vGateReset[i,j] == 0:
    #                         # Initiate
    #                         vReset[i,j] = vResetRamp[0]
    #                         vGateReset[i,j] = vGateResetRamp[0]
    #                         Mbound[i,j] = 0
    #                     else:
    #                         vReset[i,j] += vResetRamp[-1]

    #                         if vReset[i,j] > vResetRamp[1]:
    #                             vGateReset[i,j] += vGateResetRamp[-1]

    #                             if vGateReset[i,j] > vGateResetRamp[1]:
    #                                 vGateReset[i,j] = vGateResetRamp[1]
    #                                 vReset[i,j] = vResetRamp[1]
    #                                 Mbound[i,j] += 1
    #                             else:
    #                                 vReset[i,j] = vSetRamp[0]

    #         if saveHistory:
    #             hist_data['Ghist'].append(Gread)           
    #             hist_data['vSetHist'].append(vSet)
    #             hist_data['vGateSetHist'].append(vGateSet * (Mbound<=maxRetry))
    #             hist_data['vResetHist'].append(vReset)
    #             hist_data['vGateResetHist'].append(vGateReset * (Mbound<=maxRetry))
            
    #             plot_callback(hist_data)

    #         print(f'Start programming, step={s}, maxBound={sum((Mbound>=maxRetry).reshape(-1))} ' +
    #             f'yield= {sum( ((np.abs(Gread-Gtarget)<Gtol_in) * Msel).reshape(-1)) / sum(Msel.reshape(-1))*100:.2f}% - ' + 
    #                    f'{sum( ((np.abs(Gread-Gtarget)<Gtol_out) * Msel).reshape(-1)) / sum(Msel.reshape(-1))*100:.2f}%')

    #         print(f'{numLeft} devices to be programmed...reset {sum(Mreset.reshape(-1))}, set {sum(Mset.reshape(-1))}')
    #         # Start programming
    #         self.set(array, vSet, vGateSet * (Mbound<=maxRetry), verbose=True, Twidth=TwidthSet)
    #         self.reset(array, vReset, vGateReset * (Mbound<=maxRetry), verbose=True, Twidth=TwidthReset)

    #     # return hist_data
    #     return vars()

    #                             if vGateReset[i,j] > vGateResetRamp[1]:
    #                                 vGateReset[i,j] = vGateResetRamp[1]
    #                                 vReset[i,j] = vResetRamp[1]
    #                                 Mbound[i,j] += 1
    #                             else:
    #                                 vReset[i,j] = vSetRamp[0]

    #         if saveHistory:
    #             hist_data['Ghist'].append(Gread)           
    #             hist_data['vSetHist'].append(vSet)
    #             hist_data['vGateSetHist'].append(vGateSet * (Mbound<=maxRetry))
    #             hist_data['vResetHist'].append(vReset)
    #             hist_data['vGateResetHist'].append(vGateReset * (Mbound<=maxRetry))
            
    #             plot_callback(hist_data)

    #         print(f'Start programming, step={s}, maxBound={sum((Mbound>=maxRetry).reshape(-1))} ' +
    #             f'yield= {sum( ((np.abs(Gread-Gtarget)<Gtol) * Msel).reshape(-1)) / sum(Msel.reshape(-1))*100:.2f}%')
            
            
    #         currYield = sum( ((np.abs(Gread-Gtarget)<Gtol) * Msel).reshape(-1)) / sum(Msel.reshape(-1))*100
    #         if (currYield>=TargetYield):
    #             print(f'Reached target yield')
    #             break
        
    #         # Start programming
    #         self.set(array, vSet, vGateSet * (Mbound<=maxRetry), verbose=True, Twidth=TwidthSet)
    #         self.reset(array, vReset, vGateReset * (Mbound<=maxRetry), verbose=True, Twidth=TwidthReset)

    #     return hist_data
        
    def binarize_shift(self, vectors):
        '''
        Binarize the vectors with shift and add approach

        Args:
            vectors(numpy.ndarray): The normalized vector
        '''
        vec_int = np.round(vectors * (2**self.N_BIT - 1))
        vec_int = np.array(vec_int, dtype=np.uint32)

        vec_list = []
        for i in range(self.N_BIT):
            vec_list.append((vec_int >> i) & 0x1)

        return np.array(vec_list)

    def binarize_unary(self, vectors):
        '''
        Binarize the vectors with one unary pulse per bit 

        Args:
            vectors(numpy.ndarray): The normalized vector
        '''
        vec_int = np.round(vectors * (self.N_BIT))
        vec_int = np.array(vec_int, dtype=np.uint32)

        vec_list = []
        for i in range(self.N_BIT):
            vec_list.append(vec_int > (i+0.5))

        return np.array(vec_list)

    def vec2ints(self, vector, start=0):
        '''
        Convert a binarized vector to 64-bit integer for DPE input

        Args:
            vector(numpy.ndarray)
            start(int): a offset to indicate the position of the array
        '''
        int_num = 0

        for i, element in enumerate(vector):
            assert i < 64

            if element == 1:
                int_num |= 0x1 << (i + start)

        return int_num

    def get_col_en(self, c_sel=[0, 14]):
        col_en = [0, 0, 0, 0]

        for i in range(c_sel[0], c_sel[1]):
            col_en[3-(i//16)] |= 0x1 << (i % 16)

        return col_en

    def shift_n_add(self, vectors):
        '''
        Shift and add
        '''

        result = np.zeros(vectors[0].shape)
        for i in range(self.N_BIT):
            result += vectors[i] * (0x1 << i)

        return result / (2**self.N_BIT - 1)

    def unary_sum(self, vectors):
        '''
        Sum
        '''
        result = np.sum(vectors, axis=0) / self.N_BIT
        return result

    @with_ser
    def multiply(self, array, vectors, r_start=0, c_sel=[0, 14],
                 mode=0, gain=-1, **kwargs):
        '''
        The core of the DPE operation

        Args:
            array(int): The array number
            vectors(numpy.ndarray): The vectors to be multiplied
                                    ONLY POSTIVE NUMBERS ARE SUPPORTED
                                    NORMALIZE FIRST
            mode(int):  0 -> shift and add
                        1 -> unary pulses
            Tdly(int):  The delay time between vectors in microseconds
                        Default value is 1000, which is 1 ms
        Returns:
            numpy.ndarray: The multiply result
        '''

        Vread = kwargs['Vread'] if 'Vread' in kwargs.keys() else 0.2

        if mode == 0:
            # shift and add
            func_binarize = self.binarize_shift
            func_recover = self.shift_n_add
        elif mode == 1:
            # unary
            func_binarize = self.binarize_unary
            func_recover = self.unary_sum

        vectors_bin = func_binarize(vectors)

        outputs_dpe_all = []

        for vec in vectors_bin:
            inputs_dpe = []
            for v in vec.T:
                inputs_dpe.append(self.vec2ints(v, start=r_start))

            outputs_dpe = a0.pic_dpe_batch(array, inputs_dpe, gain=gain, mode=1,
                                           col_en=self.get_col_en(c_sel), **kwargs)

            outputs_dpe = outputs_dpe[:, c_sel[0]:c_sel[1]]
            outputs_dpe_all.append(outputs_dpe)

        return func_recover(outputs_dpe_all) / Vread

    @with_ser
    def multiply_w_delay(self, array, vectors, r_start=0, c_sel=[0, 14],\
                         mode=0, delay=5, debug=False, **kwargs):
        '''
        The core of DPE operation

        Args:
            array(int): The array number
            vectors(numpy.ndarray): The vectors to be multiplied
            delay(int): The delay between two ADC read in milliseconds
        Returns:
            numpy.ndarray: The multiply result
        '''

        Vread = kwargs['Vread'] if 'Vread' in kwargs.keys() else 0.2
        gain = kwargs['gain'] if 'gain' in kwargs.keys() else -1

        if mode == 0:
            # shift and add
            func_binarize = self.binarize_shift
            func_recover = self.shift_n_add
        elif mode == 1:
            # unary
            func_binarize = self.binarize_unary
            func_recover = self.unary_sum

        vectors_bin = func_binarize(vectors)

        outputs_dpe_all = []

        a0.pic_read_config(**kwargs)
        a0.pic_dpe_cols(array, col_en = self.get_col_en(c_sel))

        for vec in vectors_bin:
            inputs_dpe = []
            for v in vec.T:
                inputs_dpe.append(self.vec2ints(v))

            outputs_dpe = []
            for i, input_single in enumerate(inputs_dpe):
                if debug:
                    if i % 50 == 0:
                        print(f'[DEBUG] processing vector {i}')

                output_single = a0.pic_dpe_batch(array, [input_single], gain=gain, mode=1,
                                                 skip_conf=True)
                outputs_dpe.append(output_single)
                time.sleep(delay / 1000)

            outputs_dpe = np.concatenate(outputs_dpe, axis=0)

            outputs_dpe = outputs_dpe[:, c_sel[0]:c_sel[1]]
            outputs_dpe_all.append(outputs_dpe)

        return func_recover(outputs_dpe_all) / Vread


    def lin_corr(self, outputs, factors):
        result = np.zeros(outputs.shape)
        for c in range(outputs.shape[1]):
            result[:,c] = outputs[:,c] * factors[c][0] + factors[c][1]
            
        return result
