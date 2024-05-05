# naive solution
def digitsum(n):
    return sum(int(i) for i in str(n))

n = int(input())
while n > 9:
    n = digitsum(n)

print(n)

# smart solution using maths
# n = int(input())
# if n == 0:
#     print(0)
# else:
#     s = n % 9
#     print(9 if s == 0 else s)
