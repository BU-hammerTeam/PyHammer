# PyHammer

[![GitHub release](https://img.shields.io/github/release/BU-hammerTeam/PyHammer.svg)](https://github.com/BU-hammerTeam/PyHammer/releases/latest)
[![GitHub commits](https://img.shields.io/github/commits-since/BU-hammerTeam/PyHammer/v1.0.2.svg)](https://github.com/BU-hammerTeam/PyHammer/commits/master)
[![GitHub issues](https://img.shields.io/github/issues/BU-hammerTeam/PyHammer.svg)](https://github.com/BU-hammerTeam/PyHammer/issues)
[![license](https://img.shields.io/github/license/BU-hammerTeam/PyHammer.svg)](https://github.com/BU-hammerTeam/PyHammer/blob/master/license.txt)
[![Python Supported](https://img.shields.io/badge/Python%20Supported-3-brightgreen.svg)](conda)
[![Maintenance](https://img.shields.io/maintenance/yes/2017.svg)]()

### A Python Spectral Typing Suite 

PyHammer is a tool developed to allow rapid and automatic spectral classification of stars according to the Morgan-Keenan classification system. Working in the range of 3,650 - 10,200 Angstroms, the automatic spectral typing algorithm compares important spectral lines to template spectra and determines the best matching spectral type, ranging from O to L type stars. This tool has the additional features that it can determine a star's metallicity ([Fe/H]) and radial velocity shifts. Once the automatic classification algorithm has run, PyHammer provides the user an interface for determining spectral types visually by comparing their spectra to provided templates.

Modeled after [The Hammer: An IDL Spectral Typing Suite][thehammer] published in [Covey et al. 2007][covey+07] available on [GitHub][hammerGitHub].

See the [PyHammer Wiki](https://github.com/BU-hammerTeam/PyHammer/wiki) for more information on this program or the accompanying paper.

### Publications

We will have an peer-reviewed, published paper out soon, but in the mean time see our [arXiv version][arXiv_version].

[thehammer]: http://myweb.facstaff.wwu.edu/~coveyk/thehammer.html
[covey+07]: http://adsabs.harvard.edu/abs/2007AJ....134.2398C
[hammerGitHub]: https://github.com/jradavenport/TheHammer
[pyhammerwiki]: https://github.com/BU-hammerTeam/PyHammer/wiki
[arXiv_version]: https://arxiv.org/abs/1702.06957
