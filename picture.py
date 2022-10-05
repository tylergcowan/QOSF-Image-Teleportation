
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
    i+=1

# this is how you'll do it. use this to convert at the end
'''
c=[]
for x in bi:
    c.append(int(x,2))
c=bytearray(c)
'''

# use this
#image2 = Image.open(io.BytesIO(c))
#image2.save("testt123t123t.jpg")


final_b=[]

# split this into groups of 4, then send
i=0
# the array of 4 bytes to process
process=[]
for val in bi:
    process.append(val)
    i+=1
    if i==4:# send it pieces of 4 bytes
        i=0
        # INSERT CALLS TO PROCESS THE ARRAY OF 4
        process=[]


image2 = Image.open(io.BytesIO(final_b))
image2.save("testttt.jpg")



'''
j=0
for i in final_b:
    if(final_b[j]!=bi[j])
    j+=1

print(final_b==bi)
'''






