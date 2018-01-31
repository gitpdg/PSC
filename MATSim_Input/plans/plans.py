import xml.etree.cElementTree as ET
import random as rd
from math import exp

###


import matplotlib.pyplot as plt
import numpy as np
import math

#Map parameters
x_min=-1000
x_max=1000
y_min=-1000
y_max=1000
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
    center_tab=[[-500,-500,1],[500,-500,0.3],[-500,400,0.3]]
    return multiple_peaked_fonction(x,y,center_tab)

def dwork(x,y):
    center_tab=[[500,500,1],[-500,500,0.3],[500,-400,0.3]]
    return multiple_peaked_fonction(x,y,center_tab)

def dshop(x,y):
    center_tab=[[-500,500,0.8],[500,-400,0.6]]
    return multiple_peaked_fonction(x,y,center_tab)

#Graphic output
def density_graphs():
    resolution = 25  

    X = np.linspace(y_min,y_max,resolution)
    Y = np.linspace(y_min,y_max,resolution)
    Z=list()
    for i in X:
        Z.insert(0,[])
        for j in Y:
            Z[0].append(dpop(j,i))
    
    f, ax = plt.subplots()
    ax.set_title('Population density')
    ax.imshow(Z,interpolation='none',extent = (x_min,x_max,y_min,x_max))
    
    
    Z=list()
    for i in X:
        Z.insert(0,[])
        for j in Y:
            Z[0].append(dwork(j,i))
            
    f, ax = plt.subplots()
    ax.set_title('Work density')
    ax.imshow(Z,interpolation='none',extent = (x_min,x_max,y_min,x_max))
    
    Z=list()
    for i in X:
        Z.insert(0,[])
        for j in Y:
            Z[0].append(dshop(j,i))
            
    f, ax = plt.subplots()
    ax.set_title('Shopping and leisure density')
    ax.imshow(Z,interpolation='none',extent = (x_min,x_max,y_min,x_max))
    
    plt.show()
    return


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
