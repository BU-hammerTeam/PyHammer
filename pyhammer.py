from pyhamimports import *
from spectrum import Spectrum
from eyecheck import Eyecheck
from gui_utils import *


###
# Main Function
#

def main(options):
    """
    The main method of PyHammer which executes the overarching procedure.

    Description:
        This is the main part of the code that executes the
        actual pyhammer algorithms. This is arrived at either
        by pyhammerStartCmd or PyHammerStartGui, both of which
        get all the necessary options from the user and pass
        them to this function. The general process of this
        function should be to:
        
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
        if options['lineOutfile']: lineOutfile = open('spectralIndices.csv', 'w')
        outfile.write('#Filename,File Type,Radial Velocity (km/s),Guessed Spectral Type,Guessed [Fe/H],User Spectral Type,User [Fe/H]\n')
        rejectfile.write('#Filename,File Type,Spectra S/N\n')
        if options['lineOutfile']: lineOutfile.write('#Filename,CaK,CaK_var,Cadel,Cadel_var,CaI4217,CaI4217_var,Gband,Gband_var,Hgam,Hgam_var,FeI4383,FeI4383_var,FeI4404,FeI4404_var,Hbeta,Hbeta_var,MgI,MgI_var,NaD,NaD_var,CaI6162,CaI6162_var,Halpha,Halpha_var,CaH2,CaH2_var,CaH3,CaH3_var,TiO5,TiO5_var,VO7434,VO7434_var,VO7445,VO7445_var,VO-B,VO-B_var,VO7912,VO7912_var,Rb-B,Rb-B_var,NaI,NaI_var,TiO8,TiO8_var,TiO8440,TiO8440_var,Cs-A,Cs-A_var,CaII8498,CaII8498_var,CrH-A,CrH-A_var,CaII8662,CaII8662_var,FeI8689,FeI8689_var,FeH,FeH_var,C2-4382,C2-4382_var,C2-4737,C2-4737_var,C2-5165,C2-5165_var,C2-5636,C2-5636_var,CN-6926,CN-6926_var,CN-7872,CN-7872_var,WD-Halpha,WD-Halpha_var,WD-Hbeta,WD-Hbeta_var,WD-Hgamma,WD-Hgamma_var,\n')

        # Define the string to contain all failure messages. These will be compiled
        # and printed once at the end, if anything is put into it.
        rejectMessage = ''

        for i, line in enumerate(infile):
            # Remove extra whitespace and other unwanted characters and split
            line = line.strip()
            if ',' in line: line = line.replace(',',' ')
            if ' ' in line:
                fname, ftype = ' '.join(line.split()).rsplit(' ',1)
            else:
                fname = line
                ftype = None

            # Print statement of progress for user
            print(i+1, ') Processing ', os.path.basename(fname), sep = '')

            # Now read in the current file (this process reads in the file, converts air to 
            # vac when necessary and interpolates onto the template grid)
            message, ftype = spec.readFile(options['spectraPath']+fname, ftype)

            # If the attempt at reading the file did not succeed, then we
            # should just continue
            if message is not None:
                rejectfile.write(fname + ',' + ('N/A' if ftype is None else ftype) + ',N/A\n')
                rejectMessage += 'FILE: ' + fname + '\nREASON: ' + message.replace('\n','') + '\n\n'
                continue

            # Now that we have the necessary data in the spec object, let's
            # begin processing.

            # --- 1 ---
            # Calculate the signal to noise of the spectrum to potentially reject
            snVal = spec.calcSN()
            if options['sncut'] is not None:
                if snVal < options['sncut']:
                    rejectfile.write(fname + ',' + ftype + ',' + str(snVal) + '\n')
                    rejectMessage += 'FILE: ' + fname + '\nREASON: S/N = ' + str(snVal) + ' < ' + str(options['sncut']) + '\n\n'
                    continue
            
            # --- 2 ---
            # Normalize the input spectrum to the same place where the templates are normalized (8000A)
            try:
                spec.normalizeFlux()
            except:
                rejectfile.write(fname + ',' + ftype + ',' + str(snVal) + '\n')
                rejectMessage += 'FILE: ' + fname + '\nREASON: Could not normalize\n\n'
                continue

            # --- 3 ---
            # Call guessSpecType function for the initial guess
            # this function measures the lines then makes a guess of all parameters
            try:
                spec.guessSpecType()
            except Exception as e:
                rejectfile.write(fname + ',' + ftype + ',' + str(snVal) + '\n')
                rejectMessage += 'FILE: ' + fname + '\nREASON: Could not guess spectral type. Error Message: {}\n\n'.format(e)
                continue
            
            # If the user wants the calculated spectral indices, write them to a file
            if options['lineOutfile']:
                for key, value in spec.lines.items(): 
                    if key == 'CaK': 
                        lineOutfile.write(fname + ',' + str(value[0]) + ',' + str(value[1])+',')
                    elif key == 'WD-Hgamma':
                        lineOutfile.write(str(value[0]) + ',' + str(value[1])+'\n')
                    elif key in ['region1', 'region2', 'region3', 'region4', 'region5']:
                        continue
                    else:
                        lineOutfile.write(str(value[0]) + ',' + str(value[1])+',')
                 
            # --- 4 ---
            # Call findRadialVelocity function using the initial guess
            try:
                shift = spec.findRadialVelocity()
            except Exception as e:
                rejectfile.write(fname + ',' + ftype + ',' + str(snVal) + '\n')
                rejectMessage += 'FILE: ' + fname + '\nREASON: Could not find radial velocity. Error Message: {}\n\n'.format(e)
                continue

            # --- 5 ---
            # Call shiftToRest that shifts the spectrum to rest wavelengths,
            # then interp back onto the grid
            try:
                spec.shiftToRest(shift)
                spec.interpOntoGrid()
            except Exception as e:
                rejectfile.write(fname + ',' + ftype + ',' + str(snVal) + '\n')
                rejectMessage += 'FILE: ' + fname + '\nREASON: Could not shift to rest. Error Message: {}\n\n'.format(e)
                continue

            # --- 6 ---
            # Repeat guessSpecType function to get a better guess of the spectral 
            # type and metallicity 
            try:
                spec.guessSpecType()
            except Exception as e:
                rejectfile.write(fname + ',' + ftype + ',' + str(snVal) + '\n')
                rejectMessage += 'FILE: ' + fname + '\nREASON: Could not guess spectral type. Error Message: {}\n\n'.format(e)
                continue

            # End of the automatic guessing. We should have:
            #  1. Spectrum object with observed wavelength, flux, var,
            #  2. rest wavelength,
            #  3. spectral type (guessed),
            #  4. radial velocity and uncertainty,
            #  5. metallicity estimate,
            #  6. and line indice measurements

            # --- 7 ---
            
            # Translate the numbered spectral types into letters
            if spec._isSB2:
                # Write the file
                outfile.write(options['spectraPath']+fname + ',' +              # The spectra path and filename
                              ftype + ',' +                                     # The filetype
                              str(shift) + ',' +                                # The RV shift
                              spec._SB2_filenameList[spec.guess['specType'] - 10][:-5] + ',' +    # The auto-guessed spectral type
                              '{:+2.1f}'.format(spec.guess['metal']) +          # The auto-guessed metallicity
                              ',nan,nan\n')                                     # The to-be-determined user classifications
            else:
                letterSpt = ['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'C', 'WD'][spec.guess['specType']]
                # Write the file
                outfile.write(options['spectraPath']+fname + ',' +              # The spectra path and filename
                              ftype + ',' +                                     # The filetype
                              str(shift) + ',' +                                # The RV shift
                              letterSpt + str(spec.guess['subType']) + ',' +    # The auto-guessed spectral type
                              '{:+2.1f}'.format(spec.guess['metal']) +          # The auto-guessed metallicity
                              ',nan,nan\n')                                     # The to-be-determined user classifications
        
        # We're done so let's close all the files
        infile.close()
        outfile.close()
        rejectfile.close()
        # Only close lineOutfile if it was created
        if options['lineOutfile']:
            lineOutfile.close()

        # Check that we processed every spectrum in the infile. If not, print out
        # the reject method.
        if rejectMessage != '':
            # Prepend to the reject message
            message = 'At least one spectra was rejected. See the details for more information.'
            notifyUser(options['useGUI'], message, details = rejectMessage)
            # Check if all spectra were skipped by seeing if the number of
            # lines in the reject message is equal to the number of processed
            # times 3 (since each reject message has three newlines). If they
            # were all skipped, theres nothing to eyecheck so return.
            if rejectMessage.count('\n') == 3*(i+1):
                notifyUser(options['useGUI'], 'All spectra were bad. Exiting PyHammer.')
                # Clean up any temporary input files created
                if os.path.basename(options['infile'])[:11] == 'temp_input_':
                    os.remove(options['infile'])
                return
    
    # At this point, we should call up the GUI to do the eyechecking.
    Eyecheck(spec, options)

    # Finally, clean up any temporary input files created
    if os.path.basename(options['infile'])[:11] == 'temp_input_':
        os.remove(options['infile'])

def notifyUser(useGUI, message, details = None):
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
        print(details, flush = True)
    else:
        # More involved case, create a base pyqt window
        # derive a message box from it to display the
        # message, then close the base window and move on.
        win = QMainWindow()
        win.setWindowIcon(QIcon(os.path.join(os.path.split(__file__)[0],'resources','sun.ico')))
        MessageBox(win, message, 'PyHammer Notification', details = details)
        win.close()

###
# Get PyHammer settings through GUI
#

class PyHammerSettingsGui(QMainWindow):
    """
    Description:
        This class provies the user with a GUI for providing
        settings. These settings will define everything the
        rest of the PyHammer program needs to run including
        the input files, output files, and settings to use
        when running the auto-classify process. When the user
        is ready, they can hit the "Start PyHammer" button.
        A check will be performed to make sure the settings
        are good and if so, this window will close itself
        and call the main method in this file, passing along
        the settings that it pulls from the GUI.

    Inputs:
        options: A dict containing the options the
            user can specify. These may already
            have default values if they were
            provided when the program was launched.

    Example:
        This class inherits from the PyQt QMainWindow class.
        As such, it needs to be run with the following commands

        app = QApplication([])
        PyHammerSettingsGui(options) # Pass in options dict
        app.exec_()
    """

    def __init__(self, options):

        super().__init__()      # Call the parent class init method

        self.options = options  # Store the options

        # Create and show the GUI

        self.defineHelpText()   # Define text to be display when user hits help buttons
        self.createGui()        # Define all the variables used to create the GUI
        self.layoutGui()        # Set the layout of the GUI components in the window
        self.configureGui()     # Configure the GUI component settings
        self.updateGui()        # Perform some updates to the display of the GUI

        self.show()             # Finally, show the GUI to the user

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

        self.lineHelpText = (
            'If you would like the spectral lines used in classifying '
            'the spectra to be printed out to a .CSV file, select yes '
            'for this option. Otherwise select no. Note that this file '
            'is only output if the classification algorithm is run and '
            'you choose to NOT skip directly to the eye check.')

    def createGui(self):

        # Define the basic, top-level GUI components
        self.widget = QWidget()       # The central widget in the main window
        self.grid = QVBoxLayout()     # The layout manager of the central widget
        self.icon = QIcon(os.path.join(os.path.split(__file__)[0],'resources','sun.ico')) # The window icon

        # Input Field

        # Define Input Widgets
        self.infileFrame = QFrame()
        self.infileLabel = QLabel('Provide an existing input file or create a new input file', alignment = Qt.AlignCenter)
        self.infileEntry = QLineEdit(placeholderText = 'Input File...')
        self.infileBrowseButton = QPushButton('Browse')
        self.infileCreateButton = QPushButton('Create')
        self.createPressed = False
        self.infileHelpButton = QPushButton('?')

        # Define Create Widgets
        self.createFrame = QFrame()
        self.textArea = QTextEdit()
        self.selectSpectraButton = QPushButton('Select Spectra')
        self.dataTypeList = QComboBox()
        self.applyType = QPushButton('Apply Data Type')

        # Output Field
        self.outfileFrame = QFrame()
        self.outfileLabel = QLabel('Provide an output file', alignment = Qt.AlignCenter)
        self.outfileEntry = QLineEdit(placeholderText = 'Output File...')
        self.outfileBrowseButton = QPushButton('Browse')
        self.outfileHelpButton = QPushButton('?')

        # Reject Field
        self.rejectFrame = QFrame()
        self.rejectLabel = QLabel('Provide a reject file', alignment = Qt.AlignCenter)
        self.rejectEntry = QLineEdit(placeholderText = 'Reject File...')
        self.rejectBrowseButton = QPushButton('Browse')
        self.rejectHelpButton = QPushButton('?')

        # Full Path Field
        self.fullPathFrame = QFrame()
        self.fullPathLabel = QLabel('Do the spectra in the input file contain full paths?', alignment = Qt.AlignCenter)
        self.fullPathChoice = QButtonGroup()
        self.fullPathYes = QRadioButton('Yes', checked = True)
        self.fullPathNo = QRadioButton('No', checked = False)
        self.fullPathChoice.addButton(self.fullPathYes, 0)
        self.fullPathChoice.addButton(self.fullPathNo, 1)
        self.fullPathHelpButton = QPushButton('?')
      
        # Spectra Path Field
        self.spectraPathFrame = QFrame()
        self.spectraPathLabel = QLabel('Provide a path to the spectra files', alignment = Qt.AlignCenter)
        self.spectraPathEntry = QLineEdit(placeholderText = 'Path to spectra files...')
        self.spectraPathBrowseButton = QPushButton('Browse')
        self.spectraPathHelpButton = QPushButton('?')

        # Eyecheck Field
        self.eyecheckFrame = QFrame()
        self.eyecheckLabel = QLabel('Do you want to skip to classifying by eye?', alignment = Qt.AlignCenter)
        self.eyecheckChoice = QButtonGroup()
        self.eyecheckYes = QRadioButton('Yes', checked = True)
        self.eyecheckNo = QRadioButton('No', checked = False)
        self.eyecheckChoice.addButton(self.fullPathYes, 0)
        self.eyecheckChoice.addButton(self.fullPathNo, 1)
        self.eyecheckHelpButton = QPushButton('?')

        # S/N Cut Field
        self.sncutFrame = QFrame()
        self.sncutLabel = QLabel('Enter a signal to noise cutoff', alignment = Qt.AlignCenter)
        self.sncutEntry = QLineEdit(placeholderText = 'S/N cutoff...')
        self.sncutHelpButton = QPushButton('?')

        # Spectral Line Output File Field
        self.lineFrame = QFrame()
        self.lineLabel = QLabel('Do you print the spectral classification lines to a file?', alignment = Qt.AlignCenter)
        self.lineChoice = QButtonGroup()
        self.lineYes = QRadioButton('Yes', checked = True)
        self.lineNo = QRadioButton('No', checked = False)
        self.lineChoice.addButton(self.fullPathYes, 0)
        self.lineChoice.addButton(self.fullPathNo, 1)
        self.lineHelpButton = QPushButton('?')

        # Start Button
        self.startButton = QPushButton('Start PyHammer')

        # Separators
        self.sep = []
        for i in range(8):
            line = QFrame(frameShape = QFrame.HLine, frameShadow = QFrame.Sunken, lineWidth = 1)
            line.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            self.sep.append(line)

    def layoutGui(self):       

        # Input Field

        # Setup Input Widgets
        frameGrid = QGridLayout(spacing = 2, margin = 0)
        frameGrid.addWidget(self.infileLabel, 0, 0, 1, 4)
        frameGrid.addWidget(self.infileEntry, 1, 0)
        frameGrid.addWidget(self.infileBrowseButton, 1, 1)
        frameGrid.addWidget(self.infileCreateButton, 1, 2)
        frameGrid.addWidget(self.infileHelpButton, 1, 3)
        self.infileFrame.setLayout(frameGrid)
        self.grid.addWidget(self.infileFrame)

        # Setup Create Widgets
        frameGrid = QGridLayout(spacing = 2, margin = 0)
        frameGrid.addWidget(self.textArea, 0, 0, 1, 5)
        frameGrid.addWidget(self.selectSpectraButton, 1, 0)
        frameGrid.addWidget(QFrame(frameShape = QFrame.VLine, frameShadow = QFrame.Sunken, lineWidth = 1), 1, 1)
        frameGrid.addWidget(self.dataTypeList, 1, 2)
        frameGrid.addWidget(self.applyType, 1, 3)
        frameGrid.setColumnStretch(4, 1)
        self.createFrame.setLayout(frameGrid)
        self.grid.addWidget(self.createFrame)

        self.grid.addWidget(self.sep[0])

        # Output Field
        frameGrid = QGridLayout(spacing = 2, margin = 0)
        frameGrid.addWidget(self.outfileLabel, 0, 0, 1, 3)
        frameGrid.addWidget(self.outfileEntry, 1, 0)
        frameGrid.addWidget(self.outfileBrowseButton, 1, 1)
        frameGrid.addWidget(self.outfileHelpButton, 1, 2)
        self.outfileFrame.setLayout(frameGrid)
        self.grid.addWidget(self.outfileFrame)

        self.grid.addWidget(self.sep[1])

        # Reject Field
        frameGrid = QGridLayout(spacing = 2, margin = 0)
        frameGrid.addWidget(self.rejectLabel, 0, 0, 1, 3)
        frameGrid.addWidget(self.rejectEntry, 1, 0)
        frameGrid.addWidget(self.rejectBrowseButton, 1, 1)
        frameGrid.addWidget(self.rejectHelpButton, 1, 2)
        self.rejectFrame.setLayout(frameGrid)
        self.grid.addWidget(self.rejectFrame)

        self.grid.addWidget(self.sep[2])

        # Full Path Field
        frameGrid = QGridLayout(spacing = 2, margin = 0)
        frameGrid.addWidget(self.fullPathLabel, 0, 0, 1, 3)
        frameGrid.addWidget(self.fullPathYes, 1, 0, alignment = Qt.AlignRight)
        frameGrid.addWidget(self.fullPathNo, 1, 1)
        frameGrid.addWidget(self.fullPathHelpButton, 1, 2)
        self.fullPathFrame.setLayout(frameGrid)
        self.grid.addWidget(self.fullPathFrame)

        self.grid.addWidget(self.sep[3])

        # Spectra Path Field
        frameGrid = QGridLayout(spacing = 2, margin = 0)
        frameGrid.addWidget(self.spectraPathLabel, 0, 0, 1, 2)
        frameGrid.addWidget(self.spectraPathEntry, 1, 0)
        frameGrid.addWidget(self.spectraPathBrowseButton, 1, 1)
        frameGrid.addWidget(self.spectraPathHelpButton, 1, 2)
        self.spectraPathFrame.setLayout(frameGrid)
        self.grid.addWidget(self.spectraPathFrame)

        self.grid.addWidget(self.sep[4])

        # Eyecheck Field
        frameGrid = QGridLayout(spacing = 2, margin = 0)
        frameGrid.addWidget(self.eyecheckLabel, 0, 0, 1, 3)
        frameGrid.addWidget(self.eyecheckYes, 1, 0, alignment = Qt.AlignRight)
        frameGrid.addWidget(self.eyecheckNo, 1, 1)
        frameGrid.addWidget(self.eyecheckHelpButton, 1, 2)
        self.eyecheckFrame.setLayout(frameGrid)
        self.grid.addWidget(self.eyecheckFrame)

        self.grid.addWidget(self.sep[5])

        # S/N Cut Field
        frameGrid = QGridLayout(spacing = 2, margin = 0)
        frameGrid.addWidget(self.sncutLabel, 0, 0, 1, 2)
        frameGrid.addWidget(self.sncutEntry, 1, 0)
        frameGrid.addWidget(self.sncutHelpButton, 1, 2)
        self.sncutFrame.setLayout(frameGrid)
        self.grid.addWidget(self.sncutFrame)

        self.grid.addWidget(self.sep[6])

        # Spectral Line Output File Field
        frameGrid = QGridLayout(spacing = 2, margin = 0)
        frameGrid.addWidget(self.lineLabel, 0, 0, 1, 3)
        frameGrid.addWidget(self.lineYes, 1, 0, alignment = Qt.AlignRight)
        frameGrid.addWidget(self.lineNo, 1, 1)
        frameGrid.addWidget(self.lineHelpButton, 1, 2)
        self.lineFrame.setLayout(frameGrid)
        self.grid.addWidget(self.lineFrame)

        self.grid.addWidget(self.sep[7])

        # Start Button
        self.grid.addWidget(self.startButton)

    def configureGui(self):

        # Input Field

        # Configure Input Widgets
        self.infileEntry.setText(self.options['infile'])
        self.infileEntry.setMinimumWidth(300)
        self.infileBrowseButton.clicked.connect(lambda: self.browse(self.infileEntry))
        self.infileBrowseButton.setToolTip('Browse for an existing input file')
        self.infileCreateButton.clicked.connect(self.createButtonClicked)
        self.infileCreateButton.setToolTip('Create a new input file')
        self.infileHelpButton.setMaximumWidth(25)
        self.infileHelpButton.clicked.connect(lambda: MessageBox(self, self.infileHelpText, 'PyHammer Help'))
        self.infileHelpButton.setToolTip('Help')

        # Configure Create Widgets
        self.textArea.setMinimumSize(600,300)
        self.textArea.setLineWrapMode(QTextEdit.NoWrap)
        font = self.textArea.currentFont()
        font.setPointSize(10)
        font.setFamily('courier')
        self.textArea.setFont(font)
        self.selectSpectraButton.clicked.connect(self.selectSpectraButtonClicked)
        self.selectSpectraButton.setToolTip('Select a set of spectrum files\nto add to the input file')
        self.dataTypeList.addItems(['SDSSdr12', 'SDSSdr7', 'fits', 'txt', 'csv','tempfits'])
        self.applyType.clicked.connect(self.applyTypeClicked)
        self.applyType.setToolTip('<b>Optional:</b> Append the selected data\ntype to every file in the list to give a\nhint to PyHammer about the file type')
        self.createFrame.hide()

        # Output Field
        self.outfileEntry.setText(self.options['outfile'])
        self.outfileBrowseButton.clicked.connect(lambda: self.browse(self.outfileEntry))
        self.outfileBrowseButton.setToolTip('Browse for an existing output file or define a new one')
        self.outfileHelpButton.setMaximumWidth(25)
        self.outfileHelpButton.clicked.connect(lambda: MessageBox(self, self.outfileHelpText, 'PyHammer Help'))
        self.outfileHelpButton.setToolTip('Help')

        # Reject Field
        self.rejectEntry.setText(self.options['rejectfile'])
        self.rejectBrowseButton.clicked.connect(lambda: self.browse(self.rejectEntry))
        self.rejectBrowseButton.setToolTip('Browse for an existing reject file or define a new one')
        self.rejectHelpButton.setMaximumWidth(25)
        self.rejectHelpButton.clicked.connect(lambda: MessageBox(self, self.rejectfileHelpText, 'PyHammer Help'))
        self.rejectHelpButton.setToolTip('Help')

        # Full Path Field
        if self.options['fullPath'] is None or not self.options['fullPath']:
            self.fullPathNo.setChecked(True)
        else:
            self.fullPathYes.setChecked(True)
        self.fullPathYes.clicked.connect(self.updateGui)
        self.fullPathNo.clicked.connect(self.updateGui)
        self.fullPathHelpButton.setMaximumWidth(25)
        self.fullPathHelpButton.clicked.connect(lambda: MessageBox(self, self.fullPathHelpText, 'PyHammer Help'))
        self.fullPathHelpButton.setToolTip('Help')

        # Spectra Path Field
        self.spectraPathEntry.setText(self.options['spectraPath'])
        self.spectraPathBrowseButton.clicked.connect(lambda: self.browse(self.spectraPathEntry, 'directory'))
        self.spectraPathBrowseButton.setToolTip('Browse for the directory containing the spectra files')
        self.spectraPathHelpButton.setMaximumWidth(25)
        self.spectraPathHelpButton.clicked.connect(lambda: MessageBox(self, self.spectraPathHelpText, 'PyHammer Help'))
        self.spectraPathHelpButton.setToolTip('Help')

        # Eyecheck Field
        if self.options['eyecheck'] is None or not self.options['eyecheck']:
            self.eyecheckNo.setChecked(True)
        else:
            self.eyecheckYes.setChecked(True)
        self.eyecheckYes.clicked.connect(self.updateGui)
        self.eyecheckNo.clicked.connect(self.updateGui)
        self.eyecheckHelpButton.setMaximumWidth(25)
        self.eyecheckHelpButton.clicked.connect(lambda: MessageBox(self, self.eyecheckHelpText, 'PyHammer Help'))
        self.eyecheckHelpButton.setToolTip('Help')

        # S/N Cut Field
        self.sncutEntry.setText(self.options['sncut'])
        self.sncutHelpButton.setMaximumWidth(25)
        self.sncutHelpButton.clicked.connect(lambda: MessageBox(self, self.sncutHelpText, 'PyHammer Help'))
        self.sncutHelpButton.setToolTip('Help')

        # Spectral Line Output File Field
        if self.options['lineOutfile'] is None or not self.options['lineOutfile']:
            self.lineNo.setChecked(True)
        else:
            self.lineYes.setChecked(True)
        self.lineHelpButton.setMaximumWidth(25)
        self.lineHelpButton.clicked.connect(lambda: MessageBox(self, self.lineHelpText, 'PyHammer Help'))
        self.lineHelpButton.setToolTip('Help')

        # Start Button
        self.startButton.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.startButton.clicked.connect(self.goToMain)

        # Top Level Grid
        self.grid.setSpacing(4)
        self.grid.setContentsMargins(2,2,2,2)

        # Set the main window properties
        self.widget.setLayout(self.grid)
        self.setCentralWidget(self.widget)
        self.setWindowTitle('PyHammer Settings')
        self.setWindowIcon(self.icon)

    def updateGui(self):

        if self.fullPathYes.isChecked():
            self.spectraPathFrame.hide()
            self.sep[4].hide()
        elif self.fullPathNo.isChecked():
            self.spectraPathFrame.show()
            self.sep[4].show()

        if self.eyecheckYes.isChecked():
            self.sncutFrame.hide()
            self.sep[6].hide()
        elif self.eyecheckNo.isChecked():
            self.sncutFrame.show()
            self.sep[6].show()
           
        self.setFixedSize(self.grid.minimumSize())

    def browse(self, entry, target = 'file'):
        if target == 'file':
            if entry is self.infileEntry:
                dlg = QFileDialog(directory = __file__, windowTitle = 'Select an input file')
                dlg.setFileMode(QFileDialog.ExistingFile)
                if dlg.exec_():
                    entry.setText(dlg.selectedFiles()[0])
            elif entry is self.outfileEntry:
                dlg = QFileDialog(directory = __file__, windowTitle = 'Select or create an output file')
                dlg.setFileMode(QFileDialog.AnyFile)
                if dlg.exec_():
                    entry.setText(dlg.selectedFiles()[0])
            elif entry is self.rejectEntry:
                dlg = QFileDialog(directory = __file__, windowTitle = 'Select or create a reject file')
                dlg.setFileMode(QFileDialog.AnyFile)
                if dlg.exec_():
                    entry.setText(dlg.selectedFiles()[0])
        if target == 'directory':
            if entry is self.spectraPathEntry:
                dlg = QFileDialog(directory = __file__, windowTitle = 'Select a directory')
                dlg.setFileMode(QFileDialog.Directory)
                dlg.setOption(QFileDialog.ShowDirsOnly, True)
                if dlg.exec_():
                    entry.setText(dlg.selectedFiles()[0])

    def createButtonClicked(self):
        self.createPressed = not self.createPressed # Invert boolean

        self.infileEntry.setEnabled(not self.createPressed)
        self.infileBrowseButton.setEnabled(not self.createPressed)

        if self.createPressed:
            self.createFrame.show()
            self.infileLabel.setText('Create your input file in the text field below. '
                                     'Use the buttons to help populate your input file.')
            self.fullPathYes.setChecked(True)
            self.updateGui()
        else:
            self.createFrame.hide()
            self.infileLabel.setText('Provide an existing input file or choose to create a new input file')
            self.updateGui()

    def selectSpectraButtonClicked(self):
        dlg = QFileDialog(directory = __file__, windowTitle = 'Select your spectra files')
        dlg.setFileMode(QFileDialog.ExistingFiles)
        if dlg.exec_():
            [self.textArea.append(file) for file in dlg.selectedFiles()]

    def applyTypeClicked(self):
        # Pull out currently selected data type to apply and current
        # text in text area
        dataType = self.dataTypeList.currentText()
        originalText = self.textArea.toPlainText()

        # Go through the text line by line, remove any current types
        # that already exist, and apply the new type.
        newText = []
        for line in originalText.split('\n'):
            if line == '': continue
            comma = line.find(',')
            if comma >= 0: line = line[:comma]
            newText.append(line + ', ' + dataType)

        # Put the new text into the text area
        self.textArea.setPlainText('\n'.join(newText))

    def goToMain(self):
        """
        This will go through all the inputs of the GUI and
        first perform a check to make sure the user's input
        is valid. If it all inputs are valid, this will then
        progress to calling the main function with the options
        from the GUI being passed to it. If any of the input
        is invalid, a message will be displayed indicating
        the problems that need fixing.
        """
        message = ''    # The output message in case errors are found

        # Check each input field for errors

        # Input File
        if not self.createPressed:
            if self.infileEntry.text() == '':
                message += '- A spectra list filename was not provided.\n'
            else:
                if not os.path.isfile(self.infileEntry.text()):
                    message += '- The input file cannot be found.\n'
        else:
            if self.textArea.toPlainText() == '':
                message += '- The text field for creating an input file is empty.\n'

        # Output File
        if self.outfileEntry.text() == '':
            message += '- An output filename was not provided.\n'
        else:
            outfileExt = self.outfileEntry.text()[-4:]
            if outfileExt[0] == '.' and outfileExt[1:] != 'csv':
                message += '- The output file must be a csv file.\n'

        # Reject File
        if self.rejectEntry.text() == '':
            message += '- A reject filename was not provided.\n'
        else:
            rejectExt  = self.rejectEntry.text()[-4:]
            if rejectExt[0] == '.' and rejectExt[1:] != 'csv':
                message += '- The reject file must be a csv file.\n'

        # Spectra Path
        if self.fullPathNo.isChecked():
            if self.spectraPathEntry.text() == '':
                message += '- A path for the spectra was not provided.\n'
            else:
                if not os.path.isdir(self.spectraPathEntry.text()):
                    message += '- The spectra path is not a valid directory.\n'

        # Eyecheck
        if self.eyecheckYes.isChecked() and not os.path.isfile(self.outfileEntry.text()):
            message += '- You cannot skip to eyecheck without an existing output file.\n'
           
        # S/N Cut
        if self.eyecheckNo.isChecked() and self.sncutEntry.text() != '':
            try:
                if float(self.sncutEntry.text()) < 0:
                    message += '- The entered S/N cut must be positive.\n'
            except ValueError as e:
                message += '- The entered S/N cut is not a valid number.\n'

        # If a message was formed to notify the user, print that message and return
        if message != '':
            message = 'The following issues were found with your input.\n' \
                      'Please correct them and try again.\n\n' + message
            MessageBox(self, message, title = 'PyHammer Settings Error')
            return
           
        # If we've made it to this point, the user's inputs are valid. Store them
        # in the options dict and move to the main part of the code.
        if not self.createPressed:
            self.options['infile'] = self.infileEntry.text()
        else:
            # Create a temporary input file based on what's in the create
            # input file text field
            fname = 'temp_input_'+str(int(time()))+'.txt'
            with open(fname, 'w') as f:
                line = self.textArea.toPlainText()
                if line != '\n':
                    f.write(line)
            self.options['infile'] = fname
        self.options['outfile'] = self.outfileEntry.text() + '.csv'*(self.outfileEntry.text()[-4:] != '.csv')
        self.options['rejectfile'] = self.rejectEntry.text() + '.csv'*(self.rejectEntry.text()[-4:] != '.csv')
        self.options['fullPath'] = self.fullPathYes.isChecked()
        self.options['spectraPath'] = self.spectraPathEntry.text() * (not self.options['fullPath'])
        self.options['lineOutfile'] = self.lineYes.isChecked()
        # Append a slash to the end of the spectra path if there isn't one
        if (self.options['spectraPath'] != '' and self.options['spectraPath'][-1] not in ['\\', '/']):
                self.options['spectraPath'] += '/'
        self.options['eyecheck'] = self.eyecheckYes.isChecked()
        if (self.options['eyecheck'] or self.sncutEntry.text() == ''):
            self.options['sncut'] = None
        else:
            self.options['sncut'] = float(self.sncutEntry.text())
       
        self.close()
        
        main(self.options)

###
# Get PyHammer settings through command line
#

def pyhammerSettingsCmd(options):
    """
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
            provided when the program was launched.
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

    # Asks the user if they want to have the spectral lines written to a file.
    if (options['lineOutfile'] is None):
        ans = input('Do you want to have the spectral lines used for classification written to a file? (y/n): ')
        options['lineOutfile'] = (ans.lower() == 'y')

    # Now that all the options have been set, let's get started
    main(options)

