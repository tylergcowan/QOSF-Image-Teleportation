with open("trythis - Copy.jpg", "rb") as image:
    f = image.read()
    b = bytearray(f)
    print(len(b))
    bi=[]
    j=0
    for i in b:
        j=j+1
        bi.append(format(b[i],'08b'))







exit()

# split this into groups of 4, then send
i+=1
process=[]
for val in bi:
    pass
    #print (val)