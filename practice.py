class Vehicle:
    def __init__(self):
        self.speed = 0
        self.model=None
        self.brand=None
        print("Vehicle created. Ready to go!")

    def accelerate(self, increment):
        self.speed += increment
        print(f"Accelerating... Current speed: {self.speed} km/h")

    def brake(self, decrement):
        self.speed = max(0, self.speed - decrement)
        print(f"Braking... Current speed: {self.speed} km/h")

    def details(self, model, brand):
        self.model=model
        self.brand=brand
        print(f"Vehicle Details: {self.brand} {self.model}")
    
    def show_details(self):
        if self.model and self.brand:
            print(f"Vehicle Details: {self.brand} {self.model}")
        else:
            print("Vehicle details not set.")

# class Animal:
#     def speak(self):
#         print("Some sound")

# class Dog(Animal):
#     def speak(self):
#         print("Bark")

# d = Dog()
# d.speak()
# class Cat:
#     def speak(self):
#         print("Meow")

# class Dog:
#     def speak(self):
#         print("Bark")

# for animal in [Cat(), Dog()]:
#     animal.speak()
# a = Vehicle()
# a.details("Model S", "Tesla")
# a.accelerate(50)
# a.brake(20)
# a.show_details()

# from abc import ABC, abstractmethod

# class Payment(ABC):
#     @abstractmethod
#     def pay(self, amount):
#         pass

# class CreditCardPayment(Payment):
#    def __init__(self):
#        print("Credit Card Payment method selected.")


# a = CreditCardPayment()

# def my_decorator(func):
#     def wrapper():
#         print("Before function runs")
#         func()
#         print("After function runs")
#     return wrapper

# @my_decorator
# def say_hello():
#     print("Hello!")

# say_hello()
# def repeat(n):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             for _ in range(n):
#                 print(f"Running {func.__name__}...")
#                 print(f"Arguments: {args}, {kwargs}")
#                 func(*args, **kwargs)
#         return wrapper
#     return decorator

# @repeat(10)
# def greet(age,name="World"):
#     print(f"Hello, {name}! You are {age}.")

# greet(19,name="Alice")
# from functools import wraps

# def my_decorator(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         return func(*args, **kwargs)
#     return wrapper

# def deco1(func):
#     def wrapper():
#         print("Deco1")
#         func()
#     return wrapper

# def deco2(func):
#     def wrapper():
#         print("Deco2")
#         func()
#     return wrapper

# @deco1
# @deco2
# @deco1
# @deco2
# def test():
#     print("Hello")

# test()

# import time
# from functools import wraps

# def timer(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         start = time.time()
#         result = func(*args, **kwargs)
#         end = time.time()
#         print(f"Execution time: {end - start}")
#         return result
#     return wrapper

# class CountCalls:
#     def __init__(self, func):
#         self.func = func
#         self.count = 0

#     def __call__(self, *args, **kwargs):
#         self.count += 1
#         print(f"Called {self.count} times")
#         return self.func(*args, **kwargs)

# @CountCalls
# def say_hi():
#     print("Hi")

# say_hi()
# say_hi()

# @CountCalls
# def add(a, b):
#     return a + b

# print(add(12, 34))
# print(add(56, 78))


# class BankAccount:
#     def __init__(self,name, balance=0):
#         self.__name = name
#         self.balance = balance
#         self.audit_log = []
#         print(f"Bank account for {self.__name} created with balance {self.balance}")

#     def deposit(self, amount):
#         self.balance += amount
#         print(f"Deposited {amount}. New balance: {self.balance}")

#     def withdraw(self, amount):
#         if amount > self.balance:
#             print("Insufficient funds")
#         else:
#             self.balance -= amount
#             print(f"Withdrew {amount}. New balance: {self.balance}")

#     def __call__(self, *args, **kwds):
#         self.audit_log.append((args, kwds))
#         print(f"Audit log updated: {self.audit_log}")

# account = BankAccount("Alice", 1000)
# account.deposit(500)
# account.withdraw(200)
# account("Deposit", 500)
# account("Withdraw", 200)
# print(account._BankAccount__name)


a = [12,3,4,4]
b=list(a.append([5,6]))

print(a)
print(b)
a.append(5)
print("after appending 5 to a:")
print(a)
print(b)