# super() = Function used in a child class (subclass) to call methods from a parent class (superclass)
#           Allow you to extend the functionality of the inherited methods 
class Shape:
    def __init__(self, color, is_filled):
        self.color = color 
        self.is_filled = is_filled 
    def describe(self):
        print(f"It is {self.color} and {'filled' if self.is_filled else 'not filled'}")
class Circle(Shape):
    def __init__(self, color, is_filled, radius):
        super().__init__(color, is_filled)
        self.radius = radius
    def describe(self):
        print(f"It is a circle with an area of {3.14 * self.radius**2} cm2")
class Square(Shape):
    def __init__(self, color, is_filled, width):
        super().__init__(color, is_filled)
        self.width = width
class Triangular(Shape):
    def __init__(self, color, is_filled, width, height):
        super().__init__(color, is_filled)
        self.width = width
        self.height = height

circle = Circle (color="red", is_filled = True, radius=5)
square = Square (color="blue", is_filled = False, width=6)
triangular = Triangular (color="yellow", is_filled = True, width=6, height=7)
print(f"Triangular area: {triangular.width*triangular.height/2} cm2")

circle.describe()
# !=
triangular.describe()