#Dictionaries: unordered, mutable, key-value pairs 
mydict= {"name": "Chi", "age": 31, "feature": "pretty"}
print(mydict)
mydict2 = dict(name="Mei", age = 1, feature="cute" )
print(mydict2)
#Access the value 
value = mydict["name"] # Can't print mydict[0] => Error 
print (value)
#Add a key & a value 
mydict["hobby"]="dancing"
print(mydict)
#Replace value 
mydict["hobby"]="walking"
#Delete key / value / key&value 
del mydict["age"] # = mydict.pop("age")
print (mydict)
mydict.popitem() # delete the last pair  

#Check if a key is in the dict 
mydict= {"name": "Chi", "age": 31, "feature": "pretty"}
if 'name' in mydict: 
    print(mydict['name'])
# Option 02: 
try: 
    print(mydict['lastname'])
except: 
    print("Error")
# Print key & value  
for key in mydict: # = for x in my dict.keys(): 
    print(key)
for x in mydict.values():
    print(x)
for a,b in mydict.items(): 
    print(a,b)

# Only copy the original ver of a dict 
#Option 01: 
mydict= {"name": "Chi", "age": 31, "feature": "pretty"}
newdict=dict(mydict)
newdict["lastname"] = "Pham"
print (newdict, "\n", mydict)
#Option 02: 
newdict=mydict.copy()

# Merge 2 dicts 
mydict= {"name": "Chi", "age": 31, "feature": "pretty", "email":"lovely@socute.com"}
mydict2 = dict(name="Mei", age = 1, feature="cute" )
mydict.update(mydict2)
print(mydict)

# Key in dict can be a tuple & can't be a list 
mytuple=(8, 7)
mydict={mytuple:15}
print (mydict)
