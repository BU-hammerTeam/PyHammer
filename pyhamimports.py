###
# This program simply provides the imports to be used for
# all other PyHammer modules. Since many of the modules
# use the same imports, they are consolidated here to be
# imported by all the other PyHammer modules.
#


# Look at version specific information
import sys
ver = sys.version_info # Get Python version
if ver.major != 3:
    sys.exit('Python 3 is required to run PyHammer.')
# We need a function to determine which modules
# exist. This function is Python 3 minor version
# dependent. Pull out the relevant one.
if ver.minor < 4:
    from importlib import find_loader as findModule
else:
    from importlib.util import find_spec as findModule

# Some basic python libraries
import os
import getopt
import numpy as np
from numpy import ma
from scipy.interpolate import interp1d
import matplotlib
from astropy.io import fits
import warnings
from time import time
import bisect
import pickle
import csv

# Check which PyQt version the user may have
# installed and import the appropriate content
if findModule('PyQt5') is not None:
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QWidgets import *
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
elif findModule('PyQt4') is not None:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
    matplotlib.use('Qt4Agg')
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
else:
    sys.exit('No suitable PyQt version was found.')

# The rest of the imports. These must occur
# after the PyQt imports and choices
from matplotlib import __version__ as pltVersion
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Cursor, MultiCursor

# Used for debugging purposes
import pdb
