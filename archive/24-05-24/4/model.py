a = int(input())
i = 2

while True:
    curr = a ** (1 / i)

    if curr < 2:
        print("False")
        break

    if curr == int(curr):
        print("True")
        break

    i += 1