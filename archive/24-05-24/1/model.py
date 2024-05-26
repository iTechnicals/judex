pounds = int(input())
shillings = int(input())
pence = int(input())

shillings += pounds * 20
pence += shillings * 12

print(pence)

# one-line solution
# print(int(input()) * 240 + int(input()) * 12 + int(input()))
    