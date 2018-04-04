"""In this impact assessment, we use the data provided by the WHO in its review
of Health Risks of Air Pollutution in Europe (HRAPIE project), as well as 
the methodology provided by the EC4MACS project for the ALPHA Benefit
Assessment Model

A few approximations are made :
 - We only consider long-term risks. The effect of short-term pollution peaks
   should be assesed separatly. However, for small cities that do not 
   experience pollution peaks largerly exceeding regulated limits, this 
   approximation makes sense.
 - We do not calculate the impact of ozone (O3), since emissions of this
   pollutant are not calculated by MATSim. 
   As the dangerosity of ozone is aprticularily relevant during pollution
   peaks, this apporximation is coherent with the previous one.
 - We consider there is no cost for air pollution when air pollution is lower
   than half of the WHO limits as proposed by the HRAPIE project.
   
The uncertainties in this file are given for a 95% confidence interval
   """

##IMPORTANT VARIABLES

#Population distribution (taken from the French INSEE demographics for 2018)

pop_0_12 = 0.14459
pop_12_16 = 0.06255
pop_17_29 = 0.1510
pop_30_65 = 0.4461
pop_66_100 = 0.1722

#WHO half limits (annual means) provided by WHO Air quality guidelines
#for particulate matter, ozone, nitrogen dioxide and sulfur dioxide
limit_NO2 = 20
limit_PM = 5  #PM 2.5 (for PM 10 the threshold is two times higher)


#Costs in thousands of euros

#Value of a Statistical Life (OECD estimate)
vsl = 2800
#Chronic bronchitis (for people aged over 30, with a non remission rate of 53%)
chronic_bronchitis=190
#Respiratory hospital admissions (cost of one admission)
rha = 2
#Cardiac hospital admissions (cost of one admission)
cha = 2
#Restricted activity day, aggregated for different ages
rad = 0.075
#Respiratory symptoms
rs = 0.038

#Prevalence rates
mortality_rate=0.01*1.61
chronic_bronchitis_rate=0.01*0.38
rha_rate=617/100000
cha_rate=723/100000
rad_rate=19 #days per year
rs_rate=0.3



#Output file
file_path = "C:/Users/vroll/Desktop/costs.csv"



def impact_NO2(pop,c):
    """This function evaluates the impact of NO2 on the population.
    Imput must take into account the annual mean of NO2 in µg/m^3 and 
    population in the area.
    Data here is taken from the WHO methodology."""
    
    out = str()
    
    #______________________________Mortality______________________________
    
    #We start by evaluating the rise in mortality for adults over 30, only
    #relevant if c>20µg/m^3 : if c is under this threshold, we associate no
    #deaths to NO2. Methodology is explained in : Public-health impact of 
    #outdoor and traffic-related air pollution: a European assessment. Künzli
    #& al. 
    
    
    #impact
    impact = "Mortality for all causes, age over 30"
    #proportion of affected people
    affected = (pop_30_65+pop_66_100)*pop
    #ajusted exposure in person.µg/m^3
    exposure = (c-limit_NO2)*affected
    #concentration-response function
    cr = 0.0055
    cr_uncertain = 0.0025
    #incidence rate
    incidence = round(cr*exposure*mortality_rate,1)
    incidence_uncertain = round(cr_uncertain*exposure*mortality_rate,1)
    #cost
    unit_cost = vsl
    cost = int(incidence*unit_cost)
    cost_uncertain = int(incidence_uncertain*unit_cost)
    if incidence<0:
        exposure = "negligeable"
        incidence = "negligeable"
        incidence_uncertain = "negligeable"
        cost = "negligeable"
        cost_uncertain = "negligeable"
    
    s = "NO2;"+impact+";"+str(1+cr)+";"+str(cr_uncertain)+";"+str(incidence)+";"+str(incidence_uncertain)+";"+str(unit_cost)+";"+str(cost)+";"+str(cost_uncertain)+"\n"
    out+=s
    
    #For the study of NO2, the prevalence of bronchitic symptoms in asthmatic 
    #children aged 5–14 years, about 15% of the population according to
    #Lai & al. (2009), is not taken into account, because of the relative 
    #uncertainty in the data provided and the small fraction of the population 
    #concerned
    
    return out

