from pyhamimports import *

class Spectrum(object):
    """
    Spectrum Class

    Description:
        This is a spectrum class which defines the spectrum object, containing
        information about the wavelength, flux, and error for a given spectrum.
        Because knowledge of only one spectrum is necessary at any one time,
        a single object can be used and new spectra can be loaded into the object.
    """
    
    def __init__(self):
        # Define properties related to loaded spectrum
        self._wavelength = None
        self._flux = None
        self._var = None
        self._guess = None
        self._normWavelength = 8000

        self.letterSpt = ['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'C', 'WD']

        # The directory containing this file
        self.thisDir = os.path.split(__file__)[0]

        # Store the SB2 filenames and order for access later
        SB2ListPath = os.path.join(self.thisDir, 'resources', 'list_of_SB2_spec.txt')
        self._SB2_filenameList = np.genfromtxt(SB2ListPath, dtype="U")

        self._splitSB2spectypes = np.empty((self._SB2_filenameList.size, 4), dtype='U2')

        for ii, filename in enumerate(self._SB2_filenameList):
            type1, type2 = filename.replace("+"," ").replace("."," ").split()[:2]
            mainType1, subtype1 = self.splitSpecType(type1)
            mainType2, subtype2 = self.splitSpecType(type2)
            self._splitSB2spectypes[ii, 0] = mainType1
            self._splitSB2spectypes[ii, 1] = subtype1
            self._splitSB2spectypes[ii, 2] = mainType2
            self._splitSB2spectypes[ii, 3] = subtype2

        self._isSB2 = False

        # Define class instance variables used 
        self.defineCalcTools()


        
        # Read in indices measured from templates
        # tempLines is a list of arrays with format: [spts, subs, fehs, lums, lines]
        # lines is a list of 2D arrays with indices and variances for each line
        # index for each spectrum that goes into a template
        #
        #pklPath = os.path.join(self.thisDir, 'resources', 'tempLines.pickle')
        pklPath = os.path.join(self.thisDir, 'resources', 'tempLines_07-02-2019_SB2.pickle')
        with open(pklPath, 'rb') as pklFile:
            tempLines = pickle.load(pklFile)
        
        ## Get averages and stddevs for each line for each template
        # avgs = np.zeros([len(tempLines[4]), len(tempLines[4][0][0])], dtype='float')
        # stds = np.zeros([len(tempLines[4]), len(tempLines[4][0][0])], dtype='float')
        # for i, ilines in enumerate(tempLines[4]):
        #     weights = 1.0/np.array(ilines)[:,:,1]
        #     nonzeroweights = np.sum(weights != 0, 0, dtype='float')
        #     nonzeroweights[nonzeroweights <= 1.0] = np.nan
        #     weightedsum = np.nansum(np.array(ilines)[:,:,0] * weights, 0)
        #     sumofweights = np.nansum(weights, 0)
        #     sumofweights[sumofweights == 0.0] = np.nan
        #     avgs[i] = weightedsum / sumofweights
        #     stds[i] = np.sqrt( np.nansum(weights * (np.array(ilines)[:,:,0] - avgs[i])**2.0, 0)
        #                       / ( ((nonzeroweights-1.0)/nonzeroweights)
        #                           * sumofweights ) )

        avgs = np.zeros([len(tempLines[4]), len(tempLines[4][0])], dtype='float')
        stds = np.zeros([len(tempLines[4]), len(tempLines[4][0])], dtype='float')

        for ii in range(len(tempLines[4])):
            avgs[ii, :] =  tempLines[4][ii][:,0]
            stds[ii, :] =  np.sqrt(tempLines[4][ii][:,1])
                                  
        self._tempLines = tempLines
        self._tempLineAvgs = avgs
        self._tempLineVars = stds**2.0

    def splitSpecType(self, s):
        head = s.rstrip('0123456789')
        tail = s[len(head):]
        return head, tail

    def defineCalcTools(self):
        """
        Description:
            This method is called by the __init__ method above and used
            to define various variables used in the calculational processes
            below. These are defined here on object instantiation because
            they only need to be defined once and can be used for all
            spectra calculations.
        """
        # Define the wavelngth points to interpolate the spectrum to so it
        # can be compared to the templates. Note log10(e) = 0.43429448190325182
        self.waveGrid = 10**(5*0.43429448190325182/299792.458 * np.arange(0,65000) + 3.55)
        # Define the spectral lines to be measured in the spectrum and
        # used to be matched to the templates.
        self.indexDict = OrderedDict()
        # List the indices for each important absorption feature: numlo, numhi, denomlo, denomhi 
        # or for multi region features: num1lo, num1hi, num1weight, num2lo, num2hi, num2weight, denomlo, denomhi
        # NOTE: These are all in vacuum and Angstroms!
        self.indexDict['CaK']      = [3924.8111, 3944.8163, 3944.8163, 3954.8189]
        self.indexDict['Cadel']    = [4087.8536, 4117.8618, 4137.8670, 4177.1771]
        self.indexDict['CaI4217']  = [4217.8880, 4237.8932, 4237.8932, 4257.1981]
        self.indexDict['Gband']    = [4286.2057, 4316.2136, 4261.1992, 4286.2057]
        self.indexDict['Hgam']     = [4333.7182, 4348.7222, 4356.2242, 4371.2281] 
        self.indexDict['FeI4383']  = [4379.8305, 4389.8331, 4356.2242, 4371.2281]
        self.indexDict['FeI4404']  = [4401.0358, 4411.0384, 4416.0397, 4426.0423]
        self.indexDict['Hbeta']    = [4848.3542, 4878.3622, 4818.3463, 4848.3542]
        self.indexDict['MgI']      = [5154.1357, 5194.1463, 5101.4214, 5151.4348]
        self.indexDict['NaD']      = [5881.6297, 5906.6364, 5911.6378, 5936.6445]
        self.indexDict['CaI6162']  = [6151.7021, 6176.7088, 6121.6941, 6146.7008]
        self.indexDict['Halpha']   = [6549.8090, 6579.8171, 6584.8184, 6614.8265]
        self.indexDict['CaH2']     = [6815.8576, 6847.8664, 7043.9419, 7047.9430]
        self.indexDict['CaH3']     = [6961.9198, 6991.9279, 7043.9419, 7047.9430]
        self.indexDict['TiO5']     = [7127.9646, 7136.9670, 7043.9419, 7047.9430]
        self.indexDict['VO7434']   = [7432.0465, 7472.0573, 7552.0789, 7572.0843]
        self.indexDict['VO7445']   = [7352.0249, 7402.0384,    0.5625, 7512.0681, 7562.0816, 0.4375, 7422.0438, 7472.0573]
        self.indexDict['VO-B']     = [7862.1626, 7882.1680,    0.5000, 8082.2220, 8102.2274, 0.5000, 7962.1896, 8002.2004]
        self.indexDict['VO7912']   = [7902.1734, 7982.1950, 8102.2274, 8152.2409]
        self.indexDict['Rb-B']     = [7924.7796, 7934.7823,    0.5000, 7964.7904, 7974.7931, 0.5000, 7944.7850, 7954.7877]
        self.indexDict['NaI']      = [8179.2482, 8203.2547, 8153.2412, 8177.2477]
        self.indexDict['TiO8']     = [8402.3085, 8417.3125, 8457.3233, 8472.3274]
        self.indexDict['TiO8440']  = [8442.3193, 8472.3274, 8402.3085, 8422.3139]
        self.indexDict['Cs-A']     = [8498.4341, 8508.4368,    0.5000, 8538.4449, 8548.4476, 0.5000, 8518.4395, 8528.4422]
        self.indexDict['CaII8498'] = [8485.3309, 8515.3390, 8515.3390, 8545.3471] 
        self.indexDict['CrH-A']    = [8582.3571, 8602.3626, 8623.3682, 8643.3736]
        self.indexDict['CaII8662'] = [8652.3761, 8677.3828, 8627.3693, 8652.3761]
        self.indexDict['FeI8689']  = [8686.3853, 8696.3880, 8666.3799, 8676.3826]
        self.indexDict['FeH']      = [9880     ,10000     , 9820,      9860]
        # Color bands
        self.indexDict['region1'] = [ 4160,  4210, 7480, 7580]
        self.indexDict['region2'] = [ 4550,  4650, 7480, 7580]
        self.indexDict['region3'] = [ 5700,  5800, 7480, 7580]
        self.indexDict['region4'] = [ 9100,  9200, 7480, 7580]
        self.indexDict['region5'] = [10100, 10200, 7480, 7580] 

        self.indexDict['C2-4382'] = [4350, 4380, 4450, 4600]
        self.indexDict['C2-4737'] = [4650, 4730, 4750, 4850]
        self.indexDict['C2-5165'] = [5028, 5165, 5210, 5380] 
        self.indexDict['C2-5636'] = [5400, 5630, 5650, 5800]
        self.indexDict['CN-6926'] = [6935, 7035, 6850, 6900]
        self.indexDict['CN-7872'] = [7850, 8050, 7650, 7820]

        self.indexDict['WD-Halpha'] = [6519, 6609, 6645, 6700]
        self.indexDict['WD-Hbeta']  = [4823, 4900, 4945, 4980]
        self.indexDict['WD-Hgamma'] = [4290, 4405, 4430, 4460]
        

    ##
    # Utility Methods
    #
    
    def isNumber(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False
            
    def readFile(self, filename, filetype = None):
        """
        readFile(filename, filetype = 'fits')

        Description:
            This method will read in the file provided by
            filename and according to the input filetype.
            The result will be to store the wavelength, flux,
            and noise arrays into the instance variables of
            this object.

        Input:
            filename: The name of the file to be read. This
                will require either a full path.
            filetype: The file type to be read. This should
                be a string specifying either fits, ssdsfits,
                or txt. This is fits by default.
        
        Output:
            A boolean indicating the success of reading the file.
        """

        if isinstance(filetype, str): filetype = filetype.lower()

        self.filename = filename

        if filetype not in ['fits', 'sdssdr7', 'sdssdr12', 'txt', 'csv', 'tempfits', None]:
            # The user supplied an option not accounted for
            # in this method. Just skip the file.
            errorMessage = filename + ' with file type ' + filetype + ' is not recognized. Skipping over this file.'
            return errorMessage, None

        # Try reading a regular .fits file
        if (filetype in ['fits', None]):
            msg = self.__readFileFits(filename)
            if msg is not None: # I.e., there was a problem
                if filetype is not None:
                    return msg, None
            else:
                filetype = 'fits'

        # Try reading an SDSS .fits file from EDR to DR8
        if (filetype in ['sdssdr7', None]):
            msg = self.__readFileSDSSdr7(filename)
            if msg is not None: # I.e., there was a problem
                if filetype is not None:
                    return msg, None
            else:
                filetype = 'sdssdr7'

        # Try reading an SDSS .fits file from DR9 to DR12
        if (filetype in ['sdssdr12', None]): 
            msg = self.__readFileSDSSdr12(filename)
            if msg is not None: # I.e., there was a problem
                if filetype is not None:
                    return msg, None
            else:
                filetype = 'sdssdr12'

        # Try reading a .csv file with the data in columns
        if (filetype in ['csv', None]):
            msg = self.__readFileCsv(filename)
            if msg is not None: # I.e., there was a problem
                if filetype is not None:
                    return msg, None
            else:
                filetype = 'csv'

        # Try reading a plaintext file with the data in columns
        if (filetype in ['txt', None]):
            msg = self.__readFileTxt(filename)
            if msg is not None: # I.e., there was a problem
                if filetype is not None:
                    return msg, None
            else:
                filetype = 'txt'

        # Try reading a .fits file with the data in template fmt
        if (filetype in ['tempfits', None]):
            msg = self.__readFileTempFits(filename)
            if msg is not None: # I.e., there was a problem
                if filetype is not None:
                    return msg, None
            else:
                filetype = 'tempfits'
        # If the user didn't supply a filetype for us, and we
        # didn't manage to figure out which one it was, simply
        # return with an error message stating so.
        if filetype is None:
            return 'Could not identify format of data.', None
        

        # -----
        # If we've made it to here, then we've loaded up the
        # data from the file properly and we can try to do
        # some further processing
        self.interpOntoGrid()
        
        # Determine wavelength to normalize flux at
        normIndex = bisect.bisect_right(self._wavelength, 8000)
        if np.isnan(self._flux[normIndex]):
            # If we cannot use the default 8000 angstrom to normalize by, find the
            # median of the wavelengths to use as the new wavelength
            nonNanWave =  self._wavelength[np.isfinite(self._flux)]
            self._normWavelength = (nonNanWave[-1] + nonNanWave[0])/2
        else:
            # Use default of 8000 if the flux is defined there
            self._normWavelength = 8000
        
        return None, filetype

    def __readFileFits(self, filename):
        """Tries to read a regular fits file"""
        # Need keyword for angstrom vs micron , assume angstrom, keyword for micron 
        # Need error vs variance keyword
        try:
            with warnings.catch_warnings():
                # Ignore a very particular warning from some versions of astropy.io.fits
                # that is a known bug and causes no problems with loading fits data.
                warnings.filterwarnings('ignore', message = 'Could not find appropriate MS Visual C Runtime ')
                spec = fits.open(filename) 
        except IOError as e:
            errorMessage = 'Unable to open ' + filename + '.\n' + str(e)
            return errorMessage
        try:
            # There seems to be an array within an array (making len 1 of flux sometimes)
            # check for that
            if len(spec[0].data[0]) > 1:
                self._flux = spec[0].data[0]
            else: 
                self._flux = spec[0].data[0][0]
            # Get wavelength
            self._wavelength = ( spec[0].header['CRVAL1'] + (spec[0].header['CRPIX1']*spec[0].header['CD1_1']) *np.arange(0,len(self._flux),1))
            # Create a simple poisson error
            err = abs(self._flux)**0.05 + 1E-16
            self._var = err**2
        except Exception as e:
            errorMessage = 'Unable to use ' + filename + '.\n' + str(e)
            return errorMessage

        return None

    def __readFileTempFits(self, filename):
        """Tries to read a template fits file"""
        try:
            with warnings.catch_warnings():
                # Ignore a very particular warning from some versions of astropy.io.fits
                # that is a known bug and causes no problems with loading fits data.
                warnings.filterwarnings('ignore', message = 'Could not find appropriate MS Visual C Runtime ')
                spec = fits.open(filename) 
        except IOError as e:
            errorMessage = 'Unable to open ' + filename + '.\n' + str(e)
            return errorMessage
        try:
            self._flux = spec[1].data.field('Flux')
            self._wavelength = 10.0**spec[1].data.field('LogLam')
            err = spec[1].data.field('PropErr')
            self._var = err**2
        except Exception as e:
            errorMessage = 'Unable to use ' + filename + '.\n' + str(e)
            return errorMessage

        return None

    def __readFileSDSSdr7(self, filename):
        """Tries to read an SDSS EDR through DR8 fits file"""
        try:
            with warnings.catch_warnings():
                # Ignore a very particular warning from some versions of astropy.io.fits
                # that is a known bug and causes no problems with loading fits data.
                warnings.filterwarnings('ignore', message = 'Could not find appropriate MS Visual C Runtime ')
                spec = fits.open(filename)
        except IOError as e:
            errorMessage = 'Unable to open ' + filename + '.\n' + str(e)
            return errorMessage
        try:
            np.seterr(divide = 'ignore')    # Ignore any potential division by zero
            self._wavelength = 10**( spec[0].header['coeff0'] + spec[0].header['coeff1']*np.arange(0,len(spec[0].data[0]), 1))
            self._flux = spec[0].data[0]
            self._var = 1 / spec[0].data[2]
            #self._airToVac()
        except Exception as e:
            errorMessage = 'Unable to use ' + filename + '.\n' + str(e)
            return errorMessage

        return None

    def __readFileSDSSdr12(self, filename):
        """Tries to read an SDSS DR9 through DR12 fits file"""
        try:
            with warnings.catch_warnings():
                # Ignore a very particular warning from some versions of astropy.io.fits
                # that is a known bug and causes no problems with loading fits data.
                warnings.filterwarnings('ignore', message = 'Could not find appropriate MS Visual C Runtime ')
                spec = fits.open(filename)
        except IOError as e:
            errorMessage = 'Unable to open ' + filename + '.\n' + str(e)
            return errorMessage
        try:
            np.seterr(divide = 'ignore')    # Ignore any potential division by zero
            self._wavelength = 10**spec[1].data['loglam']
            self._flux = spec[1].data['flux']
            self._var = 1 / spec[1].data['ivar']
            #self._airToVac()
        except Exception as e:
            errorMessage = 'Unable to use ' + filename + '.\n' + str(e)
            return errorMessage

        return None

    def __readFileTxt(self, filename):
        """Reads a plaintext file"""
        # Need to add in a Keyword to have the user be able to input error but assume variance
        # Also want a vacuum keyword! 
        try:
            f = open(filename)
        except IOError as e:
            errorMessage = 'Unable to open ' + filename + '.\n' + str(e)
            return errorMessage
        try:
            data = f.read()
            f.close()
            lineList = data.splitlines()
            
            wave = []
            flux = []
            var = []
            for line in lineList:
                lTemp = line.split()
                if self.isNumber(lTemp[0]) and self.isNumber(lTemp[1]): 
                    wave.append(float(lTemp[0]))
                    flux.append(float(lTemp[1]))
                    if len(lTemp) > 2 and self.isNumber(lTemp[2]):
                        err = float(lTemp[2])
                        var.append(err**2)
                    else:
                        err = max(0,float(lTemp[1]))**0.05 + 1E-16
                        var.append(err**2)
            
            self._wavelength = np.asarray(wave) 
            self._flux = np.asarray(flux) 
            self._var = np.asarray(var) 
        except Exception as e:
            errorMessage = 'Unable to use ' + filename + '.\n' + str(e)
            return errorMessage

        return None

    def __readFileCsv(self, filename):
        """Read a .csv file"""
        # Need to add in a Keyword to have the user be able to input error but assume variance
        # Also want a vacuum keyword! 
        try:
            with open(filename, 'r') as file:
                reader = csv.reader(file)
                f = list(reader)[1:] # Ignore the header line
        except (UnicodeDecodeError, IOError) as e:
            errorMessage = 'Unable to open ' + filename + '.\n' + str(e)
            return errorMessage
        try:
            f = np.array(f)
            self._wavelength = f[:,0].astype(np.float)
            self._flux = f[:,1].astype(np.float)
            if len(f[1]) > 2:
                err = f[:,2].astype(np.float)
                self._var = err**2
            else: 
                err = abs(self._flux)**0.05 + 1E-16
                self._var = err**2
        except Exception as e:
            errorMessage = 'Unable to use ' + filename + '.\n' + str(e)
            return errorMessage
        
        return None

    def calcSN(self):
        """
        calcSN()
        
        Description:
            Calculates the median signal to noise of the spectrum 
            uses formula SNR = mu/sigma
        
        Output:
            Signal to noise for the spectrum.
        """

        # The median has to take care of the flux or variance having nans in it. We
        # specifically choose to call out finite values rather than using nanmedian
        # because np.nanmedian was only added in version 1.9 and we want to be as
        # backwards compatible with numpy as possible.
        signalToNoise = np.nanmedian(self._flux[np.isfinite(self._flux)]) / np.median((self._var[np.isfinite(self._var)])**0.5)
        
        return signalToNoise
        
    def _airToVac(self):
        """
        A method to convert the wavelengths from air to vacuum.
        
        Code originally in IDL (AIRTOVAC.pro) then translated into python 
        in pyAstronomy python library. 
        
        [Aurora]- want to have an if statement that checks if the spectrum 
        is already in vacuum or air.
        Sloan, princeton are already in vacuum but most other spectra are not. 
        """
        
        sigma2 = (1E4/self._wavelength)**2 # Convert to wavenumber squared

        # Compute conversion factor
        # Wavelength values below 2000 A will not be altered.
        # Uses the IAU standard for conversion given in Morton 
        # (1991 Ap.J. Suppl. 77, 119)

        factor = 1 + 6.4328E-5 + 2.94981E-2/(146-sigma2) + 2.5540E-4/(41-sigma2)

        self._wavelength[self._wavelength >= 2000] *= factor # Convert Wavelength

    def interpOntoGrid(self): 
        """
        Description:
            A method to put the spectrum flux and variance onto the same
            wavelength grid as the templates (5 km/s equally spaced bins)
        """
        # Interpolate flux and variance onto the wavelength grid
        interpFlux = np.interp(self.waveGrid, self._wavelength, self._flux, right=np.nan, left=np.nan)
        interpVar = np.interp(self.waveGrid, self._wavelength, self._var, right=np.nan, left=np.nan) 

        #cut the grids off at 3650 and 10200 like the templates
        startIndex = bisect.bisect_right(self.waveGrid, 3650)
        stopIndex = bisect.bisect_right(self.waveGrid, 10200)

        self._wavelength = self.waveGrid[startIndex:stopIndex]
        self._flux = interpFlux[startIndex:stopIndex]
        self._var = interpVar[startIndex:stopIndex]
        
    def measureLines(self):
        """
        A method to reproduce the functionality of the measureGoodLines
        function in the IDL version. With some careful planning, this
        should be much better written and more compact. It might require
        writing ancilliary methods to be used by this one as the hammer
        function does.
        """
        
        # Make a dictionary for the measured indices
        measuredLinesDict = OrderedDict()
        
        # Loop through the self.indexDict and measure the lines of the spectra
        for key, value in self.indexDict.items():
            #check if we should use the single or mutliple region version
            if len(value) == 4: 
                # Find the indices where the numerator and denominator
                # start and end for each absorption feature.
                numerIndexLow = bisect.bisect_right(self._wavelength, value[0])
                numerIndexHigh = bisect.bisect_right(self._wavelength, value[1])
                
                denomIndexLow = bisect.bisect_right(self._wavelength, value[2])
                denomIndexHigh = bisect.bisect_right(self._wavelength, value[3])
                
                # Check to make sure the absorption features are within the wavelength regime of the spectrum
                if len(self._wavelength) > numerIndexHigh and len(self._wavelength) > denomIndexHigh:
                    # Calculate the mean fluxes of the numerator and denominator regimes
                    numerMean = np.mean(self._flux[numerIndexLow:numerIndexHigh])
                    denomMean = np.mean(self._flux[denomIndexLow:denomIndexHigh])
                    #calculate the uncertainty in the region 
                    numerStd = np.sum((self._var[numerIndexLow:numerIndexHigh]))**(0.5)/len(self._var[numerIndexLow:numerIndexHigh])
                    denomStd = np.sum((self._var[denomIndexLow:denomIndexHigh]))**(0.5)/len(self._var[denomIndexLow:denomIndexHigh])
  
                    #if the mean is greater than zero find the index and add it to the measuredLinesDict dictionary 
                    #This uses the same keys as the self.indexDict dictionary
                    if denomMean > 0:
                        index = numerMean/denomMean
                        var = index**2 * ((numerStd/numerMean)**2 + (denomStd/denomMean)**2)
                        measuredLinesDict[key] = [index, var]
                    else:
                        measuredLinesDict[key] = [0,np.inf]
                else:
                    measuredLinesDict[key] = [0,np.inf]
                        
                
            elif len(value) == 8: 
                      
                #find the indices for the two numerators and denominators
                numer1IndexLow = bisect.bisect_right( self._wavelength, value[0])
                numer1IndexHigh = bisect.bisect_right(self._wavelength, value[1])
                
                numer2IndexLow = bisect.bisect_right( self._wavelength, value[3])
                numer2IndexHigh = bisect.bisect_right(self._wavelength, value[4])
                
                denomIndexLow = bisect.bisect_right( self._wavelength, value[6])
                denomIndexHigh = bisect.bisect_right(self._wavelength, value[7])
                
                #check to make sure the absorption features are within the wavelength regime of the spectrum
                if len(self._wavelength) > numer1IndexHigh and len(self._wavelength) > numer2IndexHigh and len(self._wavelength) > denomIndexHigh:
                    #calculate the mean fluxes of the numerator and denominator regimes
                    numer1Mean = np.mean(self._flux[numer1IndexLow:numer1IndexHigh])
                    numer2Mean = np.mean(self._flux[numer2IndexLow:numer2IndexHigh])
                    numer1Std = np.sum((self._var[numer1IndexLow:numer1IndexHigh]))**(0.5)/len(self._var[numer1IndexLow:numer1IndexHigh])
                    numer2Std = np.sum((self._var[numer2IndexLow:numer2IndexHigh]))**(0.5)/len(self._var[numer2IndexLow:numer2IndexHigh])
                    comboNumer = value[2]*numer1Mean + value[5]*numer2Mean
                    comboNumerStd = (value[2]**2 * numer1Std**2 + value[5]**2 * numer2Std**2)**(0.5)
                    denomMean = np.mean(self._flux[denomIndexLow:denomIndexHigh])
                    denomStd = np.sum((self._var[denomIndexLow:denomIndexHigh]))**(0.5)/len(self._var[denomIndexLow:denomIndexHigh])
                    
                    #if the mean is greater than zero find the index and add it to the measuredLinesDict dictionary 
                    #This uses the same keys as the self.indexDict dictionary
                    if denomMean > 0:
                        index = comboNumer/denomMean
                        var = index**2 * (comboNumerStd/comboNumer)**2 + (denomStd/denomMean)**2
                        measuredLinesDict[key] = [index, var]
                    else:
                        measuredLinesDict[key] = [0,np.inf]
                else:
                    measuredLinesDict[key] = [0,np.inf]
 
        return measuredLinesDict
    def isWD(self):
        def Gauss(x, mu,sigma, A, m, b):
            return A* np.exp(-0.5 * ((x - mu)/sigma)**2) + m*x + b

        p0 = np.array([6564.5377, 25.0, .75, -1.0, 1.0])
        range_index = np.where((self._wavelength >= 6200.0) & (self._wavelength <= 6900.0))[0] 
        with warnings.catch_warnings(): 
            #warnings.filterwarnings('ignore', message = 'Could not find appropriate MS Visual C Runtime ') 
            warnings.simplefilter("ignore")
            popt, pcov = curve_fit(Gauss, self._wavelength[range_index], self._flux[range_index], p0=p0)#, maxfev=50000)
        if popt[1] > 15.0:
            return True, popt[1]
        else:
            return False, np.nan

    def guessSpecType(self):
    
        # Measure lines
        self._lines = self.measureLines()

        # Recast values to simple 2D array
        lines = np.array(list(self._lines.values()))[np.argsort(list(self._lines.keys()))]

        # Weight by uncertainty in object lines and template lines
        weights = 1 / (np.sqrt(self._tempLineVars) + np.sqrt(lines[:,1]))

        # Find best fit
        sumOfWeights = np.nansum(weights**2, 1)
        sumOfWeights[sumOfWeights == 0] = np.nan
        self.FULLdistance = np.nansum(((lines[:,0] - self._tempLineAvgs) * weights)**2, 1) / sumOfWeights
        if np.all(np.isnan(self.FULLdistance)):
            iguess = None
            #Save guess as dict       
            self._guess = {'specType':   -1, # Spectral type, 0 for O to 7 for L
                           'subType':    -1, # Spectral subtype
                           'metal':      -1, # Metallicity
                           'luminosity': -1} # Luminosity class, 3 for giant, 5 for MS   
        else:
            iguess = np.nanargmin(self.FULLdistance)
            if np.isin(np.int(self._tempLines[0][iguess]), np.array([0, 1, 2, 3])):
                try:
                    isThisAWD, thisSigma = self.isWD()
                    if isThisAWD:
                        WD_sigma = np.array([18.3083, 35.6469, 28.7010, 26.8483, 25.3973, 20.2621, 21.1071])#0,1,2,3,4,7,8
                        WD_sigma_label = np.array([1,2,3,4,5,6,7])
                        self._guess = {'specType':   9, # Spectral type, 0 for O to 7 for L, 8 = C, 9 = WD
                                       'subType':    WD_sigma_label[np.argmin(np.abs(WD_sigma-thisSigma))], # Spectral subtype
                                       'metal':      0, # Metallicity
                                       'luminosity': 5} # Luminosity class, 3 for giant, 5 for MS   
                    else:
                        self._guess = {'specType':   np.int(self._tempLines[0][iguess]), # Spectral type, 0 for O to 7 for L, 8 = C, 9 = WD
                                      'subType':    np.int(self._tempLines[1][iguess]), # Spectral subtype
                                      'metal':      self._tempLines[2][iguess], # Metallicity
                                      'luminosity': np.int(self._tempLines[3][iguess])} # Luminosity class, 3 for giant, 5 for MS  
                except RuntimeError:
                    stillWD = True
                    stillWD_step = 1
                    while stillWD:
                        iguess_dist = np.partition(self.FULLdistance, stillWD_step)[stillWD_step]
                        iguess = np.where(self.FULLdistance == iguess_dist)[0][0]
                        if np.int(self._tempLines[0][iguess]) == 9:
                            stillWD_step += 1
                        else:
                            stillWD = False
                            stillWD_step += 1

            elif np.int(self._tempLines[0][iguess]) == 9: 
                try:
                    isThisAWD, thisSigma = self.isWD()
                    if isThisAWD:
                        self._guess = {'specType':   np.int(self._tempLines[0][iguess]), # Spectral type, 0 for O to 7 for L, 8 = C, 9 = WD
                                       'subType':    np.int(self._tempLines[1][iguess]), # Spectral subtype
                                       'metal':      self._tempLines[2][iguess], # Metallicity
                                       'luminosity': np.int(self._tempLines[3][iguess])} # Luminosity class, 3 for giant, 5 for MS  
                    else:
                        stillWD = True
                        stillWD_step = 1
                        while stillWD:
                            iguess_dist = np.partition(self.FULLdistance, stillWD_step)[stillWD_step]
                            iguess = np.where(self.FULLdistance == iguess_dist)[0][0]
                            if np.int(self._tempLines[0][iguess]) == 9:
                                stillWD_step += 1
                            else:
                                stillWD = False
                                stillWD_step += 1

                        self._guess = {'specType':   np.int(self._tempLines[0][iguess]), # Spectral type, 0 for O to 7 for L, 8 = C, 9 = WD
                                       'subType':    np.int(self._tempLines[1][iguess]), # Spectral subtype
                                       'metal':      self._tempLines[2][iguess], # Metallicity
                                       'luminosity': np.int(self._tempLines[3][iguess])} # Luminosity class, 3 for giant, 5 for MS 
                except RuntimeError:
                    stillWD = True
                    stillWD_step = 1
                    while stillWD:
                        iguess_dist = np.partition(self.FULLdistance, stillWD_step)[stillWD_step]
                        iguess = np.where(self.FULLdistance == iguess_dist)[0][0]
                        if np.int(self._tempLines[0][iguess]) == 9:
                            stillWD_step += 1
                        else:
                            stillWD = False
                            stillWD_step += 1                     
            else: 
                #Save guess as dict       
                self._guess = {'specType':   np.int(self._tempLines[0][iguess]), # Spectral type, 0 for O to 7 for L, 8 = C, 9 = WD
                               'subType':    np.int(self._tempLines[1][iguess]), # Spectral subtype
                               'metal':      self._tempLines[2][iguess], # Metallicity
                               'luminosity': np.int(self._tempLines[3][iguess])} # Luminosity class, 3 for giant, 5 for MS

        if self.guess['specType'] >= 10:
            self._isSB2 = True
            self.distance = self.FULLdistance[iguess]
        else:
            self._isSB2 = False
            self.distance = self.FULLdistance[iguess]
    
    def findRadialVelocity(self):
        """
        findRadialVelocity(spectrum)

        Description:
        Uses the cross-correlation technique. Most likely there is a pre-built
        package for this so we won't start from the ground up.

        Technique requires an at-rest reference spectrum with which to compare
        to the observed input spectrum.

        This method works best when the wavelengths are logarithmically spaced,
        otherwise, a 2 pixel shift at the blue-end of the spectrum will return
        a different radial velocity measurement than a 2 pixel shift at the red
        end of the spectrum.

        One thing that may be worth exploring is how to constrain the
        uncertainty in the radial velocity measurement. Typically I repeat the
        cross-correlation techniqe ~100 times across a few different wavelength
        regimes and then find the mean/variance of that returned radial
        velocities. There is probably a better way to do it.


        Input:
        Spectrum object - Should have the wavelength, flux, and noise of the
        observed spectrum.
        bestGuess template - The wavelength and flux of the bestGuess.

        Output:
        The radial velocity measurement and its associated uncertainty. Do we want
        add the radialvelocity to the spectrum object? Or report just report it in
        the output file.
        """

        #Get the flux and wavelength from the spectrum object 
        #This should already be interpolated onto a log scale and normalized to 8000A (where templates are normalized)
        wave = self._wavelength
        flux = self._flux
        bestGuess = self._guess

        #open the correct template spectrum 
        # I have it only using the spectral type and subtype for the original guess 
        # so I just cross correlate to the most common metallicity template for each spectral class
        path = 'resources/templates/'
        path_SB2 = 'resources/templates_SB2/'

        #Spectral type O 
        if bestGuess['specType'] == 0:
            tempName = 'O' + str(bestGuess['subType']) + '.fits'
        #Spectral type B
        elif bestGuess['specType'] == 1: 
            tempName = 'B' + str(bestGuess['subType']) + '.fits'
        #Spectral types A0, A1, A2 (where there are no metallicity changes)
        elif bestGuess['specType'] == 2 and float(bestGuess['subType']) < 3:
            tempName = 'A' + str(bestGuess['subType']) + '.fits'
        #Spectral type A3 through A9
        elif bestGuess['specType'] == 2 and float(bestGuess['subType']) > 2: 
            tempName = 'A' + str(bestGuess['subType']) + '_-1.0_Dwarf.fits'
        #Spectral type F
        elif bestGuess['specType'] == 3: 
            tempName = 'F' + str(bestGuess['subType']) + '_-1.0_Dwarf.fits'
        #Spectral type G
        elif bestGuess['specType'] == 4: 
            tempName = 'G' + str(bestGuess['subType']) + '_+0.0_Dwarf.fits'
        #Spectral type K 
        elif bestGuess['specType'] == 5: 
            tempName = 'K' + str(bestGuess['subType']) + '_+0.0_Dwarf.fits'
        #Spectral type M (0 through 8) 
        elif bestGuess['specType'] == 6 and float(bestGuess['subType']) < 9: 
            tempName = 'M' + str(bestGuess['subType']) + '_+0.0_Dwarf.fits'
        #Spectral type M9 (no metallicity)
        elif bestGuess['specType'] == 6 and bestGuess['subType'] == 9: 
            tempName = 'M' + str(bestGuess['subType']) + '.fits'
        #Spectral type L
        elif bestGuess['specType'] == 7: 
            tempName = 'L' + str(bestGuess['subType']) + '.fits'
        #Spectral type C
        elif bestGuess['specType'] == 8: 
            tempName = 'C' + str(bestGuess['subType']) + '.fits'
        #Spectral type WD
        elif bestGuess['specType'] == 9: 
            tempName = 'WD' + str(bestGuess['subType']) + '.fits'
        #Spectral type SB2
        elif self._isSB2:
            tempName = self._SB2_filenameList[bestGuess['specType'] - 10]
        # Open the template
        with warnings.catch_warnings():
            # Ignore a very particular warning from some versions of astropy.io.fits
            # that is a known bug and causes no problems with loading fits data.
            warnings.filterwarnings('ignore', message = 'Could not find appropriate MS Visual C Runtime ')
            if self._isSB2:
                temp = fits.open(path_SB2+tempName)
            else:
                temp = fits.open(path+tempName)
                                    
        tempFlux = temp[1].data['flux']
        tempWave = 10**temp[1].data['loglam']
        tempFlux = Spectrum.normalize(tempWave, self._normWavelength, tempFlux)

        # Get the regions for correlation
        specRegion1 = np.where( (wave > 5000) & (wave < 6000) )
        specRegion2 = np.where( (wave > 6000) & (wave < 7000) )
        specRegion3 = np.where( (wave > 7000) & (wave < 8000) )
        #noise regions: still not sure if we should have these or not
        noiseRegion1 = np.where( (wave > 5000) & (wave < 5100) )
        noiseRegion2 = np.where( (wave > 6800) & (wave < 6900) )
        noiseRegion3 = np.where( (wave > 7400) & (wave < 7500) )
        
        #make sure the regions we are cross correlating have data
        nonNanWave =  self._wavelength[np.where( np.isfinite(self._flux) )]

        if nonNanWave[0] < 5000 and nonNanWave[-1] > 6000:
            shift1 = float(self.xcorl(flux[specRegion1], tempFlux[specRegion1], 50, 'fine'))
            snr1 = np.mean(flux[noiseRegion1]) / np.std(flux[noiseRegion1])
            if nonNanWave[-1] > 7000:
                shift2 = float(self.xcorl(flux[specRegion2], tempFlux[specRegion2], 50, 'fine'))
                snr2 = np.mean(flux[noiseRegion2]) / np.std(flux[noiseRegion2])
                if nonNanWave[-1] > 8000:
                    shift3 = float(self.xcorl(flux[specRegion3], tempFlux[specRegion3], 50, 'fine'))
                    snr3 = np.mean(flux[noiseRegion3]) / np.std(flux[noiseRegion3])
                else:
                    print('CAUTION: radial velocity may not be accurate, smaller wavelength region than tested on')
                    shift3 = np.nan
                    snr3 = np.nan
            else:
                print('CAUTION: radial velocity may not be accurate, smaller wavelength region than tested on')
                shift2 = np.nan
                snr2 = np.nan
                shift3 = np.nan
                snr3 = np.nan
                
        elif nonNanWave[0] > 5000 and nonNanWave[0] < 6000 and nonNanWave[-1] > 7000:
            print('CAUTION: radial velocity may not be accurate, smaller wavelength region than tested on')
            shift1 = np.nan
            snr1 = np.nan
            shift2 = float(self.xcorl(flux[specRegion2], tempFlux[specRegion2], 50, 'fine'))
            snr2 = np.mean(flux[noiseRegion2]) / np.std(flux[noiseRegion2])
            if nonNanWave[-1] > 8000:
                shift3 = float(self.xcorl(flux[specRegion3], tempFlux[specRegion3], 50, 'fine'))
                snr3 = np.mean(flux[noiseRegion3]) / np.std(flux[noiseRegion3])
            else:
                shift3 = np.nan
                snr3 = np.nan

        elif nonNanWave[0] > 6000 and nonNanWave[0] < 7000 and nonNanWave[-1] > 8000:
            print('CAUTION: radial velocity may not be accurate, smaller wavelength region than tested on')
            shift1 = np.nan
            snr1 = np.nan
            shift2 = np.nan
            snr2 = np.nan
            shift3 = float(self.xcorl(flux[specRegion3], tempFlux[specRegion3], 50, 'fine'))
            snr3 = np.mean(flux[noiseRegion3]) / np.std(flux[noiseRegion3])

        else:
            print('Spectrum too short to compute accurate radial velocity')
            rvFinal = np.nan
            return rvFinal

        # Convert to Radial Velocities
        pixel = wave[1]-wave[0]
        wave0 = (wave[1]+wave[0]) / 2
        c = 299792.458 # km/s
        radVel1 = shift1 * pixel / wave0 * c
        radVel2 = shift2 * pixel / wave0 * c
        radVel3 = shift3 * pixel / wave0 * c

        # Look for convergence of the radial velocities
        rvs = np.array([radVel1, radVel2, radVel3])
        snrs = np.array([snr1, snr2, snr3])
        #make sure none of the rvs are nans, if so get rid of them
        rvs = rvs[np.isfinite(rvs)]

        true = False
        firstTime = 1
        broke = False
        while true == False:
            trueCount = 0
            chi = []

            for rv_ in rvs:
                #Start with highest signal-to-noise value
                if firstTime == 1: 
                    rvmed = rvs[np.where(snrs == np.max(snrs))]
                else: 
                    rvmed = np.median( rvs )
                if rv_ == rvmed: 
                    continue
                if rvmed < 0:
                    number = -10
                    #print 'RV', rv_, 'MEDIAN', rvmed, 'LIMITS', rvmed + number,  rvmed - number, 'WITHIN?', rv_ > rvmed + number and rv_ < rvmed - number
                    if rv_ < (rvmed + number) or rv_ > (rvmed - number):
                        chi.append( [rv_ , abs( rv_ - rvmed )] )
                        #rvs = np.delete(rvs, np.where(rvs == rv_))
                        trueCount += 1
                else:
                    number = 10
                    #print 'RV', rv_, 'MEDIAN', rvmed, 'LIMITS', rvmed + number,  rvmed - number, 'WITHIN?', rv_ < rvmed + number and rv_ > rvmed - number
                    if rv_ > (rvmed + number) or rv_ < (rvmed - number):
                        chi.append( [rv_ , abs( rv_ - rvmed )] )
                        #rvs = np.delete(rvs, np.where(rvs == rv_))
                        trueCount += 1
            #print 'TRUECOUNT', trueCount
            firstTime = 0
            if trueCount == 0:
                true = True
                break
            if trueCount == 2:
                true=True
                #print('BROKEN')
                broke = True
                break
            #print 'START CHI'
            chi = np.array(chi)
            #print chi
            #print chi[:,1]
            #print np.max(chi[:,1])
            #print chi[:,0][np.where(chi[:,1] == np.max(chi[:,1]))]
            #print np.where(rvs == chi[:,0][np.where(chi[:,1] == np.max(chi[:,1]))])[0]
            #print 'DROPPING', rvs[np.where(rvs == chi[:,0][np.where(chi[:,1] == np.max(chi[:,1]))])[0]]
            #print 'LENGTH', len(chi)
            if len(chi) > 0:
                #print 'DELETING'
                rvs = np.delete(rvs, np.where(rvs == chi[:,0][np.where(chi[:,1] == np.max(chi[:,1]))])[0])
            #print 'End', rvs
            if trueCount == 0: 
                true = True
        #print rvs
        rvFinal = np.mean( rvs )

        return rvFinal

    def shfour(self, sp, shift, *args):

        # shift of sp by (arbitrary, fractional) shift, result in newsp

        # Set Defaults
        pl = 0

        # Read the arguments
        for arg in args:
            if arg.lower() == 'plot': pl = 1

        ln = len(sp)
        nsp = sp

        # Take the inverse Fourier transform and multiply by length to put it in IDL terms
        fourtr = np.fft.ifft(nsp) * len(nsp)   
        sig = np.arange(ln)/float(ln) - .5
        sig = np.roll(sig, int(ln/2))
        sh = sig*2. * np.pi * shift

        count=0
        shfourtr = np.zeros( (len(sh), 2) )
        complexarr2 = np.zeros( len(sh), 'complex' )
        for a,b in zip(np.cos(sh), np.sin(sh)):
            comps = complex(a,b)
            complexarr2[count] = comps
            count+=1

        shfourtr = complexarr2 * fourtr

        # Take the Fourier transform
        newsp = np.fft.fft(shfourtr) / len(shfourtr)
        newsp = newsp[0:ln]

        # Plot it
        if pl == 1:
            plt.plot(sp)
            plt.plot(newsp-.5)
            plt.show()

        return newsp

    def xcorl(self, star,temp,range1,*args,**kwargs):
        #12-Jun-92 JAV	Added minchi parameter and logic.
        #17-Jun-92 JAV	Added "Max. allowable range" error message.
        #24-Aug-92 JAV	Supressed output of blank line when print keyword absent.
        #3-Jan-97 GB    Added "fine" (# pixs finely resolved) and "mult" options
        #  these give finer resolution to the peak, and use products instead of diffs.
        #8-Jan-97 GB	Added "fshft" to force one of a double peak
        #23-Oct-01 GB   Added /full keyword to simplify the call
        #28-Feb-13 CAT   Ported to Python
        #16-Jun-16 AYK   Added to hammer code
        # Set the defaults
        # Set the defaults
        pr = 0
        fine = 0
        mult=0
        fshft=0
        full=0
        ff = 0

        # Read the arguments
        for arg in args:
            if arg.lower() == 'fine': fine = 1
            if arg.lower() == 'full': full = 1

        # Read the keywords
        for key in kwargs:
            if key.lower() == 'mult':
                mult = kwargs[key]
            if key.lower() == 'fshft':
                fshft = kwargs[key]

        ln = len(temp)
        ls = len(star)
        length = np.min([ln, ls])
        slen = length
        if range1 > (length-1)/2:
            print( 'Maximum allowable "range" for this case is' + str((length-1)/2))
        newln = length - 2*range1  # Leave "RANGE" on ends for overhang.

        te = temp/(np.sum(temp)/ln)
        st = star/(np.sum(star)/ls) # Be normal already!
        newend = range1 + newln - 1
        x = np.arange(2 * range1 + 1) - range1
        chi = np.zeros(2 * range1 + 1)

        if full == 1:
            pr=1

        for j in range(-range1, range1+1):    # Goose step, baby
            if mult == 1:
                dif = te[range1:newend+1] * st[range1+j:newend+j+1]
                chi[j+range1] = np.sum(abs(dif))
            else:
                dif = te[range1:newend+1] - st[range1+j:newend+j+1]
                chi[j+range1] = np.sum(dif*dif)
        xcr = chi


        length = len(x) * 100
        xl = np.arange(length)
        xl = xl/100. - range1
        xp = xl[0:length-99]
        function2 = interp1d(x, chi, kind='cubic')
        cp = function2(xp)
        if mult != 0:
            minchi = np.max(cp)
            mm = np.where(cp == minchi)
        else:
            minchi = np.min(cp)
            mm = np.where(cp == minchi)
        shft = xp[mm[0]]
        if pr != 0:
            print( 'XCORL: The shift is: %10.2f'%(shft))
        if abs(shft) > range1:
            ff=1
            return
        if fshft != 0:
            shft = fshft

        if fine != 0:
            nf = fine*20+1
            rf = fine*10.
            nc = -1
            fchi = np.zeros(nf)
            xl = np.zeros(nf)
            for j in range(int(-rf), int(rf+1)):
                xl[nc+1] = shft + j/10.
                nst = self.shfour(st, -xl[nc+1])
                nc += 1
                if mult == 1:
                    dif = nst[range1:newend+1] * te[range1:newend+1]
                    fchi[nc] = np.sum(abs(dif))
                else:
                    dif = nst[range1:newend+1] - te[range1:newend+1]
                    fchi[nc] = np.sum(np.real(dif*dif))
            xp = np.arange( (nf-1) * 100 + 1) / 1000. + shft - fine
            function3 = interp1d(xl, fchi, kind='cubic')
            cp = function3(xp)
            if mult == 1:
                minchi = np.max(cp)
                mm = np.where(cp == minchi)
            else:
                minchi = np.min(cp)
                mm = np.where(cp == minchi)
            fshft = xp[mm]

            if pr != 0:
                print( 'XCORL: The final shift is: %10.2f'%(fshft))
        else:
            fshft=shft
        shft=fshft
        return shft
    
    def shiftToRest(self, shift):
        """
        Shift the observed wavelengths to the rest frame in the same grid as the templates using the radial velocity
        
        Input: 
        Calculated radial velocity float [km/s]
        """
        #check to see if a RV was found, if not do not shift the spectrum
        if np.isnan(shift):
            shift = 0.0
        
        self._wavelength = self._wavelength / (shift / (299792.458) + 1)
        
        return 

    def normalizeFlux(self):
        """Defined purely for convenience in normalizing the loaded spectrum."""
        self._flux = Spectrum.normalize(self._wavelength, self._normWavelength, self._flux)

    ##
    # Static Methods
    #    

    @staticmethod
    def normalize(wavelength, normWavelength, flux):
        """
        Normalize the observed flux at 8000 Angstroms (where the templates are all normalized) 
        for better comparisons to templates
        """
        
        normIndex = bisect.bisect_right(wavelength, normWavelength)

        if np.isnan(flux[normIndex]): 
            nonNanWave =  wavelength[np.where( np.isfinite(self._flux) )]
            normWavelength = (nonNanWave[-1] + nonNanWave[0])/2
            normIndex = bisect.bisect_right(wavelength, normWavelength)

        normFactor = np.mean(flux[normIndex-10:normIndex+10])

        return flux / normFactor

    @staticmethod
    def removeSdssStitchSpike(wavelength, flux):
        """
        All SDSS spectrum have a spike in the spectra between 5569 and 5588 angstroms where
        the two detectors meet. This method will remove the spike at that point by linearly
        interpolating across that gap.
        """

        # Make a copy so as to not alter the original, passed in flux
        flux = flux.copy()

        # Search for the indices of the bounding wavelengths on the spike. Use the
        # fact that the wavelength is an array in ascending order to search quickly
        # via the searchsorted method.
        lower = np.searchsorted(wavelength, 5569)
        upper = np.searchsorted(wavelength, 5588)

        # Define the flux in the stitch region to be linearly interpolated values between
        # the lower and upper bounds of the region.
        flux[lower:upper] = np.interp(wavelength[lower:upper],
                                      [wavelength[lower],wavelength[upper]],
                                      [flux[lower],flux[upper]])

        return flux

    ##
    # Property Methods
    #

    @property
    def flux(self):
        return self._flux


    @property
    def smoothFlux(self):
        # Define our own nancumsum method since numpy's nancumsum was only
        # added recently and not everyone will have the latest numpy version
        def nancumsum(x):
            return ma.masked_array(x, mask = (np.isnan(x)|np.isinf(x))).cumsum().filled(np.nan)
        
        # Simply the flux, convolved with a boxcar function to smooth it out.
        # A potential failing of this method is the case where there are a
        # small number of flux values (in the hundreds) but that seems so
        # unlikely, it isn't going to be handled.
        N = max(int(len(self._flux)/600), 100)  # Smoothing factor, Higher value = more smoothing
        cumsum = nancumsum(np.insert(self._flux,0,0))
        smoothFlux = (cumsum[N:] - cumsum[:-N]) / N
        smoothFlux = np.append(self._flux[:int(np.floor((N-1)/2))], smoothFlux)
        smoothFlux = np.append(smoothFlux, self._flux[-int(np.floor(N/2)):])
        return smoothFlux

    @property
    def var(self):
        return self._var
    
    @property
    def normWavelength(self): 
        return self._normWavelength

    @property
    def wavelength(self):
        return self._wavelength

    @property
    def loglam(self):
        return np.log10(self._wavelength)
        
    @wavelength.setter
    def wavelength(self, value):
        self._wavelength = value
        
    @property
    def lines(self):
        return self._lines   

    @property
    def guess(self):
        return self._guess 
    
