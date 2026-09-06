#Strings: ordered, immutable, text representation 
#To write ' inside a string 
mystring = "I'm soooo pretty 💅." #Option 01 
mystring = 'I\'m soooo pretty 💅.' #Option 02 
print (mystring)

#To write multiline string 
mystring = """Hello Chi. 
You're so cute 🥰."""                          #Option 01 
print (mystring)
mystring = "Hello Chi. \n You're so cute 🥰."  #Option 02 
print (mystring)
mystring = """Hello Chi. \
You're so cute 🥰. """                         #Not enter 
print (mystring)

# Access a string + Slicing: Similar to list & tuple 
# Can't change any elements in a string 

# Merge 2 strings: similar to list 
greeting = "Hello"
name = "Chi"
sentence = greeting + name 
print (sentence)

# Check if a substring 's in a string 
greeting = "Hello Chi"
if "Chi" in greeting: 
    print ("Chi is right here!!!")
else: 
    print ("Chi is not here :(.")

# Remove redundant white space (only in the lef & the right)
mystring = "         Hello        Chi    "
mystring = mystring.strip() 
print(mystring)

#Upper, lower, Startwith, Endwith, Find, Count, Replace, 
mystring = "Hello Chi"
print (mystring.upper()) #The original string can't be changed 
print (mystring.lower())
print (mystring.title())
print (mystring.startswith("h")) #Available with both an character and a substring 
print (mystring.endswith("chi"))
print (mystring.find("llo")) #Find the index of the first character in a substring 
print (mystring.count("l"))  #Count the number of a substring appearing in a string 
print (mystring.replace("World", "Universe")) #Replace "World" with "Universe"

#String ⇒ List 
mystring = "I'm okay. How are you doing, guy?"
#Option 01: 
mylist = list (mystring) #Split into characters 
#Option 02: 
mylist = mystring.split(" ") #Split string into elements by stuff in " "
print(mylist)

#List ⇒ String 
mylist = ["How", "are", "you", "doing"] 
mystring = ' '.join(mylist)
print(mystring)

#Multiple a string 
mystring = 'a'*6
print(mystring)

#Compare the complexity of using loop vs join method 
from timeit import default_timer as timer
mylist = ['a']*1000000000
# Option 01: 
start = timer()
mystring = ""
for i in mylist: 
    mystring += i
end = timer()
print (end - start)
#Option 02: 
start = timer()
mystring = ''.join(mylist)
end = timer()
print (end-start)

# %s, format(), f-Strings 
var = 3.123456789
var2 = 10
mystring = f'The variables is {round(var,2)} and {var2}.'
print(mystring)

