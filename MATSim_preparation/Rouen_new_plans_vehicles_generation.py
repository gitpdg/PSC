import random as rd
from math import exp
import matplotlib.pyplot as plt
import numpy as np
import math
import numpy.random as random

##PARAMETERS
print("Extracting map from file...")

#To be completed
mapfile = "/Users/meryembenmahdi/Documents/MATSIM/matsim-0.9.0/Rouen_new/input/sample_network.xml"

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
    link_dict[link] = node_dict[int(link_dict[link][0])]+node_dict[int(link_dict[link][1])]

#We generate the map

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

x_nodes = [num(node_dict[key][0]) for key in node_dict]
y_nodes = [num(node_dict[key][1]) for key in node_dict]

roads = list()
for link in link_dict:
    roads.append([link, [num(link_dict[link][0]),num(link_dict[link][2])],[num(link_dict[link][1]),num(link_dict[link][3])]])

print("Map in link_dict in the form [x1,y1,x2,y2].")


def parameters():
    
    keys=link_dict.keys()
    
    xmin,xmax,ymin,ymax=0,0,0,0
    
    for key in keys:
        
        xmin,xmax=float(link_dict[key][0]),float(link_dict[key][2])
        ymin,ymax=float(link_dict[key][1]),float(link_dict[key][3])
        break
    
    
    for road in link_dict:
        
        x1,x2=float(link_dict[road][0]),float(link_dict[road][2])
        y1,y2=float(link_dict[road][1]),float(link_dict[road][3])
        
        xmin=min([xmin,x1,x2])
        xmax=max([xmax,x1,x2])
        
        ymin=min([ymin,y1,y2])
        ymax=max([ymax,y1,y2])
    
    return xmin,xmax,ymin,ymax
    

#Map parameters
x_min,x_max,y_min,y_max=parameters()
amplitude_x = x_max-x_min
amplitude_y = y_max-y_min

#To be chosen
resolution = 100


# output
# paramètres
chemin_plans = "/Users/meryembenmahdi/Documents/MATSIM/matsim-0.9.0/Rouen_new/input/sample_population.xml"
chemin_vehicles = "/Users/meryembenmahdi/Documents/MATSIM/matsim-0.9.0/Rouen_new/input/sample_emissionVehicles_v2.xml"

#Full plan generation

### TRIP GENERATION

##DATA INPUT

#Total population of the model
pop = 500
#Number of person trips per day
td=3.79
#Total number of trips
Nt=int(pop*td)

#Distribution of trips by purpose
#For each pupose, we define a tuple containing the part of the total trips corresponding
#to taht purpose, an array of size containing a distribution of the trips for each   
#time of the day. For example, trip_purpose["work"][1][6] gives the percentage of people
#going to work that start their trip between 6 am and 7 am, the average lenght of the 
#activity in hours and its standard deviation in hours (exept for home)
trip_purpose={}
trip_purpose["work"]=(0.15,[0,0,0,0,0,0,0.1,0.2,0.3,0.2,0.1,0.1,0,0,0,0,0,0,0,0,0,0,0,0],8,1)
trip_purpose["home"]=(0.348,None,None,None)
trip_purpose["other"]=(0.502,[0,0,0,0,0,0,0,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0,0,0,0,0,0,0],2,1)

len_max_activity = max(len(cle) for cle in trip_purpose)

#We create cumulative distribution function for each purpose
start_time_cdf={}
for cle in trip_purpose:
    if cle!="home":
        start_time_cdf[cle]=[0]*24
        start_time_cdf[cle][0]=trip_purpose[cle][1][0]              
        for i in range(1,24):
            start_time_cdf[cle][i]=start_time_cdf[cle][i-1]+trip_purpose[cle][1][i]


##AUXILLIARY FUNCTIONS

def get_location(person):
    #To get the actual position of a person, according to his last trip
    if len(person) == 0: return "home"
    else : return person[-1][3]
    return

