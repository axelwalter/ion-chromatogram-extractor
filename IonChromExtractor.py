import tkinter as tk
from tkinter.constants import DISABLED
from tkinter.scrolledtext import *
from tkinter import StringVar, ttk
from tkinter import filedialog as fd
from pyopenms import *
import json
import os
import matplotlib.pyplot as plt
import pandas as pd

output_directory = ''
mzMLFiles = []

def open_masses():
    filename = fd.askopenfilename(filetypes=[('Text files', '*.txt')])
    with open(filename,'r') as f:
        massesText.delete('1.0','end')
        massesText.insert('end',f.read())
        print('Opened mass file: '+filename)

def save_masses():
    filename = fd.asksaveasfilename(filetypes=[('Text files', '*.txt')])
    if filename != '':
        with open(filename, 'w') as f:
            f.write(massesText.get('1.0','end'))
            print('Saved mass file: '+filename)

def open_mzML():
    filenames = fd.askopenfilenames(filetypes=[('mzML Files', '*.mzML')])
    global mzMLFiles
    mzMLFiles += filenames
    mzMLFilesText.config(state='normal')
    mzMLFilesText.delete('1.0','end')
    mzMLFilesText.insert('end','\n'.join(mzMLFiles))
    mzMLFilesText.config(state='disabled')

def clear_mzML_files():
    mzMLFilesText.config(state='normal')
    mzMLFilesText.delete('1.0','end')
    mzMLFilesText.config(state='disabled')
    global mzMLFiles
    mzMLFiles = []
    
def select_output_directory():
    global output_directory 
    output_directory = fd.askdirectory()
    print('Selected output directory: '+output_directory)

def extract_chromatograms():
    if output_directory == '':
        print('ERROR: Select an output directory!')
        return

    masses = []
    names = []
    for line in [line for line in massesText.get('1.0','end').split('\n') if line != '']:
        if '=' in line:
            mass, name = line.split('=')
        else:
            mass = line
            name = ''
        masses.append(float(mass.strip()))
        names.append(name.strip())
    extraction_window = float(extractionWindowText.get())

    print('Loading MS experiments. This may take a while...')
    for inputfile in mzMLFiles:
        print('Loading '+inputfile+' ...')
        exp = MSExperiment()
        MzMLFile().load(inputfile, exp)

        result = {'BPC':{'rt':[],'i':[]}, 'EIC':[]}
        
        # get BPC always
        for spec in exp:
            mzs, intensities = spec.get_peaks()
            result['BPC']['rt'].append(spec.getRT())
            result['BPC']['i'].append(int(max(intensities)))

        # get EICs
        for mass, name in zip(masses, names):
            rts = []
            ints = []
            for spec in exp:
                _, intensities = spec.get_peaks()
                rts.append(spec.getRT())
                index_highest_peak_within_window = spec.findHighestInWindow(mass,extraction_window,extraction_window)
                if index_highest_peak_within_window > -1:
                    ints.append(spec[index_highest_peak_within_window].getIntensity())
                else:
                    ints.append(0)
            result['EIC'].append({'mass': mass, 'name': name, 'rt': rts, 'i': ints})

        with open(os.path.join(output_directory,os.path.basename(inputfile)[:-4]+'json'), 'w') as f:
            json.dump(result, f, indent=4)
            print('SUCCESS: Saved EICs from '+os.path.basename(inputfile))

    print('SUCCESS: Extracted Chromatograms from all mzML files!')

