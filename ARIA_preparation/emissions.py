import matplotlib.pyplot as plt
import numpy as np
import math

"""
This program is used to transform the emission data from MATsim into valid inputs for ARIA. It also allows to visualise the emissions.
It is divided like this :
    - config
    - preliminary functions
    - emissions to dict
    - emission map
    - emission to CSV
    - map to CSV
    - preliminary functions
    - surfacic emissions
    - lineic emissions
    - run
"""

## CONFIG

#inputs
file = "Documents/gratuite/input/events.xml" #this is the event file generated by MATsim
mapfile = "Documents/gratuite/input/sample_network.xml" #this is the network file
pollutant = ["NOX","PM"] #the pollutant studied

#outputs
emissions_file = "Documents/gratuite/output/total_emissions.csv" #gives the emission for each hour for each link in the ARIA format
map_csv_file = "Documents/gratuite/output/map.csv" #gets the network in the simplest format
output_file = "Documents/gratuite/output/surfacic_emissions.csv" #gives the emission for each hour for each rectangle in the ARIA format
output_file_center = "Documents/gratuite/output/lineic_emissions.csv" #gives the emission for each hour for each rectangle in the ARIA format
surface_network = "Documents/gratuite/output/srf_network.csv" #a division of the zone in rectangles compatible with ARIA
lineic_network = "Documents/gratuite/output/lineic_network.csv" #gets the network in a form compatible with ARIA for the chronological emissions

date = "01/01/2018 " #written in the emissions csv file. Needs to correspond to the date used for the ARIA simulation.

resolution = 30 #number of divisions for the surfacic division
facteur = 100 #rapport de population
non_exhaust = 4 #facteur pour les PM


## PRELEMINARY FUNCTIONS

def file_len(fname):
    """This function returns the number of lines in the file"""
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def xmlline_to_dict(s):
    """This function changes a xml line to a dict"""
    s = s.replace('=', "':")
    s = s.replace('"', "'")
    s = s.replace('<event ', "{'")
    s = s.replace('  />', "}")
    s = s.replace("vehicle enters traffic", "vehicle_enters_traffic")
    s = s.replace("vehicle leaves traffic", "vehicle_leaves_traffic")
    s = s.replace("left link", "left_link")
    s = s.replace("entered link", "entered_link")
    s = s.replace("pt interaction","pt_interaction")
    s = s.replace("vehicle aborts","vehicle_aborts")
        
    for i in range(len(s)) :
        if s[i] in "azertyuiopmlkjhgfdsqwxcvbnAZERTYUIOPMLKJHGFDSQWXCVBN":
            if s[i-1] == " ":
                s = s[:i] + "'" + s[i:]
        if s[i]=="'" :
            if s[i+1] == " ":
                s = s[:i+1] + "," + s[i+1:]
    
    for i in range(len(s)) :
        if s[i] in "azertyuiopmlkjhgfdsqwxcvbnAZERTYUIOPMLKJHGFDSQWXCVBN":
            if s[i-1] == " ":
                s = s[:i] + "'" + s[i:]
        if s[i]=="'" :
            if s[i+1] == " ":
                s = s[:i+1] + "," + s[i+1:]
    
    s = s.replace(':', " : ")
        
    s_dict = eval(s)
    
    return s_dict


def time_format(secondes):
    """this function takes a time entry as a float number of seconds and returns a string "hh:mm:ss" """
    
    secondes = round(secondes)
    time = ""
    hours = secondes//3600
    if (hours > 9) :
        time += str(hours) + ":"
    else :
        time += "0" + str(hours) + ":"
    secondes %= 3600
    
    minutes = secondes//60
    if (minutes > 9) :
        time += str(minutes) + ":"
    else:
        time += "0" + str(minutes) + ":"

    secondes %= 60
    if (secondes > 9) :
        time += str(secondes)
    else:
        time += "0"+str(secondes)
    return time

def num(s):
    """ returns int(s) or float(s)"""
    try:
        return int(s)
    except ValueError:
        return float(s)

def matsim_id_to_int(link):
    """this is a bijection between ids from matsim (that may contain underscores and may end in r) with an id only composed of integers """
    linkbis=""
    for char in link:
        if char!='_':
            linkbis+=char
    
    if linkbis[-1]=='r':
        linkbis=linkbis[:-1]+'1'
    else:
        linkbis+='0'
    return linkbis

def new_id(link_dict):
    """ creates a dictionnary that gives each link an id compatible with ARIA """
    ids = dict()
    c=1
    for link in link_dict:
        ids[link]=str(c)
        c+=1
    return ids