def shuffle_people(orig):
    #To shuffle a list of people
    dest = orig[:]
    random.shuffle(dest)
    return dest

def activity_start_time(location):
    if location == "home" : return None
    #We find the start hour according to the cumulative distribution functions
    #defined in the data input
    rand=random.random()
    i=0
    while start_time_cdf[location][i]<rand:
        i=i+1
    #The activity began during the time frame (ih, i+1h)
    return int(3600*i+random.random()*3600)

def activity_duration(location):
    #Finds a duration for an activity taking place at "location"
    if location == "home" : return None
    mean = trip_purpose[location][2]
    sd = trip_purpose[location][3]
    duration = random.normal(mean,sd)*3600
    while duration<0:
        duration = random.normal(mean,sd)*3600
    return int(duration)

def generate_trip(location):
    #Generates a trip to the specified location, and the lenght of the activity if it 
    #is not staying at home
    if location !="home":
        origin = None
        start_time = activity_start_time(location)
        duration = activity_duration(location)
        destination = location
        end_time = int(start_time+duration+1800) #We estimate to half an hour the trip duration
    return (origin, start_time, duration, destination, end_time)

def start_time(trip):
    return trip[1]

def end_time(trip):
    return trip[4]

def compatible(person, trip):
    #Tells whether a trip is compatible with a person's time schedule
    if len(person)==0:
        return True
    else:
        #May be the first trip of the day before every other trip
        if end_time(trip) < start_time(person[0]): return True
        #It could also be between two already planned trips
        for i in range(len(person)-1):
            if (start_time(trip)>end_time(person[i]) and 
                end_time(trip)<start_time(person[i+1])):
                return True
        #Finally, it can be the last trip of the day
        if start_time(trip)>end_time(person[-1]) : return True
    #If none of these options work, then the trip is not compatible with the person's 
    #schedule
    return False

def add_trip_to_schedule(trip,person):
    #Adds a trip to a person's schedule
    if compatible(person,trip)==False :
        print("You tried to add an uncompatible trip to someone's schedule !")
        return
    #We first find where we should add the trip
    if len(person)==0:
        pos=0
    else:
        #May be the first trip of the day before every other trip
        if end_time(trip) < start_time(person[0]): pos=0
        #It could also be between two already planned trips
        for i in range(len(person)-1):
            if (start_time(trip)>end_time(person[i]) and 
                end_time(trip)<start_time(person[i+1])):
                pos=i+1
        #Finally, it can be the last trip of the day
        if start_time(trip)>end_time(person[-1]) : pos=len(person)
    person.insert(pos,trip)
    destination = trip[3]
    trips_todo[destination]=trips_todo[destination]-1
    return

def send_home(person):
    #Sends home people at the end of the day, exept if they are already there!
    if len(person)==0 : return 
    trip_home=(None, end_time(person[-1])+600,1800,"home",end_time(person[-1])+2400)
    person.append(trip_home)
    trips_todo["home"]=trips_todo["home"]-1
    return

def fix_schedule(person):
    #When the origin of a trip isn't known, it is set at None. This function fixes this 
    #issue and verifies that a schedule is coherent.
    person2=[]
    for trip in person:
        person2.append([item for item in trip])
    person2[0][0]="home"
    for i in range(1,len(person2)):
        person2[i][0]=person2[i-1][3]
    person=[tuple(trip) for trip in person2]
    return person
    
def convert_time_from_seconds(time):
    time2=time
    hour = time2 // 3600
    hour = str(hour)
    if len(hour)==1: hour = "0"+hour
    time2 %= 3600
    minutes = time2 // 60
    minutes = str(minutes)
    if len(minutes)==1: minutes = "0"+minutes
    time2 %= 60
    seconds = time2
    seconds = str(seconds)
    if len(seconds)==1: seconds = "0"+seconds
    return("%s:%s:%s" % (hour, minutes, seconds))

