import numpy as np

a = np.random.randint(10,size=(240,320,3))
b = np.random.randint(10,size=(240,320,3))
c = np.random.randint(10,size=(240,320,3))
d = np.random.randint(14,size=(240,320,3))

#print "---RAW---"

#print a
#print b
#print c

print "---MEAN---"

total = []
total.append(a.mean(axis=2))
total.append(b.mean(axis=2))
total.append(c.mean(axis=2))

total = np.array(total)

print total.shape

print "---OUTPUT---"

current = d.mean(axis=2)
output = total.mean(axis=0)
diff = abs(current - output)

print abs(100 - (current.sum() / output.sum()) * 100)
print (diff > 10).sum()






