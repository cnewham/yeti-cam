import numpy as np

a = np.random.randint(10,size=(320,240,3))
b = np.random.randint(10,size=(320,240,3))
c = np.random.randint(10,size=(320,240,3))
d = np.random.randint(13,size=(3,3,3))

print "---PERCENT CHANGE---"

a1 = a.mean(axis=2)
b1 = b.mean(axis=2)

diff = abs(a1-b1)
changed = np.count_nonzero(diff)
total = (diff.shape[0]*diff.shape[1])

print type(changed)
print type(total)
print (float(changed)/float(total)) * 100

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






