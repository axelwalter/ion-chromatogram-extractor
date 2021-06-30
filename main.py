with open('tests/compounds.txt','r') as f:
    masses = [float(mass.strip()) for mass in f.readlines()]

exp_path = '/home/axel/Documents/HPLC-MS-Data/mzML/CHI_Chitinase.mzML'
# /home/axel/Documents/HPLC-MS-Data/mzML/CHI_Chitinase.mzML
mass_tolerance = 0.05 # (mz)
from pyopenms import *
import numpy as np

print('loading MS experiment...')
exp = MSExperiment()
MzMLFile().load(exp_path, exp)

result = {}
for mass in masses:
    result[mass] = {'rt':[], 'i':[]}

total = exp.getNrSpectra()
counter = 1
for spec in exp:
    print(str(counter),'/',str(total))
    mzs, intensities = spec.get_peaks()
    for mass in masses:
        result[mass]['rt'].append(spec.getRT())
        index_highest_peak_within_window = spec.findHighestInWindow(mass,0.02,0.02)
        if index_highest_peak_within_window > -1:
            result[mass]['i'].append(spec[index_highest_peak_within_window].getIntensity())
        else:
            result[mass]['i'].append(0)
    counter += 1

import json
with open(exp_path[:-4]+'json', 'w') as f:
    json.dump(result, f, indent=4)

import matplotlib.pyplot as plt

with open(exp_path[:-4]+'json') as f:
    data = json.load(f)

for name, chrom in data.items():
    plt.plot(chrom['rt'], chrom['i'], label = name)

plt.legend()
plt.show()
