s, smax = 0, 0
l, lmax = 0, 0
prev = 0

while (i := int(input())) != -1:
    if i > prev:
        s += i
        l += 1
        if l > lmax or (l == lmax and s > smax):
            smax = s
            lmax = l

    else:
        s = i
        l = 1

    prev = i

print(lmax, smax)
