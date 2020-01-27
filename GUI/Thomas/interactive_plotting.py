"""
Test to see whether we can update plots live while running mem-HNN experiment. Written for python 3.7.3

Author: Thomas Van Vaerenbergh
"""

import pylab as plt
import pickle
import numpy as np
from time import sleep

fn = "./20191113-222550-Prober2_HNN_15cyc_100trials_Neg3_0Pos1_4.pkl"

data = None
with open(fn, "rb") as pkl_file:
    data = pickle.load(pkl_file)
    
"""CMat – the Hopfield weight matrix encoding the graph problem
neuronVectorHistory – this is the main variable you care about. It has dimensions (#neurons, #numTrials, #updates = numCycles*60+1)
So for 15cycles, 100 trials, it has dimensions: (60, 100, 901)
A “trial” is just a Hopfield network run with a different starting state. You will probably only want to look at one specific trial run.
columnUpdateHistory – this variable tells you what was the order of column updates.  This was randomized, so it was not a strictly sequential update. 
numCycles 
numTrials
startSchmidVal
endSchmidtVal – these variables tell you what was the starting and ending Schmidt width.  These were linearly ramped from startSchmidVal to endSchmidtVal across the cycles
SchmidtCycleVector – this is the actual Schmidt width used at each corresponding cycle number
"""

# convert these variables to names with name conventions closer to PEP-8
C_mat = data["CMat"]
num_neurons = C_mat.shape[0]
neuron_vector_history = data["neuronVectorHistory"]
column_update_history = data["columnUpdateHistory"]
num_cycles = data["numCycles"]
num_updates = num_cycles*num_neurons+1
num_trials = data["numTrials"]
start_schmidt_val = data["startSchmidtVal"]
end_schmidt_val = data["endSchmidtVal"]
schmidt_cycle_vector = data["SchmidtCycleVector"]
trial_index = 0

node_angles = np.linspace(0, 2, num_neurons+1)[:-1]*np.pi
node_pos = (np.cos(node_angles),np.sin(node_angles))

# https://stackoverflow.com/questions/4098131/how-to-update-a-plot-in-matplotlib

time_vector = np.arange(0, num_updates)

# neuron_vector_history_trial = neuron_vector_history[:,trial_index,:].reshape(num_neurons,-1)

# You probably won't need this if you're embedding things in a tkinter plot...
plt.ion()
plt.rcParams['lines.linewidth'] = 2.0 #instead of 1.5
color_map = 'jet'#'cool' #try also 'prism', check here: https://matplotlib.org/examples/color/colormaps_reference.html

fig = plt.figure(0, figsize= [plt.rcParams["figure.figsize"][0]*2., plt.rcParams["figure.figsize"][1]])
ax = fig.add_subplot(121)
color_idx_array = np.linspace(0,1.0,num_trials)
ax.set_xlabel("Time", fontsize=15)
ax.set_ylabel("Energy", fontsize=15)
ax.set_xlim([time_vector[0], time_vector[-1]])
ax.set_ylim([-500, 300.])

# fig_g = plt.figure(1)
# ax_g = fig_g.add_subplot(111)
ax_g = fig.add_subplot(122)
# line1_g=ax_g.plot(*node_pos,marker="o",linestyle="",zorder=2)
scatter_g = ax_g.scatter(*node_pos, zorder=2)
scatter_g.set_clim([-1., 1.])
ax_g.set_aspect('equal')
ax_g.axis('off')
color_list = plt.rcParams['axes.prop_cycle'].by_key()['color']
convert_to_color = lambda x: color_list[0] if (x == 1) else color_list[1]
# ax_g.get_xaxis().set_visible(False)
# ax_g.get_yaxis().set_visible(False)
for nn in range(num_neurons):
    for mm in range(num_neurons):
        if C_mat[nn,mm]!=0:
            ax_g.plot([node_pos[0][nn], node_pos[0][mm]],
                      [node_pos[1][nn], node_pos[1][mm]], "-", color="0.9", zorder=1,
                      linewidth=0.5)

vec = np.zeros(num_neurons)
old_vec = np.zeros(num_neurons)

verbose = False
plot_refresh_rate = 5  # controls how fast lines are moving

for trial_index in range(num_trials): # range as we use python3, otherwise use xrange for python2
    energy_vector = np.NaN * np.zeros(time_vector.shape[0])  # NaNs such that it's not plotted
    # line1_g = ax_g.scatter(*node_pos, zorder=2, c=neuron_vector_history[:,trial_index,0])
    line1, = ax.plot(time_vector, energy_vector, '-',
                     color=plt.get_cmap(color_map)(color_idx_array[trial_index]))  # Returns a tuple of line objects --> line1,

    vec[:] = neuron_vector_history[:,trial_index,0]
    old_vec[:] = vec[:]
    energy_value = np.dot(vec, np.dot(C_mat, vec))  # need to do this once

    for tt, time in enumerate(time_vector):
        if verbose: print("Time index: ", tt)
        vec[:] = neuron_vector_history[:, trial_index, tt]
        # line1_g = ax_g.scatter(*node_pos, zorder=2, c=vec)
        if(tt%plot_refresh_rate == 0):
            scatter_g.set_color(list(map(convert_to_color, vec)))  # not very efficient, but I don't know a better way
        # energy_vector[tt] = np.dot(vec,np.dot(C_mat, vec))  # might be faster ways
        idx_update = np.where(vec != old_vec)[0]  # instead we could just cycle through indices-> this is more general.
        if len(idx_update) != 0:
            energy_value += 2*(vec[idx_update[0]]-old_vec[idx_update[0]])*np.dot(C_mat[idx_update[0], :], old_vec)
        old_vec[:] = vec[:]
        energy_vector[tt] = energy_value
        if (tt % plot_refresh_rate == 0):
            line1.set_ydata(energy_vector)  # wonder whether we can update one point at a time
            fig.canvas.draw()
            fig.canvas.flush_events()
            # fig_g.canvas.draw()
            # fig_g.canvas.flush_events()
            # sleep(0.2)

    line1.set_linewidth(line1.get_linewidth() / 2.0)
    line1.set_alpha(0.5)

print("Done")