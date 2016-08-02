import numpy as np
from scipy import interpolate
from scipy.interpolate import interp1d
from astropy.io import fits
import bisect
import pickle
import os

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
        self._wavelength = None
        self._flux = None
        self._var = None
        self._guess = None
        
        # Read in indices measured from templates
        # tempLines is a list of arrays with format: [spts, subs, fehs, lums, lines]
        # lines is a list of 2D arrays with indices and variances for each line
        # index for each spectrum that goes into a template
        self.thisDir, _ = os.path.split(__file__)
        pklPath = os.path.join(self.thisDir, "resources", "tempLines.pickle")        
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
        readFile(filename, filetype = 'fits')

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
            # Need keyword for angstrom vs micron , assume angstrom, keyword for micron 
            # Need error vs variance keyword
            try:
                spec = fits.open(filename) 
            except IOError as e:
                errorMessage = 'Unable to open ' + filename + '.\n' + str(e)
                return False, errorMessage
            try:
                self._flux = spec[0].data[0]
                self._wavelength = ( spec[0].header['CRVAL1'] - (spec[0].header['CRPIX1']*spec[0].header['CD1_1']) *np.arange(0,len(spec[0].data[0]),1))
            except Exception as e:
                errorMessage = 'Unable to use ' + filename + '.\n' + str(e)
                return False, errorMessage
            
        elif (filetype == 'DR7fits'):
            # Implement reading a sdss EDR through DR8 fits file
            try:
                spec = fits.open(filename)
            except IOError as e:
                errorMessage = 'Unable to open ' + filename + '.\n' + str(e)
                return False, errorMessage
            try:
                self._wavelength = 10**( spec[0].header['coeff0'] + spec[0].header['coeff1']*np.arange(0,len(spec[0].data[0]), 1))
                self._flux = spec[0].data[0]
                self._var = 1/(spec[0].data[2])
                #self._airToVac()
            except Exception as e:
                errorMessage = 'Unable to use ' + filename + '.\n' + str(e)
                return False, errorMessage
            
        elif (filetype == 'DR12fits'): 
            # Implement reading a sdss DR9 through DR12 fits file
            try:
                spec = fits.open(filename)
            except IOError as e:
                errorMessage = 'Unable to open ' + filename + '.\n' + str(e)
                return False, errorMessage
            try:
                self._wavelength = 10**spec[1].data['loglam']
                self._flux = spec[1].data['flux']
                self._var = 1/(spec[1].data['ivar'])
                #self._airToVac()
            except Exception as e:
                errorMessage = 'Unable to use ' + filename + '.\n' + str(e)
                return False, errorMessage
            
        elif (filetype == 'txt'):
            # Implement reading a txt file
            # Need to add in a Keyword to have the user be able to input error but assume variance
            # Also want a vacuum keyword! 
            try:
                f = open(filename)
            except IOError as e:
                errorMessage = 'Unable to open ' + filename + '.\n' + str(e)
                return False, errorMessage
            try:
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
            except Exception as e:
                errorMessage = 'Unable to use ' + filename + '.\n' + str(e)
                return False, errorMessage
            
        else:
            # The user supplied an option not accounted for
            # in this method. Just skip the file.
            errorMessage = filename + ' with file type ' + filetype + ' is not recognized. Skipping over this file.'
            return False, errorMessage
        
        self.interpOntoGrid()
        return True, ''

    def calcSN(self):
        """
        calcSN()
        
        Description:
        calculates the median signal to noise of the spectrum 
        uses formula SNR = mu/sigma
        
        Output:
        SN for the spectrum.
        """
        
        signalToNoise = np.median(self._flux)/np.median((self._var)**0.5)
        
        return signalToNoise
        
    def _airToVac(self):
        """
        A method to convert the wavelengths from air to vacuum
        
        Code originally in IDL (AIRTOVAC.pro) then translated into python 
        in pyAstronomy python library. 
        
        [Aurora]- want to have an if statement that checks if the spectrum 
        is already in vacuum or air.
        Sloan, princeton are already in vacuum but most other spectra are not. 
        """
        
        sigma2 = (1E4/self._wavelength)**2.                 #Convert to wavenumber squared

        # Compute conversion factor
        # Wavelength values below 2000 A will not be 
        # altered.  Uses the IAU standard for conversion given in Morton 
        # (1991 Ap.J. Suppl. 77, 119)

        fact = 1. + 6.4328E-5 + 2.94981E-2/(146.-sigma2) + 2.5540E-4/(41.-sigma2)

        fact = fact*(self._wavelength >= 2000.) + 1.*(self._wavelength < 2000.)

        self._wavelength = self._wavelength*fact            #Convert Wavelength

        return 

    def interpOntoGrid(self): 
        """
        A method to put the spectra onto the same grid as the templates
        (5km/s equally space bins)

        Input:
        raw flux and wavelength

        Output:
        interpolated flux, wavelength grid

        """
        # Make the wavelength grid (resolution of template grids)
        # Note log10(e) = 0.43429448190325182
        waveGrid = 10**(5*0.43429448190325182/(299792.458) * np.arange(0,65000) + 3.55)

        #interpolate flux and variance onto the wavelength grid
        interpFlux = np.interp(waveGrid, self._wavelength, self._flux)
        interpVar = np.interp(waveGrid, self._wavelength, self._var) 

        #cut the grids off at 3650 and 10200 like the templates
        startIndex = bisect.bisect_right(waveGrid, 3650)
        stopIndex = bisect.bisect_right(waveGrid,10200)

        self._wavelength = waveGrid[startIndex:stopIndex]
        self._flux = interpFlux[startIndex:stopIndex]
        self._var = interpVar[startIndex:stopIndex]

        return
        
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
                     num_std = np.sum((self._var[numeratorIndexLow:numeratorIndexHigh]))**(0.5)/len(self._var[numeratorIndexLow:numeratorIndexHigh])
                     den_std = np.sum((self._var[denominatorIndexLow:denominatorIndexHigh]))**(0.5)/len(self._var[denominatorIndexLow:denominatorIndexHigh])
  
                     #if the mean is greater than zero find the index and add it to the measuredLinesDict dictionary 
                     #This uses the same keys as the indexDict dictionary
                     if denmean > 0:
                         index=nummean/denmean
                         var = index**2 * ((num_std/nummean)**2 + (den_std/denmean)**2)
                         indexList = [index, var]
                         measuredLinesDict[key] = indexList
                     else:
                         indexList = [0,np.inf]
                         measuredLinesDict[key] = indexList
                 else:
                     indexList = [0,np.inf]
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
                     num1_std = np.sum((self._var[num1IndexLow:num1IndexHigh]))**(0.5)/len(self._var[num1IndexLow:num1IndexHigh])
                     num2_std = np.sum((self._var[num2IndexLow:num2IndexHigh]))**(0.5)/len(self._var[num2IndexLow:num1IndexHigh])
                     combonum = value[2]*num1mean + value[5]*num2mean
                     combonum_std = (value[2]**2 * num1_std**2 + value[5]**2 * num2_std**2)**(0.5)
                     denmean = np.mean(self._flux[denominatorIndexLow:denominatorIndexHigh])
                     den_std = np.sum((self._var[denominatorIndexLow:denominatorIndexHigh]))**(0.5)/len(self._var[denominatorIndexLow:denominatorIndexHigh])
                     
                     #if the mean is greater than zero find the index and add it to the measuredLinesDict dictionary 
                     #This uses the same keys as the indexDict dictionary
                     if denmean > 0:
                         index=combonum/denmean
                         var = index**2 * ((combonum_std/combonum)**2 + (den_std/denmean)**2)
                         indexList = [index, var]
                         measuredLinesDict[key] = indexList
                     else:
                         indexList = [0,np.inf]
                         measuredLinesDict[key] = indexList
                 else:
                     indexList = [0,np.inf]
                     measuredLinesDict[key] = indexList
 
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
        #Spectral type O 
        if bestGuess['spt'] == 0:
            tempName = 'O' + str(bestGuess['sub']) + '.fits'
        #Spectral type B
        elif bestGuess['spt'] == 1: 
            tempName = 'B' + str(bestGuess['sub']) + '.fits'
        #Spectral types A0, A1, A2 (where there is no metallicity changes)
        elif bestGuess['spt'] == 2 and float(bestGuess['sub']) < 3:
            tempName = 'A' + str(bestGuess['sub']) + '.fits'
        #Spectral type A3 through A9
        elif bestGuess['spt'] == 2 and float(bestGuess['sub']) > 2: 
            tempName = 'A' + str(bestGuess['sub']) + '_-1.0_Dwarf.fits'
        #Spectral type F
        elif bestGuess['spt'] == 3: 
            tempName = 'F' + str(bestGuess['sub']) + '_-1.0_Dwarf.fits'
        #Spectral type G
        elif bestGuess['spt'] == 4: 
            tempName = 'G' + str(bestGuess['sub']) + '_+0.0_Dwarf.fits'
        #Spectral type K 
        elif bestGuess['spt'] == 5: 
            tempName = 'K' + str(bestGuess['sub']) + '_+0.0_Dwarf.fits'
        #Spectral type M (0 through 8) 
        elif bestGuess['spt'] == 6 and float(bestGuess['sub']) < 9: 
            tempName = 'M' + str(bestGuess['sub']) + '_+0.0_Dwarf.fits'
        #Spectral type M9 (no metallicity)
        elif bestGuess['spt'] == 6 and bestGuess['sub'] == 9: 
            tempName = 'M' + str(bestGuess['sub']) + '.fits'
        #Spectral type L
        elif bestGuess['spt'] == 7: 
            tempName = 'L' + str(bestGuess['sub']) + '.fits'

        temp = fits.open(path+tempName)
        tempFlux = temp[1].data['flux']
        tempWave = 10**temp[1].data['loglam']

        # Get the regions for correlation
        specRegion1 = np.where( (wave > 5000) & (wave < 6000) )
        specRegion2 = np.where( (wave > 6000) & (wave < 7000) )
        specRegion3 = np.where( (wave > 7000) & (wave < 8000) )
        #noise regions: still not sure if we should have these or not
        noiseRegion1 = np.where( (wave > 5000) & (wave < 5100) )
        noiseRegion2 = np.where( (wave > 6800) & (wave < 6900) )
        noiseRegion3 = np.where( (wave > 7400) & (wave < 7500) )



        shift1 = self.xcorl(flux[specRegion1], tempFlux[specRegion1], 50, 'fine')
        shift2 = self.xcorl(flux[specRegion2], tempFlux[specRegion2], 50, 'fine')
        shift3 = self.xcorl(flux[specRegion3], tempFlux[specRegion3], 50, 'fine')

        # Convert to Radial Velocities
        pixel = wave[1]-wave[0]
        wave0 = (wave[1]+wave[0]) / 2
        c = 2.998 * 10**5
        radVel1 = shift1 * pixel / wave0 * c
        radVel2 = shift2 * pixel / wave0 * c
        radVel3 = shift3 * pixel / wave0 * c

        # Let's look at the noise in the spectrum
        snr1 = np.mean(interpFlux[noiseRegion1]) / np.std(interpFlux[noiseRegion1])
        snr2 = np.mean(interpFlux[noiseRegion2]) / np.std(interpFlux[noiseRegion2])
        snr3 = np.mean(interpFlux[noiseRegion3]) / np.std(interpFlux[noiseRegion3])

        # Look for convergence of the radial velocities
        rvs = np.array([radVel1, radVel2, radVel3])
        snrs = np.array([snr1, snr2, snr3])

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
                    fchi[nc] = np.sum(dif*dif)
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
        
        self._wavelength = self._wavelength / (shift / (299792.458) + 1)
        
        return 
    
    def normalizeFlux(self): 
        
        """
        normalize the observed flux at 8000 Angstroms (where the templates are all normalized) 
        for better comparisons to templates
        """
        
        normIndexLow = bisect.bisect_right(self._wavelength, 8000)
        normIndexHigh = bisect.bisect_right(self._wavelength, 8010)
        normFactor = np.mean(self._flux[normIndexLow:normIndexHigh])
        self._flux = self._flux/normFactor
        
        return 
    # Define other methods in this class which are needed to process the spectra


    ##
    # Property Methods
    #

    @property
    def flux(self):
        return self._flux

    @property
    def normFlux(self):
        return self.flux / np.trapz(self.flux, x = self.wavelength)

    @property
    def var(self):
        return self._var

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
    
