import xml.etree.cElementTree as ET
import random as rd
from math import exp

###

print("Extracting map from file...")

#To be completed
mapfile = ""

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

###

import matplotlib.pyplot as plt
import numpy as np
import math


#Map parameters
x_min=354970
x_max=367550
y_min=5470440
y_max=5483500
amplitude_x = x_max-x_min
amplitude_y = y_max-y_min

#To be chosen
resolution = 1000


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
    return (28*x**2)

"""Choses the function that links road density to population density"""


#Population density
def popdensity():
    
    """Calculates the matrix of population density with the road density"""
    road_density=roaddensity()
    
    l=len(road_density[0])
    
    pop_density=np.zeros((l,l))

    for i in range(l):
        for j in range(l):
            pop_density[i][j]=roadtopop(road_density[i][j])
            
    
    return(pop_density)

    

#Graphic output
def roaddensity_graphs():

    road_density=roaddensity()
    l=len(road_density[0])
    
    
    Z=list()
    for i in range(l):
        Z.insert(0,[])
        for j in range(l):
            Z[0].append(road_density[resolution-2-i][j])
    
    f, ax = plt.subplots()
    ax.set_title('Road density')
    ax.imshow(Z,interpolation='bilinear',extent = (x_min,x_max,y_min,y_max))
    
    plt.show()
    return

roaddensity_graphs()


def popdensity_graphs():

    pop_density=popdensity()
    l=len(pop_density[0])
    
    
    Z=list()
    for i in range(l):
        Z.insert(0,[])
        for j in range(l):
            Z[0].append(pop_density[resolution-2-i][j])
    
    f, ax = plt.subplots()
    ax.set_title('Population density')
    ax.imshow(Z,interpolation='bilinear',extent = (x_min,x_max,y_min,y_max))
    
    plt.show()
    return

popdensity_graphs()
####


# paramètres
chemin = "Documents/X/2A/PSC/MATsim/matsim-0.9.0/toy_model/plans.xml"
population = 400
work_starting_time_mean = 8*3600 #in seconds
work_starting_time_standard_deviation = 20*60
work_duration_mean = 8*3600
work_duration_standard_deviation = 10*60


def creation_plans():
    
    f = open(chemin, "w")
    f.write('<?xml version="1.0" ?>\n')
    f.write('<!DOCTYPE plans SYSTEM "http://www.matsim.org/files/dtd/plans_v4.dtd">\n\n')    
    f.write('<plans>\n\n')
    
    for i in range(population) :
        # génération des lieux et horaires
        x_home, y_home = choix_spatial(dpop)
        x_work, y_work = choix_spatial(dwork)
        work_start_time = round(rd.gauss(work_starting_time_mean, work_starting_time_standard_deviation))
        work_duration = round(rd.gauss(work_duration_mean, work_duration_standard_deviation))
        
        l=[]
        l.append('<person id="'+str(i)+'">')
        l.append('      <plan>')
        l.append('           <act type="h" x="'+ str(x_home) +'" y="'+ str(y_home)+ '" start_time="00:00:00" end_time="'+ time_format(work_start_time) +'" />')
        l.append('           <leg mode="car" />')
        l.append('           <act type="w" x="'+ str(x_work) +'" y="'+ str(y_work)+ '" start_time="'+ time_format(work_start_time) +'" dur="'+ time_format(work_duration) +'" />')
        l.append('           <leg mode="car" />')
        l.append('           <act type="h" x="'+ str(x_home) +'" y="'+ str(y_home)+ '" start_time="'+ time_format(work_start_time + work_duration) +'" />')
        l.append('      </plan>')
        l.append('</person>')
        f.write("\n".join(l)+"\n")
    
    f.write('\n</plans>')
    f.close()

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
        x = (rd.random()-0.5)*2000
        y = (rd.random()-0.5)*2000
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

creation_plans()
