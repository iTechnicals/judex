a = int(input())
if int(a**0.5)**2 == a:
    print("YES")
else:
    print("NO")

# one-line solution
# print("YES" if int((a := int(input()))**0.5)**2 == a else "NO")
    