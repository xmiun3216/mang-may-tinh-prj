#Tuples: ordered, immutable, allows duplicate elements 
mytuple = "Chi", 19, "cute", "cute"
print (f"My original tuple: {mytuple}")
#Count an item 
print (mytuple.count("cute"))
#Index of an item
print (mytuple.index("cute"))
#Change items in a tuple 
mylist = list(mytuple)
mylist[1] = 20
mytuple2 = tuple(mylist)
print(mytuple2)
#Unpacking 
name, age, *feature = mytuple 
print (name, age, feature)


#Slicing with tuple 
a = (1,2,3,4,5,6,7,8,9,10)
b = a[1:4] # Print from 1st item to the 3rd item 
c = a[:5] # Print from the 1st item to the 4th item  
d = a[5:] # Print from the 5th item to the last item
print (b, c, d) 
e = a[2::1] # [Start:stop:step]
f = a[::-1] # Revese the tuple 
print (e,f)

#Compare LIST vs TUPLE 
import sys
mylist = [1,2,3,"hello Chi iu 💗", True]
mytuple = 1,2,3,"hello Chi iu 💗", True
print (sys.getsizeof(mylist),"bytes")
print (sys.getsizeof(mytuple),"bytes")

import timeit
print(timeit.timeit(stmt="[1,2,3,4,5,6,7,8,9]", number=1000000),"s")
print(timeit.timeit(stmt="(1,2,3,4,5,6,7,8,9)", number=1000000),"s")