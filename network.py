chemin = "Documents/X/2A/PSC/MATsim/matsim-0.9.0/toy_model/network.xml"
speed = "7.5"
capacity = "50"


f = open(chemin, "w")

f.write('<?xml version="1.0" ?>\n')
f.write('<!DOCTYPE network SYSTEM "http://www.matsim.org/files/dtd/network_v1.dtd">\n')

f.write('<network name="Network_Test1">')

#Node creation

f.write('\n      <nodes>\n') 

l=[]
for x in range(-5,6):
    for y in range(-5,6):
        l.append('           <node id="'+str((x+5)*100+(y+5))+'" x="'+ str(x*200)+'" y="'+str(y*200)+'"/>')

f.write("\n".join(l)+"\n")

f.write('\n      </nodes>\n')
    
#Link creation
#link id : where it's from *10000 +where it's going to.
f.write('\n      <links capperiod="01:00:00" effectivecellsize="7.5" effectivelanewidth="3.75">\n') 

l=[]
for x in range(-5,5):
    for y in range(-5,5):
        l.append('           <link id="'+str( ((x+5)*100+(y+5))*10000 + (x+5)*100+(y+6) )+'" from="'+str((x+5)*100+(y+5))+'" to="'+str((x+5)*100+(y+6))+'" length="200" freespeed="'+speed+'" capacity="'+capacity+'" permlanes="1.0" oneway="1"/>')
        l.append('           <link id="'+str( ((x+5)*100+(y+6))*10000 + (x+5)*100+(y+5) )+'" from="'+str((x+5)*100+(y+6))+'" to="'+str((x+5)*100+(y+5))+'" length="200" freespeed="'+speed+'" capacity="'+capacity+'" permlanes="1.0" oneway="1"/>')
        l.append('           <link id="'+str( ((x+5)*100+(y+5))*10000 + (x+6)*100+(y+5) )+'" from="'+str((x+5)*100+(y+5))+'" to="'+str((x+6)*100+(y+5))+'" length="200" freespeed="'+speed+'" capacity="'+capacity+'" permlanes="1.0" oneway="1"/>')
        l.append('           <link id="'+str( ((x+6)*100+(y+5))*10000 + (x+5)*100+(y+5) )+'" from="'+str((x+6)*100+(y+5))+'" to="'+str((x+5)*100+(y+5))+'" length="200" freespeed="'+speed+'" capacity="'+capacity+'" permlanes="1.0" oneway="1"/>')

for x in range(-5,5):
    l.append('           <link id="'+str( ((x+5)*100+10)*10000 + (x+6)*100+10 )+'" from="'+str((x+5)*100+10)+'" to="'+str((x+6)*100+10)+'" length="200" freespeed="'+speed+'" capacity="'+capacity+'" permlanes="1.0" oneway="1"/>')
    l.append('           <link id="'+str( ((x+6)*100+10)*10000 + (x+5)*100+10 )+'" from="'+str((x+6)*100+10)+'" to="'+str((x+5)*100+10)+'" length="200" freespeed="'+speed+'" capacity="'+capacity+'" permlanes="1.0" oneway="1"/>')
    
for y in range(-5,5):
    l.append('           <link id="'+str( (10*100+(y+5))*10000 + 10*100+(y+6))+'" from="'+str(10*100+(y+5))+'" to="'+str(10*100+(y+6))+'" length="200" freespeed="'+speed+'" capacity="'+capacity+'" permlanes="1.0" oneway="1"/>')
    l.append('           <link id="'+str( (10*100+(y+6))*10000 + 10*100+(y+5))+'" from="'+str(10*100+(y+6))+'" to="'+str(10*100+(y+5))+'" length="200" freespeed="'+speed+'" capacity="'+capacity+'" permlanes="1.0" oneway="1"/>')

f.write("\n".join(l)+"\n")

f.write('\n      </links>\n') 
    
f.write('\n</network>')
f.close()