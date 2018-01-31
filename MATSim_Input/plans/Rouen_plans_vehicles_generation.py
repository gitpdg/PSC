#Full plan generation

### TRIP GENERATION

import numpy.random as random

##DATA INPUT

#Total population of the model
pop = 50
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

import xml.etree.cElementTree as ET
import random as rd
from math import exp

###


import matplotlib.pyplot as plt
import numpy as np
import math

#Map parameters
x_min=115773.70644643574
x_max=127570.76721935476
y_min=6345748.662700792
y_max=6353071.566158524
amplitude_x = x_max-x_min
amplitude_y = y_max-y_min

#A gaussian peak in one point centered in 'center' (list of size 2 containing the x_center,y_center coordinates of the center), the function is evalutated in coordinates x,y
def peaked_function(x,y,center):
    return center[2]*math.exp(-(2*(x-center[0])/amplitude_x)**2-(2*(y-center[1])/amplitude_y)**2)

#Same, but with mutltiple peaks defined in the list center_tab
def multiple_peaked_fonction(x,y,center_tab):
    tab = list()
    for center in center_tab:
        tab.append(peaked_function(x,y,center))
    m = tab[0]
    for i in range(len(tab)):
        if tab[i]>m:
            m=tab[i]
    return m

#Densities of work, population and shopping
def dpop(x,y):
    #Here we define the coordinates of the peaks, as well as the importance of each peak
    center_tab=[[125739,6347320,0.8],[119700,6346460,0.9],[122362,6351340,1]]
    return multiple_peaked_fonction(x,y,center_tab)

def dwork(x,y):
    center_tab=[[124074,6351960,0.80],[120126,6347260,1]]
    return multiple_peaked_fonction(x,y,center_tab)

def dshop(x,y):
    center_tab=[[121363,6351720,0.8],[125097,6349770,0.65],[119603,6347250,0.7]]
    return multiple_peaked_fonction(x,y,center_tab)

#Graphic output
def density_graphs():
    resolution = 25  

    Y = np.linspace(y_min,y_max,resolution)
    X = np.linspace(x_min,x_max,resolution)
    
    # Z=list()
    # for j in Y:
    #     Z.insert(0,[])
    #     for i in X:
    #         Z[0].append(dpop(i,j))
    # 
    # f, ax = plt.subplots()
    # ax.set_title('Population density')
    # ax.imshow(Z,interpolation='none',extent = (x_min,x_max,y_min,y_max))
    # 
    
    Z=list()
    for j in Y:
        Z.insert(0,[])
        for i in X:
            Z[0].append(dwork(i,j))
            
    f, ax = plt.subplots()
    ax.set_title('Work density')
    ax.imshow(Z,interpolation='none',extent = (x_min,x_max,y_min,y_max))
    
    # Z=list()
    # for j in Y:
    #     Z.insert(0,[])
    #     for i in X:
    #         Z[0].append(dshop(i,j))
    #         
    # f, ax = plt.subplots()
    # ax.set_title('Shopping and leisure density')
    # ax.imshow(Z,interpolation='none',extent = (x_min,x_max,y_min,y_max))
    # 
    plt.show()
    return
    
#density_graphs()


####


# paramètres
chemin_plans = "/Users/meryembenmahdi/Desktop/plans.xml"
chemin_vehicles = "/Users/meryembenmahdi/Desktop/vehicles.xml"

def creation_plans():
    
    f = open(chemin_plans, "w")
    f.write('<?xml version="1.0" ?>\n')
    f.write('<!DOCTYPE plans SYSTEM "http://www.matsim.org/files/dtd/plans_v4.dtd">\n\n')    
    f.write('<plans>\n\n')
    
    for i in range(pop) :
        
        plan = people[i]
        
        # génération des lieux et horaires
        x_home, y_home = choix_spatial(dpop)
        x_work, y_work = choix_spatial(dwork)
        
        first_act_start_time = plan[0][1]
        last_act_start_time = plan[-1][4]
        
        l=[]
        l.append('<person id="'+str(i)+'">')
        l.append('      <plan>')
        #On fait le premier trajet de la journée
        l.append('           <act type="h" x="'+ str(x_home) +'" y="'+ str(y_home)+ '" start_time="00:00:00" end_time="'+ time_format(first_act_start_time) +'" />')
        l.append('           <leg mode="car" />')
        for i in range(len(plan)-1):
            dest=plan[i][3]
            if dest=='work':
                l.append('           <act type="w" x="'+ str(x_work) +'" y="'+ str(y_work)+ '" start_time="'+ time_format(plan[i][1]) +'" dur="'+ time_format(plan[i][2]) +'" />')
                l.append('           <leg mode="car" />')
            if dest=='home':
                l.append('           <act type="h" x="'+ str(x_home) +'" y="'+ str(y_home)+ '" start_time="'+ time_format(plan[i][1]) +'" dur="'+ time_format(plan[i][2]) +'" />')
                l.append('           <leg mode="car" />')
            if dest=='other':
                x_other, y_other = choix_spatial(dshop)
                l.append('           <act type="o" x="'+ str(x_other) +'" y="'+ str(y_other)+ '" start_time="'+ time_format(plan[i][1]) +'" dur="'+ time_format(plan[i][2]) +'" />')
                l.append('           <leg mode="car" />')
            
            
        #Retour à la maison
        l.append('           <act type="h" x="'+ str(x_home) +'" y="'+ str(y_home)+ '" start_time="'+ time_format(last_act_start_time) +'" />')
        l.append('      </plan>')
        l.append('</person>')
        f.write("\n".join(l)+"\n")
    
    f.write('\n</plans>')
    f.close()
    
    
