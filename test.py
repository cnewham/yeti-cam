import numpy as np
sample = 3

a = np.random.randint(10,size=(3,3,3))
b = np.random.randint(10,size=(3,3,3))
c = np.random.randint(10,size=(3,3,3))

print "---RAW---"

print a
print b
print c

print "---MEAN---"

total = []
total.append(a.mean(axis=2))
total.append(b.mean(axis=2))
total.append(c.mean(axis=2))

total = np.array(total)

print total
print "---OUTPUT---"

print total.mean(axis=2)






