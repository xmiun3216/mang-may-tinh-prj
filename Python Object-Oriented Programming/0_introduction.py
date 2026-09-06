#object = A collections of related attributes (variables) & method (functions)
#   ex: phone, car, book 
#class = blueprint: used to design the structure and layout of an object

from car import Car
car1 = Car("Mustang", 2026, "red", False)
car2 = Car("Corvette", 2025, "blue", True)
car3 = Car("Charger", 2024, "yellow", True)
print(car1.model)
print(car1.year)
print(car1.color)
print(car1.for_sale)
car1.describe()
car1.stop()