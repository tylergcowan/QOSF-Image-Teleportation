
import PIL.Image as Image
import io

with open("trythis - Copy.jpg", "rb") as image:
    f = image.read()
    b = bytearray(f)
    print(len(b))

bi=[]
i=0
for xx in b:

    bi.append(format(b[i],'08b'))  # GOAL OF THIS IS TO CONVERT FROM SAY, 216, TO LIKE 10010110
    print(b[i],bi[i], int(bi[i],2))

    i+=1

c=int(bi[0],2)
print(c)

print(type(b[1]),type(bi[1]), type(int(bi[1],2)))
exit()

# great, so the task at hand is to just send b through, and make sure it's identical (or nearly) to the original b.

image2 = Image.open(io.BytesIO(bi))
image2.save("testt123tt.jpg")

exit()
# first we need to make sure we can unambiguously

final_b=[]

# split this into groups of 4, then send
i=0
# the array of 4 bytes to process
process=[]
for val in bi:
    process.append(bytes(val,'utf-8'))
    i+=1
    if i==4:# send it pieces of 4 bytes
        i=0
        #print(process)
        #now process the 4?
        for x in process:
            #print(type(bytes(x,'utf-8')))
            final_b.append(x)
#            final_b.append(bytes(x,'utf-8'))
        process=[]

print(type(final_b))

i=0
for xy in final_b:
    final_b[i]=final_b[i].encode('utf-8')
    i+=1


image2 = Image.open(io.BytesIO(final_b))
image2.save("testttt.jpg")



'''
j=0
for i in final_b:
    if(final_b[j]!=bi[j])
    j+=1

print(final_b==bi)
'''