def trips_to_string(person):
    if len(person)==0 :
        return "Stays at home"
    string=""
    for trip in person:
        origin = trip[0]
        start_time = trip[1]
        destination = trip[3]
        end_time = trip[4]
        string=string+(convert_time_from_seconds(start_time) + "   | "+ str(origin) + 
        " "*(len_max_activity-len(str(origin))) + " --> "  + str(destination) + 
        " "*(len_max_activity-len(str(destination))) + " | " + 
            convert_time_from_seconds(end_time)+ " \n")
    return string   

def print_pop_schedules():
    print("TRIP SCHEDULES \n")
    i=1
    for person in people:
        print("Person n°"+str(i))
        print("---------------------------------------------")
        print("trip start | trip            | activity ends")
        print(trips_to_string(person))
        i=i+1
    return  

##PLAN GENERATION

#We first define the number of trips for each purpose
trips_todo={}
for cle in trip_purpose:
    trips_todo[cle]=int(trip_purpose[cle][0]*Nt)
    
#We list all people in a an array which contains the trips of each individual in the
#population, in the form of tuples (start_time, origin, activity_duration, destination,
# end_time). All times are in seconds

people = list()
for i in range(pop):
    people.append([])

#We then allocate the trips

#First, we allocate all trips to work

while(trips_todo["work"]>0):
    trip=generate_trip("work")
    i=0
    person = people[i]
    while(i<pop-1):
        if compatible(person,trip):
            add_trip_to_schedule(trip,person)
        break
        i+i+1
        person = people[i]
    #If we end up here, the trip couldn't be assigned to a person. We shuffle
    #the list of people to randomize the trip allocation
    people=shuffle_people(people)

#Then, all other trips (expect 'home' trips)

while(trips_todo["other"]>0):
    trip=generate_trip("other")
    i=0
    person = people[i]
    while(i<pop-1):
        if compatible(person,trip):
            add_trip_to_schedule(trip,person)
        break
        i+i+1
        person = people[i]
    #If we end up here, the trip couldn't be assigned to a person. We shuffle
    #the list of people to randomize the trip allocation
    people=shuffle_people(people)

#Finally, we include all trips back to home
#Note : it is very important that all of the other trips be planned before
#adding trips to home to people's schedule

#We send people home at the end of the day
for person in people:
    send_home(person)

#At the end, we fix the schedules
for i in range(pop):
    people[i]=fix_schedule(people[i])

#print(people[0])

#print_pop_schedules()

###Plan generation
def f(x1,y1,x2,y2,x):
    
    """Calculates the image of a scalar by a function the graph of which is a line"""
    a=(y2-y1)/(x2-x1)
    return(a*(x-x1)+y1)
        
    
def surroundings(X,Y,x1,x2,y1,y2):
    
    """Returns the coordinates which surround x1,x2,y1,y2 in X and Y"""
    idown,iup = 0,0
    jdown,jup= 0,0
    ymin,ymax=min(y1,y2),max(y1,y2)
    
        
    while X[idown+1]<x1 and idown < resolution-2:
        idown+=1

    
    while x2 >= X[iup] and iup < resolution-2:
        iup+=1            
    
    
    while Y[jdown+1] < ymin and jdown < resolution-2:
        jdown+=1
    

    while ymax >= Y[jup] and jup < resolution-2:
        jup+=1

    return(idown,iup,jdown,jup)


    
    
