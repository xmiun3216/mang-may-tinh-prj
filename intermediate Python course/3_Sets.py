# Set: unordered, mutable, no duplicates 
myset={1,2,3,4,1,2}
myset2=set("Hello")
print(myset)
print(myset2)

# Create empty set 
myset = set() #True 
myset2 = {} #False 
print (type(myset))
print (type(myset2))

#Add an element 
myset = set()
myset.add(1)
myset.add(2)
myset.add(3)
print(myset)

#Remove an element
#Option 01: 
myset={1,2,3,3,4,5}
myset.remove(3) #Receive "Error" if the item is not in the set 
print(myset)
#Option 02: 
myset={1,2,3,3,4,5}
myset.discard(10) #Nothing happens if the item is not in the set 
print(myset)
#Option 03: 
myset={1,2,3,3,4,5}
print(myset.pop()) #Remove the first item 
print(myset)

#Clear a set 
myset={1,2,3,3,4,5}
myset.clear()
print(myset)

#Check if an element is in the set 
myset={1,2,3,3,4,5} 
if 1 in myset: 
    print ("Yes sir, 1 is in your set")

#Union, Intersection, Difference, Symmetric difference 
odds = {1,3,5,7,9}
evens = {0,2,4,6,8}
primes = {2,3,5,7}
u=odds.union(evens)
print(u)
i=evens.intersection(primes)
print(i)
diff=odds.difference(primes)
print(diff)
diff2=odds.symmetric_difference(primes) #Elements in odds & primes but not in both 
print(diff2)

#Update, intersection update, difference update, symmetric difference update 
setA = {1,2,3,4,5,6,7,8,9}
setB = {1,2,3,10,11,13,14}
setA.update(setB)
print(setA)

#Subset, Supperset, Disjoint 
setA = {1,2,3,4,5}
setB = {1,2}
setC = {100,101}
print(setB.issubset(setA))
print(setA.issuperset(setB))
print(setA.isdisjoint(setC))

#Copy a set 📚
#Option 01: Don't change the original 
setA = {1,2,3}
setB = setA.copy()
#Option 02: Don't change the original 
setA = {1,2,3}
setB = set(setA)
#Option 03: Change the original 
setA = {1,2,3}
setB = setA 

#Frozen a set ❄️: U can't remove/add any element
setA = {1,2,3}
a = frozenset (setA) #Option 01 
a = frozenset ({1,2,3}) #Option 02 
a = frozenset ([1,2,3]) #Option 03 
print (a)