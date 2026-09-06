# Example of error: syntax error (lỗi cú pháp), type error (lỗi kiểu dữ liệu), key error ...

# Raise an xception: Force an exception to occur 
x = -5 
# Option 01: 
if x < 0:
    raise Exception('x should be positive')
#Option 02: This is 100% like the first one 
assert (x>=0), 'x should be positive'
#Option 03: 
try: 
    a = 5/0
except Exception as e: 
    print(e)
#Option 04: Use when you know the error name 
try: 
    a = 5/0
    b = a *'10'
except ZeroDivisionError as e:
    print(e)
except TypeError as e: 
    print(e)
else: 
    print ("Everything's fine.")

#Define our OWN error:
class ValueTooHighError(Exception): 
    pass
class ValueTooSmallError(Exception): 
    def __init__(self, message, value):
        self.message = message
        self.value = value 
def test_value(x): 
    if x > 100: 
        raise ValueTooHighError("Value's too high.")
    if x < 5: 
        raise ValueTooSmallError("Value is too small", x)
try: 
    test_value(200)
except ValueTooHighError as e: 
    print(e) 
except ValueTooSmallError as e: 
    print(e.message, e.value)