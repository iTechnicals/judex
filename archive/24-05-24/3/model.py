def f(n):
    if n % 2 == 0:
        return n // 2
    else:
        return 3 * n + 1


n = int(input())
i = 0

while n != 1:
    n = f(n)
    i += 1

print(i)
