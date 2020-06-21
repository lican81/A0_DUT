import numpy as np
from simArrayPy import simArrayPy as pydpe


class dpeTCAM:
    def __init__(self, array_tcam,
                 g_on=100e-6, g_off=1e-6, g_std=0.02, rw=1):

        self._rw = rw

        self.dpe = self._init_2r_dpe(array_tcam,
                                     g_on, g_off, g_std, rw=rw)

    def _init_2r_dpe(self, array_tcam,
                     g_on=100e-6, g_off=1e-6, g_std=0.02, rw=1):

        def gen_g_sta(g, g_std): return np.random.randn() * g_std * g + g

        Gm = []
        for r in array_tcam:
            Gm_row = []
            for bit in r:
                if bit == 0:
                    Gm_row.extend([gen_g_sta(g_off, g_std),
                                   gen_g_sta(g_on,  g_std)])
                elif bit == 1:
                    Gm_row.extend(
                        [gen_g_sta(g_on, g_std), gen_g_sta(g_off,  g_std)])
                else:
                    Gm_row.extend([gen_g_sta(g_off, g_std),
                                   gen_g_sta(g_off,  g_std)])
            Gm.append(Gm_row)

        return pydpe(np.array(Gm).T, rw)

    def _gen_input_2r(self, input_tcam, v_read=0.2):
        dict_sl = np.multiply([[1, 0], [0, 1], [0, 0]], v_read)
        Vm = []
        for r in input_tcam:
            Vm_row = []
            for bit in r:
                Vm_row.extend(dict_sl[int(bit)])
            Vm.append(Vm_row)
        return np.array(Vm).T

    def compare(self, input_tcam):
        v_in = self._gen_input_2r(input_tcam)
        i_out = self.dpe.read_current(v_in)

        return i_out.T


# Groud truth for comparison
def get_tcam_output(inp, array):
    res_t = []
    for inp_one in inp:
        t = []
        for tcam_row in array:
            is_match = True
            for b_in, b_tcam in zip(inp_one, tcam_row):
                if (b_in == 0 and b_tcam == 1) or (b_in == 1 and b_tcam == 0):
                    is_match = False
                    break
            t.append(is_match)
        res_t.append(t)
    return res_t


if __name__ == "__main__":

    # Generate a sample tcam array
    n_cam_size = 20
    n_input = 64
    # np.random.seed(1)
    array_tcam = np.random.rand(n_cam_size, n_cam_size) * 3
    array_tcam = np.floor(array_tcam)

    input_tcam = np.random.rand(n_input, n_cam_size) * 3
    input_tcam = np.floor(input_tcam)

    input_tcam[0] = array_tcam[0]

    # Get the ground truth
    res_t = get_tcam_output(input_tcam, array_tcam)

    # Get dpe-TCAM output
    tcam = dpeTCAM(array_tcam)
    res_dpe = tcam.compare(input_tcam)

    # Compare the result
    import matplotlib.pyplot as plt
    plt.subplot(121)
    plt.imshow(res_dpe < 10e-6)
    plt.subplot(122)
    plt.imshow(res_t)
    plt.show()
