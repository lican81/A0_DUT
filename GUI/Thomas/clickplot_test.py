import clickplot
import numpy as np
import pylab as plt

xData = np.linspace(0, 4 * np.pi, 100)
yData1 = np.cos(xData)
yData2 = np.sin(xData)
fig = plt.figure()
subPlot1 = fig.add_subplot('211')
plt.plot(xData, yData1, figure=fig)
subPlot2 = fig.add_subplot('212')
plt.plot(xData, yData2, figure=fig)

# Show the clickplot and print the return values
retval = clickplot.showClickPlot()
print('Comment = %s' % retval['comment'])
if retval['subPlot'] == None:
    print('No subplot selected')
else:
    print('You clicked in subplot %(subPlot)d at (%(x).3f, %(y).3f)' % retval)