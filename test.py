import numpy as np

threshold = 1
sample = 50
vectors = (5,20)
magnitude = 5
a = np.ndarray(shape=((vectors[1]/vectors[0]) - 1, sample))
a.fill(np.nan)

print a.shape

motion = False
for i in range(0, 75):
    index = 0
    for j in range(vectors[0],vectors[1],magnitude):
        average = np.average(a[index])
        #if average + (average * threshold) > vectors:
        #    motion = True

        a[index, 0] = i
        a[index] = np.roll(a[index], -1)

        index += 1

print a


