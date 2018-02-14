
def make_emission_global():
    """
    Author : Paul
    this algo takes as input the network "minimal" in the form id_Matsim, x1, y1, x2, y2
    this file must be in the folder that is accessed by path and must be named input_name
    In output, it creates a csv compatible with Aria. In particular, it transforms the id of matsim into an id of type int (id_matsim remains stored in the variable NAMADM) and that fills all useless columns in our case
    be careful to adapt the path
    Finally, it is in this file that we settle the units and pollutants we study.
    """
    
    path = "C:/Users/adminuser/Desktop/emissions/"
    nom_entree = "reseau_minimal.csv"
    nom_sortie = "reseau_compatible.csv"
    
    f = open(path+nom,"r")
    original = f.readlines()
    f.close()
    
    lines = [[] for i in range(len(original))]
    
    for i in range(len(original)):
        #séparation en sous tableau
        original[i]=original[i].split(';')
        lines[i]=original[i].copy()
    
    for i in range(len(original)):
        #changing the id into an int id with a one-to-one function (this only works for IDs of the type given by an OpenStreetMap export)
        id = original[i][0]
        idbis=""
        for char in id:
            if char!='_':
                idbis+=char
        
        if idbis[-1]=='r':
            lines[i][0]=idbis[:-1]+'1'
        else:
            lines[i][0]=idbis+'0'
    
    for i in range(1, len(lines)):
        #arrondi
        for j in range(1,5):
            lines[i][j]=str(round(float(lines[i][j])))
    
    new = []
    new.append("SRCEID;IDADM1;IDADM2;NAMADM;NAMGP1;NAMGP2;NAMGP3;IDCLA1;IDCLA2;IDCLA3;IDCLA4;IDCLA5;IDPROJ;SHIFTX;ORIGX;ORIGY;IDZH;X1;Y1;ZH1;X2;Y2;ZH2;SLOPE;WIDTH;IDCANYON;SPEEDX;SPEEDY;SPEEDZ;IDUNIT_PM10;Q_PM10")
    
    for i in range(1,len(lines)):
        line = lines[i][0]
        line += ";-999;-999;"
        line += original[i][0]
        line += ";route;null;null;-999;-999;-999;-999;-999;31;0;0;0;1;"
        line += lines[i][1]+";"+lines[i][2]
        line += ";0;"
        line += lines[i][3]+";"+lines[i][4]
        line += ";0;-999;-999;-1;0;0;0;1;1"
        
        new.append(line)
    
    f= open(path+nom_sortie,"w")
    for line in new:
        f.write(line+'\n')
    f.close()


make_emission_global()
