# Written by Cédric
# This program deletes the links which have a length taht is 'NaN' because MatSim does not work with these.  

import lxml.etree as le

with open('C:/Users/proprietaire/Documents/PSC Clarity/Toy Model/network_rouen_agglo.xml','r') as f:
    
    res=open("network_rouen_agglo_filtre.txt", "w")
    doc=le.parse(f)
    for link in doc.xpath('//link'):
        b3 = (link.attrib['length'] == "NaN")
        if b3:    
            parent=link.getparent()
            parent.remove(link)
    res.write(str(le.tostring(doc)))
    res.close()
