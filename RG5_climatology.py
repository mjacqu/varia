import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('/Users/mistral/Documents/CUBoulder/Science/variousprojects/permafrost/d-1cr23x-cr1000.daily.ml.data.csv')
df.date = pd.to_datetime(df.date, format = '%Y-%m-%d')
df = df.set_index(df.date)

station_elev = 3739 #m
RG5_elev = 3642 #m
lapse_rate = 6.5 * 10**(-3)

df['RG5_avg'] = df.airtemp_avg + (lapse_rate * (station_elev - RG5_elev))
df['RG5_max'] = df.airtemp_max + (lapse_rate * (station_elev - RG5_elev))


#positive degree days
df['PDD'] = df.RG5_max.gt(0)

#MAAT
yearly = pd.DataFrame()
yearly['MAAT'] = df.groupby(df.index.year).RG5_avg.mean()
yearly['PDD'] = df.groupby(df.index.year).PDD.sum()
yearly['totposdeg'] = df[df.PDD == True].groupby(df[df.PDD == True].index.year).airtemp_max.sum()
yearly.index = pd.to_datetime(yearly.index, format='%Y')

#Plot
fig, axs = plt.subplots(3,1,figsize = (10,7), sharex = 'col')
axs[0].plot(yearly.MAAT[1:], '--.', color = 'dimgrey')
axs[0].set_title('Mean annual air temperature at RG5')
axs[0].set_ylabel('Temperature [°C]')

axs[1].plot(yearly.PDD[1:], '--.', color = 'dimgrey')
axs[1].set_title('Number of positive degree days (PDD) at RG5')
axs[1].set_ylabel('Number of PDD')

axs[2].plot(yearly.totposdeg[1:], '--.', color = 'dimgrey')
axs[2].set_title('Total positive degrees at RG5')
axs[2].set_xlabel('Year')
axs[2].set_ylabel('Total positive degrees [°C]')
fig.tight_layout()
plt.savefig('/Users/mistral/Documents/CUBoulder/Science/variousprojects/permafrost/RG5temps.png')