def view_chromatograms():
    print('Plotting chromatograms...')
    if os.path.isdir(output_directory):
        filenames = [filename for filename in os.listdir(output_directory) if filename.endswith('.json')]
        for filename in filenames:
            with open(os.path.join(output_directory, filename),'r') as f:
                data = json.load(f)
            f, ax = plt.subplots()
            ax.plot(data['BPC']['rt'],data['BPC']['i'],label='BPC', color='#DDDDDD')
            ax1 = ax.twinx()
            for eic in data['EIC']:
                ax1.plot(eic['rt'],eic['i'],label=eic['name']+' '+str(eic['mass']))
            ax1.legend(loc='upper right')
            ax.set_ylabel('BPC intensity (cps)')
            ax1.set_ylabel('EIC intensity (cps)')
            ax.set_xlabel('time (s)')
            ax.set_title(os.path.basename(filename)[:-5])
            ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0),useMathText=True)
            ax1.ticklabel_format(axis='y',style='sci',scilimits=(0,0),useMathText=True)
            plt.show()
    else:
        logText.insert('end','No files in output directory. Perhaps you need to select a directory first?'+'\n')
        logText.yview('end')
    print('SUCCESS: All Chromatograms have been plotted!')   

def convert_output_to_excel():
    if tk.messagebox.askokcancel(title='Warning!', message='''This will convert all JSON output files to excel file format.
                                                You will not be able to view your plots afterwards.
                                                
                                                Do you wish to proceed?'''):
        if os.path.isdir(output_directory):
            filenames = [filename for filename in os.listdir(output_directory) if filename.endswith('.json')]
            for filename in filenames:
                with open(os.path.join(output_directory, filename),'r') as f:
                    data = json.load(f)                
                df = pd.DataFrame()
                df['time (s)'] = data['BPC']['rt']
                df['BPC'] = data['BPC']['i']
                for eic in data['EIC']:
                    df[eic['name']+'_'+str(eic['mass'])] = eic['i']
                df.to_excel(os.path.join(output_directory, filename[:-4]+'xlsx'), index=False)
                os.remove(os.path.join(output_directory, filename))
        logText.insert('end','SUCCESS: Converted all files to excel file format...'+'\n')
        logText.yview('end')

root = tk.Tk(className='Ion Chromatogram Extractor')
root.geometry('1200x350')

massesLabel = tk.Label(text="exact masses")
massesLabel.place(x = 8, y = 2)
massesText = tk.Text()
massesText.place(x = 5, y = 20, height = 330, width = 300)

mzMLFilesLabel = tk.Label(text='mzML files')
mzMLFilesLabel.place(x = 720, y = 2)
mzMLFilesText = tk.Text()
mzMLFilesText.config(state='disabled')
mzMLFilesText.place(x = 310, y = 20, height = 235, width = 885)


openMassesButton = tk.Button(text='Open Masses', command=open_masses)
openMassesButton.place(x = 310, y = 270)

saveMassesButton = tk.Button(text='Save Masses', command=save_masses)
saveMassesButton.place(x = 310, y = 310)

openFilesButton = tk.Button(text='Open mzML Files', command=open_mzML)
openFilesButton.place(x = 440, y = 270)

clearFilesButton = tk.Button(text='Clear mzML Files', command=clear_mzML_files)
clearFilesButton.place(x = 440, y = 310)

selectOutputButton = tk.Button(text='Select Output Directory', command=select_output_directory)
selectOutputButton.place(x = 640, y = 270)

convertButton = tk.Button(text='Convert Output Files to Excel', command=convert_output_to_excel)
convertButton.place(x = 640, y = 310)

extractButton = tk.Button(text='Extract Chromatograms', command=extract_chromatograms)
extractButton.place(x = 1000, y = 270)

viewButton = tk.Button(text='View Chromatograms', command=view_chromatograms)
viewButton.place(x = 1007, y = 310)

extractionWindowLabel = tk.Label(text='extraction\nwindow') 
extractionWindowLabel.place(x = 890, y = 270)
extractionWindowLabel1 = tk.Label(text='m/z')
extractionWindowLabel1.place(x = 950, y = 310)
extractionWindowText = tk.Entry()
extractionWindowText.place(x = 900, y = 310,width=50)
extractionWindowText.insert('end','0.02')

tk.mainloop()