###
# PyHammer Entry Point
#

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
               'useGUI': None, 'lineOutfile': None}
    
    # *** Check input conditions ***

    opts, args = getopt.getopt(sys.argv[1:], 'hi:o:r:fp:es:cgl',
                               ['help', 'infile=', 'outfile=', 'rejectfile=',
                                'full', 'path=', 'eyecheck', 'sncut',
                                'cmd', 'gui', 'lineFile'])

    # Loop through the flags and options the
    # user passed in when calling PyHammer
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

                   '-l, --lineFile\t\t'
                   'Flag indicating if the spectral line output file\n'
                   '\t\t\t\t\tshould be produced. Can only be produced if the user\n'
                   '\t\t\t\t\tdoes NOT skip to the eyecheck.\n'

                   '\nExample:\n'
                   'python pyhammer.py -g -l -f -s 3 -i C:/Path/To/File/inputFile.txt -o '
                   'C:/Path/To/File/outputFile.csv -r C:/Path/To/File/rejectFile.csv\n').expandtabs(4),
                  flush = True)
            
            # Quit out without doing anything more
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

        if (opt == '-l' or opt == '--lineFile'):
            options['lineOutfile'] = True

    # If no interface is chose, use the GUI by default
    if options['useGUI'] is None: options['useGUI'] = True

    if options['useGUI'] == True:
        app = QApplication([])
        PyHammerSettingsGui(options)
        app.exec_()
    elif options['useGUI'] == False:
        pyhammerSettingsCmd(options)

else:
    
    sys.exit("Do not import pyhammer. Run this script with the run command "
             "in the python environment, or by invoking with the python command "
             "on the command line. Use the -h flag for more information.")

