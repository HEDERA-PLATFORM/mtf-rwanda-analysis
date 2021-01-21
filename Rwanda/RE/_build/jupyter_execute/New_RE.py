#!/usr/bin/env python
# coding: utf-8

# # Evaluation of Multi-Tier Framework for measuring access to electricity - Rwanda

# The Multi-Tier Framework (MTF) helps to measure the energy access taking into consideration seven attributes that can be categorized on Tiers from 0 to 5. Meaning that tier 0 is no access at all and tier 5 full access. The variables that measure the tiers change depending on the attributes.

# ## Importing the useful libraries

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import pie, axis, show
import seaborn as sns
sns.set_style('darkgrid')
import warnings
warnings.filterwarnings("ignore")
import math
import plotly.express as px


# From the data collected, the analysis of the attributes is as follows:

# ## Importing the dataset

# In[2]:


df = pd.read_csv('Main_dataset.csv')


# In[454]:


df.head()


# ## Analysing different Attributes
# 
# Attributes which are analysed for MTF_Rwanda_Questionnaire_Household: 
# 
# 1. Capacity
# 2. Availability
# 3. Reliability
# 4. Quality
# 5. Affordability
# 6. Formality
# 7. Health and safety

# # Attribute: Capacity

# This attribute corresponds to the power capacity of the household and is measured in Wh. To find out the power capacity, we need to know the different sources of power available. From our dataset:
#     
# 1. C22: Power available from the national grid
# 2. C64: Power available from the mini grid
# 3. C88: Power available from the generator set
# 4. C117: Power available from the inverter
# 5. C119: Power available from the batteries
# 6. C151: Power available from solar panel (Not present in the dataset but is there in the survey)
# 7. C154: Power available from solar batteries (Not present in the dataset but is there in the survey)
# 8. Other source: Pico-Hyro (power capacity question not mentioned in the survey)

# In[455]:


df_total= df[['C22', 'C64','C88','C117','C119A']]


# ## Renaming the columns

# For a better understanding of the dataset, the columns are named as follows:
# 
# 1. C22: National_Grid
# 2. C64: Mini_Grid
# 3. C88: Generator
# 4. C117: Inverter
# 5. C119A: Battery

# In[456]:


df_total.columns = ['National_Grid', 'Mini_Grid','Generator','Inverter','Battery']


# ## Adding "Total capacity to the dataset"

# In[457]:


lst=[]
for i in range(df_total.shape[0]):
    add=0
    gotnum= False
    for j in range(df_total.shape[1]):
        if math.isnan(df_total.iat[i,j])==False:
            gotnum=True
            add = add + df_total.iat[i,j]
    if gotnum :
        lst.append(add)
    else:
        lst.append(math.nan)
    
# Adding the above list to dataframe
df_total["Total_Capacity"] = lst

# Replacing the 0 values again with NaN
df_total.replace(0, np.nan, inplace=True)


# ## Formulating the column "Total capacity"

# In[458]:


# The power capacity units provided in the dataset are in monthly kWh. 
# However, for TIER analysis the units are in daily Wh consumption. 
# Therefore, dividing the dataset by 30 and multiplying it by 1000.


df_total['Total_Capacity']= df_total.Total_Capacity.apply(lambda x: x if math.isnan(x) else (x*1000)/30)


# In[459]:


df_total["Total_Capacity"] = df_total.Total_Capacity.apply(lambda x: "Missing_data" if math.isnan(x) else x)


# In[460]:


df_total.tail()


# ## Adding column "TIER" to the dataset 

# In[461]:


def conditions(Total_Capacity):
    if Total_Capacity =='Missing_data':
        return "Missing_data"
    elif Total_Capacity<12:
        return "0"
    elif 12<=Total_Capacity<200:
        return "1"
    elif 200<=Total_Capacity<1000:
        return "2"
    elif 1000<=Total_Capacity<3400:
        return "3"
    elif 3400<=Total_Capacity<8200:
        return "4"
    else:
        return "5"
    
func = np.vectorize(conditions)
transform = func(df_total.Total_Capacity)
df_total["TIER_cap"] = transform


# ## Printing the TIER counts

# In[462]:


