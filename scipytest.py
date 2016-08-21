__author__ = 'chris'
import matplotlib.pyplot as plt
import scipy.ndimage as spimg
import numpy as np

sensitivity = (66/255.0) ** 2 * 100
threshold = (162/255.0) * 100
alpha = (18/255.0) ** 3 #learning rate

print sensitivity, threshold, alpha

background = None
variance = None

for i in range(4,100):

    frame = spimg.imread("/home/chris/sequence/image%02d.jpg" % i)

    if background is None:
        background = np.array(frame, dtype=np.float64)
        variance = np.full(frame.shape, threshold, dtype=np.float64)
        continue

    delta = background - frame

    #pixel classification
    foreground = (delta ** 2/variance).sum(axis=2)
    foreground[foreground < sensitivity] = 0
    foreground[foreground >= sensitivity] = 255

    #Model update
    background += delta * alpha
    variance += ((background - frame) ** 2 - variance) * alpha
    np.clip(variance,0,threshold,out=variance)

    plt.imshow(foreground, cmap='Greys_r')
    print('Foreground Changed Pixels: %s' % np.count_nonzero(foreground))
    plt.show()
