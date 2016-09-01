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

####Inputs

Before running the program, you need an input file to specify which spectrum to classify. The input file can be created either before hand as a text or csv file, or else in the program itself. The input file format should be to list the filenames of the spectra you want to classify in the first column and the spectrum data types in the second column. The spectra filenames can have the full path specified or a common path for all spectra files can be specified during execution. The spectrum data types accepted are  `DR7fits` (SDSS EDR - DR8), `DR12fits` (SDSS DR9 - DR12), `fits`, `txt`, and `csv`. 

The [example input file](/test_case/exampleInputFile.txt) in the [test_case](/test_case) directory is defined below for reference.

    test_case/spec-0618-52049-0372.fits DR12fits
    test_case/spec-1079-52621-0509.fits DR12fits
    test_case/spec-1123-52882-0065.fits DR12fits
    test_case/spec-4068-55445-0924.fits DR12fits
    test_case/spec-4961-55719-0378.fits DR12fits
    test_case/spec-7332-56683-0788.fits DR12fits
    test_case/spec-7454-56751-0770.fits DR12fits
    test_case/spec-5047-55833-0936.fits DR12fits
    test_case/spec-3764-55514-0972.fits DR12fits

##Running PyHammer

On the command line, navigate to the PyHammer folder and run with the command `python pyhammer.py`. In the ipython environment, the command `run pyhammer.py` can be used. This code should not be imported!

Along with the run command, various flags and command line options can be provided. The first time you run the code, you can supply the flag `-h` to see all options and flags available to the run command. By default, PyHammer will run in GUI mode, but command line mode can be used with the `-c` flag. A list of all options is shown below

    Options             Description
    -c, --cmd           Flag to choose to run on the command line.
    -e, --eyecheck      Flag indicating pyhammer should skip classifying
                        and go straight to checking the spectra by eye.
    -f, --full          Flag indicating the full path to the spectra is
                        provided in the input file list.
    -g, --gui           Flag to choose to run using the gui.
    -i, --infile        The full path to the input file or the name, if it
                        is in the pyhammer folder. If nothing is
                        provided, it will be asked for later.
    -o, --outfile       The full path to the output file or a filename
                        which outputs to the pyhammer folder. If nothing is
                        provided, the default pyhammerResults.csv will be
                        created in the pyhammer folder.
    -p, --path          The full path to the spectra. This is only necessary
                        if the input file list does not prepend the path to
                        the spectra filenames.
    -r, --rejectfile    The full path to the file where reject spectra will
                        be listed or a filename which outputs to the
                        pyhammer folder . If nothing is provided, the
                        default rejectSpectra.csv will be created in the
                        pyhammer folder.
    -s, --sncut         The S/N necessary before a spectra will be classified.
                        A signal to noise of ~3-5 per pixel is recommended.

####Test Case

In the [test_case](/test_case) directory is an example input file and a set of 10 corresponding spectra. Run this test case from the command line with the following command.

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