def getlength(link):
    """calculates the length of a link"""
    return ( ((float(link_dict[link][0])-float(link_dict[link][2]))**2 + (float(link_dict[link][1])-float(link_dict[link][3]))**2)**0.5)

###EMISSIONS TO DICT


def emissions_to_dict(pollutant):
    """extracts polluant corresponding to the string "pollutant" in a dict"""
    source = open(file, "r")
    
    #Skip the first two lines
    source.readline()
    source.readline()
    
    events=list()
    
    #Reads all lines, except for the last one
    for i in range(file_len(file)-3):
        ligne = source.readline()
        events.append(xmlline_to_dict(ligne))
        
    emissions=dict()
    
    #On ajoute les heures au dictionnaire
    for i in range(24):
        emissions[str(i)]=dict()
        
    for event in events :
        event_type = event["type"]
        if event_type=="coldEmissionEvent" or event_type=="warmEmissionEvent" :
            link = event["linkId"]
            for pol in pollutant:
                amount = float(event[pol])
                if amount>0:
                    time = (int(float(event["time"]))//3600)%24
                    if not(matsim_id_to_int(link) in emissions[str(time)]):
                        emissions[str(time)][matsim_id_to_int(link)] = dict()
                    if pol in emissions[str(time)][matsim_id_to_int(link)].keys():
                        if pol=="PM":
                            emissions[str(time)][matsim_id_to_int(link)][pol] += amount*facteur*non_exhaust/1000 #g into kg
                        else:
                            emissions[str(time)][matsim_id_to_int(link)][pol] += amount*facteur/1000 #g into kg

                    else :
                        if pol=="PM":
                            emissions[str(time)][matsim_id_to_int(link)][pol] = amount*facteur*non_exhaust/1000 #g into kg
                        else:
                            emissions[str(time)][matsim_id_to_int(link)][pol] = amount*facteur/1000 #g into kg
        
    # #to avoid nullPointers
    # for hour in emissions.keys():
    #     for link in emissions[hour].keys():
    #         for pol in pollutant:
    #             if not(pol in emissions[hour][link].keys()):
    #                 emissions[hour][link][pol]=0;
    
    return emissions

def agregate_data(emissions):
    """ returns a dictionnary containing, for each hour, the emissions aggregated spatially"""
    agregate = dict()
    for hour in emissions:
        for pol in pollutant:
            tot_em=0
            for link in emissions[hour] :
                tot_em += emissions[hour][link][pol]
            agregate[pol][hour] = tot_em
    return agregate

def trace_agregate_data(emissions,pol):
    """ plots the spatially-aggregated emissions data over time"""
    agreg_data=agregate_data(emissions)[pol]
    X=[i for i in range(24)]
    Y=[agreg_data[str(i)] for i in range(24)]
    plt.plot(X,Y)
    plt.show()
    return


###EMISSION MAP

def map_to_dict():
    """ this function transforms the xml network used by MATSim into :
    - a dictionnary link_dict, whose keys are the links id (as strings), whose value is the list x1,y1,x2,y2 (as strings)
    - a list roads, each line of the form [link id as string, [x1,x2 as int], [y1,y2 as int]]
     """
    
    source = open(mapfile, "r")
    
    #We get the content of the file
    s = source.readlines()
    
    #We make one big string
    s2 = str()
    for i in s : 
        s2=s2+i
    s=s2
    
    #We get rid of the first part of the string, and get the links and nodes
    s=s.split('<nodes>')[1]
    nodes, links = s.split('</nodes>')
    links = links.split('</links>')[0]
    links = links.split('<links')[1]
    
    #We make dicts of all nodes and links
    
    #First the nodes
    nodes = nodes.split("<node")
    #We get rid of anomalies
    nodes2 = list()
    for node in nodes:
        if ("id" in node):
            nodes2.append(node.split("/>")[0])
    nodes = nodes2
    node_dict = dict()
    #We make a dictionnary
    for node in nodes:
        l1 = node.split('="')
        l2 = list()
        for i in l1:
            l2=l2+i.split('"')
        node_dict[int(l2[1])]=[l2[3],l2[5]]
    
    #Then the links
    links = links.split("<link")
    #We get rid of anomalies
    links2 = list()
    for link in links:
        if ("id=" in link):
            links2.append(link.split("/>")[0])
    links = links2
    link_dict = dict()
    #We make a dictionnary
    for link in links:
        l1 = link.split('="')
        l2 = list()
        for i in l1:
            l2=l2+i.split('"')
        link_dict[matsim_id_to_int(l2[1])]=[l2[3],l2[5]]
        
    #Then, we mix the two to get the map
    for link in link_dict:
        link_dict[link] = node_dict[int(link_dict[link][0])] + node_dict[int(link_dict[link][1])]
    
    #We generate the map
    
    #x_nodes = [num(node_dict[key][0]) for key in node_dict]
    #y_nodes = [num(node_dict[key][1]) for key in node_dict]
    
    roads = list()
    for link in link_dict:
        roads.append([link, [num(link_dict[link][0]),num(link_dict[link][2])],[num(link_dict[link][1]),num(link_dict[link][3])]])
    
    return roads, link_dict

#Hour by hour 

def colorcode(hour, link):
    """ this function takes as arguments the hour (e.g. '23') and the link (as a list containing the link id in the first position) and returns the color (coded by a char) of the link (green, yellow or red respectively for low, medium and high emissions). """
    
    #parameters
    limit_low_medium = 0.01
    limit_medium_high = 0.1
    
    if link[0] in emissions[hour].keys():
        emission = emissions[hour][link[0]]
        if emission<limit_low_medium : 
            return 'g'
        if emission<limit_medium_high :
            return 'y'
        else :
            return 'r'
    #if link[0] is not in the keys of emissions[hour], it means there are no emissions, so color is green
    return 'g'

def image_output(roads):
    """saves the 24 images, showing the network emissions for each hour. """
    for link in roads:
        plt.plot(link[1], link[2], color='k')
    
    for hour in range(24):
        
        #Size and font
        #Size
        plt.figure(figsize=(10,10))
        #Font
        ax = plt.subplot(111,title="Situation at hour "+str(hour))
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
            ax.get_xticklabels() + ax.get_yticklabels()):
                item.set_fontsize(20)
        for link in roads:
            plt.plot(link[1], link[2], color=colorcode(str(hour), link), linewidth=5)
        plt.savefig('images/hour'+str(hour)+'.png')
        #plt.show()
    return


