#author : Paul
#Creates a 10x10 grid of receptors (with ARIA format) to be used for Rouen

f = open("Documents/recepteurs.csv","w")
f.write("R_INDEX;R_NAME;R_X;R_Y;R_ALTI\n")
id=1
x_min,x_max,y_min,y_max = (354.9933893242981, 367.6196486670857, 5470.383826645574, 5483.701332441034)
division = 10

for i in range(division):
    R_X = round(x_min + (x_max-x_min)*(1/2+i)/division,1)
    for j in range(division):
        R_Y = round(y_min + (y_max-y_min)*(1/2+j)/division,1)
        f.write(str(id) +";"+str(int((R_X-355)*10))+"_"+str(int((R_Y-5471)*10))+";"+str(R_X)+";"+str(R_Y)+";0\n")
        id += 1

f.close()