def roaddensity():
    
    """Returns a matrix with the road density in each square"""
    
    
    #Cutting the city into small squares
    X = np.linspace(x_min,x_max,resolution)
    Y = np.linspace(y_min,y_max,resolution)
        
    
    #Density matrix
    road_density=np.zeros((resolution-1,resolution-1))

    
    for road in link_dict:
        
        #Visited squares matrix
        alreadyseen=np.zeros((resolution-1,resolution-1))

        #Coordinates of the beginning and the end of the road
        x1,x2=float(link_dict[road][0]),float(link_dict[road][2])
        y1,y2=float(link_dict[road][1]),float(link_dict[road][3])
        
        
        #Surroundigs
        idown,iup,jdown,jup=surroundings(X,Y,x1,x2,y1,y2)
    
        
        for i in range(idown+1,iup):
            x=X[i]
                            
            #Ordinate of the intersection point between the road and the verticle line (equation x=...)                        
            ord=f(x1,y1,x2,y2,x)

            for j in range(jdown,jup) :
                    
                    
                if ord >= Y[j] and ord<=Y[j+1]:
                    
                    if alreadyseen[resolution-2-j][i]==0:
                        road_density[resolution-2-j][i]+=1
                        alreadyseen[resolution-2-j][i]=1
                                
                    
                    if alreadyseen[resolution-2-j][i-1]==0:
                        road_density[resolution-2-j][i-1]+=1
                        alreadyseen[resolution-2-j][i-1]=1
        
        
        
        for j in range(jdown+1,jup):
            y=Y[j]
            
            #Abscissa of the intersection point between the road and the horizontal line (equation y=...)
            absc=f(y1,x1,y2,x2,y)
            
            for i in range(idown,iup):
                
                if absc >= X[i] and absc <= X[i+1]:
                    
                    if alreadyseen[resolution-2-j][i]==0:
                        road_density[resolution-2-j][i]+=1
                        alreadyseen[resolution-2-j][i]=1
                                
                    
                    if alreadyseen[resolution-2-j+1][i]==0:
                        road_density[resolution-2-j+1][i]+=1
                        alreadyseen[resolution-2-j+1][i]=1
        
        

    #Final road_density
    somme = 0
    for i in range(resolution-1):
        for j in range(resolution-1):
            somme+=road_density[i][j]
            
    for i in range(resolution-1):
        for j in range(resolution-1):
            road_density[i][j]=road_density[i][j]/somme
        
    
    
    return road_density


def roadtopop(x):
    
    """Choses the function that links road density to population density"""
    return (28*x**2)



#Population density
def popdensity():
    
    """Calculates the matrix of population density with the road density"""
    road_density=roaddensity()
    
    l=len(road_density[0])
    
    pop_density=np.zeros((l,l))
    
    maxdensity=0

    for i in range(l):
        for j in range(l):
            pop_density[i][j]=roadtopop(road_density[i][j])
            maxdensity=max(maxdensity,pop_density[i][j])
    
    for i in range(l):
        for j in range(l):
            pop_density[i][j]/=maxdensity
    
    return(pop_density)




#Densities of work, population and shopping
pop_density=popdensity()

def dpop(x,y):
    '''Returns the population density in point (x,y)'''
    
    #Cutting the city into small squares
    X = np.linspace(x_min,x_max,resolution)
    Y = np.linspace(y_min,y_max,resolution)
    
    #Determines the square where the point (x,y) is
    i,j=0,0
            
    while X[i+1]<x and i < resolution-2:
        i+=1            

    while Y[j+1] < y and j < resolution-2:
        j+=1

    return(pop_density[resolution-2-j][i])
    
    
    
shopsfile="/Users/paguyomar/Desktop/Densités/shops_final.txt"
source = open(shopsfile,"r")
    
     
#We get the content of the file
s = source.readlines()
for i in range(len(s)):
    s[i]=s[i].split(",")
    s[i][2]=s[i][2][:-1]
    

resolution3=50

