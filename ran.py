import random

n = 10
arr = [0, 1] * (n//2) + [0] * (n%2)
random.shuffle(arr)
print(arr)