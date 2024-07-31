freqList = {}
for i in range(21, 109):
    n = i - 20
    freqList[i] = 2**((n-49)/12) * 440

for i in range(21, 109):
    print(i, freqList[i])