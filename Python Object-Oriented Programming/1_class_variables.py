# class variables = Shares data among all instances / objects created from a class 
#                   Defined outside the constructor 

class Student:
    graduate_year = 2030    # class variable
    num_students = 0 
    def __init__ (self, name, age):
        self.name = name    # instance/object variable 
        self.age = age
        Student.num_students += 1 
student1 = Student("Spongebob", 10)
student2 = Student("Harry Potter", 12)
student3 = Student("Emma Watson", 13)
student4 = Student("Sandy", 14)

print(student1.graduate_year)
print(student2.graduate_year)
# = 
print(Student.graduate_year)

print(Student.num_students)

print(f"My graduating class of {Student.graduate_year} has {Student.num_students} students:")
print(student1.name)
print(student2.name)
print(student3.name)
print(student4.name)