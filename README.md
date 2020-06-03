# PyHammer

[![GitHub release](https://img.shields.io/github/release/BU-hammerTeam/PyHammer.svg)](https://github.com/BU-hammerTeam/PyHammer/releases/latest)
[![GitHub commits](https://img.shields.io/github/commits-since/BU-hammerTeam/PyHammer/v2.0.0.svg)](https://github.com/BU-hammerTeam/PyHammer/commits/master)
[![GitHub issues](https://img.shields.io/github/issues/BU-hammerTeam/PyHammer.svg)](https://github.com/BU-hammerTeam/PyHammer/issues)
[![license](https://img.shields.io/github/license/BU-hammerTeam/PyHammer.svg)](https://github.com/BU-hammerTeam/PyHammer/blob/master/license.txt)
[![Python Supported](https://img.shields.io/badge/Python%20Supported-3-brightgreen.svg)](conda)
[![Maintenance](https://img.shields.io/maintenance/yes/2020.svg)]()
[![Powered by Astropy](https://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org)

### A Python Spectral Typing Suite 

PyHammer is a tool developed to allow rapid and automatic spectral classification of stars according to the Morgan-Keenan classification system. Working in the range of 3,650 - 10,200 Angstroms, the automatic spectral typing algorithm compares important spectral lines to template spectra and determines the best matching spectral type, ranging from O to L type stars. This tool has the additional features that it can determine a star's metallicity ([Fe/H]) and radial velocity shifts. Once the automatic classification algorithm has run, PyHammer provides the user an interface for determining spectral types visually by comparing their spectra to provided templates.

Version 2.0.0 of PyHammer adds the ability to spectral type double-lined spectroscopic binaries (SB2). This updates adds new SB2 templates which were constructed in natural units (i.e. ergs /s /&#x212B;) using GaiaDR2 distances. This is done using a library of luminosity normalized spectra. This library was created from a combination of the [MaStar](https://www.sdss.org/surveys/mastar/) survey from [SDSS-IV](https://www.sdss.org) and the [Pickles+1998](https://ui.adsabs.harvard.edu/abs/1998PASP..110..863P/abstract) library. The Pickles library was used for OBAF stars while MaStar and SDSS was used for the GKM, C, WD stars. 

Modeled after [The Hammer: An IDL Spectral Typing Suite][thehammer] published in [Covey et al. 2007][covey+07] available on [GitHub][hammerGitHub].

See the [PyHammer Wiki](https://github.com/BU-hammerTeam/PyHammer/wiki) for more information on how to install and use this program.

Information on how the luminosity spectra are added to create SB2 templates can be found in the [Roulston+2020][Roulston_arXiv] paper.

### Publications

PyHammer 1.0.0 is detailed in our accepted Astrophysical Journal Supplements [Kesseli et al. (2017)][Kesseli_apjs].

PyHammer 2.0.0 is detailed in our upcoming Astrophysical Journal Supplements [Roulston et al. (2020)][Roulston_arXiv]

![GUI](./resources/PyHammer2_GUI.png?raw=true)

[thehammer]: http://myweb.facstaff.wwu.edu/~coveyk/thehammer.html
[covey+07]: http://adsabs.harvard.edu/abs/2007AJ....134.2398C
[hammerGitHub]: https://github.com/jradavenport/TheHammer
[pyhammerwiki]: https://github.com/BU-hammerTeam/PyHammer/wiki
[Kesseli_apjs]: http://iopscience.iop.org/article/10.3847/1538-4365/aa656d/pdf
[Roulston_arXiv]: https://arxiv.org/abs/2006.01199
[SB2_GitHub]: https://github.com/broulston/SB2