df_total['TIER_cap'].value_counts()


# ### Visualizing the TIER levels with "Missing_data"

# In[463]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df_total['TIER_cap'].value_counts().plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on power capacity')

#Boxplot
sns.countplot('TIER_cap',data=df_total,ax=ax[1])
ax[1].set_title('TIER levels based on power capacity')


# ### Visualizing the TIER levels without "Missing_data"

# In[464]:


df2_total = df_total[df_total != 'Missing_data'] 
df2_total=df2_total[['TIER_cap']]


# In[465]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df2_total['TIER_cap'].value_counts().plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on power capacity')

#Boxplot
sns.countplot('TIER_cap',data=df2_total,ax=ax[1])
ax[1].set_title('TIER levels based on power capacity')


# In the above graph it can be seen:
# 
# 1. TIER 1 corresponds to 30% of the households which recieves at least 12Wh of power supply
# 2. TIER 2 corresponds to 54% of the households which recieves at least 200Wh of power supply
# 3. TIER 3 corresponds to 13% of the households which recieves at least 1kWh of power supply
# 4. TIER 4 corresponds to 2% of the households which recieves at least 3.4kWh of power supply
# 5. TIER 5 corresponds to less than 1% of the households which recieves at least 8.2kWh of power supply
# 

# # Attribute: Availabilty

# The availability relates to the hours of electricity supply that the household receives. For a better analysis the availability is measured per day hours (24/7), and evening hours (maximum of 4 hours).

# ## Availability: Day and night

# Methodology:
# 
# To understand the attribute more carefully, features from every power souce have been taekn into consideration; 
# 
# * C26A represents the hours of electricity available each day and night from the national grid in the worst months. 
# * Whereas, C26B represents the hours of electricity available each day and night from  the national grid in the typical months.
# * C68A represents the hours of electricity available each day and night from the mini grid in the worst months.
# * Whereas, C68B represents the hours of electricity available each day and night from  the mini grid in the typical months.
# * C107A represents the hours of electricity available each day and night from the generator set in the worst months.
# * Whereas, C107B represents the hours of electricity available each day and night from  the generator set in the typical months.
# * C127 represents the hours of electricity available each day from the rechargeable battery.
# * C137A represents the hours of electricity available each day and night from pico-hydro in the worst months.
# * Whereas, C137B represents the hours of electricity available each day and night from  pico-hydro in the typical months.
# * C172A represents the hours of electricity available each day and night from  main solar based devices in the worst months.
# * Whereas, C172B represents the hours of electricity available each day and night from  main solar based devices in the typical months.

# In[466]:


df_av= df[['C26A','C26B','C68A','C68B','C107A','C107B','C127','C137A','C137B','C172A','C172B']]


# ### Renaming the columns

# In[467]:


df_av.columns = ['National_grid_Worst', 'National_grid_Typical','Mini_grid_Worst','Mini_grid_Typical','Generator_set_Worst','Generator_set_Typical','Battery','Pico_hydro_Worst','Pico_hydro_Typical','Solar_device_Worst','Solar_device_Typical']


# In[468]:


df_av.tail()


# In[469]:


df_av.info()


# ### Calculation
# 
# In this step Total availabilty for all the power sources has been analysed. Taking the worst months into consideration, the missing values in "worst" months have been added from the "typical" months. This is done as the World bank takes the worst condition into account for enery access assessment.

# In[470]:


#National Grid
df_av['National_grid_Total'] = df_av.National_grid_Worst.fillna(value=df_av.National_grid_Typical)

#National Grid
df_av['Mini_grid_Total'] = df_av.Mini_grid_Worst.fillna(value=df_av.Mini_grid_Typical)

#Generator Set
df_av['Generator_set_Total'] = df_av.Generator_set_Worst.fillna(value=df_av.Generator_set_Typical)

#Pico Hydro
df_av['Pico_hydro_Total'] = df_av.Pico_hydro_Worst.fillna(value=df_av.Pico_hydro_Typical)

#Solar Devicce
df_av['Solar_device_Total'] = df_av.Solar_device_Worst.fillna(value=df_av.Solar_device_Typical)


