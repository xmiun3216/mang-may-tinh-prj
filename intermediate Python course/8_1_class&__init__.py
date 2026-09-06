#Ex 01: 
class Smartphone: #Smartphone: Instance (Đối tượng)
    def __init__(self, brand, price): 
        self.brand = brand 
        self.price = price
        self.battery = 100 #Giá mặc định cho mọi điện thoại mới 
    def info(self): 
        print(f"Brand: {self.brand}, Price: {self.price}, Pin level: {self.battery}")
phone1=Smartphone('iPhone', 1200)
phone2=Smartphone("Samsung", 1000)
phone1.info()

#Ex 02: Tạo class YourAccount; Dùng __init__ để gán tên tài khoản và số dư ban đầu; 
# Tạo phương thức add(self) để nhập số tiền muốn nạp
# Tạo phương thức remain(self) để in ra tên tài khoản + số dư hiện tại 
class YourAccount: 
    def __init__(self,name, budget):
        self.name = name
        self.budget = budget
    def add(self):
        money = int(input("Enter the amount of input money: "))
        print ("You have just add: ", money)
        self.budget += money
    def remain(self): 
        return f"Your account: {self.name}\nCurrent money: {self.budget}" 
account1 = YourAccount("Cheese", 1000)
account1.add()
print(account1.remain())