###EMISSIONS TO CSV

def emissions_to_csv():
    """ this function creates (or overwrites) the emissions csv file, in a format that is directly usable as ARIA's lineic chronologic emission file"""
    csv = open(emissions_file, "w")
    csv.write("SRCEID;DATEDEB;DATEFIN")
    for pol in pollutant:
        csv.write(";Q_"+pol)
    csv.write("\n")
    
    for hour in range(24):
        if str(hour) in emissions.keys():
            for link in emissions[str(hour)]:
                linkid = num(link)
                datedeb = date + time_format(hour*3600)
                datefin = date + time_format((hour+1)*3600)
                
                csv.write(str(linkid)+';'+datedeb+';'+datefin)
                for pol in pollutant:
                    csv.write(';'+str(round(emissions[str(hour)][link][pol],5)))
                csv.write("\n")
    
    csv.close()
    return

###MAP TO CSV

def map_to_csv():
    """this function creates (or overwrites) the map csv file, which contains the column id, x1, y1, x2, y2, all of type int"""
    csv = open(map_csv_file, "w")
    
    csv.write("id1;x1;y1;x2;y2\n")
    for link in link_dict:
        x1=link_dict[link][0]
        y1=link_dict[link][1]
        x2=link_dict[link][2]
        y2=link_dict[link][3]
        csv.write(str(link)+';'+x1+';'+y1+';'+x2+';'+y2+"\n")
    
    csv.close()
    return



### PRELLIMINARY FUNCTIONS


def get_bounderies():
    """returns x_min,x_max,y_min,y_max, using link_dict. Does not work if coordinates are bigger than 10**9."""
    x_min=10000000000
    x_max=-10000000000
    y_min=10000000000
    y_max=-10000000000
    for link in link_dict:
        if float(link_dict[link][0])<x_min:
            x_min=float(link_dict[link][0])
        if float(link_dict[link][0])>x_max:
            x_max=float(link_dict[link][0])
            
        if float(link_dict[link][2])<x_min:
            x_min=float(link_dict[link][2])
        if float(link_dict[link][2])>x_max:
            x_max=float(link_dict[link][2])

        if float(link_dict[link][1])<y_min:
            y_min=float(link_dict[link][1])
        if float(link_dict[link][1])>y_max:
            y_max=float(link_dict[link][1])
        
        if float(link_dict[link][3])<y_min:
            y_min=float(link_dict[link][3])
        if float(link_dict[link][3])>y_max:
            y_max=float(link_dict[link][3])
    
    return x_min-1,x_max+1,y_min-1,y_max+1
       



