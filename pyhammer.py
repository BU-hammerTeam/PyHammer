import sys
import os.path
import getopt
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from time import time
import pdb
from spectrum import Spectrum
from eyecheck import Eyecheck
from gui_utils import *

def main(options):
    """
    The main method of PyHammer which executes the overarching procedure.

    Description:
        This is the main part of the code that executes the
        actual pyhammer algorithms. This is arrived at either
        by startCmd or StartGUI, both of which get all the
        necessary options from the user and pass them to
        this function. The general process of this function
        should be to:
        
        - Define a Spectrum object to be used in reading files.
        - Load each spectrum sequentially.
        - Guess the spectral type.
        - Use the best guess for the spectral type and find the radial
          velocity shift. Shift the spectrum to rest.
        - Guess the spectral type again.
        - Repeat for all spectra
        - Bring up eyecheck GUI.

    Input:
        options: A dict containing the options the user has specified.

    Output:
        This program outputs two files, an outfile and a rejectfile.
        The outfile contains all results of the spectral type guess
        as well as the user's eyecheck guess and the rejectfile contains
        the list of spectra which could not be classified for some reason.
    """

    # Create a Spectrum object
    spec = Spectrum()

    # If the user has decided to not skip to the eyecheck, let's
    # do some processing
    if not options['eyecheck']:
    
        # Open the input file
        try:
            infile = open(options['infile'], 'r')
        except IOError as e:
            notifyUser(options['useGUI'], str(e))
            return

        # Open and setup the output files
        outfile = open(options['outfile'], 'w')
        rejectfile = open(options['rejectfile'], 'w')
        outfile.write('#Filename,Radial Velocity (km/s),Guessed Spectral Type,Guessed Metallicity,User Spectral Type,User Metallicity\n')
        rejectfile.write('#Filename,File Type,Spectra S/N\n')

        # Define the string to contain all failure messages. These will be compiled
        # and printed once at the end, if anything is put into it.
        rejectMessage = ''

        for i, line in enumerate(infile):
            # Remove extra whitespace and other unwanted characters and split
            line = line.strip()
            if line.find(',') > 0: line = line.replace(',',' ')
            fname, ftype = ' '.join(line.split()).rsplit(' ',1)

            # Print statement of progress for user
            print(i+1, ') Processing ', os.path.basename(fname), sep = '')

            # Now read in the current file (this process reads in the file, converts air to 
            # vac when necessary and interpolates onto the template grid)
            success, message = spec.readFile(options['spectraPath']+fname, ftype)

            # If the attempt at reading the file did not succeed, then we
            # should just continue
            if not success:
                rejectfile.write(fname + ',' + ftype + ',N/A\n')
                rejectMessage += 'FILE: ' + fname + '  REASON: ' + message.replace('\n','') + '\n'
                continue

            # Now that we have the necessary data in the spec object, let's
            # begin processing.

            # --- 1 ---
            # Calculate the signal to noise of the spectrum to potentially reject
            if options['sncut'] is not None:
                snVal = spec.calcSN()
                if snVal < options['sncut']:
                    rejectfile.write(fname + ',' + ftype + ',' + str(snVal) + '\n')
                    rejectMessage += 'FILE: ' + fname + '  REASON: S/N = ' + str(snVal) + ' < ' + str(options['sncut']) + '\n'
                    continue
            
            # --- 2 ---
            # Normalize the input spectrum to the same place where the templates are normalized (8000A)
            spec.normalizeFlux()

            # --- 3 ---
            # Call guessSpecType function for the initial guess
            # this function measures the lines then makes a guess of all parameters
            spec.guessSpecType()

            # --- 4 ---
            # Call findRadialVelocity function using the initial guess
            shift = spec.findRadialVelocity()

            # --- 5 ---
            # Call shiftToRest that shifts the spectrum to rest wavelengths,
            # then interp back onto the grid
            spec.shiftToRest(shift)
            spec.interpOntoGrid()

            # --- 6 ---
            # Repeat guessSpecType function to get a better guess of the spectral 
            # type and metallicity 
            spec.guessSpecType()

            # End of the automatic guessing. We should have:
            #  1. Spectrum object with observed wavelength, flux, var,
            #  2. rest wavelength,
            #  3. spectral type (guessed),
            #  4. radial velocity and uncertainty,
            #  5. metallicity estimate,
            #  6. and line indice measurements

            # --- 7 ---
            
            # Translate the numbered spectral types into letters
            letterSpt = ['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L'][spec.guess['specType']]
            
            # Write the file
            outfile.write(fname + ',' + str(shift) + ',' + letterSpt + str(spec.guess['subType']) +
                          ',' + '{:+2.1f}'.format(spec.guess['metal']) + ',nan,nan' + '\n')
        
        # We're done so let's close all the files.
        infile.close()
        outfile.close()
        rejectfile.close()

        # Check that we processed every spectrum in the infile. If not, print out
        # the reject method.
        if rejectMessage != '':
            # Prepend to the reject message
            rejectMessage = 'The following is a list of rejected spectra\n' \
                            'along with the reason for its rejection.\n\n' + rejectMessage
            notifyUser(options['useGUI'], rejectMessage)
            # Check if all spectra were skipped by seeing if the number of
            # lines in the reject message is equal to the number of spectra
            # processed (plus three lines for the prepended message). If
            # they were all skipped, theres nothing to eyecheck so return.
            if rejectMessage.count('\n') == i+4:
                notifyUser(options['useGUI'], 'All spectra were bad. Exiting PyHammer.')
                # Clean up any temporary input files created
                if os.path.basename(options['infile'])[:11] == 'temp_input_':
                    os.remove(options['infile'])
                return
    
    # At this point, we should call up the GUI to do the eyechecking.
    Eyecheck(spec, options)

    # Clean up any temporary input files created
    if os.path.basename(options['infile'])[:11] == 'temp_input_':
        os.remove(options['infile'])

