#Collection: Counter, namedtuple, defaultdict, deque

# 1. Counter: a container storing the elements as dict keys & their counts as dict values 
from collections import Counter
a = "aaaaaaabbbbbbcccc"
mycounter = Counter(a)
print(mycounter)
print(mycounter.items())
print(mycounter.keys())
print(mycounter.values())
# Most common 
print(mycounter.most_common(1)) # Print the n most common character(s)
print(mycounter.most_common(1)[0][0]) #Print the most common's the first 's the first 
# Element 
print(list(mycounter.elements()))

# 2. namedtuple 
from collections import namedtuple 
Point = namedtuple('Point', 'x,y')
pt = Point (1, -4)
print (pt)
print (pt.x, pt.y)

# 3. defaultdict 
from collections import defaultdict
d = defaultdict(int)         #int: default type 
d = defaultdict(list)        # Or tuple, dict, set 
d = defaultdict(float)       # Or str 
d['a'] = 10
d['b'] = 20
print(d['a'])
print(d['c'])                #Return default type of 0 

# 4. deque 
from collections import deque
d = deque()
d.insert(1,2)
d.append(2)
d.appendleft(0)
print (d)
d.pop()
d.popleft()
print (d)
d.extend ([6,7,8])
print (d)
d.extendleft ([0,-1,-2]) #Insert elements from the right → the left
print (d)
d.rotate(1)
print (d)
d.clear()
print(d)