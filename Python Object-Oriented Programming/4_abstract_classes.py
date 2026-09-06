# Abstract class: A class that cannot be instantiated on its own = Subclassed    (instantiate = create instances)
#                 They can contain abstract methods, which are declared but have no implementation 
#                 Abstract class benifits:
#                 1. Prevents instantiation of the class itself -> get rid of vague objects like (ex. animal) -> prevent logic errors 
#                 2. Requires children to use inherited abstract methods 

from abc import ABC, abstractmethod # abc/ABC = Abstract Base Classes
class Vehicle(ABC):

    @abstractmethod
    def go(self):
        pass

    @abstractmethod
    def stop(self):
        pass 

class Car(Vehicle):
    def go(self):
        print ("You drive the car.")
    def stop(self):
        print ("You stop the car.")

class Boat(Vehicle):
    def go(self):
        print ("You sail the boat.")
    def stop(self):
        print ("You anchor the boat.")

boat = Boat()
boat.go()
boat.stop()