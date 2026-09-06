#Lists: ordered, mutable, allows duplicate elements 
mylist = ["banana", "cheery", "apple"]
mylist2 = list()
mylist2= [1, True, "Chi", "Chi"]
print(mylist2)
#Print an item
item = mylist[-2]
print(item)
#Check if an item is in the list
if "Chi" in mylist2: 
    print("She is so charming 💃.")
else: 
    print("She is still charming but she is not here 💃.")

#Things u knew: len, append, insert
#Remove the last item
mylist = ["banana", "cheery", "apple"]
lastitem=mylist.pop() 
print(lastitem)
#Remove an item: 
mylist.remove("banana")
print(mylist)
#Remove all items: 
mylist.clear()
print(mylist)

#Reverse the list 
mylist = ["banana", "cheery", "apple"]
#Option 01: 
newlist=list(reversed(mylist))
print (newlist)
#Option 02: 
newlist=mylist[::-1]
print (newlist)
#Option 03: Reverse the original list 
mylist.reverse()
print(mylist)

#Sort the list 
mylist = ["banana", "cheery", "apple", "kiwi"]
#Basic sort
newlist = sorted (mylist)
print(newlist)
#Reverse sorting 
newlist = sorted(mylist, reverse=True)
print(newlist) 
#Sorting by length: Not available with int 
newlist = sorted(mylist, key=len) #If you want to sort by something other than alphabetical order, use the "key"
print(newlist)
#Sort the original list 
mylist.sort() 
print (mylist)

# Merge 2 lists 
mylist = [0]*5
mylist2=[1,2,3,4,5]
newlist=mylist+mylist2
print (newlist)

#Slicing: is the same with tuple 

#Copy a list 
#Option 01: 
list_org=["a", "b", "c"]
list_cpy=list(list_org)
print(list_cpy)
#Option 02: 
list_org=["a", "b", "c"]
list_cpy=list_org.copy()
print(list_cpy)
#Option 03: 
list_org=["a", "b", "c"]
list_cpy=list_org[::-1]
print(list_cpy)
#Option 04: Change the origin 
list_org=["a", "b", "c"]
list_cpy=list_org

#List comprehension 
a = [1,2,3,4,5,6,7,8]
b = [i**2 for i in a]
print (a)
print (b)

# 2D collections
fruits = ["apple", "orange", "banana", "coconut"]
vegetables = ["celery", "carrot", "patatoes"]
meats = ["chicken", "fish", "turkey"]

groceries = [fruits, vegetables, meats]
print(groceries[0][1])

for collection in groceries: 
    for food in collection:
        print (food, end = " ")
    print() # enter when ends an collection 
