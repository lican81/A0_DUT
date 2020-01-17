import matplotlib.pyplot as plt
import numpy as np

def plot_history(x, y, data):

    histdata = data['hist_data']
    Gtarget = data['Gtarget']
    Gtol_in = data['Gtol_in']
    Gtol_out = data['Gtol_out']

    vSetHist = np.array(histdata['vSetHist'])
    vGateSetHist = np.array(histdata['vGateSetHist'])

    Ghist = np.array(histdata['Ghist'])
    vResetHist = np.array(histdata['vResetHist'])
    vGateResetHist = np.array(histdata['vGateResetHist'])

    plt.figure(figsize=(10,5))
    plt.subplot(311)
    plt.plot(Ghist[:, x, y]*1e6, '.-')

    plt.plot([0, len(Ghist[:, x, y])-1], [(Gtarget[x,y]-Gtol_out)*1e6, (Gtarget[x,y]-Gtol_out)*1e6], '--', color='green', linewidth=0.5)
    plt.plot([0, len(Ghist[:, x, y])-1], [(Gtarget[x,y]+Gtol_out)*1e6, (Gtarget[x,y]+Gtol_out)*1e6], '--', color='green', linewidth=0.5)

    plt.plot([0, len(Ghist[:, x, y])-1], [(Gtarget[x,y]-Gtol_in)*1e6, (Gtarget[x,y]-Gtol_in)*1e6], '--', color='red', linewidth=0.5)
    plt.plot([0, len(Ghist[:, x, y])-1], [(Gtarget[x,y]+Gtol_in)*1e6, (Gtarget[x,y]+Gtol_in)*1e6], '--', color='red', linewidth=0.5)
    plt.ylabel('Conductance ($\mu$S)')

    plt.subplot(312)
    plt.plot(vSetHist[:, x, y], '.-')
    plt.plot(vGateSetHist[:, x, y], '.-')
    plt.ylabel('Set voltages')

    plt.subplot(313)
    plt.plot(vResetHist[:, x, y], '.-')
    plt.plot(vGateResetHist[:, x, y], '.-')
    plt.ylabel('Reset voltages')

def plot_g_history(x, y, histdata, Gtarget, Gtol=5e-6):
    Ghist = np.array(histdata['Ghist'])

    if Ghist[-1, x, y] < Gtarget[x,y]+Gtol and Ghist[-1, x, y] > Gtarget[x,y]-Gtol:
        plt.plot(Ghist[:, x, y]*1e6, '.-', color='g')
    else:
        plt.plot(Ghist[:, x, y]*1e6, '.-', color='r')

    Ghist = np.array(histdata['Ghist'])

    plt.plot([0, len(Ghist[:, x, y])-1], [(Gtarget[x,y]-Gtol)*1e6, (Gtarget[x,y]-Gtol)*1e6], '--')
    plt.plot([0, len(Ghist[:, x, y])-1], [(Gtarget[x,y]+Gtol)*1e6, (Gtarget[x,y]+Gtol)*1e6], '--')
    plt.ylabel('Conductance ($\mu$S)')

def plot_iv(dpe, x, y, array=0, Vread=0.2, nPt=30):
    pass