#Taking only the total values into consideration
df_av_new=df_av[['National_grid_Total','Mini_grid_Total','Generator_set_Total','Pico_hydro_Total','Solar_device_Total','Battery']]


# In[471]:


df_av_new.tail()


# ### Changing the string variables into float/int 

# In[472]:


df_av_new=df_av_new.replace(to_replace="Don't know",value=0)


# In[473]:


df_av_new= df_av_new.apply(pd.to_numeric, errors='coerce')


# In[474]:


df_av_new.info()


# ### Calculating the total availability

# In[475]:


lst=[]
for i in range(df_av_new.shape[0]):
    add=0
    gotnum= False
    for j in range(df_av_new.shape[1]):
        if math.isnan(df_av_new.iat[i,j])==False:
            gotnum=True
            add = add + df_av_new.iat[i,j]
    if gotnum :
        lst.append(add)
    else:
        lst.append(math.nan)
    
# adding list to dataframe
df_av_new["Total_availability"] = lst


# In[476]:


df_av_new.tail()


# In[477]:


df_av_new=df_av_new[['Total_availability']]


# ### Replacing NaN and "Don't know" values with "Missing_data" 
# 
# This is done to keep the missing values into analysis (As it is important to know how many missing values do we have)

# In[478]:


df_av_new['Total_availability'] = df_av_new.replace(np.nan, 'Missing_data', regex=True)


# In[479]:


df_av_new.tail()


# ### Adding column "TIER" to the dataset 

# In[480]:


# AVAILABILITY: Day
#Note: conditions for TIER 1 and 2 are the same

def conditions(Total_availability):
    if Total_availability == 'Missing_data':
        return "Missing_data"
    elif Total_availability<4:
        return "0"
    elif 4<=Total_availability<8:
        return "1&2"
    elif 8<=Total_availability<16:
        return "3"
    elif 16<=Total_availability<23:
        return "4"
    else:
        return "5"
    
func = np.vectorize(conditions)
transform = func(df_av_new.Total_availability)
df_av_new["TIER_av"] = transform


# In[481]:


df_av_new['TIER_av'].value_counts()


# #### Visualizing the TIER levels with "Missing_data"

# In[482]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df_av_new['TIER_av'].value_counts().plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on day and night power availability')

#Barplot
sns.countplot('TIER_av',data=df_av_new,ax=ax[1])
ax[1].set_title('TIER levels based on day and night power availability')


# #### Visualizing the TIER levels without "Missing_data"

# In[483]:


df2_av = df_av_new[df_av_new != 'Missing_data'] 


# In[484]:


df2_av=df2_av[['TIER_av']]


# In[485]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df2_av['TIER_av'].value_counts().plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on power capacity')

#Boxplot
sns.countplot('TIER_av',data=df2_av,ax=ax[1])
ax[1].set_title('TIER levels based on power capacity')


# In the above graph we can see that the daily availability in:
# 
# 1. TIER 0 contributes to 6% of evening availability which is less than 4 hours
# 2. TIER 1&2 contributes to 6% of evening availability which is at least 4 hours
# 3. TIER 3 contributes to 12% of evening availability which is at least 8 hours
# 4. TIER 4 contributes to 35% of evening availability which is at least 16 hours
# 4. TIER 5 contributes to 41% of evening availability which is at least 23 hours

# ## Attribute: Availabilty (Evening)

# Methodology:
# 
# To understand the attribute more carefully, features from every power souce have been taekn into consideration; 
# 
# * C27A represents the hours of electricity available each evening from the national grid in the worst months. 
# * Whereas, C27B represents the hours of electricity available each evening from  the national grid in the typical months.
# * C69A represents the hours of electricity available each evening from the mini grid in the worst months.
# * Whereas, C69B represents the hours of electricity available each evening from  the mini grid in the typical months.
# * C108A represents the hours of electricity available each evening from the generator set in the worst months.
# * Whereas, C108B represents the hours of electricity available each evening from  the generator set in the typical months.
# * C138A represents the hours of electricity available each evening from pico-hydro in the worst months.
# * Whereas, C138B represents the hours of electricity available each evening from  pico-hydro in the typical months.
# * C173A represents the hours of electricity available each evening from main solar based devices in the worst months.
# * Whereas, C173B represents the hours of electricity available each evening from  main solar based devices in the typical months.

