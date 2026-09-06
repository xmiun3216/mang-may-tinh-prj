# Itertools: product, permutations, combinations, accumulate, groupby, and infinite iterators

# 1. Product (Tích) 
from itertools import product
a = [1,2]
b = [3]
prod = product(a,b)
print(list(prod))
prod = product(a,b,repeat=2)
print(list(prod))

# 2. Permutations (Hoán vị): We see all the different orderings 
from itertools import permutations
a = [1,2,3]
perm = permutations(a, 2)  # n: len of each tuple 
print(list(perm))

# 3. Combinations (Tổ hợp)
from itertools import combinations
a = [1,2,3,4]




# 4. Accumulate (Tích )
# 5. Groupby 
# 6. Infinite iterators 