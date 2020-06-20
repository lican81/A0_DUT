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
    vec = np.reshape(vec, -1)
#     vec = vec / np.linalg.norm(vec)

    vec_pos = vec.copy()
    vec_pos[vec_pos<0] = 0


    vec_neg = vec.copy()
    vec_neg[vec_neg>0] = 0

    scaling = max( vec_pos.max(), -vec_neg.min())

    vec_neg = -vec_neg/scaling
    vec_pos =  vec_pos/scaling

    return vec_neg, vec_pos

def post_curr_pn(Ipos, Ineg):
    Ires = (Ipos - Ineg).reshape(-1)
    h = (Ires[::2] > Ires[1::2]).astype(int)
    return h

def get_lsh_g(vec, g):
    vec_neg, vec_pos = vec_pn(vec)

    Ipos = vec_pos @ g
    Ineg = vec_neg @ g

    return post_curr_pn(Ipos, Ineg)

def get_lsh_dpe(vec, dpe):
    '''Get lsh code from a normalized vector'''
    vec_neg, vec_pos = vec_pn(vec)

    Ipos = dpe.multiply(
            0, 
            np.expand_dims(vec_pos, 1), 
            c_sel=[0, 64], 
            r_start=0, mode=0, Tdly=500).T

    Ineg = dpe.multiply(
            0, 
            np.expand_dims(vec_neg, 1), 
            c_sel=[0, 64], 
            r_start=0, mode=0, Tdly=500).T
    
    return post_curr_pn(Ipos, Ineg)


def get_lsh_dpe_cor(vec, dpe, lin_cor):
    '''Get lsh code from a normalized vector'''
    vec_neg, vec_pos = vec_pn(vec)

    Ipos = dpe.multiply(
            0, 
            np.expand_dims(vec_pos, 1), 
            c_sel=[0, 64], 
            r_start=0, mode=0, Tdly=500)

    Ipos = dpe.lin_corr(Ipos, lin_cor).T

    Ineg = dpe.multiply(
            0, 
            np.expand_dims(vec_neg, 1), 
            c_sel=[0, 64], 
            r_start=0, mode=0, Tdly=500)

    Ineg = dpe.lin_corr(Ineg, lin_cor).T
    
    return post_curr_pn(Ipos, Ineg)