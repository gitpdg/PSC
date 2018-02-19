import matplotlib.pyplot as plt
import matplotlib.patches as patches

###CONFIG

#Define the file of the concentration (ARIA output), 
#and the distance (in 100m ?) x and y between two sensors

file = "Documents/exemples de formats/concentrations.csv"
dx=2
dy=2

##READ EVENTS

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

    nb_receptors = (len(header)-6)//3 #the 6 comes from the first columns of the concentration file. IS THIS DEPENDING ON THE WEATHER INPUT FOR ARIA ? The 3 comes from the fact that there are 3 columns for each sensor (concentration, dry and wet deposition)
    
    receptor_list=list()
    for i in range(nb_receptors):
        receptor_list.append(header[6+3*i])
    
    #Dict containing concentrations for each hour and 
    concentrations = dict()
    
    for hour in range(nb_events):
        event = source.readline()
        event = event.split(";")
        time = event[1] 
        concentrations[time]=dict()
        for i in range(nb_receptors):
            concentrations[time][receptor_list[i]]=find_undef(num(event[6+3*i]))
    
    source.close()
    
    print("Done !")
    
    return concentrations
       
###IMAGE OUTPUT


def color_code(x):
    """ Color code for image output, dividing into 8 categories"""
    limits=[5,7.5,10,13,15,18,20]
    
    if x > limits[6]:
        return 'red'
    if x > limits[5]:
        return 'orangered'
    if x > limits[4]:
        return 'coral'
    if x > limits[3]:
        return 'darkorange'
    if x > limits[2]:
        return 'orange'
    if x > limits[1]:
        return 'goldenrod'
    if x > limits[0]:
        return 'khaki'
    return 'green'


def image_output(concentrations):
    """ Saves images for each hour of the day. The input is the concentration dictionnary. """
    
    print("Creating images...")
    
    image=0
    
    for hour in concentrations :
        image=image+1
        
        event=concentrations[hour]
        
        fig = plt.figure()
        ax = fig.add_subplot(111, aspect='equal')
        ax.set_xlim([-10, 10])
        ax.set_ylim([-10, 10])
        
        
        for zone in event:
            x=num(zone.split("_")[1])
            y=num(zone.split("_")[2])
            conc=event[zone]
            ax.add_patch(patches.Rectangle((x-dx/2, y-dy/2), dx, dy,facecolor=color_code(conc)))
        
        fig.savefig('image'+str(image)+'.png', dpi=90, bbox_inches='tight')
        plt.close()

       
        print("Image n°"+str(image)+" created.")
    
    print("Done !")
        
    return 


### RUN

concentrations = file_to_dict()  
image_output(concentrations)
