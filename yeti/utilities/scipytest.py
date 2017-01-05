__author__ = 'chris'
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy.ndimage as spimg
import numpy as np

sensitivity = (100/255.0) ** 2 * 100
threshold = (250/255.0) * 100
alpha = (5/255.0) ** 3 #learning rate

print sensitivity, threshold, alpha

fig = plt.figure()
frame = np.array(spimg.imread("/home/chris/sequence2/image07.jpg"),dtype=np.float64)
background = np.array(frame, dtype=np.float64)
variance = np.full(frame.shape, threshold, dtype=np.float64)
previous_foreground = 0.

output = plt.imshow(frame, cmap = plt.get_cmap('gray'), vmin = 0, vmax = 255)

def update(i):
    global background, variance, previous_foreground

    frame = np.array(spimg.imread("/home/chris/sequence2/image%02d.jpg" % i),dtype=np.float64)

    delta = background - frame

    #pixel classification
    foreground = (delta ** 2/variance).sum(axis=2)
    foreground[foreground < sensitivity] = 0
    foreground[foreground >= sensitivity] = 255

    #Model update
    background += delta * alpha
    variance += (delta ** 2 - variance) * alpha
    np.clip(variance,threshold,255,out=variance)

    # set the data in the axesimage object
    output.set_array(foreground)
    # return the artists set

    foreground_pixels = np.count_nonzero(foreground)
    if foreground_pixels > 0:
        magnitude = abs(previous_foreground/foreground_pixels) * 100
    else:
        magnitude = 0

    previous_foreground = foreground_pixels

    #print('Foreground Changed Pixels: %s' % foreground_pixels)
    print('Magnitude of Change: %s', magnitude)

    return output,

# kick off the animation
ani = animation.FuncAnimation(fig, update, frames=range(7,599), interval=100)

plt.show()