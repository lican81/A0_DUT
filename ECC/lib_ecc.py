import numpy as np


def weight2conductance(Mweight):
    '''
    Convert normalized weight to conductances

    Try to map them to low conductance as possible
    '''
    Glow  = 0.0
    Ghigh = 100e-6 # corresponding to 1s 
                    # Could be higher than this value for weight values
                    # larger than 1
    
    Gpos = np.ones_like(Mweight) * Glow
    Gpos[Mweight>0] +=  Mweight[Mweight>0] * Ghigh
    
    Gneg = np.ones_like(Mweight) * Glow
    Gneg[Mweight<0] += -Mweight[Mweight<0] * Ghigh
    
    G = np.zeros((Mweight.shape[0], Mweight.shape[1]*2))
    G[:, ::2] = Gpos
    G[:, 1::2] = Gneg
    
    return G


def correct_ecc(y1, ecc, verbose=False):
    # ECC
    # S = (y1 @ G_parity_ecc / nn.Gratio)
    # S = S[:, ::2] - S[:, 1::2]

    n_detected = 0
    n_corrected = 0
    n_error = 0

    for yy in y1:
        ecc_loc, ecc_range = ecc.decode(yy)
        
        if ecc_loc != -1:
            if ecc_loc == -2:
                # Detected but could not be corrected
                n_detected += 1
            elif ecc_loc >=0:
                # Correct
                yy[ecc_loc] -= (ecc_range[0]+ecc_range[1])/2
                n_corrected += 1
            else:
                n_error += 1

    if verbose:
        return y1, (n_detected, n_corrected, n_error)
    else:
        return y1

def dense(x, nn, finalGfc):
    x = x.reshape(20, 20, -1)

    x1 = nn.relu(x)
    x1 = nn.max_pooling(x1)
    x1 = nn.flattern(x1)
    x1 = np.append(x1, 1)

    y = x1.T @ finalGfc

    y = y.reshape(-1)
    y = y[::2] - y[1::2]

    return y.argmax()