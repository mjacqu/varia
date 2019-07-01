import Taan_fjord_helpers as tfh
import glob
import numpy as np
import matplotlib.pyplot as plt
import re
from datetime import datetime
import pandas as pd

#set path
path = '/Users/mistral/Documents/CUBoulder/Science/variousprojects/Brie_TaanFjord/'
# set distance from terminus at which to grab velocites and radius in which to get median velocity
distances = [200, 750, 1500]
radius = 100
# initialize dataframe
df = pd.DataFrame()
columns = ['start_date', 'end_date', 'vel_date', 'vel1', 'vel2', 'vel3']
# define crs of tiffs and geojson, and local utm crs (for calcs in m)
data_crs = 'EPSG:4326'
local_crs = 'EPSG:32607'

# Get sorted list of all geotiffs
gtiffs = glob.glob(path + '*.tif')
gtiffs.sort()

# Get centerline into utm coordinates (same for all)
centerline = path + 'centerline.geojson'
cl = tfh.geojson_to_numpy(centerline)
cl_utm = tfh.convert_crs(cl, data_crs, local_crs)

for f in gtiffs:
    vel_reg = re.findall(r'\d+',f)
    vel_start = datetime.strptime(vel_reg[0], '%Y%m%d')
    vel_end = datetime.strptime(vel_reg[2], '%Y%m%d')
    vel_date = vel_start + (vel_end - vel_start)/2
    # get terminus position corresponding to start date (vel_start)
    tmns_fp = path + 'terminus' + vel_reg[0] +'.geojson'
    # load tmns, convert to utm
    tmns = tfh.geojson_to_numpy(tmns_fp)
    tmns_utm = tfh.convert_crs(tmns, data_crs, local_crs)
    # Get center points for velocity extraction
    cutln, vel_pts = tfh.get_points_on_line(cl_utm, tmns_utm, distances)
    # Get median velocities around selected points
    velocity = []
    for i in range(0, len(distances)):
        vel, coords = tfh.median_of_circle(f, vel_pts[i], local_crs, radius, line = tmns_utm)
        velocity.append(vel)
    vel1, vel2, vel3 = velocity
    df = df.append(pd.DataFrame([(vel_start, vel_end, vel_date, vel1, vel2, vel3)], columns = columns))


# Make plot velocities
fig = plt.subplots(figsize = (12,5))
plt.plot(df.vel_date, df.vel1, '*--', label = str(distances[0])+'m')
plt.plot(df.vel_date, df.vel2, '*--', label = str(distances[1])+'m')
plt.plot(df.vel_date, df.vel3, '*--', label = str(distances[2])+'m')
plt.title('Tyndall glacier velocites at distance from terminus')
plt.xlabel('Date')
plt.ylabel('Velocity (units?)')
plt.legend()
plt.show()
