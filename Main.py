
"""
Main(spectraFilename)

Description: 
This is the main portion of the code. It calls the other functions used. It's main function is to: 
call the Spectrum class, do the radial velocity measurements, 
cross correlate the lines to get the inital spectral type and metallicity guess, bring up the GUI. 

Input: 
spectraFilename - a list of the filenames of each of the spectra to be classified (one per line), 
and the corresponding filetype (i.e., sdssfits, fits, txt, etc.)

Output: 
autoSpTResults.tbl - list of the spectra with the results of the auto spectral typing, radial velocity and metallicity results. 
"""

#function that does the radial velocity code
def radialVelocity(): 
    #Dylan's code goes here

#function that compares the indices and gets a spectral type guess
def guessSpecType():
    #CAN TRANSLATE FROM HAMMER
    #need to add in metallicity guess

#Check for the correct path
#CAN TRANSLATE

#Check if user wants to run the autospectral typing
#CAN TRANSLATE

#Check if user wants a S/N cut
#CAN TRANSLATE


#Read in the files
#Call the Spectrum object for each spectra in the list
#Call the measurelines function in the Spectrum object to get the initial line measurements

#Call the guessSpType function to get an inital guess of the spectral type

#Call radialVelocity function
#When we have an RV recall measurelines function in Spectrum object
#Recall the guessSpType function to get a better guess of the spectral type and metallicity

#Write results in autoSpTResults.tbl (includes spectral type, metallicity and RV measurements)
#Call the GUI to do the by eye spectral typing





