f = open("C:/Users/adminuser/Desktop/recepteurs/recepteurs.csv","w")
f.write("R_INDEX;R_NAME;R_X;R_Y;R_ALTI\n")
id=1
for i in range(10):
    R_X = round(-0.9+i*0.2,1)
    for j in range(10):
        R_Y = round(-0.9+j*0.2,1)
        f.write(str(id) +";"+str(int(R_X*10))+"_"+str(int(R_Y*10))+";"+str(R_X)+";"+str(R_Y)+";0\n")
        id += 1

f.close()