def creation_vehicles() :
    
    f = open(chemin_vehicles, "w")
    
    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n\n")
    
    f.write('<vehicleDefinitions xmlns="http://www.matsim.org/files/dtd"\n')
    f.write(' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
    f.write(' xsi:schemaLocation="http://www.matsim.org/files/dtd http://www.matsim.org/files/dtd/vehicleDefinitions_v1.0.xsd">\n')
    f.write('	<vehicleType id="car_average">\n')
    f.write('		<description>\n')
    f.write('			BEGIN_EMISSIONSPASSENGER_CAR;average;average;averageEND_EMISSIONS\n')
    f.write('		</description>\n')
    f.write('		<length meter="7.5"/>\n')
    f.write('		<width meter="1.0"/>\n\n')
    
    f.write('		<accessTime secondsPerPerson="1.0"/>\n')
    f.write('		<egressTime secondsPerPerson="1.0"/>\n')
    f.write('		<doorOperation mode="serial"/>\n')
    f.write('	</vehicleType>\n')
    f.write('	<vehicleType id="car_petrol">\n')
    f.write('		<description>\n')
    f.write('			BEGIN_EMISSIONSPASSENGER_CAR;petrol (4S);&gt;=2L;PC-P-Euro-1END_EMISSIONS\n')
    f.write('		</description>\n')
    f.write('		<length meter="7.5"/>\n')
    f.write('		<width meter="1.0"/>\n\n')
    
    f.write('		<accessTime secondsPerPerson="1.0"/>\n')
    f.write('		<egressTime secondsPerPerson="1.0"/>\n')
    f.write('		<doorOperation mode="serial"/>\n')
    f.write('	</vehicleType>\n')
    f.write('	<vehicleType id="car_diesel">\n')
    f.write('		<description>\n')
    f.write('			BEGIN_EMISSIONSPASSENGER_CAR;diesel;&lt;1,4L;PC-D-Euro-3END_EMISSIONS\n')
    f.write('		</description>\n')
    f.write('		<length meter="7.5"/>\n')
    f.write('		<width meter="1.0"/>\n\n')
    		
    f.write('		<accessTime secondsPerPerson="1.0"/>\n')
    f.write('		<egressTime secondsPerPerson="1.0"/>\n')
    f.write('		<doorOperation mode="serial"/>\n')
    f.write('	</vehicleType>\n')
    f.write('	<vehicleType id="truck">\n')
    f.write('		<description>\n')
    f.write('			BEGIN_EMISSIONSHEAVY_GOODS_VEHICLE;average;average;averageEND_EMISSIONS\n')
    f.write('		</description>\n')
    f.write('		<length meter="7.5"/>\n')
    f.write('		<width meter="1.0"/>\n\n')
    		
    f.write('		<accessTime secondsPerPerson="1.0"/>\n')
    f.write('		<egressTime secondsPerPerson="1.0"/>\n')
    f.write('		<doorOperation mode="serial"/>\n')
    f.write("	</vehicleType>\n\n")
    for i in range(pop) :
        
        f.write("       <vehicle id=\""+ str(i) +"\" type=" + vehicle_type() + "/>\n")
    f.close()
    
    

def choix_spatial(fonction):
    """ détermine un choix de x,y selon la méthode du rejet """
    acceptable = False
    while (not acceptable):
        x = x_min+(rd.random())*(x_max-x_min)
        y = y_min+(rd.random())*(y_max-y_min)
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

def vehicle_type():
    rand=random.randint(1,5)
    if (rand == 1 ) : return("\"car_average\"")
    if (rand == 2 ) : return("\"car_petrol\"")
    if (rand == 3 ) : return("\"car_diesel\"")    
    if (rand == 4 ) : return("\"truck\"")


creation_vehicles()
creation_plans()
