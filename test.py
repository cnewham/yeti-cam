import numpy as np
sample = 3

a = np.random.randint(10,size=(5,4,3))
b = np.random.randint(10,size=(5,4,3))
c = np.random.randint(10,size=(5,4,3))

print "---RAW---"

print a.shape
print a
print b
print c

print "---MEAN---"

total = []
total.append(a.mean(axis=2))
total.append(b.mean(axis=2))
total.append(c.mean(axis=2))

total = np.array(total)

print total.shape
print total
print "---OUTPUT---"

output = total.mean(axis=0)

print output.shape
print output






