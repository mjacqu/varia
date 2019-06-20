import rasterio
import numpy as np
from osgeo import gdal
import argparse

parser = argparse.ArgumentParser(description='Mask E-W and N-S displacement bands'
            ' with Signal-to-Noise ratio (SNR) and compute displacement magnitude from'
            ' COSI Corr inputs (ENVI files)')
parser.add_argument('-snr', action = 'store', type = float,
                        default = 0.9, help='set SNR threshold (default 0.9)')
parser.add_argument('src', metavar = 'src_file', action = 'store', type=str,
                        help='input file path')
parser.add_argument('dst', metavar = 'dst_file', action = 'store', type=str,
                        help='output file path')

inps = parser.parse_args()
print('snr     =', inps.snr)
print ('input   =', inps.src)
print ('output   =', inps.dst)

SNR = inps.snr
in_file = inps.src

rasterio.open(in_file, mode='r', driver='ENVI')
with rasterio.open(in_file, mode='r', driver='ENVI') as src:
    data = src.read()
    metadata = src.profile

data[0][data[2] < SNR] = np.nan
data[1][data[2] < SNR] = np.nan
magnitude = np.expand_dims(np.sqrt(data[0]**2 + data[1]**2), axis = 0) #magnitude
data = np.concatenate((data, magnitude), axis = 0)

metadata['driver'] = 'GTiff'
metadata['count'] = 4

with rasterio.open(inps.dst, 'w', **metadata) as dst:
    dst.set_band_description(1, 'East-West masked')
    dst.set_band_description(2, 'North-South masked')
    dst.set_band_description(3, 'SNR')
    dst.set_band_description(4, 'Magnitude')
    dst.write(data)
