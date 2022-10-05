with open("cropped_qosf.jpg", "rb") as image:
  f = image.read()
  b = bytearray(f)
  for i in b:
        
    print (format(b[i],'08b'))

