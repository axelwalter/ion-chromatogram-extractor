# ion-chromatogram-extractor
Extract ion chromatograms from a mzML file using pyOpenMS and store retention time and intensity values.

A list of exact masses for extraction can be loaded from a .txt file or entered directly, which a single mass
in each line. A basepeak chromatogram (BPC) will always be calculated. The mass list can be stored for later use
in a text file.
The sample (mzML file) path names need to be specified each in a separate line.
An output directory needs to be selected. Here the results will be stored in JSON format with a single file for each
mzML sample file.
The output files can be inspected and the chromatograms will be plotted with matplotlib.
A convienient feature for the conversion of JSON output files to Excel files is provided as well.

Prerequisite python packages are pyopenms, matplotlib, pandas and openpyxl.

The main functionality in this tool is derived from pyOpenMS!
https://www.openms.de/
https://github.com/OpenMS/OpenMS
