import numpy as np
from astropy.io import fits
import bisect
import pickle
import os

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
        self._var = None
        self._guess = None
        
        ###########################################
        #Not the best way to do this. Shouldn't
        #need to read in template data for each 
        #spectrum. Common Block?
        ###########################################
        
        #Read in indices measured from templates
        #tempLines is a list of arrays with format: [spts, subs, fehs, lums, lines]
        #lines is a list of 2D arrays with indices and variances for each line
        # index for each spectrum that goes into a template
        thisDir, thisFile = os.path.split(__file__)
        pklPath = os.path.join(thisDir, "resources", "tempLines.pickle")        
        with open(pklPath, 'rb') as pklFile:
            tempLines = pickle.load(pklFile)
        
        #Get averages and stddevs for each line for each template
        avgs = np.zeros([len(tempLines[4]), len(tempLines[4][0][0])], dtype='float')
        avgs[:,:] = np.nan
        stds = np.zeros([len(tempLines[4]), len(tempLines[4][0][0])], dtype='float')
        stds[:,:] = np.nan
        for i, ilines in enumerate(tempLines[4]):
            weights = 1.0/np.array(ilines)[:,:,1]
            nonzeroweights = np.sum(weights != 0, 0)
            weightedsum = np.nansum(np.array(ilines)[:,:,0] * weights, 0)
            sumofweights = np.nansum(weights, 0)
            avgs[i] = weightedsum / sumofweights
            stds[i] = np.sqrt( np.nansum(weights * (np.array(ilines)[:,:,0] - avgs[i])**2.0, 0)
                              / ( ((nonzeroweights-1.0)/nonzeroweights)
                                  * sumofweights ) )
                                  
        self._tempLines = tempLines
        self._tempLineAvgs = avgs
        self._tempLineVars = stds**2.0

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
            
        elif (filetype == 'DR7fits'):
            # Implement reading a sdss DR7 fits file
            #print('Not Implemented')
            spec = fits.open(filename)
            self._wavelength = 10**( spec[0].header['coeff0'] + spec[0].header['coeff1']*np.arange(0,len(spec[0].data[0]), 1))
            self._flux = spec[0].data[0]
            self._var = 1/(spec[0].data[2])
            #self._airToVac()
            
        elif (filetype == 'DR12fits'): 
            # Implement reading a sdss DR7 fits file
            spec = fits.open(filename) 
            self._wavelength = 10**spec[1].data['loglam']
            self._flux = spec[1].data['flux']
            self._var = 1/(spec[1].data['ivar'])
            
        elif (filetype == 'txt'):
            # Implement reading a txt file
            #print('Not Implemented')
            f = open(filename)
            data = tbl.read()
            f.close()
            lineList = data.splitlines()
            
            wave = []
            flux = []
            var = []
            for line in LineList:
                l = line.split()
                wave.append(l[0])
                flux.append(l[1])
                if len(l) > 2:
                    err = l[2]
                    var.append(err**2)
                    
            self._wavelength = np.asarray(wave) 
            self._flux = np.asarray(flux) 
            if len(ivar) > 0: 
                self._var = np.asarray(var) 
            
            
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
        #create a dictionary for all the corresponding wavelengths of the absorption features
        indexDict = {}
        #list the indices for each important absorption feature: numlo, numhi, denomlo, denomhi 
        # or for multi region features: num1lo, num1hi, num1weight, num2lo, num2hi, num2weight, denomlo, denomhi
        # THESE ARE ALL IN VACUUM and angstroms!!
        indexDict['CaK']  = [3924.8111, 3944.8163, 3944.8163, 3954.8189]
        indexDict['Cadel'] = [4087.8536, 4117.8618, 4137.8670, 4177.1771]
        indexDict['CaI4217'] = [4217.8880, 4237.8932, 4237.8932, 4257.1981]
        indexDict['Gband'] = [4286.2057, 4316.2136, 4261.1992, 4286.2057]
        indexDict['Hgam'] = [4333.7182, 4348.7222, 4356.2242, 4371.2281] 
        indexDict['FeI4383'] = [4379.8305, 4389.8331, 4356.2242, 4371.2281]
        indexDict['FeI4404'] = [4401.0358, 4411.0384, 4416.0397, 4426.0423]
        indexDict['Hbeta'] = [4848.3542, 4878.3622, 4818.3463, 4848.3542]
        indexDict['MgI'] = [5154.1357, 5194.1463, 5101.4214, 5151.4348]
        indexDict['NaD'] = [5881.6297, 5906.6364, 5911.6378, 5936.6445]
        indexDict['CaI6162'] = [6151.7021, 6176.7088, 6121.6941, 6146.7008]
        indexDict['Halpha'] = [6549.8090, 6579.8171, 6584.8184, 6614.8265]
        indexDict['CaH2'] = [6815.8576, 6847.8664, 7043.9419, 7047.9430]
        indexDict['CaH3'] = [6961.9198, 6991.9279, 7043.9419, 7047.9430]
        indexDict['TiO5'] = [7127.9646, 7136.9670, 7043.9419, 7047.9430]
        indexDict['VO7434'] = [7432.0465, 7472.0573, 7552.0789, 7572.0843]
        indexDict['VO7445'] = [7352.0249, 7402.0384, 0.56250000, 7512.0681, 7562.0816, 0.43750000, 7422.0438, 7472.0573]
        indexDict['VO-B'] = [7862.1626, 7882.1680, 0.50000000, 8082.2220, 8102.2274, 0.50000000, 7962.1896, 8002.2004]
        indexDict['VO7912'] = [7902.1734, 7982.1950, 8102.2274, 8152.2409]
        indexDict['Rb-B'] = [7924.7796, 7934.7823, 0.50000000, 7964.7904, 7974.7931, 0.50000000, 7944.7850, 7954.7877]
        indexDict['NaI'] = [8179.2482, 8203.2547, 8153.2412, 8177.2477]
        indexDict['TiO8'] = [8402.3085, 8417.3125, 8457.3233, 8472.3274]
        indexDict['TiO8440'] = [8442.3193, 8472.3274, 8402.3085, 8422.3139]
        indexDict['Cs-A'] = [8498.4341, 8508.4368, 0.50000000, 8538.4449, 8548.4476, 0.50000000, 8518.4395, 8528.4422]
        indexDict['CaII8498'] = [8485.3309, 8515.3390, 8515.3390, 8545.3471] 
        indexDict['CrH-A'] = [8582.3571, 8602.3626, 8623.3682, 8643.3736]
        indexDict['CaII8662'] = [8652.3761, 8677.3828, 8627.3693, 8652.3761]
        indexDict['FeI8689'] = [8686.3853, 8696.3880, 8666.3799, 8676.3826]
        indexDict['FeH'] = [9880, 10000, 9820,9860]
        #color bands
        indexDict['region1'] = [4160,4210,7480,7580]
        indexDict['region2'] = [4550,4650,7480,7580]
        indexDict['region3'] = [5700,5800,7480,7580]
        indexDict['region4'] = [9100,9200,7480,7580]
        indexDict['region5'] = [10100,10200,7480,7580]
        
        
        #make a dictionary for the measured indices
        measuredLinesDict = {}
        
        #Loop through the indexDict and measure the lines
        for key, value in indexDict.items():
            #check if we should use the single or mutliple region version
            if len(value) == 4: 
                #find the indices where the numerator and denominator start and end for each absorption feature
                numeratorIndexLow = bisect.bisect_right(self._wavelength, value[0])
                numeratorIndexHigh = bisect.bisect_right(self._wavelength, value[1])
                
                denominatorIndexLow = bisect.bisect_right( self._wavelength, value[2])
                denominatorIndexHigh = bisect.bisect_right(self._wavelength, value[3])
                
                #check to make sure the absorption features are within the wavelength regime of the spectrum
                if len(self._wavelength) > numeratorIndexHigh and len(self._wavelength) > denominatorIndexHigh:
                    #calculate the mean fluxes of the numerator and denominator regimes
                    nummean = np.mean(self._flux[numeratorIndexLow:numeratorIndexHigh])
                    denmean = np.mean(self._flux[denominatorIndexLow:denominatorIndexHigh])
                    #calculate the uncertainty in the region 
                    num_std = np.sum(1/(self._ivar[numeratorIndexLow:numeratorIndexHigh]))**(0.5)/len(self._ivar[numeratorIndexLow:numeratorIndexHigh])
                    den_std = np.sum(1/(self._ivar[denominatorIndexLow:denominatorIndexHigh]))**(0.5)/len(self._ivar[denominatorIndexLow:denominatorIndexHigh])
 
                    #if the mean is greater than zero find the index and add it to the measuredLinesDict dictionary 
                    #This uses the same keys as the indexDict dictionary
                    if denmean > 0:
                        index=nummean/denmean
                        var = index**2 * ((num_std/nummean)**2 + (den_std/denmean)**2)
                        indexList = [index, var]
                        measuredLinesDict[key] = indexList
                
            elif len(value) == 8: 
                      
                #find the indices for the two numerators and denominators
                num1IndexLow = bisect.bisect_right( self._wavelength, value[0])
                num1IndexHigh = bisect.bisect_right(self._wavelength, value[1])
                
                num2IndexLow = bisect.bisect_right( self._wavelength, value[3])
                num2IndexHigh = bisect.bisect_right(self._wavelength, value[4])
                
                denominatorIndexLow = bisect.bisect_right( self._wavelength, value[6])
                denominatorIndexHigh = bisect.bisect_right(self._wavelength, value[7])
                
                #check to make sure the absorption features are within the wavelength regime of the spectrum
                if len(self._wavelength) > num1IndexHigh and len(self._wavelength) > num2IndexHigh and len(self._wavelength) > denominatorIndexHigh:
                    #calculate the mean fluxes of the numerator and denominator regimes
                    num1mean = np.mean(self._flux[num1IndexLow:num1IndexHigh])
                    num2mean = np.mean(self._flux[num2IndexLow:num2IndexHigh])
                    num1_std = np.sum(1/(self._ivar[num1IndexLow:num1IndexHigh]))**(0.5)/len(self._ivar[num1IndexLow:num1IndexHigh])
                    num2_std = np.sum(1/(self._ivar[num2IndexLow:num2IndexHigh]))**(0.5)/len(self._ivar[num2IndexLow:num1IndexHigh])
                    combonum = value[2]*num1mean + value[5]*num2mean
                    combonum_std = (value[2]**2 * num1_std**2 + value[5]**2 * num2_std**2)**(0.5)
                    denmean = np.mean(self._flux[denominatorIndexLow:denominatorIndexHigh])
                    den_std = np.sum(1/(self._ivar[denominatorIndexLow:denominatorIndexHigh]))**(0.5)/len(self._ivar[denominatorIndexLow:denominatorIndexHigh])
                    
                    #if the mean is greater than zero find the index and add it to the measuredLinesDict dictionary 
                    #This uses the same keys as the indexDict dictionary
                    if denmean > 0:
                        index=combonum/denmean
                        var = index**2 * ((combonum_std/combonum)**2 + (den_std/denmean)**2)
                        indexList = [index, var]
                        measuredLinesDict[key] = indexList
        
        
        #print('Not implemented')

        return measuredLinesDict
        
    def guessSpecType(self):
    
        #Measure lines
        linesDict = self.measureLines()
        
        #Recast values to simple 2D array
        #lines = np.array(list(linesDict.values()))
        lines = np.array(list(linesDict.values()))[np.argsort(list(linesDict.keys()))]
        
        #Weight by uncertainty in object lines and template lines
        weights = 1.0 / (np.sqrt(self._tempLineVars) + np.sqrt(lines[:,1]))
        
        #print(lines)
        #print(weights)
        
        #Find best fit
        iguess = np.nanargmin(np.nansum(((lines[:,0] - self._tempLineAvgs) * weights)**2, 1) / np.nansum(weights**2, 1))
        
        #print(iguess)
        
        #Save guess as dict       
        self._guess = {'spt':self._tempLines[0][iguess], # Spectral type - 0 for O to 6 for M
                       'sub':self._tempLines[1][iguess], # Spectral subtype
                       'feh':self._tempLines[2][iguess], # Metallicity
                       'lum':self._tempLines[3][iguess]} # Luminosity class - 3 for giant, 5 for MS        

    def shiftToRest(self, shift):
        """
        Shift the observed wavelengths to the rest frame using the radial velocity
        **Shift needs to be in km/s**
        """
        
        self._wavelength = self._wavelength/(shift/(2.998*10**5) + 1)
        
        print('Not Implemented')
    
    # Define other methods in this class which are needed to process the spectra


    ##
    # Property Methods
    #

    @property
    def flux(self):
        return self._flux
        
    @flux.setter
    def flux(self, value):
        self._flux = value        
        
    @property
    def ivar(self):
        return self._ivar
        
    @ivar.setter
    def ivar(self, value):
        self._ivar = value  

    @property
    def wavelength(self):
        return self._wavelength
        
    @wavelength.setter
    def wavelength(self, value):
        self._wavelength = value
        
    @property
    def lines(self):
        return self._lines   

    @property
    def guess(self):
        return self._guess 
    