def notifyUser(useGUI, message):
    """
    Description:
        A method for handling sending messages to the
        user during the execution of the main function.
        The reason for making this a separate function
        is to handle where we need to send the message.
        If the user started using a GUI, we want to
        use a GUI to notify them, otherwise, if they
        were using the command line, print to the command
        line.

    Input:
        useGUI: A boolean indicating whether or not to
            use a GUI to notify the user. This is set
            in the options dict.
        message: The message to present to the user.
    """

    if not useGUI:
        # Simple case, just print the message.
        print(message, flush = True)
    else:
        # More involved case, create a tk window to
        # display the message.
        InfoWindow(message, title = 'PyHammer Notification')

class StartGUI(object):

    def __init__(self, options):

        self.options = options

        self.defineHelpText()

        # --- Create Window ---

        self.root = tk.Tk()
        self.root.title('PyHammer Settings')
        self.root.iconbitmap(os.path.join(os.path.split(__file__)[0],'resources','sun.ico'))
        self.root.resizable(False,False)
        self.root.geometry('+100+100')

        
        self.defineWidgets()

        self.layoutWidgets()

        self.updateGui()

        self.root.mainloop()

    def defineHelpText(self):
        
        self.infileHelpText = (
            'Here you can provide an input file of spectra to process. '
            'Browse for an already created file, or else choose to create '
            'the file within the GUI. If you supply a path to an already '
            'defined file, you should include the full path, or else a '
            'path relative to the PyHammer directory. The input file can '
            'be any ascii file including txt and csv.\n\n'
            'To create the input file, list all your spectra in one column '
            'and the corresponding spectra type in the second column. '
            'You should ideally supply the full path for each spectra, '
            "but if they're all in the same directory, a later setting "
            'allows for prepending the same path to all spectra.')
        
        self.outfileHelpText = (
            'You should include the full path to the output file '
            'which will contain the results of PyHammer. However, '
            'if no path is supplied, the file will be saved to the '
            'the pyhammer folder. The output file is, by default, '
            'set to PyHammerResults.csv unless specified otherwise. '
            'The output filetype should be a csv file.')
        
        self.rejectfileHelpText = (
            'You should include the full path to the reject file '
            'which will contain the list of any spectra unable to '
            'be classified. However, if no path is supplied, the '
            'file will be saved to the the pyhammer folder. The '
            'reject file is, by default, set to RejectSpectra.csv '
            'unless specified otherwise. The reject filetype should '
            'be a csv file.')
        
        self.fullPathHelpText = (
            'Choose whether or not the spectra listed in your input '
            'file have a full path specified. If you choose no, you '
            'will need to specify the full path to the spectra. ')
        
        self.spectraPathHelpText = (
            'If your spectra list does not contain the full path '
            'to the files in the name, provide a path to prepend '
            'to each spectra filename.')
        
        self.eyecheckHelpText = (
            'If you have already classified your spectra you can '
            'choose to skip directly to checking them by eye, rather '
            'than re-running the classification algorithm again. Note '
            'that you cannot skip to eye checking without first '
            'classifying your spectra and creating an output file.')
        
        self.sncutHelpText = (
            'If you would like to only classify spectra with a S/N '
            'above a threshold, provide that value here. If you do not '
            'want to provide a cutoff, leave this field blank. This '
            'option does not apply if you choose to skip to the eyecheck.')

    def defineWidgets(self):
        
        # --- Input Field ---

        # Define Input Widgets
        self.infileFrame = ttk.Frame(self.root, relief = tk.FLAT)
        self.infileLabel = ttk.Label(self.infileFrame, text = 'Provide an existing input file or create a new input file.')
        self.infile = tk.StringVar(value = ('' if options['infile'] is None else options['infile']))
        self.infileEntry = ttk.Entry(self.infileFrame, textvariable = self.infile)
        self.infileBrowseButton = ttk.Button(self.infileFrame, text = 'Browse', command = lambda: self.browse(self.infileEntry, 'file'))
        self.infileBrowseToolTip = ToolTip(self.infileBrowseButton, 'Browse for an existing input file')
        self.createPressed = False
        self.createButton = ttk.Button(self.infileFrame, text = 'Create', command = self.createInputFile)
        ToolTip(self.createButton, 'Create a new input file')
        self.infileHelpButton = ttk.Button(self.infileFrame, text = '?', width = 2, command = lambda: InfoWindow(self.infileHelpText, parent = self.root, title = 'PyHammer Help', pos = 'right'))

        # Define Create Widgets
        self.createFrame = ttk.Frame(self.infileFrame, relief = tk.FLAT)
        self.createWindow = tk.Text(self.createFrame, relief = tk.FLAT, wrap = tk.NONE, font = '-family courier -size 10')
        self.scrollV = ttk.Scrollbar(self.createFrame, command = self.createWindow.yview)
        self.scrollH = ttk.Scrollbar(self.createFrame, orient = tk.HORIZONTAL, command = self.createWindow.xview)
        self.selectFiles = ttk.Button(self.createFrame, text = 'Select Spectra', command = self.createInputFromDirectory)
        ToolTip(self.selectFiles, 'Select a set of spectrum files\nto add to the input file')
        ttk.Separator(self.createFrame, orient = tk.VERTICAL).grid(row = 2, column = 1, padx = 4, stick = 'wns')
        self.dataType = tk.StringVar()
        self.dataTypeList = ttk.OptionMenu(self.createFrame, self.dataType, 'DR12fits', 'DR12fits', 'DR7fits', 'fits', 'txt', 'csv')
        self.applyType = ttk.Button(self.createFrame, text = 'Apply Data Type', command = self.applyType)
        ToolTip(self.applyType, 'Append the selected data type to every file in the list')

        # --- Output Field ---

        self.outfileFrame = ttk.Frame(self.root, relief = tk.FLAT)
        self.outfileLabel = ttk.Label(self.outfileFrame, text = 'Provide an output file')
        self.outfile = tk.StringVar(value = options['outfile'])
        self.outfileEntry = ttk.Entry(self.outfileFrame, textvariable = self.outfile)
        self.outfileBrowseButton = ttk.Button(self.outfileFrame, text = 'Browse', command = lambda: self.browse(self.outfileEntry, 'file'))
        self.outfileBrowseToolTip = ToolTip(self.outfileBrowseButton, 'Browse for an existing output file or define a new one')
        self.outfileHelpButton = ttk.Button(self.outfileFrame, text = '?', width = 2, command = lambda: InfoWindow(self.outfileHelpText, parent = self.root, title = 'PyHammer Help', pos = 'right'))

        # --- Reject Field ---

        self.rejectfileFrame = ttk.Frame(self.root, relief = tk.FLAT)
        self.rejectfileLabel = ttk.Label(self.rejectfileFrame, text = 'Provide a reject file')
        self.rejectfile = tk.StringVar(value = options['rejectfile'])
        self.rejectfileEntry = ttk.Entry(self.rejectfileFrame, textvariable = self.rejectfile)
        self.rejectfileBrowseButton = ttk.Button(self.rejectfileFrame, text = 'Browse', command = lambda: self.browse(self.rejectfileEntry, 'file'))
        self.rejectfileBrowseToolTip = ToolTip(self.rejectfileBrowseButton, 'Browse for an existing reject file or define a new one')
        self.rejectfileHelpButton = ttk.Button(self.rejectfileFrame, text = '?', width = 2, command = lambda: InfoWindow(self.rejectfileHelpText, parent = self.root, title = 'PyHammer Help', pos = 'right'))

        # --- Full Path Field ---

        self.fullPathFrame = ttk.Frame(self.root, relief = tk.FLAT)
        self.fullPathLabel = ttk.Label(self.fullPathFrame, text = 'Do the spectra in the input file contain full paths?')
        self.fullPath = tk.IntVar(value = (0 if options['fullPath'] is None else options['fullPath']))
        self.fullPathYes = ttk.Radiobutton(self.fullPathFrame, text = 'Yes', value = 1, variable = self.fullPath, command = self.updateGui)
        self.fullPathNo = ttk.Radiobutton(self.fullPathFrame, text = 'No', value = 0, variable = self.fullPath, command = self.updateGui)
        self.fullPathHelpButton = ttk.Button(self.fullPathFrame, text = '?', width = 2, command = lambda: InfoWindow(self.fullPathHelpText, parent = self.root, title = 'PyHammer Help', pos = 'right'))

        # --- Spectra Path Field ---

        self.spectraPathFrame = ttk.Frame(self.root, relief = tk.FLAT)
        self.spectraPathLabel = ttk.Label(self.spectraPathFrame, text = 'Provide the path to the spectra files')
        self.spectraPath = tk.StringVar(value = ('' if options['spectraPath'] is None else options['spectraPath']))
        self.spectraPathEntry = ttk.Entry(self.spectraPathFrame, textvariable = self.spectraPath)
        self.spectraPathBrowseButton = ttk.Button(self.spectraPathFrame, text = 'Browse', command = lambda: self.browse(self.spectraPathEntry, 'directory'))
        ToolTip(self.spectraPathBrowseButton, 'Browse for the directory containing the spectra files')
        self.spectraPathHelpButton = ttk.Button(self.spectraPathFrame, text = '?', width = 2, command = lambda: InfoWindow(self.spectraPathHelpText, parent = self.root, title = 'PyHammer Help', pos = 'right'))

        # --- Eyecheck Field ---

        self.eyecheckFrame = ttk.Frame(self.root, relief = tk.FLAT)
        self.eyecheckLabel = ttk.Label(self.eyecheckFrame, text = 'Do you want to skip to classifying by eye?')
        self.eyecheck = tk.IntVar(value = (0 if options['eyecheck'] is None else options['eyecheck']))
        self.eyecheckYes = ttk.Radiobutton(self.eyecheckFrame, text = 'Yes', value = 1, variable = self.eyecheck, command = self.updateGui)
        self.eyecheckNo = ttk.Radiobutton(self.eyecheckFrame, text = 'No', value = 0, variable = self.eyecheck, command = self.updateGui)
        self.eyecheckHelpButton = ttk.Button(self.eyecheckFrame, text = '?', width = 2, command = lambda: InfoWindow(self.eyecheckHelpText, parent = self.root, title = 'PyHammer Help', pos = 'right'))

        # --- S/N Cut Field ---

        self.sncutFrame = ttk.Frame(self.root, relief = tk.FLAT)
        self.sncutLabel = ttk.Label(self.sncutFrame, text = 'Enter a signal to noise cutoff')
        self.sncut = tk.StringVar(value = ('' if options['sncut'] is None else options['sncut']))
        self.sncutEntry = ttk.Entry(self.sncutFrame, textvariable = self.sncut)
        self.sncutHelpButton = ttk.Button(self.sncutFrame, text = '?', width = 2, command = lambda: InfoWindow(self.sncutHelpText, parent = self.root, title = 'PyHammer Help', pos = 'right'))

        # --- Start Button ---

        self.startButton = ttk.Button(self.root, text = 'Start PyHammer', command = self.goToMain)

    def layoutWidgets(self):
        
        # --- Input Field ---
        
        # Layout Create Widgets
        self.createWindow.grid(row = 0, column = 0, columnspan = 4)
        self.scrollV.grid(row = 0, column = 4, sticky = 'ns')
        self.scrollH.grid(row = 1, column = 0, columnspan = 4, sticky = 'ew')
        self.selectFiles.grid(row = 2, column = 0, sticky = 'w')
        self.dataTypeList.grid(row = 2, column = 2, padx = (0,4), sticky = 'w')
        self.applyType.grid(row = 2, column = 3, sticky = 'w')
        self.createFrame.columnconfigure(3, weight = 1)
        self.createWindow.configure(yscrollcommand = self.scrollV.set, xscrollcommand = self.scrollH.set)

        # Layout Input Widgets
        self.infileLabel.grid(row = 0, column = 0, columnspan = 4)
        self.infileEntry.grid(row = 1, column = 0, padx = 1, pady = 1, sticky = 'ew')
        self.infileBrowseButton.grid(row = 1, column = 1, padx = 1, pady = 1)
        self.createButton.grid(row = 1, column = 2, padx = 1, pady = 1)
        self.infileHelpButton.grid(row = 1, column = 3, padx = 1, pady = 1, sticky = 'e')

        # Configure Input Frame
        self.infileFrame.grid(row = 0, column = 0)
        self.infileFrame.columnconfigure(0, minsize = 250, weight = 1)
        self.infileFrame.columnconfigure(1, weight = 0)
        self.infileFrame.columnconfigure(2, weight = 0)
        self.infileFrame.columnconfigure(3, weight = 0)

        # --- Output Field ---

        # Layout Output Widgets
        self.outfileLabel.grid(row = 0, column = 0, columnspan = 3)
        self.outfileEntry.grid(row = 1, column = 0, padx = 1, pady = 1, sticky = 'ew')
        self.outfileBrowseButton.grid(row = 1, column = 1, padx = 1, pady = 1)
        self.outfileHelpButton.grid(row = 1, column = 2, padx = 1, pady = 1, sticky = 'e')

        # Configure Output Frame
        self.outfileFrame.grid(row = 2, column = 0, sticky = 'ew')
        self.outfileFrame.columnconfigure(0, minsize = 250, weight = 1)

        # --- Reject Field ---

        # Layout Reject Widgets
        self.rejectfileLabel.grid(row = 0, column = 0, columnspan = 3)
        self.rejectfileEntry.grid(row = 1, column = 0, padx = 1, pady = 1, sticky = 'ew')
        self.rejectfileBrowseButton.grid(row = 1, column = 1, padx = 1, pady = 1)
        self.rejectfileHelpButton.grid(row = 1, column = 2, padx = 1, pady = 1, sticky = 'e')

        # Configure Reject Frame
        self.rejectfileFrame.grid(row = 4, column = 0, sticky = 'ew')
        self.rejectfileFrame.columnconfigure(0, minsize = 250, weight = 1)

        # --- Full Path Field ---

        # Layout Full Path Widgets
        self.fullPathLabel.grid(row = 0, column = 0, columnspan = 3)
        self.fullPathYes.grid(row = 1, column = 0, padx = 5, stick = 'e')
        self.fullPathNo.grid(row = 1, column = 1, padx = 5, sticky = 'w')
        self.fullPathHelpButton.grid(row = 1, column = 2, padx = 1, pady = 1, sticky = 'e')

        # Configure Full Path Frame
        self.fullPathFrame.grid(row = 6, column = 0, sticky = 'ew')
        self.fullPathFrame.columnconfigure(0, minsize = 0, weight = 1)
        self.fullPathFrame.columnconfigure(1, weight = 1)
        self.fullPathFrame.columnconfigure(2, weight = 0)

        # --- Spectra Path Field ---

        # Layout Reject Widgets
        self.spectraPathLabel.grid(row = 0, column = 0, columnspan = 3)
        self.spectraPathEntry.grid(row = 1, column = 0, padx = 1, pady = 1, sticky = 'ew')
        self.spectraPathBrowseButton.grid(row = 1, column = 1, padx = 1, pady = 1)
        self.spectraPathHelpButton.grid(row = 1, column = 2, padx = 1, pady = 1, sticky = 'e')

        # Configure Spectra Path Frame
        self.spectraPathFrame.grid(row = 8, column = 0, sticky = 'ew')
        self.spectraPathFrame.columnconfigure(0, minsize = 250, weight = 1)

        # --- Eyecheck Field ---

        # Layout Eyecheck Widgets
        self.eyecheckLabel.grid(row = 0, column = 0, columnspan = 3)
        self.eyecheckYes.grid(row = 1, column = 0, padx = 5, stick = 'e')
        self.eyecheckNo.grid(row = 1, column = 1, padx = 5, sticky = 'w')
        self.eyecheckHelpButton.grid(row = 1, column = 2, padx = 1, pady = 1, sticky = 'e')

        # Configure Eyecheck Frame
        self.eyecheckFrame.grid(row = 10, column = 0, sticky = 'ew')
        self.eyecheckFrame.columnconfigure(0, minsize = 0, weight = 1)
        self.eyecheckFrame.columnconfigure(1, weight = 1)
        self.eyecheckFrame.columnconfigure(2, weight = 0)

        # --- SN Cut Field ---

        # Layout Reject Widgets
        self.sncutLabel.grid(row = 0, column = 0, columnspan = 2)
        self.sncutEntry.grid(row = 1, column = 0, padx = 1, pady = 1, sticky = 'ew')
        self.sncutHelpButton.grid(row = 1, column = 1, padx = 1, pady = 1, sticky = 'e')

        # Configure S/N Cutoff Frame
        self.sncutFrame.grid(row = 12, column = 0, sticky = 'ew')
        self.sncutFrame.columnconfigure(0, minsize = 250, weight = 1)

        # --- Separators ---

        self.sep = []
        for i in range(7):
            self.sep.append(ttk.Separator(self.root, orient = tk.HORIZONTAL))
            self.sep[-1].grid(row = i*2+1, column = 0, padx = 2, pady = 2, stick = 'nsew')

        # --- Start Button ---
        self.startButton.grid(row = 14, column = 0, padx = 2, pady = (4,2), stick = 'nsew')

    def updateGui(self):

        if self.fullPath.get() == 0:
            self.spectraPathFrame.grid(row = 8, column = 0, sticky = 'ew')
            self.sep[4].grid(row = 9, column = 0, padx = 2, pady = 2, stick = 'nsew')
            eyecheckRow = 10
        else:
            self.spectraPathFrame.grid_forget()
            self.sep[4].grid_forget()
            eyecheckRow = 8

        self.eyecheckFrame.grid(row = eyecheckRow, column = 0, sticky = 'ew')
        self.sep[5].grid(row = eyecheckRow + 1, column = 0, padx = 2, pady = 2, stick = 'nsew')
        sncutRow = eyecheckRow + 2
        
        if self.eyecheck.get() == 0:
            self.sncutFrame.grid(row = sncutRow, column = 0, sticky = 'ew')
            self.sep[6].grid(row = sncutRow + 1, column = 0, padx = 2, pady = 2, stick = 'nsew')
            startRow = sncutRow + 2
        else:
            self.sncutFrame.grid_forget()
            self.sep[6].grid_forget()
            startRow = eyecheckRow + 2

        self.startButton.grid(row = startRow, column = 0, padx = 2, pady = (4,2), stick = 'nsew')


    def createInputFile(self):
        self.createPressed = not self.createPressed # Invert boolean

        self.infileEntry.configure(state = ('disabled' if self.createPressed else 'normal'))
        self.infileBrowseButton.configure(state = ('disabled' if self.createPressed else 'normal'))

        # Add create frame to gui if create button is "selected"
        if self.createPressed:
            self.createFrame.grid(row = 2, column = 0, columnspan = 4, padx = 2, pady = (2,5), sticky = 'nsew')
            self.infileLabel.configure(text = ('Create your input file in the text field below. '
                                              'Use the buttons to help populate your input file.'))
            self.fullPath.set(True)
            self.updateGui()
        else:
            self.createFrame.grid_forget()
            self.infileLabel.configure(text = 'Provide an existing input file or choose to create a new input file')

    def createInputFromDirectory(self):
        files = filedialog.askopenfilename(title = 'Select spectra file(s)', multiple = True, parent = self.root)
        for i, f in enumerate(files):
            self.createWindow.insert(tk.END, f+'\n'*(i+1 < len(files)))

    def applyType(self):
        datatype = self.dataType.get()
        if datatype == '': return
        lineCount = int(self.createWindow.index('end-1c').split('.')[0])
        for line in range(1, lineCount+1):
            curLine = self.createWindow.get('{}.0'.format(line), '{}.end'.format(line))
            if curLine == '': continue
            comma = curLine.find(',')
            if comma >= 0:
                self.createWindow.delete('{}.{}'.format(line,comma),'{}.end'.format(line))
            self.createWindow.insert('{}.end'.format(line), ', '+datatype)

    def browse(self, entry, target = 'file'):
        if target == 'file':
            if entry is self.infileEntry:
                file = filedialog.askopenfilename(title = 'Select an input file', parent = self.root)
                if file != '':
                    self.infile.set(file)
            elif entry is self.outfileEntry:
                file = filedialog.asksaveasfilename(title = 'Select or create an output file', parent = self.root)
                if file != '':
                    self.outfile.set(file)
            elif entry is self.rejectfileEntry:
                file = filedialog.asksaveasfilename(title = 'Select a reject file', parent = self.root)
                if file != '':
                    self.rejectfile.set(file)
        if target == 'directory':
            if entry is self.spectraPathEntry:
                directory = filedialog.askdirectory(title = 'Select a directory', mustexist = True, parent = self.root)
                if directory != '':
                    self.spectraPath.set(directory)

    def goToMain(self):
        """
        Accepts as options all the input parameters from the
        gui so they can be used to update the options dict.
        First a check is done to make sure the user's input
        is valid. If it is, his will then progress to calling
        the main function with the options being passed to it.
        """
        message = ''    # The output message in case errors are found

        # --- Input File ---
        if not self.createPressed:
            if self.infile.get() == '':
                message += '- A spectra list filename was not provided.\n'
            else:
                if not os.path.isfile(self.infile.get()):
                    message += '- The input file cannot be found.\n'
        else:
            if self.createWindow.get('0.0',tk.END) == '\n':
                message += '- The text field for creating an input file is empty.\n'
            # Make sure each line ends with data type
            lineCount = int(self.createWindow.index('end-1c').split('.')[0])
            for line in range(1, lineCount+1):
                curLine = self.createWindow.get('{}.0'.format(line), '{}.end'.format(line)).lower().strip()
                if curLine == '' or curLine == '\n': continue
                if not any([curLine.endswith(','+s) or curLine.endswith(' '+s) for s in ['fits', 'dr7fits', 'dr12fits', 'csv', 'txt']]):
                    message += '- Not all lines in the input file have a correctly supplied data type.'
                    break

        # --- Output File ---
        if self.outfile.get() == '':
            message += '- An output filename was not provided.\n'
        else:
            outfileExt = self.outfile.get()[-4:]
            if outfileExt[0] == '.' and outfileExt[1:] != 'csv':
                message += '- The output file must be a csv file.\n'

        # --- Reject File ---
        if self.rejectfile.get() == '':
            message += '- A reject filename was not provided.\n'
        else:
            rejectExt  = self.rejectfile.get()[-4:]
            if rejectExt[0] == '.' and rejectExt[1:] != 'csv':
                message += '- The reject file must be a csv file.\n'

        # --- Spectra Path ---
        if self.fullPath.get() == 0:
            if self.spectraPath.get() == '':
                message += '- A path for the spectra was not provided.\n'
            else:
                if not os.path.isdir(self.spectraPath.get()):
                    message += '- The spectra path is not a valid directory.\n'

        # --- Eyecheck ---
        if self.eyecheck.get() == 1 and not os.path.isfile(self.outfile.get()):
            message += '- You cannot skip to eyecheck without an existing output file.\n'
            
        # --- S/N Cut ---
        if self.eyecheck.get() == 0 and self.sncut.get() != '':
            try:
                if float(self.sncut.get()) < 0:
                    message += '- The entered S/N cut must be greater than zero.\n'
            except ValueError as e:
                message += '- The entered S/N cut is not a valid number.\n'

        # Print out the message, if there is one, and return
        if message != '':
            message = 'The following issues were found with your input.\n' \
                      'Please correct them and try again.\n\n' + message
            InfoWindow(message, parent = self.root, title = 'PyHammer Error')
            return
            
        # If we've made it to this point, the user's inputs are valid. Store them
        # in the options dict and move to the main part of the code.
        if not self.createPressed:
            self.options['infile'] = self.infile.get()
        else:
            # Create a temporary input file based on what's in the createWindow text field
            fname = 'temp_input_'+str(int(time()))+'.txt'
            with open(fname, 'w') as f:
                line = self.createWindow.get('0.0', tk.END)
                if line != '\n':
                    f.write(line)
            self.options['infile'] = fname
        self.options['outfile'] = self.outfile.get() + '.csv'*(self.outfile.get()[-4:] != '.csv')
        self.options['rejectfile'] = self.rejectfile.get() + '.csv'*(self.rejectfile.get()[-4:] != '.csv')
        self.options['fullPath'] = (self.fullPath.get() == 1)
        self.options['spectraPath'] = self.spectraPath.get() * (not self.options['fullPath'])
        # Append a slash to the end of the spectra path if there isn't one
        if (self.options['spectraPath'] != '' and self.options['spectraPath'][-1] not in ['\\', '/']):
                self.options['spectraPath'] += '/'
        self.options['eyecheck'] = (self.eyecheck.get() == 1)
        if (self.options['eyecheck'] or self.sncut.get() == ''):
            self.options['sncut'] = None
        else:
            self.options['sncut'] = float(self.sncut.get())
        
        self.root.destroy()

        main(self.options)

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
        options: A dict containing the options the
            user can specify. These may already
            have default values if they were
            provided on the command line.
    """

    ##
    # If the input options were not provided on the command line at
    # execution, we need to ask for them here.
    #

    # Get the input filename if one was not provided
    if options['infile'] is None:
        while True:
            options['infile'] = input('Please enter the filename which contains the spectra list: ')
            if options['infile'].find('.') == -1:
                print('Make sure to supply an extension for your input file.', flush = True)
                continue
            if not os.path.isfile(options['infile']):
                print('The input file cannot be found.', flush = True)
                continue
            break

    # Ask user if they want to change the results file and what to use if they do.
    if options['outfile'] == 'PyHammerResults.csv':
        ans = input('The results file is set to PyHammerResults.csv. Do you want to change it? (y/n): ')
        if ans.lower() == 'y':
            while True:
                options['outfile'] = input('Please enter the filename for the results file: ')
                outfileExt[0] = options['outfile'][-4:]
                if outfileExt[0] == '.' and outfileExt[1:] != 'csv':
                    print('The output file must be a csv file.', flush = True)
                    continue
                break
    # Append a .csv extension to the filename if none was provided
    options['outfile'] += '.csv'*(options['outfile'][-4:] != '.csv')

    # Ask user if they want to change the reject file and what to use if they do.
    if options['rejectfile'] == 'RejectSpectra.csv':
        ans = input('The reject file is set to RejectSpectra.csv. Do you want to change it? (y/n): ')
        if ans.lower() == 'y':
            while True:
                options['rejectfile'] = input('Please enter the filename for the reject file: ')
                rejectExt[0] = options['rejectfile'][-4:]
                if rejectExt[0] == '.' and rejectExt[1:] != 'csv':
                    print('The reject file must be a csv file.', flush = True)
                    continue
                break
    # Append a .csv extension to the filename if none was provided
    options['rejectfile'] += '.csv'*(options['rejectfile'][-4:] != '.csv')

    # Check whether the input file list contains the full path if
    # the user didn't already specify.
    if options['fullPath'] is None:
        ans = input('Does your input list give the full path to each spectrum? (y/n): ')
        if ans.lower() == 'y':
            options['fullPath'] = True
            options['spectraPath'] = ''
        else:
            options['fullPath'] = False
            while True:
                options['spectraPath'] = input('Enter the necessary path for each file: ')
                if not os.path.isdir(options['spectraPath']):
                    print('The path provided is not a valid directory.', flush = True)
                    continue
                break
            # Append a slash to the end of the spectra path, if there isn't one
            if options['spectraPath'][-1] not in ['\\', '/']:
                options['spectraPath'] += '\\'

    # Asks the user if they want to skip the auto-classifying and go straight
    # to checking by eye, if they have not already specified.
    if (options['eyecheck'] is None):
        ans = input('Do you want to skip straight to eye-checking? (y/n): ')
        options['eyecheck'] = (ans.lower() == 'y')

    # Asks the user if they want to apply a S/N cut when classifying the spectra.
    # This only applies if they chose not to skip the auto-classification
    if (options['eyecheck'] == False and options['sncut'] is None):
        ans = input('Do you want to supply a S/N cut when auto-classifying? (y/n): ')
        if ans.lower() == 'y':
            while True:
                ans = input('Choose a S/N cutoff (~3-5 recommended): ')
                try:
                    options['sncut'] = float(ans)
                    break
                except Error as e:
                    print(str(e), flush = True)

    # Now that all the options have been set, let's get started
    main(options)

if (__name__ == "__main__"):

    thisDir = os.path.split(__file__)[0]

    # Check if this is the first time this code has been executed by looking
    # for the runbefore file in the resources folder
    if not os.path.isfile(os.path.join(thisDir, 'resources', 'runbefore')):
        # The file doesn't exist. Let's create it and display the welcome message
        f = open(os.path.join(thisDir, 'resources', 'runbefore'), 'w')
        f.close()
        print('Welcome to PyHammer, a tool for spectral classification!\n'
              'First time users should run this program with the -h flag '
              'to learn more information.', flush = True)
    
    # Define default options
    options = {'infile': None, 'outfile': 'PyHammerResults.csv',
               'rejectfile': 'RejectSpectra.csv', 'fullPath': None,
               'spectraPath': None, 'eyecheck': None, 'sncut': None,
               'useGUI': None}
    
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

            print(('\nWelcome to the PyHammer, a tool for spectral '
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
                   '\t\t\t\t\tprovided, the default pyhammerResults.csv will be\n'
                   '\t\t\t\t\tcreated in the pyhammer folder.\n'

                   '-p, --path\t\t\t'
                   'The full path to the spectra. This is only necessary\n'
                   '\t\t\t\t\tif the input file list does not prepend the path to\n'
                   '\t\t\t\t\tthe spectra filenames.\n'
                   
                   '-r, --rejectfile\t'
                   'The full path to the file where reject spectra will\n'
                   '\t\t\t\t\tbe listed or a filename which outputs to the\n'
                   '\t\t\t\t\tpyhammer folder . If nothing is provided, the\n'
                   '\t\t\t\t\tdefault rejectSpectra.csv will be created in the\n'
                   '\t\t\t\t\tpyhammer folder.\n'

                   '-s, --sncut\t\t\t'
                   'The S/N necessary before a spectra will be classified.\n'
                   '\t\t\t\t\tA signal to noise of ~3-5 per pixel is recommended.\n'

                   '\nExample:\n'
                   'python pyhammer.py -g -f -s 3 -i C:/Path/To/File/inputFile.txt -o'
                   'C:/Path/To/File/outputFile.csv -r C:/Path/To/File/rejectFile.csv\n').expandtabs(4),
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
            options['rejectfile'] = arg

        # User indicated that the full path to the spectra is in the
        # input file list
        if (opt == '-f' or opt == '--full'):
            if (options['fullPath'] is not None):
                sys.exit('Cannot supply -f and -p at the same time. Use -h for more info.')
            else:
                options['fullPath'] = True
                options['spectraPath'] = ''

        # User provided a path to prepend to the spectra file names
        if (opt == '-p' or opt == '--path'):
            if (options['fullPath'] is not None):
                sys.exit('Cannot supply -f and -p at the same time. Use -h for more info.')
            else:
                options['fullPath'] = False
                options['spectraPath'] = arg
                # Append a slash to the end if there isn't one
                if (options['spectraPath'][-1] not in ['\\', '/']):
                    options['spectraPath'] += '\\'
            
        # User indicated they want to skip to the eyecheck
        if (opt == '-e' or opt == '--eyecheck'):
            if (options['sncut'] is not None):
                sys.exit('Flag -s is unnecessary when -e is provided. Use -h for more info.')
            else:
                options['eyecheck'] = True

        # User indicates they want a S/N cut to be applied
        if (opt == '-s' or opt == '--sncut'):
            if (options['eyecheck'] == True):
                sys.exit('Flag -s is unnecessary when -e is provided. Use -h for more info.')
            else:
                options['eyecheck'] = False
                options['sncut'] = arg

        # Command line interface is requested.
        if (opt == '-c' or opt == '--cmd'):
            if (options['useGUI'] is not None):
                sys.exit('Cannot supply -c and -g at the same time. Use -h for more info.')
            else:
                options['useGUI'] = False
        
        # GUI interface is requested.
        if (opt == '-g' or opt == '--gui'):
            if (options['useGUI'] is not None):
                sys.exit('Cannot supply -c and -g at the same time. Use -h for more info.')
            else:
                options['useGUI'] = True

    if options['useGUI'] == True:
        StartGUI(options)
    elif options['useGUI'] == False:
        startCmd(options)
    else:
        # If no interface is chosen, use the GUI by default
        options['useGUI'] = True
        StartGUI(options)

else:
    
    sys.exit("Do not import pyhammer. Run this script with the run command "
             "in the python environment, or by invoking with the python command "
             "on the command line. Use the -h flag for more information.")