# In[486]:


df_ave= df[['C27A','C27B','C69A','C69B','C108A','C108B','C138A','C138B','C173A','C173B']]


# ### Renaming the columns

# In[487]:


df_ave.columns = ['National_grid_Worst', 'National_grid_Typical','Mini_grid_Worst','Mini_grid_Typical','Generator_set_Worst','Generator_set_Typical','Pico_hydro_Worst','Pico_hydro_Typical','Solar_device_Worst','Solar_device_Typical']


# In[488]:


df_ave.tail()


# In[489]:


df_ave.info()


# ### Calculation
# 
# In this step Total availabilty for all the power sources has been analysed. Taking the worst months into consideration, the missing values in "worst" months have been added from the "typical" months. This is done as the World bank takes the worst condition into account for enery access assessment.

# In[490]:


#National Grid
df_ave['National_grid_Total'] = df_ave.National_grid_Worst.fillna(value=df_ave.National_grid_Typical)

#National Grid
df_ave['Mini_grid_Total'] = df_ave.Mini_grid_Worst.fillna(value=df_ave.Mini_grid_Typical)

#Generator Set
df_ave['Generator_set_Total'] = df_ave.Generator_set_Worst.fillna(value=df_ave.Generator_set_Typical)

#Pico Hydro
df_ave['Pico_hydro_Total'] = df_ave.Pico_hydro_Worst.fillna(value=df_ave.Pico_hydro_Typical)

#Solar Devicce
df_ave['Solar_device_Total'] = df_ave.Solar_device_Worst.fillna(value=df_ave.Solar_device_Typical)


#Taking only the total values into consideration
df_ave_new=df_ave[['National_grid_Total','Mini_grid_Total','Generator_set_Total','Pico_hydro_Total','Solar_device_Total']]


# ### Changing the string variables into float/int 

# In[491]:


df_ave_new=df_ave_new.replace(to_replace="Don't know",value=0)


# In[492]:


df_ave_new= df_ave_new.apply(pd.to_numeric, errors='coerce')


# ### Calculating the total availability

# In[493]:


lst=[]
for i in range(df_ave_new.shape[0]):
    add=0
    gotnum= False
    for j in range(df_ave_new.shape[1]):
        if math.isnan(df_ave_new.iat[i,j])==False:
            gotnum=True
            add = add + df_ave_new.iat[i,j]
    if gotnum :
        lst.append(add)
    else:
        lst.append(math.nan)
    
# adding list to dataframe
df_ave_new["Total_availability"] = lst


# In[494]:


df_ave_new=df_ave_new[['Total_availability']]


# ### Replacing NaN values with "Missing_data" 
# 
# This is done to keep the missing values into analysis (As it is important to know how many missing values do we have)

# In[495]:


df_ave_new['Total_availability'] = df_ave_new.replace(np.nan, 'Missing_data', regex=True)


# ### Adding column "TIER" to the dataset 

# In[496]:


# AVAILABILITY: Day
#Note: conditions for TIER 4 and 5 are the same

def conditions(Total_availability):
    if Total_availability == 'Missing_data':
        return "Missing_data"
    elif Total_availability==0:
        return "Missing_data"
    elif 0<Total_availability<1:
        return "0"
    elif 1<=Total_availability<2:
        return "1"
    elif 2<=Total_availability<3:
        return "2"
    elif 3<=Total_availability<4:
        return "3"
    else:
        return "4&5"
    
func = np.vectorize(conditions)
transform = func(df_ave_new.Total_availability)
df_ave_new["TIER"] = transform


# In[497]:


df_ave_new['TIER'].value_counts()


# #### Visualizing the TIER levels with "Missing_data"

# In[498]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df_ave_new['TIER'].value_counts().plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on evening power availability')

#Barplot
sns.countplot('TIER',data=df_ave_new,ax=ax[1])
ax[1].set_title('TIER levels based on evening power availability')


# #### Visualizing the TIER levels without "Missing_data"

# In[499]:


df2 = df_ave_new[df_ave_new != 'Missing_data'] 


