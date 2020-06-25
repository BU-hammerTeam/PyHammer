# %load_ext autoreload
# %autoreload 2

import numpy as np

from pyhamimports import *
from spectrum import Spectrum
import glob
from tqdm import tqdm
from subprocess import check_output

datestr = check_output(["/bin/date","+%F"])
datestr = datestr.decode().replace('\n', '')

singleTemp_dir = "resources/templates/"
SB2Temp_dir = "resources/templates_SB2/"

singleTemp_list = np.array([os.path.basename(x)
                            for x in glob.glob(singleTemp_dir + "*.fits")])
singleTemp_list.sort()

SB2Temp_list = np.array([os.path.basename(x)
                         for x in glob.glob(SB2Temp_dir + "*.fits")])
SB2Temp_list.sort()

# 0, 1, 2, 3, 4, 5, 6, 7, 8, 9 = O, B, A, F, G, K, M, L, C, WD
single_letter_specTypes = np.array(['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'C', 'D'])
specTypes = np.array(['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'dC', 'DA'])

new_tempLines_0 = np.empty(singleTemp_list.size, dtype=int)
new_tempLines_1 = np.empty(singleTemp_list.size, dtype=np.float64)
new_tempLines_2 = np.empty(singleTemp_list.size, dtype=np.float64)
new_tempLines_3 = np.ones(singleTemp_list.size, dtype=int) * 5
new_tempLines_4 = []

for ii in range(singleTemp_list.size):
    new_tempLines_0[ii] = np.where(
        single_letter_specTypes == singleTemp_list[ii][0])[0][0]
    if new_tempLines_0[ii] == 9:
        new_tempLines_1[ii] = spec.splitSpecType(singleTemp_list[ii].replace(".fits", ""))[1]
    else:
        new_tempLines_1[ii] = singleTemp_list[ii][1]
    if len(singleTemp_list[ii].replace("_", " ").split()) == 1:
        new_tempLines_2[ii] = 0.
    else:
        new_tempLines_2[ii] = np.float64(
            singleTemp_list[ii].replace("_", " ").split()[1])

spec = Spectrum()
ftype = None
print("Measuring lines for single star templates:")
for ii in tqdm(range(singleTemp_list.size)):
    message, ftype = spec.readFile(singleTemp_dir + singleTemp_list[ii], ftype)
    spec._lines = spec.measureLines()
    lines = np.array(list(spec._lines.values()))[
        np.argsort(list(spec._lines.keys()))]
    new_tempLines_4.append(lines)

SB2_index_start = new_tempLines_0.max() + 1  # 10
new_tempLines_0 = np.append(new_tempLines_0, np.arange(
    SB2_index_start, SB2_index_start + SB2Temp_list.size, step=1))
new_tempLines_1 = np.append(new_tempLines_1, np.zeros(SB2Temp_list.size))
new_tempLines_2 = np.append(new_tempLines_2, np.zeros(SB2Temp_list.size))
new_tempLines_3 = np.append(new_tempLines_3, np.ones(SB2Temp_list.size) * 5)
# new_tempLines_4 = new_tempLines_4

spec = Spectrum()
ftype = None
print("Measuring lines for SB2 templates:")
for ii, filename in enumerate(tqdm(SB2Temp_list)):
    # temp_list = []
    message, ftype = spec.readFile(SB2Temp_dir + filename, ftype)
    measuredLines = spec.measureLines()
    spec._lines = measuredLines
    lines = np.array(list(spec._lines.values()))[
        np.argsort(list(spec._lines.keys()))]
    linesLabels = np.array(list(spec._lines.keys()))[
        np.argsort(list(spec._lines.keys()))]
    # temp_list.append(lines)
    new_tempLines_4.append(lines)

new_tempLines = [new_tempLines_0, new_tempLines_1,
                 new_tempLines_2, new_tempLines_3, new_tempLines_4]

pklPath = os.path.join(spec.thisDir, 'resources',
                       f'tempLines_{datestr}.pickle')
with open(pklPath, 'wb') as pklFile:
    pickle.dump(new_tempLines, pklFile)
