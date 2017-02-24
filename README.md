# PyHammer

[![GitHub release](https://img.shields.io/github/release/BU-hammerTeam/PyHammer.svg)](https://github.com/BU-hammerTeam/PyHammer/releases/latest)
[![GitHub commits](https://img.shields.io/github/commits-since/BU-hammerTeam/PyHammer/v1.0.svg)](https://github.com/BU-hammerTeam/PyHammer/commits/master)
[![GitHub issues](https://img.shields.io/github/issues/BU-hammerTeam/PyHammer.svg)](https://github.com/BU-hammerTeam/PyHammer/issues)
[![license](https://img.shields.io/github/license/BU-hammerTeam/PyHammer.svg)](https://github.com/BU-hammerTeam/PyHammer/blob/master/license.txt)
[![Python Supported](https://img.shields.io/badge/Python%20Supported-3-brightgreen.svg)](conda)
[![Maintenance](https://img.shields.io/maintenance/yes/2017.svg)]()

###A Python Spectral Typing Suite 

PyHammer is a tool developed to allow rapid and automatic spectral classification of stars according to the Morgan-Keenan classification system. Working in the range of 3,650 - 10,200 Angstroms, the automatic spectral typing algorithm compares important spectral lines to template spectra and determines the best matching spectral type, ranging from O to L type stars. This tool has the additional features that it can determine a star's metallicity ([Fe/H]) and radial velocity shifts. Once the automatic classification algorithm has run, PyHammer provides the user an interface for determining spectral types visually by comparing their spectra to provided templates.

Modeled after [The Hammer: An IDL Spectral Typing Suite][thehammer] published in [Covey et al. 2007][covey+07] available on [GitHub][hammerGitHub]

##Requirements

PyHammer is written in and should be run with **Python 3**. It *will not* work in Python 2.

####Python Module Dependencies

PyHammer relies on several core Python modules as well as third party modules. It is suggested that Python be installed with [Anaconda][conda], which comes packaged with all required modules. The table below lists all third party modules as well as suggested minimum versions. Modules can be upgraded through the commands `pip install --upgrade <module_name>` or else `conda update <module_name>` if Anaconda is installed.

| Module   | Minimum Version | Command to Check Version<sup>1</sup>      |
|:--------:|:----------------|:------------------------------------------|
|NumPy     | 1.11            |`import numpy; numpy.__version__`          |
|SciPy     | 0.18            |`import scipy; scipy.__version__`          |
|Matplotlib| 1.5             |`import matplotlib; matplotlib.__version__`|
|TkInter   | 8               |`import tkinter; tkinter.TkVersion`        |
|AstroPy   | 1.2.1           |`import astropy; astropy.__version__`      |
<sup>1</sup>Commands are run in Python environment

####Inputs

Before running the program, you need an input file to specify which spectrum to classify. The input file can be created either beforehand as a text or csv file and choosing that file (by clicking `Browse` in the GUI), or else created in the program itself (by clicking `Create` in the GUI). The input file format should be to list the filenames of the spectra you want to classify in the first column and the spectrum data types in the second column. The spectrum filenames can have the full path specified or a common path for all spectra files can be specified during execution.

The [example input file](/test_case/exampleInputFile.txt) in the [test_case](/test_case) directory is defined below for reference.

    test_case/spec-0618-52049-0372.fits SDSSdr12
    test_case/spec-1079-52621-0509.fits SDSSdr12
    test_case/spec-1123-52882-0065.fits SDSSdr12
    test_case/spec-4068-55445-0924.fits SDSSdr12
    test_case/spec-4961-55719-0378.fits SDSSdr12
    test_case/spec-7332-56683-0788.fits SDSSdr12
    test_case/spec-7454-56751-0770.fits SDSSdr12
    test_case/spec-5047-55833-0936.fits SDSSdr12
    test_case/spec-3764-55514-0972.fits SDSSdr12
    
All the spectra need to be in Angstroms, and must cover part (but not all) of the region between 3650 and 10200 Angstroms. The following spectrum data types are accepted.

 - `SDSSdr7` – Fits files given by the Sloan Digital Sky Survey's Early Data Release through Data Release 8
 - `SDSSdr12` – Fits files given by Sloan Digital Sky Survey's Data Release 9 through Data Release 13. 
 - `fits` – Fits files created with IRAF or PyRAF. 
 - `txt` – Files must have at least two columns containing wavelength (in Angstroms) in the first column and flux in the second column. An optional third column can be provided containing the error. If this is not provided, it will be calculated.
 - `csv` – Files should have the same format as the `txt` files with columns separated by commas rather than spaces, first having wavelength, then flux, and an optional error in the third column.

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

##FAQ

1. **What wavelength range can this classify over?**

   The templates used to classify your spectra are defined over the range 3,650 to 10,200 Angstroms. The process for classifying involves matching on specifically chosen spectral lines which range from 3,925 Angstroms to 10,000 Angstroms. Your spectrum should be defined for at least part of that range, although it need not span the full range and can be defined outside that range. Small wavelength coverage can lead to less accurate radial velocity, metallicity and spectral type estimates however. 

2. **Why is a template not showing during the eyecheck process?**

   The templates were compiled by averaging SDSS DR12 spectra for each spectral and metallicity type. In some cases, not enough spectra existed to provide a template. If you choose a spectral type in the eyecheck program for which a template is not available, nothing will be shown.

3. **I'm seeing an output of the form _setCanCycle: is deprecated.  Please use setCollectionBehavior instead_. What is this?**
   
   This is a warning output by the tkinter module for Mac users using the Anaconda distribution. It is a known warning as a result of their compiling tkinter into the distribution under an older version of OS X. It causes no issues or problems and can be ignored.

4. **Why can't I choose to classify my spectra as K8 or K9?**

   It is a general consensus (though by no means unanimous, ref. [Johnson & Morgan 1953][Johnson_Morgan], [Keenan & McNeil 1989](Keenan_McNeil)) that the K8 and K9 stellar types are sufficiently similar to their neighboring spectral types that they need not exist. Instead, the spectral classification jumps from K7 directly to M0. As such, we disallow selecting those spectral types in the eyecheck GUI. Corresondingly, the automatic spectral typing algorithm will not match to a K8 or K9 spectral type.
  
5. **Can I use my own templates?**
   
   Yes. You can choose to replace the templates in the [template directory](/resources/templates), or else provide your own for the templates which don't exist. Note however, that templates must conform to specific conventions.

   a. In order to be recognized, the filename must take one of three forms: `SS.fits`, `SS_+M.M.fits`, `SS_+M.M_Dwarf.fits`. In these names, `SS` is the spectral type and subtype (e.g., M5) and `+M.M` is the [Fe/H] metallicity where you must specify the sign, either positive or negative (0.0 is considered positive) (e.g., +0.0, -0.5, +1.0).
   
   b. The template itself must be configured such that it is "normalized" to the flux at 8000 Angstroms. In other words, the flux in the template file must be divided by the flux at 8000 Angstroms, making the flux at that point equal to one.

##Publications

This project and accompanying work is described Appendix A in Kesseli et al. (2017). This paper is also published at  	[arXiv:1702.06957][arXiv_version]. If you use the program, please cite Kesseli et al. (2017). 

##Acknowledgements

This project was developed by a select group of graduate students at the Department of Astronomy at Boston University. The project was lead by Aurora Kesseli with development help and advice provided by Andrew West, Mark Veyette, Brandon Harrison, and Dan Feldman. Contributions were further provided by Dylan Morgan, Chris Theissen, and Connor Robinson.

![Boston University Logo](https://www.bu.edu/brand/files/2012/10/BU-Master-Logo.gif "Boston University")

[thehammer]: http://myweb.facstaff.wwu.edu/~coveyk/thehammer.html
[covey+07]: http://adsabs.harvard.edu/abs/2007AJ....134.2398C
[hammerGitHub]: https://github.com/jradavenport/TheHammer
[conda]: https://www.continuum.io/downloads
[backend_problem]: https://github.com/mperrin/webbpsf/issues/103
[Johnson_Morgan]: http://adsabs.harvard.edu/abs/1953ApJ...117..313J
[Keenan_McNeil]: http://adsabs.harvard.edu/abs/1989ApJS...71..245K
[arXiv_version]: https://arxiv.org/abs/1702.06957
