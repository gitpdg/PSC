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
    center_tab=[[-500,-500,1],[500,-500,0.6],[-500,400,0.6]]
    return multiple_peaked_fonction(x,y,center_tab)

def dwork(x,y):
    center_tab=[[500,500,1],[-500,500,0.6],[500,-400,0.6]]
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


