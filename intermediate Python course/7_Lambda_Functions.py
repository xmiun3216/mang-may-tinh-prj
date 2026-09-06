# 1. lambda arguments: expression 
#Eg 01
add10 = lambda x: x + 10
print (add10(10))
# Lambda is the same with def function (but shorter)
def add10(x):
    return x + 10 

#Eg 02 
mult = lambda x,y: x*y
print(mult(3,4))

#Eg 03 
#Basic 
points2D = [(1,2), (15,10), (-1,0), (10,4)]
points2D_sorted = sorted(points2D) # sort tuples by the first element 
print(points2D_sorted)
#Advance: With lambda function 
points2D = [(1,2), (15,10), (-1,0), (10,4)] 
points2D_sorted = sorted(points2D, key=lambda x:x[1]) #sort by the second element 
print(points2D_sorted)
#With def function: 
points2D = [(1,2), (15,10), (-1,0), (10,4)] 
def sort_by_y(x):
    return x[1]
points2D_sorted = sorted(points2D, key=sort_by_y)
print(points2D_sorted)
#Advance:
points2D = [(1,2), (15,10), (-1,0), (10,4)] 
points2D_sorted = sorted(points2D, key=lambda x:x[0] + x[1]) #sort by sum of each tuple 
print(points2D_sorted)

#2. Map(func, seq)
#With lambda 
a = [1,2,3,4,5]
b = map(lambda x:x*2, a)
print(list(b))
# With list comprehension 
a = [1,2,3,4,5] 
b = [x*2 for x in a]
print (b)

#3. filter(func, seq): Return all elements that the function evaluates to True 
#With lambda
a = [1,2,3,4,5] 
b = filter(lambda x:x%2 == 0,a) #Get only even numbers 
print(list(b))
#With list comprehension 
a = [1,2,3,4,5]
b = [x for x in a if x%2 == 0]
print(b)

#4. reduce(func, seq): Return one new element from the original 
from functools import reduce 
a = [1,2,3,4,5,6]
b = reduce(lambda x,y: x*y,a) # This is about 1000 times lower than using for loop 
print(b)
# Prove my above statement 
from timeit import default_timer as timer

a = [1,2,3,4,5,6]
start = timer()
from functools import reduce
b = reduce(lambda x,y: x*y,a)
end = timer()
print((end-start) * 1000000)

start = timer()
s=0
for x in a: 
    s+=x
end = timer()
print((end-start) * 1000000)
