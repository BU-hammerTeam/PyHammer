%load_ext autoreload
%autoreload 2

import numpy as np

from pyhamimports import *
from spectrum import Spectrum
from eyecheck import Eyecheck
from gui_utils import *
import glob

singleTemp_dir = "/Users/benjaminroulston/Dropbox/GitHub/PyHammer/resources/templates/"
SB2Temp_dir = "/Users/benjaminroulston/Dropbox/GitHub/PyHammer/resources/templates_SB2/"

singleTemp_list = np.array([os.path.basename(x) for x in glob.glob(singleTemp_dir+"*.fits")])
singleTemp_list.sort()

SB2Temp_list = np.array([os.path.basename(x) for x in glob.glob(SB2Temp_dir+"*.fits")])
SB2Temp_list.sort()
#singleTemp_list = np.genfromtxt("/Users/benjaminroulston/Dropbox/GitHub/PyHammer/resources/list_of_single_temps.txt",dtype="U")
#SB2Temp_list = np.genfromtxt("/Users/benjaminroulston/Dropbox/GitHub/PyHammer/resources/list_of_SB2_temps.txt", dtype="U")

# 0, 1, 2, 3, 4, 5, 6, 7 = O, B, A, F, G, K, M, L
single_letter_specTypes = np.array(['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'C', 'W'])
specTypes = np.array(['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'C', 'WD'])

new_tempLines_0 = np.empty(singleTemp_list.size, dtype=int)
new_tempLines_1 = np.empty(singleTemp_list.size, dtype=int)
new_tempLines_2 = np.empty(singleTemp_list.size, dtype=np.float64)
new_tempLines_3 = np.ones(singleTemp_list.size, dtype=int) * 5
new_tempLines_4 = []

for ii in range(singleTemp_list.size):
    new_tempLines_0[ii] = np.where(single_letter_specTypes == singleTemp_list[ii][0])[0][0]
    if new_tempLines_0[ii]==9:
        new_tempLines_1[ii] = singleTemp_list[ii][2]
    else:
        new_tempLines_1[ii] = singleTemp_list[ii][1]
    if len(singleTemp_list[ii].replace("_"," ").split()) == 1:
        new_tempLines_2[ii] = 0.
    else:
        new_tempLines_2[ii] = np.float64(singleTemp_list[ii].replace("_"," ").split()[1])

spec = Spectrum()
ftype = None
for ii in range(singleTemp_list.size):
    message, ftype = spec.readFile(singleTemp_dir+singleTemp_list[ii], ftype)
    spec._lines = spec.measureLines()
    lines = np.array(list(spec._lines.values()))[np.argsort(list(spec._lines.keys()))]
    new_tempLines_4.append(lines)

SB2_index_start = new_tempLines_0.max()+1#10
new_tempLines_0 = np.append(new_tempLines_0, np.arange(SB2_index_start, SB2_index_start+SB2Temp_list.size, step=1))
new_tempLines_1 = np.append(new_tempLines_1, np.zeros(SB2Temp_list.size))
new_tempLines_2 = np.append(new_tempLines_2, np.zeros(SB2Temp_list.size))
new_tempLines_3 = np.append(new_tempLines_3, np.ones(SB2Temp_list.size)*5)
#new_tempLines_4 = new_tempLines_4

spec = Spectrum()
ftype = None
for ii, filename in enumerate(SB2Temp_list):
    #temp_list = []
    message, ftype = spec.readFile(SB2Temp_dir+filename, ftype)
    measuredLines = spec.measureLines()
    spec._lines = measuredLines
    lines = np.array(list(spec._lines.values()))[np.argsort(list(spec._lines.keys()))]
    linesLabels = np.array(list(spec._lines.keys()))[np.argsort(list(spec._lines.keys()))]
    #temp_list.append(lines)
    new_tempLines_4.append(lines)

new_tempLines = [new_tempLines_0, new_tempLines_1, new_tempLines_2, new_tempLines_3, new_tempLines_4]

pklPath = os.path.join(spec.thisDir, 'resources', 'tempLines_04-07-2020.pickle')
with open(pklPath, 'wb') as pklFile:
    pickle.dump(new_tempLines, pklFile)
