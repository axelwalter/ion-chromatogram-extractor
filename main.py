import tkinter as tk
from tkinter.scrolledtext import *
from tkinter import ttk
from tkinter import filedialog as fd
from pyopenms import *
import json
import os
import matplotlib.pyplot as plt
import pandas as pd

output_directory = ''

def open_masses():
    filename = fd.askopenfilename(filetypes=[('Text files', '*.txt')])
    with open(filename,'r') as f:
        massesText.delete('1.0','end')
        massesText.insert('end',f.read())
        logText.insert('end','Opened mass file: '+filename+'\n')
        logText.yview('end')

def save_masses():
    filename = fd.asksaveasfilename(filetypes=[('Text files', '*.txt')])
    with open(filename, 'w') as f:
        f.write(massesText.get('1.0','end'))
        logText.insert('end','Saved mass file: '+filename+'\n')
        logText.yview('end')
        

def open_mzML():
    filenames = fd.askopenfilenames(filetypes=[('mzML Files', '*.mzML')])
    for filename in filenames:
        mzMLFilesText.insert('end',filename+'\n')

def select_output_directory():
    global output_directory 
    output_directory = fd.askdirectory()
    logText.insert('end','Selected output directory: '+output_directory+'\n')
    logText.yview('end')

def extract_chromatograms():
    if output_directory == '':
        logText.insert('end','ERROR: Select an output directory!'+'\n')
        logText.yview('end')
        return

    inputfiles = [inputfile for inputfile in mzMLFilesText.get('1.0','end').split('\n') if inputfile != '']
    masses = set([float(mass) for mass in massesText.get('1.0','end').split('\n') if mass != ''])
    extraction_window = float(extractionWindowText.get())

    for inputfile in inputfiles:
        logText.insert('end','Loading MS experiment '+os.path.basename(inputfile)+' ...'+'\n')
        logText.yview('end')
        exp = MSExperiment()
        MzMLFile().load(inputfile, exp)

        logText.insert('end','Extracting chromatograms...'+'\n')
        logText.yview('end')

        result = {'BPC':{'rt':[],'i':[]}, 'EIC':[]}
        
        # get BPC always
        for spec in exp:
            mzs, intensities = spec.get_peaks()
            result['BPC']['rt'].append(spec.getRT())
            result['BPC']['i'].append(int(max(intensities)))

        # get EICs
        for mass in masses:
            rts = []
            ints = []
            for spec in exp:
                mzs, intensities = spec.get_peaks()
                rts.append(spec.getRT())
                index_highest_peak_within_window = spec.findHighestInWindow(mass,extraction_window,extraction_window)
                if index_highest_peak_within_window > -1:
                    ints.append(spec[index_highest_peak_within_window].getIntensity())
                else:
                    ints.append(0)
            result['EIC'].append({'mass': mass, 'rt': rts, 'i': ints})

        with open(os.path.join(output_directory,os.path.basename(inputfile)[:-4]+'json'), 'w') as f:
            json.dump(result, f, indent=4)
            logText.insert('end','SUCCESS: Saved EICs from '+os.path.basename(inputfile)+'\n')
            logText.yview('end')

    logText.insert('end','SUCCESS: Extracted Chromatograms from all mzML files!'+'\n')
    logText.yview('end')

def view_chromatograms():
    logText.insert('end','Viewing chromatograms...'+'\n')
    logText.yview('end')
    if os.path.isdir(output_directory):
        filenames = [filename for filename in os.listdir(output_directory) if filename.endswith('.json')]
        for filename in filenames:
            with open(os.path.join(output_directory, filename),'r') as f:
                data = json.load(f)
            plt.plot(data['BPC']['rt'],data['BPC']['i'],label='BPC', color='#DDDDDD')
            for eic in data['EIC']:
                plt.plot(eic['rt'],eic['i'],label=eic['mass'])
            plt.legend()
            plt.ylabel('intensity (cps)')
            plt.xlabel('time (s)')
            plt.title(os.path.basename(filename)[:-5])
            plt.ticklabel_format(axis='y',style='sci',scilimits=(0,0),useMathText=True)
            plt.show()
    else:
        logText.insert('end','No files in output directory. Perhaps you need to select a directory first?'+'\n')
        logText.yview('end')
    logText.insert('end','SUCCESS: All Chromatograms have been plotted!'+'\n')
    logText.yview('end')    

def convert_output_to_excel():
    if tk.messagebox.askokcancel(title='Warning!', message='''This will convert all JSON output files to excel file format.
                                                You will not be able to view your plots afterwards.
                                                
                                                Do you wish to proceed?'''):
        logText.insert('end','Converting output files to excel file format...'+'\n')
        logText.yview('end')
        if os.path.isdir(output_directory):
            filenames = [filename for filename in os.listdir(output_directory) if filename.endswith('.json')]
            for filename in filenames:
                with open(os.path.join(output_directory, filename),'r') as f:
                    data = json.load(f)                
                df = pd.DataFrame()
                df['time'] = data['BPC']['rt']
                for eic in data['EIC']:
                    df[eic['mass']] = eic['i']
                df.to_excel(os.path.join(output_directory, filename[:-4]+'xlsx'), index=False)
                os.remove(os.path.join(output_directory, filename))
        logText.insert('end','SUCCESS: Converted all files to excel file format...'+'\n')
        logText.yview('end')

root = tk.Tk(className='Ion Chromatogram Extractor')
root.geometry('1000x600')

massesLabel = tk.Label(text="exact masses")
massesLabel.place(x = 10, y = 2)
massesText = tk.Text()
massesText.place(x = 5, y = 20, height = 490, width = 100)

mzMLFilesLabel = tk.Label(text='mzML files')
mzMLFilesLabel.place(x = 520, y = 2)
mzMLFilesText = tk.Text()
mzMLFilesText.place(x = 110, y = 20, height = 235, width = 885)

logLabel = tk.Label(text="log")
logLabel.place(x = 520, y = 255)
logText = ScrolledText()
logText.place(x = 110, y = 275, height = 235, width = 885)

openMassesButton = tk.Button(text='Open Masses', command=open_masses)
openMassesButton.place(x = 10, y = 520)

saveMassesButton = tk.Button(text='Save Masses', command=save_masses)
saveMassesButton.place(x = 10, y = 560)

openMassesButton = tk.Button(text='Open mzML Files', command=open_mzML)
openMassesButton.place(x = 150, y = 520)

openMassesButton = tk.Button(text='Select Output Directory', command=select_output_directory)
openMassesButton.place(x = 320, y = 520)

openMassesButton = tk.Button(text='Convert Output Files to Excel', command=convert_output_to_excel)
openMassesButton.place(x = 320, y = 560)

openMassesButton = tk.Button(text='Extract Chromatograms', command=extract_chromatograms)
openMassesButton.place(x = 800, y = 520)

openMassesButton = tk.Button(text='View Chromatograms', command=view_chromatograms)
openMassesButton.place(x = 807, y = 560)

extractionWindowLabel = tk.Label(text='extraction\nwindow') 
extractionWindowLabel.place(x = 690, y = 520)
extractionWindowLabel1 = tk.Label(text='m/z')
extractionWindowLabel1.place(x = 750, y = 560)
extractionWindowText = tk.Entry()
extractionWindowText.place(x = 700, y = 560,width=50)
extractionWindowText.insert('end','0.02')

tk.mainloop()