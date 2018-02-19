import matplotlib.pyplot as plt

###CONFIG

#inputs
file = "Documents/exemples de formats/10.events2.xml"
mapfile = "Documents/exemples de formats/network.xml"
pollutant = "PM"

#outputs
emissions_file = "Documents/emissions.csv"
map_csv_file = "Documents/map.csv"

date = "01/01/2018 " #written in the emissions csv file. Needs to correspond to the date used for the ARIA simulation.

###PRELEMINARY FUNCTIONS

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
    s = s.replace("entered link", "entred_link")
        
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
    try:
        return int(s)
    except ValueError:
        return float(s)

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
            PM = float(event["PM"])
            time = int(float(event["time"]))//3600
            if link in emissions[str(time)]:
                emissions[str(time)][link]+=PM
            else :
                emissions[str(time)][link]=PM
    
    return emissions

def agregate_data(emissions):
    """ returns a dictionnary containing, for each hour, the emissions aggregated spatially"""
    agregate = dict()
    for hour in emissions:
        tot_em=0
        for link in emissions[hour] :
            tot_em+=emissions[hour][link]
        agregate[hour]=tot_em
    return agregate

def trace_agregate_data(emissions):
    """ plots the spatially-aggregated emissions data over time"""
    agreg_data=agregate_data(emissions)
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
        link_dict[l2[1]]=[l2[3],l2[5]]
        
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
    csv.write("SRCEID;DATEDEB;DATEFIN;Q_PM10\n")
    for hour in range(24):
        if str(hour) in emissions.keys():
            for link in emissions[str(hour)]:
                linkid = num(link)
                datedeb = date + time_format(hour*3600)
                datefin = date + time_format((hour+1)*3600)
                em = round(emissions[str(hour)][link],5)
                csv.write(str(linkid)+';'+datedeb+';'+datefin+';'+str(em)+"\n")
    
    csv.close()
    return

###MAP TO CSV

def map_to_csv():
    """this function creates (or overwrites) the map csv file, which contains the column id, x1, y1, x2, y2, all of type int"""
    csv = open(map_csv_file, "w")
    
    csv.write("id1;x1;y1;x2;y2\n")
    for link in link_dict:
        linkid = link
        x1=link_dict[link][0]
        y1=link_dict[link][1]
        x2=link_dict[link][2]
        y2=link_dict[link][3]
        csv.write(str(linkid)+';'+x1+';'+y1+';'+x2+';'+y2+"\n")
    
    csv.close()
    return

### RUN

emissions = emissions_to_dict(pollutant)
#trace_agregate_data(emissions)
roads, link_dict = map_to_dict()
#image_output(roads)
emissions_to_csv()
map_to_csv()
