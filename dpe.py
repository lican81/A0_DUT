import dut_a0 as a0
import numpy as np
import serial
import time

dut = a0.dut
drv = dut.drv


class DPE:
    ser_name = None
    N_BIT = 8

    def __init__(self, ser_name='COM6'):
        self.ser_name = ser_name
        self.init_dut()

    def with_ser(func):
        '''
        A decorator handles all the functions require a serial communication
        '''
        def wrapper_with_ser(*args, **kwargs):
            print('Connecting to serial')
            with serial.Serial(args[0].ser_name, 9600, timeout=1) as ser:
                dut.connect(ser)

                ts = time.time()
                result = func(*args, **kwargs)
                print(f'[INFO] Elapsed time = {time.time()-ts:.2f}s')

            print('Serial disconnected')
            return result
        return wrapper_with_ser

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

    @with_ser
    def read(self, array, Vread=0.2):
        '''
        Read the array conductance

        Args:
            array(int): The array #
        Returns:
            numpy.ndarray: The conductance map
        '''
        Gmap = a0.pic_read_batch(array, Vread=Vread, gain=-1) / Vread
        return Gmap

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

        result = np.zeros( vectors[0].shape )
        for i in range(self.N_BIT):
            result += vectors[i] * (0x1<<i)

        return result / (2**self.N_BIT -1)


    @with_ser
    def multiply(self, array, vectors, r_start=0, c_sel=[0, 14]):
        '''
        The core of DPE operation

        Args:
            array(int): The array number
            vectors(numpy.ndarray): The vectors to be multiplied
        Returns:
            numpy.ndarray: The multiply result
        '''

        vectors_bin = self.binarize_shift(vectors)

        outputs_dpe_all = []

        for vec in vectors_bin:
            inputs_dpe = []
            for v in vec.T:
                inputs_dpe.append(self.vec2ints(v))

            outputs_dpe = a0.pic_dpe_batch(array, inputs_dpe, gain=-1, mode=1,
                                            col_en=self.get_col_en(c_sel) )

            outputs_dpe = outputs_dpe[:,c_sel[0]:c_sel[1] ]
            outputs_dpe_all.append(outputs_dpe)

        return self.shift_n_add( outputs_dpe_all )