# In[500]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df2['TIER'].value_counts().plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on power capacity')

#Boxplot
sns.countplot('TIER',data=df2,ax=ax[1])
ax[1].set_title('TIER levels based on power capacity')


# In the above graph we can see that the evening availability in:
# 
# 1. TIER 1 contributes to 8% of evening availability which is at least 1 hours
# 2. TIER 2 contributes to 15% of evening availability which is at least 2 hours
# 3. TIER 3 contributes to 24% of evening availability which is at least 3 hours
# 4. TIER 4&5 contributes to 53% of evening availability which is at least 4 hours

# # Attribute: Reliability
# 
# Methodology:
# 
# This indicator was developed to know how many disruptions of energy supply does the household suffer, and the duration of it. To understand the attribute more carefully, features from all the power sources have been taekn into consideration; 
# * C29A represents the electricity disruption from the national grid in the worst months. 
# * Whereas, C29B represents the electricity disruption from the national grid in the actual months.
# * C30A represents the duration of the outages from the national grid in the worst months. 
# * C30B represents the duration of the outagesfrom the national grid in the worst months. 
# * C71A represents the electricity disruption from the mini grid in the actual months. 
# * Whereas, C71B represents the electricity disruption from the mini grid in the actual months.
# * C72A represents the duration of the outages from the mini grid in the worst months. 
# * C72B represents the duration of the outages from the mini grid in the actual months. 
# 

# In[501]:


df_rel= df[['C29A','C29B','C30A','C30B','C71A','C71B','C72A','C72B']]


# ## Renaming the columns

# In[502]:


df_rel.columns = ['National_grid_Worst','National_grid_Typical','National_duration_Worst','National_duration_Typical','Mini_grid_Worst','Mini_grid_Typical','Mini_duration_Worst','Mini_duration_Typical']


# In[503]:


df_rel=df_rel.replace(to_replace=888,value=math.nan)


# ## Calculation
# 
# In this step Total reliability from all the power sources has been analysed. Taking the worst months into consideration, the missing values in "worst" months have been added from the "typical" months. This is done as the World bank takes the worst condition into account for enery access assessment.

# In[504]:


#National Grid
df_rel['National_grid_Total'] = df_rel.National_grid_Worst.fillna(value=df_rel.National_grid_Typical)

#Duration_national
df_rel['National_duration_Total'] = df_rel.National_duration_Worst.fillna(value=df_rel.National_duration_Typical)

#Mini Grid
df_rel['Mini_grid_Total'] = df_rel.Mini_grid_Worst.fillna(value=df_rel.Mini_grid_Typical)

#Duration_mini
df_rel['Mini_duration_Total'] = df_rel.Mini_duration_Worst.fillna(value=df_rel.Mini_duration_Typical)

#Taking only the total values into consideration
df_rel_new=df_rel[['National_grid_Total','National_duration_Total','Mini_grid_Total','Mini_duration_Total']]


# In[505]:


df_rel_new.tail()


# ## Replacing NaN values with "Missing_data" 
# 
# This is done to keep the missing values into analysis (As it is important to know how many missing values do we have)

# In[506]:


df_rel_new=df_rel_new.replace(to_replace=math.nan,value='Missing_data',regex=True)


# ## Adding column "TIER" to the dataset 

# In[507]:


lst=[]
for i in range (df_rel_new.shape[0]):
    value=""
    grid_total = df_rel_new.iat[i,0]
    duration_total = df_rel_new.iat[i,1]
    if isinstance(grid_total, str) and grid_total=="Missing_data":
        value = "Missing_data"
    elif isinstance(duration_total, str) and duration_total=="Missing_data":
        value = "Missing_data"
    elif 0<grid_total<=3 and duration_total<2 :
        value = "5"
    elif 3<grid_total<=14 and duration_total>2:
        value = "3&4"
    else:
        value = "0,1&2"
    lst.append(value)
       
# adding list to dataframe
df_rel_new["TIER_rel"] = lst


# In[508]:


df_rel_new['TIER_rel'].value_counts()


# ### Visualizing the TIER levels with "Missing_data"

# In[509]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df_rel_new['TIER_rel'].value_counts().plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on reliability')