def impact_PM(pop,c):
    """This function evaluates the impact of PM on the population.
    Imput must take into account the annual mean of PM in µg/m^3 and 
    population in the area.
    Data here is taken from the EC4MACS methodology."""
    
    out = str()
    
    #______________________________Mortality______________________________
      
    #impact
    impact = "Mortality for all causes, age over 30"
    #proportion of affected people
    affected = (pop_30_65+pop_66_100)*pop
    #ajusted exposure in person.µg/m^3
    exposure = (c-limit_PM)*affected
    #concentration-response function
    cr = 0.006
    cr_uncertain = cr*0.04
    #incidence rate
    incidence = round(cr*exposure*mortality_rate,1)
    incidence_uncertain = round(cr_uncertain*exposure*mortality_rate,1)
    #cost
    unit_cost = vsl
    cost = int(incidence*unit_cost)
    cost_uncertain = int(incidence_uncertain*unit_cost)
    if incidence<0:
        exposure = "negligeable"
        incidence = "negligeable"
        incidence_uncertain = "negligeable"
        cost = "negligeable"
        cost_uncertain = "negligeable"
    
    s = "PM;"+impact+";"+str(1+cr)+";"+str(cr_uncertain)+";"+str(incidence)+";"+str(incidence_uncertain)+";"+str(unit_cost)+";"+str(cost)+";"+str(cost_uncertain)+"\n"
    out+=s
    
    #_________________________Chronic Bronchitis________________________
      
    #impact
    impact = "Chronic Bronchitis, age over 30"
    #proportion of affected people
    affected = (pop_30_65+pop_66_100)*pop
    #ajusted exposure in person.µg/m^3
    exposure = (c-limit_PM)*affected
    #concentration-response function
    cr = 0.007
    cr_uncertain = cr*2*0.037
    #incidence rate
    #Non remission rate of 53% included in calculation
    incidence = round(cr*exposure*chronic_bronchitis_rate*0.53,1)
    incidence_uncertain = round(cr_uncertain*exposure*chronic_bronchitis_rate*0.53,1)
    #cost
    unit_cost = chronic_bronchitis
    cost = int(incidence*unit_cost)
    cost_uncertain = int(incidence_uncertain*unit_cost)
    if incidence<0:
        exposure = "negligeable"
        incidence = "negligeable"
        incidence_uncertain = "negligeable"
        cost = "negligeable"
        cost_uncertain = "negligeable"
    
    s = "PM;"+impact+";"+str(1+cr)+";"+str(cr_uncertain)+";"+str(incidence)+";"+str(incidence_uncertain)+";"+str(unit_cost)+";"+str(cost)+";"+str(cost_uncertain)+"\n"
    out+=s
    
    #___________________Respiratory Hospital Admissions________________________
      
    #impact
    impact = "Respiratory Hospital Admissions"
    #proportion of affected people
    affected = pop
    #ajusted exposure in person.µg/m^3
    exposure = (c-limit_PM)*affected
    #concentration-response function
    cr = 0.00114
    cr_uncertain = cr*2*0.0026
    #incidence rate
    incidence = round(cr*exposure*rha_rate,1)
    incidence_uncertain = round(cr_uncertain*exposure*rha_rate,1)
    #cost
    unit_cost = rha
    cost = int(incidence*unit_cost)
    cost_uncertain = int(incidence_uncertain*unit_cost)
    if incidence<0:
        exposure = "negligeable"
        incidence = "negligeable"
        incidence_uncertain = "negligeable"
        cost = "negligeable"
        cost_uncertain = "negligeable"
    
    s = "PM;"+impact+";"+str(1+cr)+";"+str(cr_uncertain)+";"+str(incidence)+";"+str(incidence_uncertain)+";"+str(unit_cost)+";"+str(cost)+";"+str(cost_uncertain)+"\n"
    out+=s
    
    #___________________Cardiac Hospital Admissions________________________
      
    #impact
    impact = "Cardiac Hospital Admissions"
    #proportion of affected people
    affected = pop
    #ajusted exposure in person.µg/m^3
    exposure = (c-limit_PM)*affected
    #concentration-response function
    cr = 0.00060
    cr_uncertain = cr*2*0.0015
    #incidence rate
    incidence = round(cr*exposure*cha_rate,1)
    incidence_uncertain = round(cr_uncertain*exposure*cha_rate,1)
    #cost
    unit_cost = cha
    cost = int(incidence*unit_cost)
    cost_uncertain = int(incidence_uncertain*unit_cost)
    if incidence<0:
        exposure = "negligeable"
        incidence = "negligeable"
        incidence_uncertain = "negligeable"
        cost = "negligeable"
        cost_uncertain = "negligeable"
    
    s = "PM;"+impact+";"+str(1+cr)+";"+str(cr_uncertain)+";"+str(incidence)+";"+str(incidence_uncertain)+";"+str(unit_cost)+";"+str(cost)+";"+str(cost_uncertain)+"\n"
    out+=s
    
    #___________________Restricted activity days________________________
      
    #impact
    impact = "Restricted activity days"
    #proportion of affected people
    affected = pop
    #ajusted exposure in person.µg/m^3
    exposure = (c-limit_PM)*affected
    #concentration-response function
    cr = 0.00048
    cr_uncertain = cr*2*0.0003
    #incidence rate
    incidence = round(cr*exposure*rad_rate,1)
    incidence_uncertain = round(cr_uncertain*exposure*rad_rate,1)
    #cost
    unit_cost = rad
    cost = int(incidence*unit_cost)
    cost_uncertain = int(incidence_uncertain*unit_cost)
    if incidence<0:
        exposure = "negligeable"
        incidence = "negligeable"
        incidence_uncertain = "negligeable"
        cost = "negligeable"
        cost_uncertain = "negligeable"
    
    s = "PM;"+impact+";"+str(1+cr)+";"+str(cr_uncertain)+";"+str(incidence)+";"+str(incidence_uncertain)+";"+str(unit_cost)+";"+str(cost)+";"+str(cost_uncertain)+"\n"
    out+=s
    
    #___________________Lower respiratory symptoms________________________
      
    #impact
    impact = "Lower respiratory symptoms"
    #proportion of affected people
    affected = pop
    #ajusted exposure in person.µg/m^3
    exposure = (c-limit_PM)*affected
    #concentration-response function
    cr = 0.00048
    cr_uncertain = cr*2*0.0003
    #incidence rate
    incidence = round(cr*exposure*rs_rate,1)
    incidence_uncertain = round(cr_uncertain*exposure*rs_rate,1)
    #cost
    unit_cost = rs
    cost = int(incidence*unit_cost)
    cost_uncertain = int(incidence_uncertain*unit_cost)
    if incidence<0:
        exposure = "negligeable"
        incidence = "negligeable"
        incidence_uncertain = "negligeable"
        cost = "negligeable"
        cost_uncertain = "negligeable"
    
    s = "PM;"+impact+";"+str(1+cr)+";"+str(cr_uncertain)+";"+str(incidence)+";"+str(incidence_uncertain)+";"+str(unit_cost)+";"+str(cost)+";"+str(cost_uncertain)+"\n"
    out+=s
    
    return out


def costs_to_csv(pop,c_NO2,c_PM):
      
    file = open(file_path,"w") 
 
    header = "Pollutant;Studied impact;Concertration-response function (for an increase of 1µg/m^3);Uncertainty in CR function;Case incidence;Uncertainty in case incidence;Unit cost in thousands of euros;Calculated cost;Uncertainty in calculated cost\n"
    file.write(header+impact_NO2(pop,c_NO2)+impact_PM(pop,c_PM))
 
    file.close() 
    return

costs_to_csv(10000,80,20)
