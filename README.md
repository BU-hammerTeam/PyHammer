# New_Hammer
BU_pycon's new hammer code: A Python Spectral Typing Suite (modeled after Covey+07: The Hammer)

CURRENTLY UNDER DEVELOPMENT, USE AT OWN RISK!

RUNNING THE CODE: In the New\_Hammer folder, run pyHammer by typing python pyHammer.py. The first time you run the code type python pyHammer.py -h to see all the options available to run. For each run, you will need an input file that contains a list of all the spectra you would like to classify, along with what filetype each one is. An example of this file is available (test_case/exampleInputFile.txt). The filetypes accepted are .txt, .csv, SDSS EDR - DR8 (DR7fits), SDSS DR9 - DR12 (DR12fits), fits. 


KNOWN ISSUES: 
1.) When running the GUI, some computers crash, display this (and many more) error becuase of a problem with the maplotlib backend: 
-[NSApplication _setup:]: unrecognized selector sent to instance 0x10c138de0

We have not found a universal fix at the moment since implementing the following fix on some computers crashes the code. If you are running into this error go into eyecheck.py and uncomment the import matplotlib, matplotlib.use("TkAgg") lines. This should fix the problem


