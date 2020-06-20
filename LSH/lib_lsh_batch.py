import numpy as np


def hamming(vec, matrix):
    
    vec = np.expand_dims(vec, 0)
    vec_matrix = np.tile(vec, [np.shape(matrix)[0], 1])
    
    res = np.logical_xor(vec_matrix, matrix)
    hamming = np.sum(res, axis=1)
    
    return hamming

def get_lsh(vec, hash_planes, normalize=True):
    if normalize:
        vec = vec / np.linalg.norm(vec)
        
    k_hash = vec @ hash_planes.T
    return (k_hash > 0).astype(int)


def vec_pn(vec):
     # Make sure the vector is normalized
#     vec = vec / np.linalg.norm(vec)

    vec_pos = vec.copy()
    vec_pos[vec_pos<0] = 0


    vec_neg = vec.copy()
    vec_neg[vec_neg>0] = 0

    # scaling = max( vec_pos.max(), -vec_neg.min())

    # vec_neg = -vec_neg/scaling
    # vec_pos =  vec_pos/scaling
    vec_neg = -vec_neg

    return vec_pos, vec_neg

def post_curr_pn(Ipos, Ineg):
    Ires = (Ipos - Ineg)
    h = (Ires[:, ::2] > Ires[:, 1::2]).astype(int)

    return h

def get_lsh_g(vec, g):
    vec = np.array(vec)

    vec_neg, vec_pos = vec_pn(vec)

    Ipos = vec_pos @ g
    Ineg = vec_neg @ g

    return post_curr_pn(Ipos, Ineg)

def get_lsh_dpe(vec, dpe):
    '''Get lsh code from a normalized vector'''
    vec = np.array(vec)

    vec_pos, vec_neg = vec_pn(vec)

    if (abs(vec).max() > 1):
        print('Normalize vector first!')
        print(f'max vec value={vec_pos.max(), vec_neg.max(), abs(vec).max()}')
        return -1

    Ipos = dpe.multiply(
            0, 
            vec_pos.T, 
            c_sel=[0, 64], 
            r_start=0, mode=0, Tdly=500)

    Ineg = dpe.multiply(
            0, 
            vec_neg.T, 
            c_sel=[0, 64], 
            r_start=0, mode=0, Tdly=500)
    
    return post_curr_pn(Ipos, Ineg)


def get_lsh_dpe_cor(vec, dpe, lin_cor):
    '''Get lsh code from a normalized vector'''
    vec = np.array(vec)

    vec_pos, vec_neg = vec_pn(vec)

    if (abs(vec).max() > 1):
        print('Normalize vector first!')
        print(f'max vec value={vec_pos.max(), vec_neg.max(), abs(vec).max()}')
        return -1

    Ipos = dpe.multiply(
            0, 
            vec_pos.T, 
            c_sel=[0, 64], 
            r_start=0, mode=0, Tdly=500)

    Ineg = dpe.multiply(
            0, 
            vec_neg.T, 
            c_sel=[0, 64], 
            r_start=0, mode=0, Tdly=500)

    Ires = Ipos - Ineg
    Ires = dpe.lin_corr(Ires, lin_cor)
    h = (Ires[:, ::2] > Ires[:, 1::2]).astype(int)
    
    return h