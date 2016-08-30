###_CURRENTLY UNDER DEVELOPMENT, USE AT OWN RISK!_

# PyHammer

###A Python Spectral Typing Suite 

PyHammer is a tool developed to allow rapid and automatic spectral classification of stars according to the Morgan-Keenan classification system. Working in the range of 3,650 - 10,200 Angstroms, the automatic spectral typing algorithm compares important spectral lines to template spectra and determines the best matching spectral type, ranging from O to L type stars. This tool has the additional features that it can determine a star's metallicity and radial velocity shifts. Once the automatic classification algorithm has run, PyHammer provides the user an interface for determine spectral types for themselves by comparing their spectra to provided templates.

Modeled after [The Hammer: An IDL Spectral Typing Suite][thehammer] published in [Covey et al. 2007][covey+07]

##Requirements

PyHammer is written in and should be run with **Python 3**. It *will not* work in Python 2.

####Python Module Dependencies

PyHammer relies on several core Python modules as well as third party modules. It is suggested that Python be installed with [Anaconda][conda], which comes packaged with all required modules. The table below lists all third party modules as well as suggested versions. Modules can be upgraded through the commands `pip install --upgrade <module_name>` or else `conda update <module_name>` if Anaconda is installed.

| Module   | Suggested Version | Command to Check Version<sup>1</sup>      |
|:--------:|:------------------|:------------------------------------------|
|NumPy     | 1.11              |`import numpy; numpy.__version__`          |
|SciPy     | 0.18              |`import scipy; scipy.__version__`          |
|Matplotlib| 1.5               |`import matplotlib; matplotlib.__version__`|
|TkInter   | 8                 |`import tkinter; tkinter.TkVersion`        |
|AstroPy   | 1.2.1             |`import astropy; astropy.__version__`      |
<sup>1</sup>Commands are run in Python environment

##Running PyHammer

On the command line, navigate to the PyHammer folder and run with the command `python pyhammer.py`. In the ipython environment, the command `run pyhammer.py` can be used. This code should not be imported!

The first time you run the code, you can supply the flag `-h` to see all options and flags available to the run command. By default, PyHammer will run in GUI mode, but command line mode can be used with the `-c` flag.

For each run, you will need an input file that contains a list of all the spectra fits files you would like to classify, along with which fits data type each file is. The fits data types accepted are  `DR7fits` (SDSS EDR - DR8), `DR12fits` (SDSS DR9 - DR12), `fits`, `txt`, and `csv`.

####Test Case

An [example input file](/test_case/exampleInputFile.txt) along with a set of ten corresponding spectra are located in the [test_case](/test_case) directory. Run this test case from the command line with the following command.

    python pyhammer.py -f -i test_case/exampleInputFile.txt

From the ipython environment use the following command.

    run pyhammer.py -f -i test_case/exampleInputFile.txt

##Publications

This project and accompanying work is described Appendix A in Kesseli et al. (in prep.)

##Acknowledgements

This project was developed by a select group of graduate students at the Department of Astronomy at Boston University. The project was lead by Aurora Kesseli with development help and advice provided by Andrew West, Mark Veyette, Brandon Harrison, and Dan Feldman. Contributions were further provided by Dylan Morgan and Chris Theissen.

![Boston University Logo](https://www.bu.edu/brand/files/2012/10/BU-Master-Logo.gif "Boston University")

[thehammer]: http://myweb.facstaff.wwu.edu/~coveyk/thehammer.html
[covey+07]: http://adsabs.harvard.edu/abs/2007AJ....134.2398C
[conda]: https://www.continuum.io/downloads
[backend_problem]: https://github.com/mperrin/webbpsf/issues/103
