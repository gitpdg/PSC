# Written by Cédric
# Convert a network.xml into a .xls that contains all the links and the coordinates of their two ends. Is to be completed with another Python script that writes a complete input file for Aria lineic emissions 

from xlwt import Workbook  

from lxml import etree

book = Workbook()
    
feuil1 = book.add_sheet('feuille 1')
    
feuil1.write(0,0,'id1')
feuil1.write(0,1,'x1')
feuil1.write(0,2,'y1')
feuil1.write(0,3,'x2')
feuil1.write(0,4,'y2')

tree = etree.parse("C:/Users/proprietaire/Documents/PSC Clarity/Toy Model/network_rouen.xml")
num=1
for link in tree.xpath("/network/links/link"):
    ligne = feuil1.row(num)
    ligne.write(0,link.get("id"))
    id1 = link.get("from")
    id2 = link.get("to")
    for node1 in tree.xpath("/network/nodes/node"):
        if node1.get("id")==(id1):
            x1=node1.get("x") 
            y1=node1.get("y")
    for node2 in tree.xpath("/network/nodes/node"):
        if node2.get("id")==(id2):
            x2=node2.get("x") 
            y2=node2.get("y")
    ligne.write(1,x1)
    ligne.write(2,y1)
    ligne.write(3,x2)
    ligne.write(4,y2)
    num+=1
    
# création matérielle du fichier résultant
book.save('minimal_network.xls')

