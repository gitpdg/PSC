
def format_compatible():
    """
    Author : Paul
    cet algo prend en entrée le réseau "minimal" sous la forme id_Matsim, x1,y1,x2,y2
    ce fichier doit se trouver dans le dossier auquel on accède par chemin et doit s'appeler nom_entree
    En sortie, cela créé un csv compatible avec Aria. En particulier, cela transforme l'id de matsim en un id de type int (id_matsim reste stocké dans la variable NAMADM) et cela remplit toutes les colonnes inutiles dans notre cas
    attention à adapter le chemin d'accès
    Enfin, c'est dans ce fichier qu'on règle les unités et les polluants qu'on étudie
    """
    
    chemin = "C:/Users/adminuser/Desktop/emissions/"
    nom_entree = "reseau_minimal.csv"
    nom_sortie = "reseau_compatible.csv"
    
    f = open(chemin+nom,"r")
    original = f.readlines()
    f.close()
    
    lines = [[] for i in range(len(original))]
    
    for i in range(len(original)):
        #séparation en sous tableau
        original[i]=original[i].split(';')
        lines[i]=original[i].copy()
    
    for i in range(len(original)):
        #redéfinition de l'id
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
    
    f= open(chemin+nom_sortie,"w")
    for line in new:
        f.write(line+'\n')
    f.close()


format_compatible()
