#%%
# %reload_ext autoreload
# %autoreload 2

import dut_func as dut
import serial
import time
import struct
import numpy as np
# from bitarray import bitarray
from bitstring import BitArray
import matplotlib.pyplot as plt
# %config InlineBackend.figure_formats = ['svg']


from dpe import DPE
from lib_data import *
import matplotlib.pyplot as plt
import numpy as np
from lib_nn_dpe import NN_dpe
from IPython import display

import serial
import matplotlib

dpe = DPE('COM6')
dpe.set_clock(50)


load_workspace(vars(), 'demo')

#%%
from PIL import ImageTk, Image, ImageDraw
import PIL
from tkinter import *
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from PIL import Image 

nn = NN_dpe(weights)

#%%
width = 200
height = 200
center = height//2
white = (255, 255, 255)
green = (0,128,0)

def classify():
    filename = "image.png"
    image1.save(filename)
    img = Image.open(filename)
    #userImage = np.array( img, dtype='uint8' )
    smallImg = Image.open(filename).resize((24,24), Image.ANTIALIAS)
    #userImage = np.array(Image.open(filename).convert('L'))
    userImage = np.array(smallImg.convert('L'))
    mxPixel = np.max(userImage)
    mnPixel = np.min(userImage)
    userImage = 1-((userImage-mnPixel)/(mxPixel-mnPixel))
    newImage = np.zeros((24,24,1))
    newImage[:,:,0] = userImage
    
    #NOW PERFORM THE MNIST CLASSIFICATION
    vectors = nn._conv_flattern(newImage)
    
    # Convolution hardware call
    output = dpe.multiply(1, vectors, c_sel=[0, 14], mode=0) / (nn.Gratio/2)
    output_cor = dpe.lin_corr(output, lin_cor_conv)
    x = output_cor[:,::2] - output_cor[:,1::2]
    x = x.reshape(20,20,-1)
    convFilters = x    
    x1 = nn.relu(x)
    x1 = nn.max_pooling(x1)
    x1 = nn.flattern(x1)        
    ## Start Hardware Fully Connect
    # print(np.shape(x1))    
    x = x1    
    x1 = x[:57].T
    x2 = x[57:].T
    sc1 = x1.max()
    sc2 = x2.max()
    Gfc1 = nn.Gfc[:57]
    Gfc2 = nn.Gfc[57:]
    x1 = x1 / sc1
    x2 = x2 / sc2
    
    x1 = x1[x1 >= 0]
    x2 = x2[x2 >= 0]    
    newX1 = x1.reshape(-1,1)
    newX2 = x2.reshape(-1,1)
    #break
    output1  = dpe.multiply(0, newX1, c_sel=[0, 20], mode=0, Tdly=0)
    output1 = dpe.lin_corr(output1, new_lin_cor_fc1) * sc1

    output2  = dpe.multiply(0, newX2, c_sel=[20, 40], mode=0, Tdly=0)
    output2 = dpe.lin_corr(output2, new_lin_cor_fc2) * sc2
    outputs = output1 + output2    
    y = outputs[:,::2] - outputs[:,1::2]    
    ## End Hardware Fully Connect

    #display.clear_output(wait=True)
    classificationResult = y.argmax()
    #END CLASSIFICATION
  
    cv.create_text(5, 190, anchor=W, font="Purisa",
            text="You drew: "+str(classificationResult))
   
    # Plot
    fig = plt.figure()
    for ii in range(7):
        plt.subplot('33' + str(ii+1))
        plt.title('Channel #' + str(ii))
        plt.imshow(convFilters[:,:,ii])
    plt.tight_layout()
    display.display(fig)

    fig2 = plt.figure()
    plt.bar(np.arange(10), y[0] * 1e6)
    plt.grid(True, alpha=.3)
    plt.title(f'Recognized {y.argmax()}')
    plt.xticks(np.arange(10))
    plt.xlabel('Digits')
    plt.ylabel('Analog Engine Output') 
    display.display(fig2)
    
    
def clearAll():
    draw.rectangle([0, 0, width, height], fill='white')
    cv.delete("all")
    
def paint(event):
    # python_green = "#476042"
    x1, y1 = (event.x - 1), (event.y - 1)
    x2, y2 = (event.x + 1), (event.y + 1)
    cv.create_oval(x1, y1, x2, y2, fill="black",width=7)
    draw.line([x1, y1, x2, y2],fill="black",width=7)

#%%
root = Tk()

# Tkinter create a canvas to draw on
cv = Canvas(root, width=width, height=height, bg='white')
cv.pack()

image1 = PIL.Image.new("RGB", (width, height), white)
draw = ImageDraw.Draw(image1)

cv.pack(expand=YES, fill=BOTH)
cv.bind("<B1-Motion>", paint)

button=Button(text="Classify with Analog Engine",command=classify)
button.pack()
button2=Button(text="Clear",command=clearAll)
button2.pack()
root.mainloop()
#%%
