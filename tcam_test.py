
#%%
table = [
    [0, 0, 0, 1, 1, 0, 0, 0, 0, 1],
    [0, 1, 0, 1, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 1, 1, 0, 0, 0, 1, 0],
    [1, 2, 0, 1, 1, 0, 0, 0, 1, 1]
]

ns = [
    [0, 1],
    [1, 0],
    [1, 0],
    [1, 1]
]

#%%

from lib_tcam import *

G = gen_tcam_2r(table)

# %%
import matplotlib.pyplot as plt
plt.imshow(G.T)
plt.colorbar()



#%%
inputstring = 'janslgi?sid=ABCDEF0987654321F9C4D4ABB6200000ksdelnf'.lower()

print(inputstring)

cs = [0, 0]
for c in inputstring:
    charlist = [int(d) for d in f'{ord(c):08b}']
    input = cs + charlist

    inp = gen_input_2r([input], 0.2)

    res = G.T@inp
    # print(c, input)
    # print(G.T@inp)

    matches = np.where( res.T[0]<3e-6 )[0]
    
    # print(cs)
    if len(matches) >0:
        accept = True
        # print((matches))
        cs = ns[matches[0]]
    else:
        accept = False
        cs = [0, 0]

    # ns, accept = regex_proc(input)
    # cs = ns

    if accept:
        print('^', end='')
    else:
        print(' ', end='')
# %%
len(np.where( res.T[0]<10e-5 )[0])

# %%
inp.shape

# %%
a = np.array([1, 3, 4])

np.where(a<4)

# %%