#Barplot
sns.countplot('TIER_rel',data=df_rel_new,ax=ax[1])
ax[1].set_title('TIER levels based on reliability')


# ### Visualizing the TIER levels without "Missing_data"

# In[510]:


df2_rel = df_rel_new[df_rel_new != 'Missing_data'] 


# In[511]:


df2_rel=df2_rel[['TIER_rel']]


# In[512]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df2_rel['TIER_rel'].value_counts().plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on reliability')

#Boxplot
sns.countplot('TIER_rel',data=df2_rel,ax=ax[1])
ax[1].set_title('TIER levels based on reliability')


# In the above graph we can see:
# 
# 1. TIER 5 contributes to only 10% of disruptions which is at most 3 disruptions per week with total duration of less than 2 hours
# 2. TIER 3 & 4 contributes to 8% of disruptions which is at most 14 disruptions per week and more than 3 disruptions per week with total duration of more than 2 hours
# 3. Most of the disruptions/outages in the power supply is in TIER 0,1 and 2 which is 83%

# # Attribute: Quality
# 
# Methodology:
# 
# The quality attribute refers to if the household had experienced voltage problems that damaged the appliances or its desired use. To understand the attribute more carefully, features from all the power sources have been taekn into consideration; 
# 
# * C39 represents the damaged appliances from the national grid. 
# * C81 represents the damaged appliances from the mini grid.
# * C110 represents the damaged appliances from the generator set.
# * C140 represents the damaged appliances from the Pico-hydro.

# In[513]:


df_q= df[['C39','C81','C110','C140']]


# ## Renaming the columns

# In[514]:


df_q.columns = ['National_grid', 'Mini_grid','Generator_set','Pico_hydro']


# In[515]:


df_q.tail()


# In[516]:


df_q.info()


# ## Changing the string variables into float/int 

# In[517]:


df_q=df_q.replace(to_replace="Don?t know",value='Missing_data')


# ## Replacing NaN values with "Missing_data" 
# 
# This is done to keep the missing values into analysis (As it is important to know how many missing values do we have)

# In[518]:


df_q = df_q.replace(np.nan, 'Missing_data', regex=True)


# In[519]:


df_q=df_q[['National_grid']]


# In[520]:


def conditions(National_grid):
    if National_grid == 'Missing_data':
        return "Missing_data"
    elif National_grid==888:
        return "Missing_data"
    elif National_grid==1:
        return "0,1,2&3"
    else:
        return "4&5"
    
func = np.vectorize(conditions)
transform = func(df_q.National_grid)
df_q["TIER_q"] = transform


# ### Visualizing the TIER levels with "Missing_data"

# In[521]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df_q['TIER_q'].value_counts().plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on power quality')

#Barplot
sns.countplot('TIER_q',data=df_q,ax=ax[1])
ax[1].set_title('TIER levels based on power quality')


# ### Visualizing the TIER levels without "Missing_data"

# In[522]:


df2_q = df_q[df_q != 'Missing_data'] 


# In[523]:


df2_q=df2_q[['TIER_q']]


# In[524]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df2_q['TIER_q'].value_counts().plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on quality')

#Barplot
sns.countplot('TIER_q',data=df2_q,ax=ax[1])
ax[1].set_title('TIER levels based on quality')


# In the above graph it can be seen that:
# 
# 1. The products damaged by national grid are 24% which comes in the TIER 0-3
# 2. The products which are not damaged by national grid are 76% and it comes in the TIER 4-5.
# 3. The data for the other power sources is not sufficient to visualize.

# # Attribute: Affordability 
# 

# For the case of Rwanda, the information about affordability couldn’t be collected.
# 

# # Attribute: Formality
# 
# Methodology:
# 
# This attribute relates to the payments of the electricity supply. To understand the attribute more carefully, features from all the power sources have been taekn into consideration; 
# 
# * C17 represents the electricity bill payment for using the national grid. 
# * C57 represents the electricity bill payment for using the mini grid.

# In[525]:


df_f= df[['C17','C57']]


# ## Renaming the columns

# In[526]:


df_f.columns = ['National_grid', 'Mini_grid']


# In[527]:


