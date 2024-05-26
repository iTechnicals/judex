from functools import cache

@cache
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

for i in range(int(input())):
    m = int(input())
    r = 1
    while fib(r) % m != 0:
        r += 1

    print(fib(r) // m)