def shop_density():
    
    #Cutting the city into small squares
    X = np.linspace(x_min,x_max,resolution3)
    Y = np.linspace(y_min,y_max,resolution3)
    
    shopdensity=np.zeros((resolution3-1,resolution3-1))


    for shop in s:
        x,y=float(shop[1]),float(shop[2])
    
        #Determines the square where the point (x,y) is
        i,j=0,0
                
        while X[i+1]<x and i < resolution3-2:
            i+=1            
        
        
        while Y[j+1] < y and j < resolution3-2:
            j+=1
        
        shopdensity[resolution3-2-j][i]+=1
        
        
    somme = 0
    for i in range(resolution3-1):
        for j in range(resolution3-1):
            somme+=shopdensity[i][j]
            
    for i in range(resolution3-1):
        for j in range(resolution3-1):
            shopdensity[i][j]=shopdensity[i][j]/somme
    
    
    maxdensity=0

    for i in range(resolution3-1):
        for j in range(resolution3-1):
            maxdensity=max(maxdensity,shopdensity[i][j])
    
    for i in range(resolution3-1):
        for j in range(resolution3-1):
            shopdensity[i][j]/=maxdensity
    
        
    return(shopdensity)
    


shopdensity=shop_density()


def dshop(x,y):
    
    '''Returns the shop density in point (x,y)'''
    
    #Cutting the city into small squares
    X = np.linspace(x_min,x_max,resolution3)
    Y = np.linspace(y_min,y_max,resolution3)
    
    
    #Determines the square where the point (x,y) is
    i,j=0,0
            
            
    while X[i+1]<x and i < resolution3-2:
        i+=1            
    
    
    while Y[j+1] < y and j < resolution3-2:
        j+=1


    return(shopdensity[resolution3-2-j][i])
    


officefile="/Users/paguyomar/Desktop/Densités/offices_final.txt"
source = open(officefile,"r")
    
     
#We get the content of the file
s2 = source.readlines()
for i in range(len(s2)):
    s2[i]=s2[i].split(",")
    s2[i][2]=s2[i][2][:-1]
    


def office_density():
    
    #Cutting the city into small squares
    X = np.linspace(x_min,x_max,resolution3)
    Y = np.linspace(y_min,y_max,resolution3)
    
    officedensity=np.zeros((resolution3-1,resolution3-1))


    for office in s2:
        x,y=float(office[1]),float(office[2])
    
        #Determines the square where the point (x,y) is
        i,j=0,0
                
        while X[i+1]<x and i < resolution3-2:
            i+=1            
        
        
        while Y[j+1] < y and j < resolution3-2:
            j+=1
        
        officedensity[resolution3-2-j][i]+=1
    
        
    for i in range(resolution3-1):
        for j in range(resolution3-1):
            officedensity[i][j]=10*officedensity[i][j]+shopdensity[i][j]
            
        
    somme = 0
    for i in range(resolution3-1):
        for j in range(resolution3-1):
            somme+=officedensity[i][j]
            
    for i in range(resolution3-1):
        for j in range(resolution3-1):
            shopdensity[i][j]=officedensity[i][j]/somme
        
    
    
    maxdensity=0

    for i in range(resolution3-1):
        for j in range(resolution3-1):
            maxdensity=max(maxdensity,officedensity[i][j])
    
    for i in range(resolution3-1):
        for j in range(resolution3-1):
            officedensity[i][j]/=maxdensity
    
    return(officedensity)
    
    
  
officedensity=office_density()
  

def dwork(x,y):
    
    '''Returns the shop density in point (x,y)'''
    
    #Cutting the city into small squares
    X = np.linspace(x_min,x_max,resolution3)
    Y = np.linspace(y_min,y_max,resolution3)
    
    
    
    #Determines the square where the point (x,y) is
    i,j=0,0
            
            
    while X[i+1]<x and i < resolution3-2:
        i+=1            
    
    
    while Y[j+1] < y and j < resolution3-2:
        j+=1


    return(officedensity[resolution3-2-j][i])



