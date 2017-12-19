### TRIP GENERATION

import numpy.random as random

##DATA INPUT

#Total population of the model
pop = 10 
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

print_pop_schedules()
