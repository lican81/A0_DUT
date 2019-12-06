import numpy as np


# gen_dpe_2r(array):
def gen_tcam_2r(array_tcam, g_on=100e-6, g_off=1e-6, g_std=0):
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

    return np.array(Gm).T


V_read = 0.2


def gen_input_2r(input_tcam, V_read):
    dict_sl = np.multiply([[1, 0], [0, 1], [0, 0]], V_read)
    Vm = []
    for r in input_tcam:
        Vm_row = []
        for bit in r:
            Vm_row.extend(dict_sl[int(bit)])
        Vm.append(Vm_row)
    return np.array(Vm).T
