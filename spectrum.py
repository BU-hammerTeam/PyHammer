import numpy as np
from astropy.io import fits

class Spectrum(object):
    """
    Spectrum Class

    Description:
    This is a spectrum class which defines the spectrum object, containing
    information about the wavelength, flux, and error for a given spectrm.
    Because knowledge of only one spectrum is necessary at any one time,
    a single object can be used and new spectra can be loaded into the object.
    """
    
    def __init__(self):
        self._wavelength = None
        self._flux = None
        self._noise = None

    ##
    # Utility Methods
    #
    
    def readFile(self, filename, filetype = 'fits'):
        """
        readFIle(filename, filetype = 'fits')

        Description:
        This method will read in the file provided by
        filename and according to the input filetype.
        The result will be to store the wavelength, flux,
        and noise arrays into the instance variables of
        this object.

        Input:
        filename - The name of the file to be read. This
                   will require either a full path.
        filetype - The file type to be read. This should
                   be a string specifying either fits,
                   ssdsfits, or txt. This is fits by default.
        
        Output:
        A boolean indicating the success of reading the file.
        """

        if (filetype == 'fits'):
            # Implement reading a regular fits file
            print('Not Implemented')
            
        elif (filetype == 'ssdsfits'):
            # Implement reading a sdss fits file
            print('Not Implemented')
            
            self._vacToAir()
        elif (filetype == 'txt'):
            # Implement reading a txt file
            print('Not Implemented')
            
        else:
            # The user supplied an option not accounted for
            # in this method. Just skip the file.
            print('Warning: "' + filename + '" with file type "' + filetype +
                  '" is not readable. Skipping over this file.', flush = True)
            return False

        
        self._interpOntoGrid()
        return True
        
    def _airToVac(self):
        """
        A method to convert the wavelengths from air to vacuum
        
        [Aurora]- want to have an if statement that checks if the spectrum 
        is already in vacuum or air.
        Sloan, princeton are already in air but most other spectra are not. 
        """

        print('Not implemented')

    def _interpOntoGrid(self):
        """
        A method to interpolate the wavelength, flux and noise
        onto a logarithmic wavelength spacing. The observed spectrum
        and the templates need to be consistent with one another.
        
        [Aurora] need some if statement to check to see if the spectrum 
        is in equal RV space. If it is not, we will want to choose the 
        blue (lower RV) end to interpolate onto
        """

        print('Not Implemented')

    def measureLines(self):
        """
        A method to reproduce the functionality of the measureGoodLines
        function in the IDL version. With some careful planning, this
        should be much better written and more compact. It might require
        writing ancilliary methods to be used by this one as the hammer
        function does.
        """
        print('Not implemented')

        return lineIndices

    def shiftToRest(self, shift):
        """
        Shift the observed wavelengths to the rest frame using the radial velocity
        """

        print('Not Implemented')
    
    # Define other methods in this class which are needed to process the spectra


    ##
    # Property Methods
    #

    @property
    def flux(self):
        return _flux

    @property
    def noise(self):
        return _noise

    @property
    def wavelength(self):
        return _wavelength
    