df_f.head()


# ## Replacing NaN values with "Missing_data"

# In[528]:


df_f = df_f.replace(np.nan, 'Missing_data', regex=True)


# ## Focusing on National grid

# In[529]:


# No bill paid for electricity= TIER 0-3
# Bill paid for electricity= TIER 4&5

def conditions(National_grid):
    if National_grid == 'Missing_data':
        return "Missing_data"
    elif National_grid==111:
        return "0,1,2&3"
    else:
        return "4&5"
    
func = np.vectorize(conditions)
transform = func(df_f.National_grid)
df_f["TIER_f"] = transform


# ### Visualizing the TIER levels with "Missing_data"

# In[530]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

df_f['TIER_f'].value_counts().plot.pie( autopct='%1.0f%%',figsize=(18,6))
ax[0].set_title('TIER levels based on formality')


# ### Visualizing the TIER levels without "Missing_data"

# In[531]:


df2_f = df_f[df_f != 'Missing_data'] 


# In[532]:


df2_f=df2_f[['TIER_f']]


# In[533]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

df2_f['TIER_f'].value_counts().plot.pie( autopct='%1.0f%%',figsize=(18,6))
ax[0].set_title('TIER levels based on formality')


# In the above graph we can see:
# 
# 1. Only 2% lies in TIER 0-3 for not paying the electricity bill
# 2. 98% lies in TIER 4-5 for paying the electricity bill

# # Attribute: Health and Safety
# 
# Methodology:
# 
# Health and Safety relates to the accidents (serious or fatal) that could occur because of the electricity connection. To understand the attribute more carefully, features from all the power sources have been taekn into consideration; 
# 
# * C41 represents the accidents caused using the national grid. 
# * C83 represents the accidents caused using the mini grid.
# * C112 represents the accidents caused using the generator set.
# * C130 represents the accidents caused using the battery.
# * C142 represents the accidents caused using the Pico-hydro.
# * C175 represents the accidents caused using the solar based devices.

# In[534]:


df_hs= df[['C41','C83','C112','C130','C142','C175']]


# In[535]:


df_hs.columns = ['National_grid', 'Mini_grid','Generator_set','Battery','Pico_hydro','Solar_devices']


# In[536]:


df_hs.head()


# ## Focusing on National grid

# In[537]:


df_hs = df_hs.replace(np.nan, 'Missing_data', regex=True)


# In[538]:


def conditions(National_grid):
    if National_grid == 'Missing_data':
        return "Missing_data"
    elif National_grid=='Yes' :
        return "0,1,2&3"
    else:
        return "4&5"
    
func = np.vectorize(conditions)
transform = func(df_hs.National_grid)
df_hs["TIER_hs"] = transform


# ### Visualizing the TIER levels with "Missing_data"

# In[539]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

df_hs['TIER_hs'].value_counts().plot.pie( autopct='%1.0f%%',figsize=(18,6))
ax[0].set_title('TIER levels based on Health and safety')


# ### Visualizing the TIER levels without "Missing_data"

# In[540]:


df2_hs = df_hs[df_hs != 'Missing_data'] 


# In[541]:


df2_hs=df2_hs[['TIER_hs']]


# In[542]:


# Setting up the ESMAP color pallette
esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']
sns.set_palette(esmap_colors)

df2_hs['TIER_hs'].value_counts().plot.pie( autopct='%1.0f%%',figsize=(18,6))
ax[0].set_title('TIER levels based on Health and safety')


# The above figure shows that no one from grid-connected households reported a serious accident caused by
# electrocution.

# # Visualising all the grouped TIERs together

# In[543]:


df_TIER= pd.concat([df2_total,df2_av,df2_rel,df2_q,df2_f,df2_hs])


# In[544]:


df_TIER.columns = ['Capacity', 'Availability','Reliability','Quality','Formality','Health_Safety']


# In[545]:


df_plot = pd.DataFrame(columns=['Attribute'])
df_plot['Attribute']=["Capacity","Availability","Reliability","Quality","Formality","Health_Safety"]


# In[546]:


df_plot


# In[547]:


