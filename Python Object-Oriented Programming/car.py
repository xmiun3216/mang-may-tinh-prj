class Car: # self = object = instance 
    def __init__(self, model, year, color, for_sale):  # Constructor: hàm khởi tạo 
        self.model = model # attributes = (instance) variables 
        self.year = year
        self.color = color
        self.for_sale = for_sale 
    def drive (self): # methods = functions 
        print (f"You drive the {self.color} {self.model}.")
    def stop (self):
        print (f"You stop the {self.color} {self.model}.")
    def describe(self):
        print(f"{self.year} {self.color} {self.model}")