import numpy as np
import os
import shutil

'''
Move all directories listed in file_list to other target directory. File_list created in Photo Mechanic based on 
selection of low quality ifgs. 
'''

file_list = '/net/tiampostorage/volume1/MyleneShare/Bigsur_desc/az1rng2/ifgs_lowCoherence.txt'
target = '/net/tiampostorage/volume1/MyleneShare/Bigsur_desc/low_coherence_az1rng2'

move = np.loadtxt(file_list, dtype = str, skiprows = 1)

[shutil.move(i, target) for i in move]