op=df_TIER['Capacity'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot.loc[0, tier] = items[1]

op=df_TIER['Availability'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot.loc[1, tier] = items[1]
    
op=df_TIER['Reliability'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot.loc[2, tier] = items[1]
    
op=df_TIER['Quality'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot.loc[3, tier] = items[1]

op=df_TIER['Formality'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot.loc[4, tier] = items[1]
    
op=df_TIER['Health_Safety'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot.loc[5, tier] = items[1]


# In[548]:


df_plot = df_plot.replace(np.nan, 0)


# In[549]:


esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']

sns.set_palette(esmap_colors)

ax=df_plot.plot(x="Attribute", y=["2","1","3","4","5","1&2","0","0,1&2","3&4","4&5","0,1,2&3"],kind='bar', stacked=True,figsize=(15,7))

ax.set(ylabel="Households",xlabel='Attributes', title="Households by TIER")

#Adjusting the ticks
for item in ax.get_xticklabels():
    item.set_rotation(0)

plt.show()


# # Visualising only TIERs 0-5

# In[550]:


df_TIER_new=df_TIER


# In[551]:


df_TIER_new['Reliability'].value_counts()


# In[552]:


df_TIER_new = df_TIER_new.replace(('0,1,2&3','0,1&2','1&2','3&4','4&5'), ('0','0','1','3','4'),regex=True)


# In[553]:


df_plot_new = pd.DataFrame(columns=['Attribute'])
df_plot_new['Attribute']=["Capacity","Availability","Reliability","Quality","Formality","Health_Safety"]


# In[554]:


op=df_TIER_new['Capacity'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot_new.loc[0, tier] = items[1]

op=df_TIER_new['Availability'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot_new.loc[1, tier] = items[1]
    
op=df_TIER_new['Reliability'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot_new.loc[2, tier] = items[1]
    
op=df_TIER_new['Quality'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot_new.loc[3, tier] = items[1]

op=df_TIER_new['Formality'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot_new.loc[4, tier] = items[1]
    
op=df_TIER_new['Health_Safety'].value_counts()
for items in op.iteritems(): 
    tier = items[0]
    df_plot_new.loc[5, tier] = items[1]
    

#Replacing nan values with 0    
df_plot_new = df_plot_new.replace(np.nan, 0)


# In[555]:


esmap_colors=['#864241','#B85F57','#E49202','#5797B0','#84B0B1','#5C9989']

sns.set_palette(esmap_colors)

ax=df_plot_new.plot(x="Attribute", y=['0',"1","2","3","4","5"],kind='bar', stacked=True,figsize=(15,7))

ax.set(ylabel="Households",xlabel='Attributes', title="Households by TIER")

#Adjusting the ticks
for item in ax.get_xticklabels():
    item.set_rotation(0)

plt.show()


# # Aggregated Analysis: Index of Access to Household Electricity

# To compile the information captured by the multi-tier matrix into a single number representing the level
# of access to household electricity in a selected geographic area, a simple index can be calculated by
# weighting the tiers and arriving at a weighted average. The following formula is applied:

# $
# \sum \limits _{k=0} ^{5}  20 * P_{k} * k $   |  Where,  $k$: tier number & $P_{k}$: proportion of households at the kth tier 
# 

# In[556]:


df_plot_new


# In[557]:


df_AA= df_plot_new.sum(axis=0,numeric_only=True)
df_AA_new = df_AA/df_AA.sum()

add=0
for items in df_AA_new.iteritems(): 
    
    add= add + (20*float(items[0])*float(items[1]))
    
print("The Access Index (AI) for Rwanda is", int(add))


# In[558]:


df_AA=df_AA.to_frame(name="TIER")

#Pie plot
f,ax=plt.subplots(1,2, figsize=(18,6))
df_AA['TIER'].plot.pie( autopct='%1.0f%%',ax=ax[0])
ax[0].set_title('TIER levels based on Index Calculation')

#Barplot
sns.barplot(x=['2',"1","3","4","5","0"], y="TIER", data=df_AA)
ax[1].set_title('TIER levels based on Index Calculation')


# In[ ]:





# 
# ```{toctree}
# :hidden:
# :titlesonly:
# 
# 
# content
# ```
# 