### SURFACIC EMISSIONS
    
def create_surfacic_emissions(hour):
    """Returns a matrix with the surfacic emissions in each square. Time here is fixed."""
    
    division = 10 #we are going to cut the lineic emissions into ponctual emissions. Each line is divided into division part

    #Cutting the city into small squares
    dx = (x_max-x_min)/resolution
    dy = (y_max-y_min)/resolution
    
    #Density matrix
    surfacic_emissions=[]
    for pol in pollutant:
        surfacic_emissions.append(np.zeros((resolution,resolution)))

    for link in link_dict:
        
        #Coordinates of the beginning and the end of the link
        x1,x2=float(link_dict[link][0]),float(link_dict[link][2])
        y1,y2=float(link_dict[link][1]),float(link_dict[link][3])        
        
        #if it's outside the center of the map, we count it as surfacic
        if not ( (x_min_box <= x1 <= x_max_box and y_min_box <= y1 <= y_max_box) or (x_min_box <= x2 <= x_max_box and y_min_box <= y2 <= y_max_box)):
            if link in emissions[hour]: #if there are emissions :
                for i in range(division):
                    x = x1 + (x2-x1)*i/(division-1)
                    y = y1 + (y2-y1)*i/(division-1)
                    for p in range(len(pollutant)):
                        surfacic_emissions[p][int((x-x_min)//dx),int((y-y_min)//dy)] += emissions[hour][link][pollutant[p]]/division

    return surfacic_emissions

def create_csv_surfacic():
    """This creates the CSV file used in ARIA to give for each hour and for each surface the amount of pollutant emitted. """
    f = open(output_file, "w")
    
    f.write("SRCEID;DATEDEB;DATEFIN")
    for pol in pollutant:
        f.write(";Q_"+pol)
    f.write("\n")
    
    for hour in range(24):
        surfacic_emissions = create_surfacic_emissions(str(hour))
        
        for i in range(len(surfacic_emissions[0])):
            for j in range(len(surfacic_emissions[0][0])):
                positive=False
                for p in range(len(pollutant)):
                    if surfacic_emissions[p][i][j]>0:
                        positive=True
                        break
                if positive:
                    f.write(str(i+1000*j)+";"+date+time_format(hour*3600)+";"+date+time_format((hour+1)*3600))
                    for p in range(len(pollutant)):
                        f.write(";"+str(surfacic_emissions[p][i][j]))
                    f.write("\n")
    f.close()
    return

def create_surface_network():
    """this creates the file used in ARIA to define where are the surfacic emissions taking place : it links IDs to coordinates. The only parameters here are x_min,x_may,y_min,y_max, and the resolution ; it does not depend on the emissions."""
    new = []
    first_line="SRCEID;IDADM1;IDADM2;NAMADM;NAMGP1;NAMGP2;NAMGP3;IDCLA1;IDCLA2;IDCLA3;IDCLA4;IDCLA5;IDPROJ;SHIFTX;ORIGX;ORIGY;IDZH;X1;Y1;X2;Y2;X3;Y3;X4;Y4;DZ;ENVOL;SPEEDX;SPEEDY;SPEEDZ"
    for pol in pollutant:
        first_line += ";IDUNIT_"+pol+";Q_"+pol

    new.append(first_line)
        
    for i in range(resolution):
        for j in range(resolution):
            x_left = x_min + i*amplitude_x/resolution
            y_up = y_min + (j+1)*amplitude_y/resolution
            
            line = str(i+1000*j)
            line += ";-999;-999;NULL;STEP;NULL;"
            line += str(i+1000*j)
            line += ";-999;-999;-999;-999;-999;31;0;0;0;1;"
            line += str(x_left)+";"+str(y_up-amplitude_y/resolution)+";"
            line += str(x_left+amplitude_x/resolution)+";"+str(y_up-amplitude_y/resolution)+";"
            line += str(x_left+amplitude_x/resolution)+";"+str(y_up)+";"
            line += str(x_left)+";"+str(y_up)+";"            
            line += "0;0;0;0;0" 
            for pol in pollutant:
                line += ";3;0"#the 3 corresponds to units, here in kg/hour
            new.append(line)
    
    f= open(surface_network,"w")
    for line in new:
        f.write(line+'\n')
    f.close()


def graph(hour, pol, interpolation = True):
    """Draws the emissions generated at a given hour. By default, data is interpolated. """
    
    surfacic_emissions=create_surfacic_emissions(hour)[pol]
    l=len(surfacic_emissions[0])
    
    Z=list()
    for i in range(l):
        Z.insert(0,[])
        for j in range(l):
            Z[0].append(surfacic_emissions[j][i])
    
    f, ax = plt.subplots()
    ax.set_title('emissions')
    if interpolation:
        ax.imshow(Z,interpolation='bilinear',extent = (x_min,x_max,y_min,y_max))
    else:
        ax.imshow(Z,interpolation='none',extent = (x_min,x_max,y_min,y_max))
        
    plt.show()
    return

### LINEIC EMISSIONS

def create_csv_lineic():
    """This creates the CSV file used in ARIA to give for each hour and for each surface the amount of pollutant emitted. """
    f = open(output_file_center, "w")
    
    f.write("SRCEID;DATEDEB;DATEFIN")
    for pol in pollutant:
        f.write(";Q_"+pol)
    f.write("\n")
    
    for hour in range(24):
        for link in emissions[str(hour)]:
            x1,y1,x2,y2 = link_dict[link]
            #if it's outside the center of the map, we count it as surfacic
            if (x_min_box <= float(x1) <= x_max_box and y_min_box <= float(y1) <= y_max_box) or (x_min_box <= float(x2) <= x_max_box and y_min_box <= float(y2) <= y_max_box):
                f.write(ids[link]+";"+date+time_format(hour*3600)+";"+date+time_format((hour+1)*3600))
                for pol in pollutant:
                    f.write(";"+str(emissions[str(hour)][link][pol]))
                f.write("\n")

    f.close()
    return

def create_lineic_network():
    """
    In output, it creates a csv compatible with Aria. In particular, it fills all useless columns in our case.
    It does not depend on the emissions and can be run once and for all as long as the network is not changed.
    Finally, it is in this file that we settle the units and pollutants we study.
    """
    
    new = []
    first_line="SRCEID;IDADM1;IDADM2;NAMADM;NAMGP1;NAMGP2;NAMGP3;IDCLA1;IDCLA2;IDCLA3;IDCLA4;IDCLA5;IDPROJ;SHIFTX;ORIGX;ORIGY;IDZH;X1;Y1;ZH1;X2;Y2;ZH2;SLOPE;WIDTH;IDCANYON;SPEEDX;SPEEDY;SPEEDZ"
    for pol in pollutant:
        first_line += ";IDUNIT_"+pol+";Q_"+pol
    new.append(first_line)
    
    for link in link_dict:
        x1=link_dict[link][0]
        y1=link_dict[link][1]
        x2=link_dict[link][2]
        y2=link_dict[link][3]
        
        if (x_min_box <= float(x1) <= x_max_box and y_min_box <= float(y1) <= y_max_box) or (x_min_box <= float(x2) <= x_max_box and y_min_box <= float(y2) <= y_max_box):
            
            line = ids[link]
            line += ";-999;-999;"
            line += link[:8]
            line += ";route;null;null;-999;-999;-999;-999;-999;31;0;0;0;1;"
            line += str(round(float(x1)))+";"+str(round(float(y1)))
            line += ";0;"
            line += str(round(float(x2)))+";"+str(round(float(y2)))
            line += ";0;-999;-999;-1;0;0;0" #the 3 corresponds to units, here in kg/hour
            for pol in pollutant:
                line += ";3;0"#the 3 corresponds to units, here in kg/hour

            new.append(line)
    
    f= open(lineic_network,"w")
    for line in new:
        f.write(line+'\n')
    f.close()
    

### RUN


#formatting data to simplify the following
print("processing input data ...")
emissions = emissions_to_dict(pollutant)
roads, link_dict = map_to_dict()
ids = new_id(link_dict)

x_min,x_max,y_min,y_max=get_bounderies()
amplitude_x = x_max-x_min
amplitude_y = y_max-y_min 

#to be set properly
x_min_box = x_min + amplitude_x/3
x_max_box = x_min + 2*amplitude_x/3
y_min_box = y_min + amplitude_y/3
y_max_box = y_min + 2*amplitude_y/3


#visualization of results
#trace_agregate_data(emissions)
#image_output(roads)
#graph("8")

#writing output files
print("writing output files ...")
#emissions_to_csv()
map_to_csv()

create_csv_surfacic()
create_surface_network()

create_lineic_network()
create_csv_lineic()

print("Done !")
