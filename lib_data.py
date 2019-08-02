import scipy.io as sio
import dill
import datetime
import numpy as np

'''
This file provides functions to save and load data
'''


def save(variable, filename='', note=''):
    if filename == '':
        currentDT = datetime.datetime.now()
        filename = currentDT.strftime("%Y%m%d-%H%M%S") + f'-{note}'

    with open(filename+'.pkl', 'wb') as f:
        dill.dump(variable, f)

    try:
        sio.savemat(filename+'.mat', variable)
    except Exception as e:
        print('something is wrong saving variables to mat')
        print(e)

    print('variable saved to ' + filename + '.pkl/.mat')


def load(filename=''):
    with open(filename+'.pkl', 'rb') as f:
        return dill.load(f)

def save_workspace( vars_all, filename='', note=''):
    if filename == '':
        currentDT = datetime.datetime.now()
        filename = currentDT.strftime("%Y%m%d-%H%M%S") + f'-{note}'
      
    types_to_dill = (dict, list, np.ndarray, int, float, str, np.float64)
    types_to_mat = (list, np.ndarray, int, float, str, np.float64)

    d = {}
    print('Saving ', end='')
    for k in vars_all.keys():
        if k.startswith('_'):
            continue
        if isinstance( (vars_all[k]), types_to_dill):  
            d[k] = vars_all[k]
            print(f'{k}({type(vars_all[k])}), ', end='')
    print(f'to {filename}.pkl')

    with open(filename+'.pkl', 'wb') as f:
        dill.dump(d, f)

    print('Saving ', end='')
    d = {}
    for k in vars_all.keys():
        if k.startswith('_'):
            continue
        if isinstance( (vars_all[k]), types_to_mat):  
            d[k] = vars_all[k]
            print(f'{k}({type(vars_all[k])}), ', end='')
    print(f'to {filename}.mat')

    try:
        sio.savemat(filename+'.mat', d)
    except Exception as e:
        print('something is wrong saving workspace to mat')
        print(e)


def load_workspace( vars_all, filename=''):
    with open(filename+'.pkl', 'rb') as f:
        variables = dill.load(f)

    loaded_vars = ''
    for k in variables.keys():
        loaded_vars += k + ', '
        vars_all[k] = variables[k]

    print('Loaded: ' + loaded_vars)