
"""
Main(spectraFilename)

Description:
This is the main portion of the code. It calls the other functions used.
It's main function is to:
    1) Call the Spectrum class
    2) Call Spectrum.measureLines to calculate line indices
    3) Run guessSpecType to get the initial guessed spectral type.
    4) Use the best-guess from guessSpecType() and run radialVelocity() to the
    radial velocity measurements, cross correlate the lines to get the inital
    spectral type and metallicity guess, bring up the GUI.

Input:
spectraFilename - a list of the filenames of each of the spectra to be
classified (one per line), and the corresponding filetype (i.e., sdssfits,
fits, txt, etc.)

Output:
autoSpTResults.tbl - list of the spectra with the results of the auto spectral
typing, radial velocity and metallicity results.
"""

# Function for radial velocity measurements.
def radialVelocity(spectrum, bestGuess):
    """
    Description:
    Uses the cross-correlation technique. Most likely there is a pre-built
    package for this so we won't start from the ground up.

    Technique requires an at-rest reference spectrum with which to compare
    to the observed input spectrum.

    This method works best when the wavelengths are logarithmically spaced,
    otherwise, a 2 pixel shift at the blue-end of the spectrum will return
    a different radial velocity measurement than a 2 pixel shit at the red
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

    # Do we want this as part of the Spectrum class instead?

    return rv


#function that compares the indices and gets a spectral type guess
def guessSpecType():
    # CAN TRANSLATE FROM HAMMER
    # need to add in metallicity guess

def specInterp():
    # Inerpolate the spectrum to logarithmic wavelength spacing.

    # The observed spectrum and the templates need to be consistent with
    # one another.

# -------------------------------------
# ------------ Hammer Time ------------
# -------------------------------------

# [Dylan] - How are we reading in the input list of files? We can 1) ask
# via user input or 2) provide an input file list as part of calling the main
# function.

# Check for the correct path
# CAN TRANSLATE

# Check if user wants to run the autospectral typing
# CAN TRANSLATE

# Check if user wants a S/N cut
# CAN TRANSLATE

# Read in the files

# Loop over spectra in the Input
for specFiles, numspecFiles in enumerate(inFiles):
    # Call the Spectrum object for each spectra in the list

    # Interpolate the observed spectrum to be logarithmically spaced.
    # def specInterp(): or do we want it as part of the Spectrum class?

    # Call the Spectrum.measurelines() function in the Spectrum object to get
    # the initial line measurements

    # Call the guessSpType function to get an inital guess of the spectral type

    # Call radialVelocity function

    # Call a Spectrum.shiftToRest() that shifts the spectrum to rest
    # wavelengths. Save as a new property to Sepctrum (I think?).

    # Repeat the Spectrum.measurelines() on using the new rest-calibrated
    # spectrum.

    # Repeat guessSpType function to get a better guess of the spectral type
    # and metallicity

    # End of the automatic guessing. We should have:
    #    1) Spectrum object with observed wavelength, flux, noise
    #    2) rest wavelength
    #    3) Spectral type (guessed)
    #    4) radial velocity and uncertainty,
    #    5) metallicity estimate,
    #    6) and line indice measurements.
    #    7) (eventually reddening?)

    # Write results in autoSpTResults.tbl
    # (includes spectral type, metallicity and RV measurements)

# Call the GUI to do the by eye spectral typing