#Graphic output
def density_graphs():
    resolution2 = 50

    X = np.linspace(x_min,x_max,resolution2)
    Y = np.linspace(y_min,y_max,resolution2)
    

    Z=list()
    for y in Y:
        Z.insert(0,[])
        for x in X:
            Z[0].append(dpop(x,y))
    
    f, ax = plt.subplots()
    ax.set_title('Population density')
    ax.imshow(Z,interpolation='bilinear',extent = (x_min,x_max,y_min,y_max))
    

    Z=list()
    for y in Y:
        Z.insert(0,[])
        for x in X:
            Z[0].append(dwork(x,y))
            
    f, ax = plt.subplots()
    ax.set_title('Work density')
    ax.imshow(Z,interpolation='none',extent = (x_min,x_max,y_min,y_max))
    
    
    Z=list()
    for y in Y:
        Z.insert(0,[])
        for x in X:
            Z[0].append(dshop(x,y))
            
    f, ax = plt.subplots()
    ax.set_title('Shopping and leisure density')
    ax.imshow(Z,interpolation='none',extent = (x_min,x_max,y_min,y_max))
    
    plt.show()
    return



####


def creation_plans_vehicles():
    
    f1 = open(chemin_plans, "w")
    f1.write('<?xml version="1.0" ?>\n')
    f1.write('<!DOCTYPE plans SYSTEM "http://www.matsim.org/files/dtd/plans_v4.dtd">\n\n')    
    f1.write('<plans>\n\n')
    
    
    
    f2 = open(chemin_vehicles, "w")
    
    f2.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\n")
    
    f2.write('<vehicleDefinitions xmlns="http://www.matsim.org/files/dtd"\n')
    f2.write(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
    f2.write(' xsi:schemaLocation="http://www.matsim.org/files/dtd http://www.matsim.org/files/dtd/vehicleDefinitions_v1.0.xsd">\n')
    f2.write('	<vehicleType id="car_average">\n')
    f2.write('		<description>\n')
    f2.write('			BEGIN_EMISSIONSPASSENGER_CAR;average;average;averageEND_EMISSIONS\n')
    f2.write('		</description>\n')
    f2.write('		<length meter="7.5"/>\n')
    f2.write('		<width meter="1.0"/>\n\n')
    
    f2.write('		<accessTime secondsPerPerson="1.0"/>\n')
    f2.write('		<egressTime secondsPerPerson="1.0"/>\n')
    f2.write('		<doorOperation mode="serial"/>\n')
    f2.write('	</vehicleType>\n')
    f2.write('	<vehicleType id="car_petrol">\n')
    f2.write('		<description>\n')
    f2.write('			BEGIN_EMISSIONSPASSENGER_CAR;petrol (4S);&gt;=2L;PC-P-Euro-1END_EMISSIONS\n')
    f2.write('		</description>\n')
    f2.write('		<length meter="7.5"/>\n')
    f2.write('		<width meter="1.0"/>\n\n')
    
    f2.write('		<accessTime secondsPerPerson="1.0"/>\n')
    f2.write('		<egressTime secondsPerPerson="1.0"/>\n')
    f2.write('		<doorOperation mode="serial"/>\n')
    f2.write('	</vehicleType>\n')
    f2.write('	<vehicleType id="car_diesel">\n')
    f2.write('		<description>\n')
    f2.write('			BEGIN_EMISSIONSPASSENGER_CAR;diesel;&lt;1,4L;PC-D-Euro-3END_EMISSIONS\n')
    f2.write('		</description>\n')
    f2.write('		<length meter="7.5"/>\n')
    f2.write('		<width meter="1.0"/>\n\n')
    		
    f2.write('		<accessTime secondsPerPerson="1.0"/>\n')
    f2.write('		<egressTime secondsPerPerson="1.0"/>\n')
    f2.write('		<doorOperation mode="serial"/>\n')
    f2.write('	</vehicleType>\n')
   
    f2.write('	<vehicleType id="bicycle">\n')
    f2.write('		<description>\n')
    f2.write('			BEGIN_EMISSIONSZERO_EMISSION_VEHICLE;average;average;averageEND_EMISSIONS\n')
    f2.write('		</description>\n')
    f2.write('		<length meter="2.0"/>\n')
    f2.write('		<width meter="1.0"/>\n\n')
    		
    f2.write('		<accessTime secondsPerPerson="1.0"/>\n')
    f2.write('		<egressTime secondsPerPerson="1.0"/>\n')
    f2.write('		<doorOperation mode="serial"/>\n')
    f2.write("	</vehicleType>\n\n")

    
    for i in range(pop) :
        
        legmode = leg_mode()
        vehicle = legmode
        if (legmode == '\"car\"') :
            vehicle = car_type()
            
        
        plan = people[i]
        f2.write("       <vehicle id=\""+ str(i) +"\" type=" + vehicle + "/>\n")
        
        # génération des lieux et horaires
        x_home, y_home = choix_spatial(dpop)
        x_work, y_work = choix_spatial(dwork)
        
        first_act_start_time = plan[0][1]
        last_act_start_time = plan[-1][4]
        
        l=[]
        l.append('<person id="'+str(i)+'">')
        l.append('      <plan>')
        #On fait le premier trajet de la journée
        l.append('           <act type="home" x="'+ str(x_home) +'" y="'+ str(y_home)+ '" start_time="00:00:00" end_time="'+ time_format(first_act_start_time) +'" />')
        l.append("           <leg mode=" + legmode + "/>\n")
        for i in range(len(plan)-1):
            dest=plan[i][3]
            if dest=='work':
                l.append('           <act type="work" x="'+ str(x_work) +'" y="'+ str(y_work)+ '" start_time="'+ time_format(plan[i][1]) +'" dur="'+ time_format(plan[i][2]) +'" />')
                l.append("           <leg mode=" + legmode + "/>\n")
            if dest=='home':
                l.append('           <act type="home" x="'+ str(x_home) +'" y="'+ str(y_home)+ '" start_time="'+ time_format(plan[i][1]) +'" dur="'+ time_format(plan[i][2]) +'" />')
                l.append("           <leg mode=" + legmode + "/>\n")
            if dest=='other':
                x_other, y_other = choix_spatial(dshop)
                l.append('           <act type="other" x="'+ str(x_other) +'" y="'+ str(y_other)+ '" start_time="'+ time_format(plan[i][1]) +'" dur="'+ time_format(plan[i][2]) +'" />')
                l.append("           <leg mode=" + legmode + "/>\n")
           
        #Retour à la maison
        l.append('           <act type="home" x="'+ str(x_home) +'" y="'+ str(y_home)+ '" start_time="'+ time_format(last_act_start_time) +'" />')
        l.append('      </plan>')
        l.append('</person>')
        f1.write("\n".join(l)+"\n")
        
    
    f1.write('\n</plans>')
    f1.close()
    f2.write("</vehicleDefinitions>")   
    f2.close()
    




def dpoptoy(x,y):
    """ définie sur [-1000,1000]^2, de norme infinie inférieure à 1"""
    return (exp(-((x/1000)**2+(y/1000)**2)))

def dworktoy(x,y):
    """ définie sur [-1000,1000]^2, de norme infinie inférieure à 1"""
    return (exp(-((x/1000)**2+(y/1000)**2)))
        
def choix_spatial(fonction):
    """ détermine un choix de x,y selon la méthode du rejet """
    acceptable = False
    while (not acceptable):
        x = x_min + rd.random()*amplitude_x
        y = y_min + rd.random()*amplitude_y
        t = rd.random()
        acceptable = (fonction(x,y)>t)
    return (round(x),round(y))

def time_format(secondes):
    """ takes a time entry as a float number of seconds and returns a string "hh:mm:ss" """
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

def car_type():
    rand=random.randint(1,4)
    if (rand == 1 ) : return("\"car_average\"")
    if (rand == 2 ) : return("\"car_petrol\"")
    if (rand == 3 ) : return("\"car_diesel\"")  

    
    
def leg_mode() :
    rand=random.randint(1,3)
    if (rand == 1 ) : return("\"car\"")
    if (rand == 2 ) : return("\"bicycle\"")

creation_plans_vehicles()