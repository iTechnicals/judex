pence = int(input())

shillings = pence // 12
pence %= 12

pounds = shillings // 20
shillings %= 20

print(f"£{pounds} {shillings}s {pence}d")
    