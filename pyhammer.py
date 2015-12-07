import sys
import os.path
import getopt
import numpy as np
import tkinter as tk
from tkinter import ttk
from spectrum import Spectrum
import eyecheck

def findRadialVelocity(spectrum, bestGuess):
    """
    findRadialVelocity(spectrum, bestGuess)

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

    # Do we want this as part of the Spectrum class instead?

    return rv

def guessSpecType():
    
    # CAN TRANSLATE FROM HAMMER
    # need to add in metallicity guess
    # Might need to be in spectrum class, depending on its usage.

    print('Not Implemented')


def main(options):
    """
    main(options)

    Description:
    This is the main part of the code that executes the
    actual pyhammer algorithms. This is arrived at either
    by startCmd or startGui, both of which get all the
    necessary options from the user and pass them to
    this function. The general process of this function
    should be to:
    
    1) Define a Spectrum object to be used in reading files
    2) Call the measureLines() method to find the good lines
    3) Run guessSpecType() to get the initial guessed spectral type.
    4) Use the best-guess from guessSpecType() and run findRadialVelocity() to find the
       radial velocity measurements, cross correlate the lines to get the inital
       spectral type and metallicity guess. Repeat for all spectra
    5) Bring up eyecheck GUI.

    Input:
    options  - A dict containing the options the
               user can specify. These may already
               have default values if they were
               provided on the command line.

    Output:
    autoSpTResults.tbl - list of the spectra with the results of the auto spectral
    typing, radial velocity and metallicity results.
    """

    # If the user has decided to not skip to the eyecheck, let's
    # do some processing
    if (not options['eyecheck']):
    
        # Open the input file and define a Spectrum object
        infile = open(options['infile'], 'r')
        spec = Spectrum()

        # Open and setup the output files
        outfile = open(options['outfile'], 'w')
        rejectfile = open(options['rejectfile'], 'w')
        outfile.write('Filename\t\tFile Type\t\tSpectra S/N\t\tSpectral Type\n')
        rejectfile.write('Filename\t\tFile Type\t\tSpectra S/N\n')

        for line in infile:
            # Remove extra whitespace and other unwanted characters and split
            fname, ftype = ' '.join(line.strip().split()).split(' ')

            # Now read in the current file
            success = spec.readFile(options['spectraPath']+fname, ftype)

            # If the attempt at reading the file did not succeed, then we
            # should just continue
            if (not success):
                rejectfile.write(fname + '\t' + ftype + '\tN/A\n')
                continue

            # Now that we have the necessary data in the spec object, let's
            # begin processing.

            ##########################
            ### OUTLINE OF PROCESS ###
            ##########################
            
            # Interpolate the observed spectrum to be logarithmically spaced.
            # Use interpSpec in spectrum class

            # Call the Spectrum.measureLines() function on the Spectrum object to get
            # the initial line measurements

            # Call the guessSpecType function to get an inital guess of the spectral type

            # Call findRadialVelocity function

            # Call a Spectrum.shiftToRest() that shifts the spectrum to rest
            # wavelengths.
            
            # Repeat the Spectrum.measurelines() on using the new rest-calibrated
            # spectrum.

            # Repeat guessSpecType function to get a better guess of the spectral type
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

            ######################
            ### END OF OUTLINE ###
            ######################
        
        # We're done so let's close all the files for now.
        infile.close()
        outfile.close()
        rejectfile.close()
    
    # At this point, we should call up the GUI to do the eyechecking.
    eyecheck.main()

def showHelpWindow(root, helpText):
    """
    showHelpWindow(root, helpText)

    Description:
    This brings up a new window derived from root
    that displays helpText and has a button to close
    the window when user is done.

    Input:
    root     - A tkinter Tk() window
    helpText - This should be a string to display
    """
    
    helpWindow = tk.Toplevel(root)
    helpWindow.title('PyHammer Help')
    helpWindow.iconbitmap(r'resources\sun.ico')
    helpWindow.resizable(False, False)
    helpWindow.geometry('+%i+%i' % (root.winfo_rootx()+50, root.winfo_rooty()+50))
    
    label = ttk.Label(helpWindow, text = helpText, font = '-size 10')
    label.grid(row = 0, column = 0, padx = 2, pady = 2)
    but = ttk.Button(helpWindow, text = 'OK', command = lambda: helpWindow.destroy())
    but.grid(row = 1, column = 0, sticky = 'nsew', padx = 2, pady = 5)
    helpWindow.rowconfigure(1, minsize = 40)

def startGui(options):
    """
    startGUI(options)

    Description:
    This brings up the beginning GUI the user can
    use to input initial options necessary for
    pyhammer to run. When the user hits the START
    button, these options update and are sent to the
    main function. Any options the user specified
    on the command line will be automatically set
    in the GUI.

    Inputs:
    options  - A dict containing the options the
               user can specify. These may already
               have default values if they were
               provided on the command line.
    """
    
    ##
    # Define some nested functions which will be
    # used by widgets in the GUI
    #

    def setState(entry, var):
        """
        Changes the state of the entry widget based on
        the value of the tk object var
        """
        entry.configure(state = ('disabled' if var.get() == 1 else 'normal'))

    def goToMain(root, infile, fullPath, spectraPath, eyecheck, sncut):
        """
        Accepts as options all the input parameters from the
        gui so they can be used to update the options dict.
        This will then progress to calling the main function
        with the options being passed to it.
        """
        options['infile'] = infile.get()
        if (fullPath.get() == 0):
            options['fullPath'] = False
            options['spectraPath'] = spectraPath.get()
        else:
            options['fullPath'] = True
            options['spectraPath'] = ''
        options['eyecheck'] = (eyecheck.get() == 1)
        if (options['eyecheck'] or sncut == ''):
            options['sncut'] = None
        else:
            options['sncut'] = float(sncut.get())
        
        root.destroy()

        main(options)

    ##
    # Start off by making the GUI and pass in whatever input options were
    # provided as the defaults, then let the user fill in the rest.
    #

    # Define the main window settings
    root = tk.Tk()
    root.title('PyHammer')
    root.iconbitmap(r'resources\sun.ico')
    root.resizable(False,False)
    root.geometry('+100+100')

    # --- Input Filename ---

    # Define the label
    label = ttk.Label(root, text = 'Spectra List\nFilename:')
    label.grid(row = 0, column = 0, padx = (2,1), pady = 1)

    # Define the entry box
    infile = tk.StringVar();
    infile.set('' if options['infile'] is None else options['infile'])
    entry = ttk.Entry(root, textvariable = infile, width = 40)
    entry.grid(row = 0, column = 1, columnspan = 3,  padx = 1, pady = 1)

    # Define the help text and button for this section
    infileHelpText = \
        'You should enter the full path to the input file\n' \
        'which contains a list of spectra files to process.\n' \
        'However, if the input file is located in the pyhammer.\n' \
        'folder, then simply the filename will suffice.'
    b = ttk.Button(root, text = '?', width = 2,
                   command = lambda: showHelpWindow(root, infileHelpText))
    b.grid(row = 0, column = 4, padx = (1,2), pady = 1)

    
    # --- Spectra File Path ---

    # Define the label
    label = ttk.Label(root, text = 'Spectra File\nPath:')
    label.grid(row = 2, column = 0, padx = (2,1), pady = 1)

    # Define the entry box
    spectraPath = tk.StringVar();
    spectraPath.set('' if options['spectraPath'] is None else options['spectraPath'])
    sPathEntry = ttk.Entry(root, textvariable = spectraPath, width = 40)
    sPathEntry.grid(row = 2, column = 1, columnspan = 3,  padx = 1, pady = 1)
    sPathEntry.configure(state = ('disabled' if options['fullPath'] else 'normal'))

    # Define the help text and button for this section
    spectraPathHelpText = \
        'If your spectra list does not contain the full path\n' \
        'to the files in the name, provide a path to prepend\n' \
        'to each spectra filename.'
    b = ttk.Button(root, text = '?', width = 2,
                   command = lambda: showHelpWindow(root, spectraPathHelpText))
    b.grid(row = 2, column = 4, padx = (1,2), pady = 1)


    # --- Full Path ---

    # Define the label
    label = ttk.Label(root, text = 'Spectra list contains the full path:')
    label.grid(row = 1, column = 0, columnspan = 2, padx = 2, pady = 2, stick = 'w')

    # Define the radiobuttons
    fullPath = tk.IntVar()
    fullPath.set(0 if options['fullPath'] == None else options['fullPath'])
    rbuttonYes = ttk.Radiobutton(root, text = 'Y', value = 1, variable = fullPath,
                                 command = lambda: setState(sPathEntry, fullPath))
    rbuttonYes.grid(row = 1, column = 2, padx = 1, pady = 1)
    rbuttonNo = ttk.Radiobutton(root, text = 'N', value = 0, variable = fullPath,
                                command = lambda: setState(sPathEntry, fullPath))
    rbuttonNo.grid(row = 1, column = 3, padx = 1, pady = 1)

    # Define the help text and button for this section
    fullPathHelpText = \
        'Choose whether or not the spectra listed in your input\n' \
        'file have a full path specified. If you choose no, you\n' \
        'will need to specify the full path to the spectra.'
    b = ttk.Button(root, text = '?', width = 2,
                   command = lambda: showHelpWindow(root, fullPathHelpText))
    b.grid(row = 1, column = 4, padx = (1,2), pady = 1)


    # --- S/N Cutoff ---

    # Define the label
    label = ttk.Label(root, text = 'S/N Cutoff:')
    label.grid(row = 4, column = 0, padx = (2,1), pady = 1)

    # Define the entry box
    sncut = tk.StringVar();
    sncut.set('' if options['sncut'] is None else options['sncut'])
    sncutEntry = ttk.Entry(root, textvariable = sncut, width = 40)
    sncutEntry.grid(row = 4, column = 1, columnspan = 3,  padx = 1, pady = (4,1))
    sncutEntry.configure(state = ('disabled' if options['eyecheck'] else 'normal'))

    # Define the help text and button for this section
    sncutHelpText = \
        'If you would like to only classify spectra with a S/N\n' \
        'above a threshold, provide that value here. If you do not\n' \
        'want to provide a cutoff, leave this field blank. This\n' \
        'option does not apply if you choose to skip to the eyecheck.'
    b = ttk.Button(root, text = '?', width = 2,
                   command = lambda: showHelpWindow(root, sncutHelpText))
    b.grid(row = 4, column = 4, padx = (1,2), pady = (4,1))

    
    # --- Skip to Eye Check ---
    
    # Define the label
    label = ttk.Label(root, text = 'Skip to eyecheck:')
    label.grid(row = 3, column = 0, columnspan = 2, padx = 2, pady = 2, stick = 'w')

    # Define the radiobuttons
    eyecheck = tk.IntVar()
    eyecheck.set(0 if options['eyecheck'] == None else options['eyecheck'])
    rbuttonYes = ttk.Radiobutton(root, text = 'Y', value = 1, variable = eyecheck,
                                 command = lambda: setState(sncutEntry, eyecheck))
    rbuttonYes.grid(row = 3, column = 2, padx = 1, pady = 1)
    rbuttonNo = ttk.Radiobutton(root, text = 'N', value = 0, variable = eyecheck,
                                command = lambda: setState(sncutEntry, eyecheck))
    rbuttonNo.grid(row = 3, column = 3, padx = 1, pady = 1)

    # Define the help text and button for this section
    eyecheckHelpText = \
        'If you have already classified your spectra you can\n' \
        'choose to skip directly to checking them by eye, rather\n' \
        'than re-running the classification algorithm again.'
    b = ttk.Button(root, text = '?', width = 2,
                   command = lambda: showHelpWindow(root, eyecheckHelpText))
    b.grid(row = 3, column = 4, padx = (1,2), pady = 1)

    
    # --- Start Button ---
    b = ttk.Button(root, text = 'START',
                   command = lambda: goToMain(root, infile, fullPath,
                                              spectraPath, eyecheck, sncut))
    b.grid(row = 5, column = 0, columnspan = 5, sticky = 'nswe', padx = 5, pady = 5)
    root.rowconfigure(5, minsize = 40)

    root.mainloop()

def startCmd(options):
    """
    startCmd(options)

    Description:
    This provides command line inputs for the user
    to enter options. It will only ask questions
    about options the user has not already specified
    at run time. This will then pass the updated
    options to the main function.

    Inputs:
    options  - A dict containing the options the
               user can specify. These may already
               have default values if they were
               provided on the command line.
    """

    ##
    # If the input options were not provided on the command line at
    # execution, we need to ask for them here.
    #

    # Get the input filename if one was not provided
    if (options['infile'] is None):
        options['infile'] = input('Please enter the filename which contains the spectra list: ')

    # Check whehter the input file list contains the full path if
    # the user didn't already specify.
    if (options['fullPath'] is None):
        ans = input('Does your input list give the full path to each spectrum? (y/n): ')
        if (ans == 'y' or ans == 'Y'):
            options['fullPath'] = True
            options['spectraPath'] = ''
        else:
            options['fullPath'] = False
            options['spectraPath'] = input('Enter the necessary path for each file: ')
            # Append a slash to the end if there isn't one
            if (options['spectraPath'][-1] not in ['\\', '/']):
                options['spectraPath'] += '\\'

    # Asks the user if they want to skip the auto-classifying and skip straight
    # to checking by eye, if they have not already specified.
    if (options['eyecheck'] is None):
        ans = input('Do you want to skip straight to eye-checking? (y/n): ')
        options['eyecheck'] = True if ans == 'y' or ans == 'Y' else False

    # Asks the user if they want to apply a S/N cut when classifying the spectra.
    # This only applies if they chose not to skip the auto-classification
    if (options['eyecheck'] == False and options['sncut'] is None):
        ans = input('Do you want to supply a S/N cut when auto-classifying? (y/n): ')
        if (ans == 'y' or ans == 'Y'):
            ans = input('Choose a S/N cutoff (~3-5 recommended): ')
            options['sncut'] = float(ans)

    # Now that all the options have been set, let's get started
    main(options)

if (__name__ == "__main__"):

    # Check if this is the first time this code has been executed by looking
    # for the runbefore file in the resources folder
    if (not os.path.isfile('resources/runbefore')):
        # The file doesn't exist. Let's create it and display the welcome message
        f = open('resources/runbefore', 'w')
        f.close()
        print('Welcome to pyhammer, a tool for spectral classification!\n'
              'First time users should run this program with the -h flag '
              'to learn more information.', flush = True)
    
    # Define default options
    options = {'infile': None, 'outfile': 'pyhammerResults.txt',
               'rejectfile': 'rejectSpectra.txt', 'fullPath': None,
               'spectraPath': None, 'eyecheck': None, 'sncut': None}
    
    ##
    # Check input conditions
    #

    opts, args = getopt.getopt(sys.argv[1:], 'hi:o:r:fp:es:cg',
                               ['help', 'infile=', 'outfile=', 'rejectfile=',
                                'full', 'path=', 'eyecheck', 'sncut',
                                'cmd', 'gui'])

    # First check if help is requested and options
    for opt, arg in opts:

        # Help option is chosen
        if (opt == '-h' or opt == '--help'):

            print(('\nWelcome to the pyhammer, a tool for spectral '
                   'classification.\n'
                   
                   '\nOptions:\n'
                   
                   '-c, --cmd\t\t\t'
                   'Flag to choose to run on the command line.\n'

                   '-e, --eyecheck\t\t'
                   'Flag indicating pyhammer should skip classifying\n'
                   '\t\t\t\t\tand go straight to checking the spectra by eye.\n'
                   
                   '-f, --full\t\t\t'
                   'Flag indicating the full path to the spectra is\n'
                   '\t\t\t\t\tprovided in the input file list.\n'
                   
                   '-g, --gui\t\t\t'
                   'Flag to choose to run using the gui.\n'
                   
                   '-i, --infile\t\t'
                   'The full path to the input file or the name, if it\n'
                   '\t\t\t\t\tis in the pyhammer folder. If nothing is\n'
                   '\t\t\t\t\tprovided, it will be asked for later.\n'
                   
                   '-o, --outfile\t\t'
                   'The full path to the output file or a filename\n'
                   '\t\t\t\t\twhich outputs to the pyhammer folder. If nothing is\n'
                   '\t\t\t\t\tprovided, the default pyhammerResults.txt will be\n'
                   '\t\t\t\t\tcreated in the pyhammer folder.\n'

                   '-p, --path\t\t\t'
                   'The full path to the spectra. This is only necessary\n'
                   '\t\t\t\t\tif the input file list does not prepend the path to\n'
                   '\t\t\t\t\tthe spectra filenames.\n'
                   
                   '-r, --rejectfile\t'
                   'The full path to the file where reject spectra will\n'
                   '\t\t\t\t\tbe listed or a filename which outputs to the\n'
                   '\t\t\t\t\tpyhammer folder . If nothing is provided, the\n'
                   '\t\t\t\t\tdefault rejectSpectra.txt will be created in the\n'
                   '\t\t\t\t\tpyhammer folder.\n'

                   '-s, --sncut\t\t\t'
                   'The S/N necessary before a spectra will be classified.\n'
                   '\t\t\t\t\tA signal to noise of ~3-5 per pixel is recommended.\n').expandtabs(4),
                  flush = True)
            sys.exit(0)

        # User provided input file listing spectra
        if (opt == '-i' or opt == '--infile'):
            options['infile'] = arg

        # User provided output file for spectra classification
        if (opt == '-o' or opt == '--outfile'):
            options['outfile'] = arg

        # User provided output file for reject spectra
        if (opt == '-r' or opt == '--rejectfile'):
            options['rejectfile'] == arg

        # User indicated that the full path to the spectra is in the
        # input file list
        if (opt == '-f' or opt == '--full'):
            if (options['fullPath'] is not None):
                sys.exit('Cannot supply -f and -p at the same time.')
            else:
                options['fullPath'] = True
                options['spectraPath'] = ''

        # User provided a path to prepend to the spectra file names
        if (opt == '-p' or opt == '--path'):
            if (options['fullPath'] is not None):
                sys.exit('Cannot supply -f and -p at the same time.')
            else:
                options['fullPath'] = False
                options['spectraPath'] = arg
                # Append a slash to the end if there isn't one
                if (options['spectraPath'][-1] not in ['\\', '/']):
                    options['spectraPath'] += '\\'
            
        # User indicated they want to skip to the eyecheck
        if (opt == '-e' or opt == '--eyecheck'):
            if (options['sncut'] is not None):
                sys.exit('Flag -s is unnecessary when -e is provided.')
            else:
                options['eyecheck'] = True

        # User indicates they want a S/N cut to be applied
        if (opt == '-s' or opt == '--sncut'):
            if (options['eyecheck'] == True):
                sys.exit('Flag -s is unnecessary when -e is provided.')
            else:
                options['eyecheck'] = False
                options['sncut'] = arg
                
    
    # Now check whether user requested command line or GUI interface
    for opt, arg in opts:
        
        # Command line interface is requested.
        if (opt == '-c' or opt == '--cmd'):
            startCmd(options)
            sys.exit(0)

        # GUI interface is requested.
        if (opt == '-g' or opt == '--gui'):
            startGui(options)
            sys.exit(0)

    # If no interface is chosen, run on the command line by default
    startCmd(options)

else:
    
    sys.exit("Do not import pyhammer. Run this script with the run command "
             "in the python environment, or by invoking with the python command "
             "on the command line. Use the -h flag for more information.")
