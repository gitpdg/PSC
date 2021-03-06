"""
This program processes ARIA's output, in order to get visualisations and a cost analysis.
It is divided like this :
    - config
    - preliminary functions
    - reading the concentration file
    - image output
    - calculating the costs
    - run
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

###CONFIG

#input
file = "Documents/base_case/output/new-recept.csv" #this is an ARIA output
listing = "Documents/base_case/output/scratch.txt" #this is an ARIA output
#the distance (in km) x and y between two sensors
dx=1.3
dy=1.3

#output
mean_file = "Documents/base_case/output/mean_file.txt"

##PRELEMINARY FUNCTIONS

def file_len(fname):
    """ returns the number of lines in the file as an int"""
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def num(s):
    """Converts string to number"""
    try:
        return int(s)
    except ValueError:
        return float(s)

def find_undef(x):
    """Returns 0 if undefined value (ARIA's undefined value is -999), otherwise returns the input value"""
    if x==-999:
        return 0
    return x

###READING THE CONCENTRATION FILE

def file_to_dict(): 
    """ returns a dictionnary of the concentrations, whose keys are the hour (example format : '01/01/2018  01:00:00'), and whose value is itself a dictionnary, whose keys are the sensors id, and whose associated value is the concentration at this point. """
    
    print("Extracting concentrations from file...")

    nb_events=file_len(file)-1
    
    source = open(file, "r")
    
    header = source.readline()
    header=header.split(";")

    nb_receptors = (len(header)-6)//3 #the 6 comes from the first columns of the concentration file. The 3 comes from the fact that there are 3 columns for each sensor (concentration, dry and wet deposition)
    
    receptor_list=list()
    for i in range(nb_receptors):
        receptor_list.append(header[6+3*i])
    
    #Dict containing concentrations for each hour and 
    concentrations = dict()
    
    for h in range(nb_events):
        event = source.readline()
        event = event.split(";")
        time = event[1]
        pol = event[0]
        if pol not in concentrations.keys():
            concentrations[pol]=dict()
        concentrations[pol][time]=dict()
        for i in range(nb_receptors):
            concentrations[pol][time][receptor_list[i]]=find_undef(num(event[6+3*i]))
    
    source.close()
    
    print("Done !")
    
    return concentrations
       
###IMAGE OUTPUT


def color_code(x):
    """ Color code for image output, dividing into 8 categories"""
    limits=[1,2,3,4,5,6,7]
    factor = 0.0001
    
    if x > factor*limits[6]:
        return 'red'
    if x > factor*limits[5]:
        return 'orangered'
    if x > factor*limits[4]:
        return 'coral'
    if x > factor*limits[3]:
        return 'darkorange'
    if x > factor*limits[2]:
        return 'orange'
    if x > factor*limits[1]:
        return 'goldenrod'
    if x > factor*limits[0]:
        return 'khaki'
    return 'green'


def image_output(concentrations, pol='PM'):
    """ Saves images for each hour of the day. The input is the concentration dictionnary. """
    
    print("Creating images...")
    
    image=0
    
    for hour in concentrations[pol] :
        image=image+1
        
        event=concentrations[pol][hour]
        
        fig = plt.figure()
        ax = fig.add_subplot(111, aspect='equal')
        ax.set_xlim([355, 367])
        ax.set_ylim([5471, 5483])
        
        
        for zone in event:
            x=num(zone.split("_")[1])/10+355
            y=num(zone.split("_")[2])/10+5471
            conc=event[zone]
            ax.add_patch(patches.Rectangle((x-dx/2, y-dy/2), dx, dy,facecolor=color_code(conc)))
        
        fig.savefig('Documents/image'+str(image)+'.png', dpi=90, bbox_inches='tight')
        plt.close()

       
        print("Image n°"+str(image)+" created.")
    
    print("Done !")
        
    return 

### CALCULATING THE COSTS

def mean_concentrations():
    """
    creates (or overwrites) the file mean_file, which contains the average concentration on each sensor. It gets that data from the file listing, which is a direct output of ARIA.
    """
    f= open (listing, "r")
    lines = f.readlines()
    f.close()
    
    f = open(mean_file,"w")
    i = lines.index(' CONCENTRATION EN MOYENNE ANNUELLE\n')
    j = lines.index(' DEPOTS SECS EN MOYENNE ANNUELLE\n')
    for k in range(i,j):
        f.write(lines[k])
    
    f.close()
    

### RUN

concentrations = file_to_dict()  
image_output(concentrations)
mean_concentrations()
