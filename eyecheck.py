from pyhamimports import *
from gui_utils import *
from spectrum import *

class Eyecheck(QMainWindow):

    def __init__(self, specObj, options):

        super().__init__()

        # Store Input Variables
        self.specObj = specObj      # The Spectrum object created in the pyhammer script
        self.options = options      # The list of options input by the user in the pyhammer script

        # Create and show the GUI
        self.defineUsefulVars()     # Setup some basic variables to be used later
        self.readOutfile()          # Read the output file created
        self.createGui()            # Define and layout the GUI elements
        self.selectInitialSpectrum()# Determine which spectrum to display first
        if self.specIndex == -1:    # If no initial spectrum is chosen
            qApp.quit()             # Quit the QApplication
            return                  # Return back to the main pyhammer routine
        self.loadUserSpectrum()     # Otherwise, oad the appropriate spectrum to be displayed
        self.updatePlot()           # Update the plot showing the template and spectrum

        self.show()                 # Show the final GUI window to the user

    ###
    # Initialization Methods
    #

    def defineUsefulVars(self):
        """
        Description:
            This method simply defines some useful variables as part of the
            class that can be used in various places.
        """

        # Define some basic spectra related information
        self.specType  = ['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'C', 'WD']
        self.subType   = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.metalType = ['-2.0', '-1.5', '-1.0', '-0.5', '+0.0', '+0.5', '+1.0']
        self.templateDir = os.path.join(os.path.split(__file__)[0], 'resources', 'templates')

        # Define an index to point to the current spectra in the list
        # of spectra in the output file. We will start by assuming we're
        # looking at the first spectra in the list. The selectInitialSpectrum
        # method will update this as necessary.
        self.specIndex = 0

        # Define plot related variables
        plt.style.use('ggplot')
        self.full_xlim = None           # +--
        self.full_ylim = None           # | Store these to keep track
        self.zoomed_xlim = None         # | of zoom states on the plot
        self.zoomed_ylim = None         # |
        self.zoomed = False             # +--

        # Define the help strings to display when the user chooses a help
        # option from the menu bar
        self.helpStr = (
            'Welcome to the main GUI for spectral typing your spectra.\n\n'
            'Each spectra in your spectra list file will be loaded in '
            'sequence and shown on top of the template it was matched '
            'to. From here, fine tune the spectral type by comparing '
            'your spectrum to the templates and choose "Next" when '
            "you've landed on the correct choice. Continue through each "
            'spectrum until finished.')
        
        self.buttonStr = (
            'Upon opening the Eyecheck program, the first spectrum in your '
            'list will be loaded and displayed on top of the template determined '
            'by the auto-classification algorithm.\n\n'
            'Use the "Earlier" and "Later" buttons to change the spectrum '
            'templates. Note that not all templates exist for all spectral '
            'types. This program specifically disallows choosing K8 and K9 '
            'spectral types as well.\n\n'
            'The "Higher" and "Lower" buttons change the metallicity. Again, '
            'not all metallicities exist as templates.\n\n'
            'The "Odd" button allows you to mark a spectrum as something other '
            'than a standard classification, such as a white dwarf or galaxy.\n\n'
            'The "Bad" button simply marks the spectrum as BAD in the output '
            'file, indicating it is not able to be classified.\n\n'
            'You can cycle between your spectra using the "Back" and "Next" buttons. '
            'Note that hitting "Next" will save the currently selected state as '
            'the classification for that spectra.')

        self.keyStr = (
            'The following keys are mapped to specific actions.\n\n'
            '<Left>\t\tEarlier spectral type button\n'
            '<Right>\tLater spectral type button\n'
            '<Up>\t\tHigher metallicity button\n'
            '<Down>\tLower metallicity button\n'
            '<Enter>\tAccept spectral classification\n'
            '<Ctrl-K>\tMove to previous spectrum\n'
            '<Ctrl-O>\tClassify spectrum as odd\n'
            '<Ctrl-B>\tClassify spectrum as bad\n'
            '<Ctrl-E>\tToggle the template error\n'
            '<Ctrl-S>\tSmooth/Unsmooth the spectrum\n'
            '<Ctrl-L>\tLock the smooth state between spectra\n'
            '<Ctrl-R>\tToggle removing the stiching spike in SDSS spectra\n'
            '<Ctrl-Q>\tQuit PyHammer\n'
            '<Ctrl-P>')

        self.tipStr = (
            'The following are a set of tips for useful features of the '
            'program.\n\n'
            'The drop down list in the upper left of the Eyecheck window '
            'displays all the spectra in your list. Select a different spectra '
            'from this drop down to automatically jump to a different spectra. '
            'This will save the choice for the current spectrum.\n\n'
            'Any zoom applied to the plot is held constant between switching '
            'templates. This makes it easy to compare templates around specific '
            'features or spectral lines. Hit the home button on the plot '
            'to return to the original zoom level.\n\n'
            'The smooth menu option will allow you to smooth or unsmooth '
            'your spectra in the event that it is noisy. This simply applies '
            'a boxcar convolution across your spectrum, leaving the edges unsmoothed.\n\n'
            'By default, every new, loaded spectrum will be unsmoothed and '
            'the smooth button state reset. You can choose to keep the smooth '
            'button state between loading spectrum by selecting the menu option '
            '"Lock Smooth State".\n\n'
            'In SDSS spectra, there is a spike that occurs between 5569 and 5588 '
            'Angstroms caused by stitching together the results from both detectors.'
            'You can choose to artificially remove this spike for easier viewing by'
            'selecting the "Remove SDSS Stitch Spike" from the Options menu.\n\n'
            'At the bottom of the sidebar next to the figure is the template match '
            'metric. This is a measure of how close a match the current template is '
            'to the spectrum. A lower value indicates a closer match. Conceptually, '
            'this is simply the Euclidean distance between the template and the spectrum '
            "Use this to help classify, but don't trust it to be foolproof.\n\n"
            'Some keys may need to be hit rapidly.')

        self.aboutStr = (
            'This project was developed by a select group of graduate students '
            'at the Department of Astronomy at Boston University. The project '
            'was lead by Aurora Kesseli with development help and advice provided '
            'by Andrew West, Mark Veyette, Brandon Harrison, and Dan Feldman. '
            'Contributions were further provided by Dylan Morgan and Chris Theissan.\n\n'
            'See the accompanying paper Kesseli et al. (2017) or the PyHammer github\n'
            'site for further details.')

        # Other variables
        self.pPressNum = 0
        self.pPressTime = 0

    def readOutfile(self):
        """
        Description:
            Opens up the output file contained in the passed in options
            dict, reads it, and stores the data in a variable for later
            use. This stored output data will be updated as the user
            interacts with the program and written to the output file
            when they close the program.
        """
        with open(self.options['outfile'], 'r') as file:
            reader = csv.reader(file)
            self.outData = np.asarray(list(reader)[1:]) # Ignore the header line

    def selectInitialSpectrum(self):
        """
        Description:
            Before displaying the main GUI, this method will go through
            the outfile data and figure out which spectrum from the list
            to display first. If the user has never classified any data
            before for this particular file, it will just display the first
            file in the list. If they've already got results, it will choose
            the first spectra without results and ask the user if they
            want to start where they left off. If all the spectra already
            have user classification results, it will ask if they want to
            start over.
        """
        
        # Loop through the outData and see if some classification has occured already
        for data in self.outData:
            # If classification by the user has already occured for the
            # current spectrum, then move our index to the next one.
            if data[5] != 'nan' or data[6] != 'nan':
                self.specIndex += 1
            else:
                # Break out if we can get to a spectrum that hasn't been
                # classified by the user yet
                break
        
        # If the outfile already has eyecheck results, indicated by the fact
        # that the specIndex isn't pointing to the first spectrum in the list,
        # ask if they want to start where they left off.
        if self.specIndex != 0:
            # If every outfile spectra already has an eyecheck result
            # they've classified everything and ask them if they want
            # to start over instead.
            if self.specIndex == len(self.outData):
                msg = MessageBox(self, ('Every spectrum in the output file already has\n'
                                        'an eyecheck result. Do you want to start over?'),
                                 buttons = QMessageBox.Yes|QMessageBox.No)
                if msg.reply == QMessageBox.Yes:
                    self.specIndex = 0
                else:
                    self.specIndex = -1 # Indicates we don't want to classify anything
                    return
            else:
                msg = MessageBox(self, ('The output file already has eyecheck results. The\n'
                                        'eyecheck will start with the next unclassified\n'
                                        'spectrum. Do you want to start over instead?'),
                                 buttons = QMessageBox.Yes|QMessageBox.No)
                if msg.reply == QMessageBox.Yes:
                    self.specIndex = 0

    def createGui(self):
        """
        Description:
            Method to create all the GUI components. This method uses a few
            helper methods, partiularly for creating the slider sections and
            button sections.
        """

        # Define the basic, top-level GUI components
        self.widget = QWidget()       # The central widget in the main window
        self.grid = QGridLayout()     # The layout manager of the central widget
        self.icon = QIcon(os.path.join(os.path.split(__file__)[0],'resources','sun.ico'))

        # The menu bar
        self.createMenuBar()
            
        # *** Setup the main GUI components ***

        # The spectrum choosing components
        label = QLabel('Spectrum', alignment = Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.grid.addWidget(label, 0, 0, 1, 3)

        self.spectrumList = QComboBox(self.widget)
        self.spectrumList.addItems([os.path.split(d[0])[-1] for d in self.outData])
        self.spectrumList.currentIndexChanged.connect(self.spectrumChosen)
        self.grid.addWidget(self.spectrumList, 1, 0, 1, 3)

        # The collection of sliders and their accompanying labels
        self.specTypeLabel, self.specTypeSlider = self.createSlider('Stellar\nType', self.specType, self.specTypeChanged)
        self.subTypeLabel, self.subTypeSlider = self.createSlider('Stellar\nSubtype', self.subType, self.specSubtypeChanged)
        self.metalLabel, self.metalSlider = self.createSlider('Metallicity\n[Fe/H]', self.metalType, self.metallicityChanged)

        # The collection of buttons
        self.createButtons('Change Spectral Type', ['Earlier', 'Later'],
                           ['Move to an eariler spectrum template', 'Move to a later spectrum template'],
                           [self.earlierCallback, self.laterCallback])
        self.createButtons('Change Metallicity [Fe/H]', ['Lower', 'Higher'],
                           ['Move to a lower metallicity template', 'Move to a higher metallicity template'],
                           [self.lowerMetalCallback, self.higherMetalCallback])
        self.createButtons('Spectrum Choices', ['Odd', 'Bad', 'Previous', 'Next'],
                           ['Classify your spectrum as a non-standard spectral type',
                            'Classify your spectrum as bad',
                            'Move to the previous spectrum',
                            'Classify your spectrum as the current selection and move to the next spectrum'],
                           [self.oddCallback, self.badCallback, self.previousCallback, self.nextCallback])

        # The distance metric frame
        self.distMetric = self.createDistanceMetric()

        # Create the matplotlib plot
        self.figure = plt.figure(figsize = (12,6))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        vgrid = QVBoxLayout(spacing = 0)
        vgrid.addWidget(self.toolbar)
        vgrid.addWidget(self.canvas, 1)
        self.grid.addLayout(vgrid, 0, 3, 8, 1)

        # Map the keyboard shortcuts
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_O), self).activated.connect(self.oddCallback)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_B), self).activated.connect(self.badCallback)
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.nextCallback)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_K), self).activated.connect(self.previousCallback)
        QShortcut(QKeySequence(Qt.Key_Left), self).activated.connect(self.earlierCallback)
        QShortcut(QKeySequence(Qt.Key_Right), self).activated.connect(self.laterCallback)
        QShortcut(QKeySequence(Qt.Key_Down), self).activated.connect(self.lowerMetalCallback)
        QShortcut(QKeySequence(Qt.Key_Up), self).activated.connect(self.higherMetalCallback)
        QShortcut(QKeySequence(Qt.CTRL + Qt.Key_P), self).activated.connect(self.callback_hammer_time)

        # *** Setup the Grid ***
        
        self.grid.setRowStretch(7, 1)
        self.grid.setColumnStretch(3, 1)
        self.grid.setContentsMargins(2,2,2,2)
        self.grid.setSpacing(5)
        
        # *** Set the main window properties ***
        
        self.widget.setLayout(self.grid)
        self.setCentralWidget(self.widget)
        self.setWindowTitle('PyHammer Eyecheck')
        self.setWindowIcon(self.icon)

    def createMenuBar(self):
        """
        Description:
            A helper function of the create GUI method which is used to define
            the menubar for the GUI.
        """

        # Use the PyQt menu construct. This is particularly important
        # for Macs because it will keep the menubar with the GUI window
        # rather than placing it at the top of the screen, as is usual
        # for Macs. We don't want this to happen because Macs take control
        # of the menus if you have it up there and can cause unexpected results.
        self.menuBar().setNativeMenuBar(False)

        # *** Define Options Menu ***
        
        optionsMenu = self.menuBar().addMenu('Options')
        optionsMenu.setTearOffEnabled(True)

        # Show Template Error Menu Item
        self.showTemplateError = QAction('Show Template Error', optionsMenu, checkable = True, shortcut = 'Ctrl+E')
        self.showTemplateError.setChecked(True)
        self.showTemplateError.toggled.connect(self.updatePlot)
        optionsMenu.addAction(self.showTemplateError)

        # Smooth Spectrum Menu Item
        self.smoothSpectrum = QAction('Smooth Spectrum', optionsMenu, checkable = True, shortcut = 'Ctrl+S')
        self.smoothSpectrum.toggled.connect(self.updatePlot)
        optionsMenu.addAction(self.smoothSpectrum)

        # Lock Smooth State Menu Item
        self.lockSmoothState = QAction('Lock Smooth State', optionsMenu, checkable = True, shortcut = 'Ctrl+L')
        optionsMenu.addAction(self.lockSmoothState)

        # Remove SDSS Stitch Spike Menu Item
        self.removeStitchSpike = QAction('Remove SDSS Stitch Spike', optionsMenu, checkable = True, shortcut = 'Ctrl+R')
        self.removeStitchSpike.toggled.connect(self.updatePlot)
        optionsMenu.addAction(self.removeStitchSpike)

        optionsMenu.addSeparator()

        # Quit Menu Item
        quitMenuItem = QAction('Quit', optionsMenu, shortcut = 'Ctrl+Q')
        quitMenuItem.triggered.connect(self.close)
        optionsMenu.addAction(quitMenuItem)
        
        # *** Define Help Menu ***
        
        helpMenu = self.menuBar().addMenu('Help')

        # Help Menu Item
        showHelpWindow = QAction('Eyecheck Help', helpMenu)
        showHelpWindow.triggered.connect(lambda: MessageBox(self, self.helpStr, title = 'Help'))
        helpMenu.addAction(showHelpWindow)

        # Buttons Menu Item
        showButtonsWindow = QAction('Buttons', helpMenu)
        showButtonsWindow.triggered.connect(lambda: MessageBox(self, self.buttonStr, title = 'Buttons'))
        helpMenu.addAction(showButtonsWindow)
        
        # Keyboard Shortcuts Menu Item
        showKeyboardShortcutWindow = QAction('Keyboard Shortcuts', helpMenu)
        showKeyboardShortcutWindow.triggered.connect(lambda: MessageBox(self, self.keyStr, title = 'Keyboard Shortcuts'))
        helpMenu.addAction(showKeyboardShortcutWindow)

        # Tips Menu Item
        showTipsWindow = QAction('Tips', helpMenu)
        showTipsWindow.triggered.connect(lambda: MessageBox(self, self.tipStr, title = 'Tips'))
        helpMenu.addAction(showTipsWindow)

        # Separator
        helpMenu.addSeparator()

        # About Menu Item
        showAboutWindow = QAction('About', helpMenu)
        showAboutWindow.triggered.connect(lambda: MessageBox(self, self.aboutStr, title = 'About'))
        helpMenu.addAction(showAboutWindow)

    def createSlider(self, title, labels, callback):
        """
        Description:
            A helper method of the create GUI method. This method creates
            a frame and puts a label at the top, a vertical slider, and
            a collection of labels next to the slider. Note that both the
            slider and labels use customized objects from the gui_utils
            class which were written on top of the respective QWidgets and
            provide additional functionality. See those respective classes
            for details.

        Input:
            title: The label to put at the top of the frame as the title
                for the section.
            labels: The labels to use for the slider. The slider itself
                will be given a set of discrete options to match the number
                of labels provided.
            callback: The callback to use when the slider is set to a new
                value.

        Return:
            Returns the slider and collection of label objects. These are
            returned so the GUI can interact with the labels and slider
            later on.
        """
        
        # Define or update the column of the top-level grid to
        # put this slider component into
        if not hasattr(self, 'column'):
            self.column = 0
        else:
            self.column += 1

        # Create the frame and put it in the top layer grid
        frame = QFrame(frameShape = QFrame.StyledPanel, frameShadow = QFrame.Sunken, lineWidth = 0)
        sliderGrid = QGridLayout()
        frame.setLayout(sliderGrid)
        self.grid.addWidget(frame, 2, self.column)

        # Create the label at the top of the frame
        label = QLabel(title, alignment = Qt.AlignCenter)
        sliderGrid.addWidget(label, 0, 0, 1, 2)

        # Add the slider
        slider = Slider(Qt.Vertical, minimum = 0, maximum = len(labels)-1, tickInterval = 1, pageStep = 1, invertedAppearance = True)
        slider.valueChanged.connect(callback)
        slider.setTickPosition(QSlider.TicksLeft)
        slider.setTracking(False)
        sliderGrid.addWidget(slider, 1, 1, len(labels), 1)

        # Add the text labels to the left of the slider
        tickLabels = []
        for i,text in enumerate(labels):
            label = SliderLabel(text, slider, i)
            tickLabels.append(label)
            sliderGrid.addWidget(label, i+1, 0)

        # Return the labels and slider so we can access them later
        return tickLabels, slider

    def createButtons(self, title, buttonTexts, tooltips, callbacks):
        """
        Description:
            Creates the frames with a title at the top and groups of
            buttons. The tooltips and callbacks are applied to the
            buttons. This method is designed to allow any number of
            buttons to be passed in and it will arrange it in a 2xN
            fashion.

        Input:
            title: A label to place at the top of the frame which
                prodives a title for the group of buttons.
            buttonTexts: A list of the set of texts to for each button.
            tooltips: A list of tooltips to assign to each button.
            callbacks: The list of callbacks to attribute to each button.
        """
        
        # Define or update the row of the top-level grid to
        # put this button frame into
        if not hasattr(self, 'row'):
            self.row = 3
        else:
            self.row += 1

        # Create the frame and put it in the top layer grid
        frame = QFrame(frameShape = QFrame.StyledPanel, frameShadow = QFrame.Sunken, lineWidth = 0)
        buttonGrid = QGridLayout(margin = 2, spacing = 2)
        frame.setLayout(buttonGrid)
        self.grid.addWidget(frame, self.row, 0, 1, 3)

        # Add the label which acts as the title of the button frame
        label = QLabel(title, alignment = Qt.AlignCenter)
        buttonGrid.addWidget(label, 0, 0, 1, 2)

        # Add the buttons. This is done by putting the buttons in rows
        # with two buttons per row until the loop has run out of buttons.
        # Each button is assigned its callback method. The button variable
        # itself is not saved as it is not needed.
        for i,(text,tt,cb) in enumerate(zip(buttonTexts, tooltips, callbacks)):
            button = QPushButton(text)
            button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            button.setToolTip(tt)
            button.clicked.connect(cb)
            buttonGrid.addWidget(button, i//2+1, i%2)

    def createDistanceMetric(self):

        # Create the frame
        frame = QFrame(frameShape = QFrame.StyledPanel, frameShadow = QFrame.Sunken, lineWidth = 0)
        frame.setToolTip('This metric indicates how well the current\n'
                         'template matches the spectrum. The lower\n'
                         'the value, the better the match.')
        distGrid = QVBoxLayout(margin = 2, spacing = 2)
        frame.setLayout(distGrid)
        self.grid.addWidget(frame, self.row + 1, 0, 1, 3)

        # Create the distance metric label
        label = QLabel('Template Match Metric', alignment = Qt.AlignCenter)
        distGrid.addWidget(label)

        # Create the distance metric value label
        label = QLabel('0.0', alignment = Qt.AlignCenter)
        distGrid.addWidget(label)

        return label

    ###
    # Plot Creation Method
    #

    def updatePlot(self):
        """
        Description:
            This is the method which handles all the plotting on the matplotlib
            plot. It will plot the template (if it exists), the user's spectrum
            and do things like control the zoom level on the plot.
        """
        
        # Before updating the plot, check the current axis limits. If they're
        # set to the full limit values, then the plot wasn't zoomed in on when
        # they moved to a new plot. If the limits are different, they've zoomed
        # in and we should store the current plot limits so we can set them
        # to these limits at the end.
        if self.full_xlim is not None and self.full_ylim is not None:
            if (self.full_xlim == plt.gca().get_xlim() and
                self.full_ylim == plt.gca().get_ylim()):
                self.zoomed = False
            else:
                self.zoomed = True
                self.zoomed_xlim = plt.gca().get_xlim()
                self.zoomed_ylim = plt.gca().get_ylim()


        # *** Define Initial Figure ***

        with warnings.catch_warnings():
            warnings.filterwarnings('ignore') # Ignore depreciation warnings
            plt.cla()
            ax = self.figure.add_subplot(111)
            #self.cursor = Cursor(ax, color = '#C8D2DC', lw = 0.5) # THIS BREAKS THE PLOT!
            if self.toolbar._active != 'ZOOM':
                # Make it so the zoom button is selected by default
                self.toolbar.zoom()


        # *** Plot the template ***

        # Determine which, if any, template file to load
        templateFile = self.getTemplateFile()
        
        if templateFile is not None:
            # Load in template data
            with warnings.catch_warnings():
                # Ignore a very particular warning from some versions of astropy.io.fits
                # that is a known bug and causes no problems with loading fits data.
                warnings.filterwarnings('ignore', message = 'Could not find appropriate MS Visual C Runtime ')
                hdulist = fits.open(templateFile)
            lam = np.power(10,hdulist[1].data['loglam'][::10]) # Downsample the templates to save on time
            flux = hdulist[1].data['flux'][::10]
            std = hdulist[1].data['std'][::10]

            # The templates are all normalized to 8000 Angstroms. The loaded spectrum
            # are normalized to this by default as well, but if they're not defined at 8000 Angstroms,
            # it is normalized to a different value that the template needs to be normalized to
            if self.specObj.normWavelength != 8000:
                flux = Spectrum.normalize(lam, self.specObj.normWavelength, flux)
            
            # Plot template error bars and spectrum line
            ax.plot(lam, flux, '-k', label = 'Template')
            if self.showTemplateError.isChecked(): # Only plot template error if option is selected to do so
                ax.fill_between(lam, flux+std, flux-std, color = 'b', edgecolor = 'None', alpha = 0.1, label = 'Template RMS')
            # Determine and format the template name for the title, from the filename
            templateName = os.path.basename(os.path.splitext(templateFile)[0])
            if '_' in templateName:
                ii = templateName.find('_')+1 # Index of first underscore, before metallicity
                templateName = templateName[:ii] + '[Fe/H] = ' + templateName[ii:]
                templateName = templateName.replace('_',',\;')
        else:
            # No template exists, plot nothing
            templateName = 'Not\;Available'


        # *** Plot the user's data ***


        # Get the flux and fix it as the user requested
        if self.smoothSpectrum.isChecked():
            flux = self.specObj.smoothFlux
        else:
            flux = self.specObj.flux
            
        if self.removeStitchSpike.isChecked():
            flux = Spectrum.removeSdssStitchSpike(self.specObj.wavelength, flux)

        # Plot it all up and define the title name
        ax.plot(self.specObj.wavelength, flux, '-r', alpha = 0.75, label = 'Your Spectrum')
        spectraName = os.path.basename(os.path.splitext(self.outData[self.specIndex,0])[0])

        # *** Set Plot Labels ***
                
        ax.set_xlabel(r'$\mathrm{Wavelength\;[\AA]}$', fontsize = 16)
        ax.set_ylabel(r'$\mathrm{Normalized\;Flux}$', fontsize = 16)
        ax.set_title(r'$\mathrm{Template:\;' + templateName + '}$\n$\mathrm{Spectrum:\;' + spectraName.replace('_','\_') + '}$', fontsize = 16)

        # *** Set Legend Settings ***

        handles, labels = ax.get_legend_handles_labels()
        # In matplotlib versions before 1.5, the fill_between plot command above
        # does not appear in the legend. In those cases, we will fake it out by
        # putting in a fake legend entry to match the fill_between plot.
        if pltVersion < '1.5' and self.showTemplateError.isChecked() and templateFile is not None:
            labels.append('Template RMS')
            handles.append(Rectangle((0,0),0,0, color = 'b', ec = 'None', alpha = 0.1))
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
        leg = ax.legend(handles, labels, loc = 0)
        leg.get_frame().set_alpha(0)
        # Set legend text colors to match plot line colors
        if templateFile is not None:
            # Don't adjust the template error if it wasn't plotted
            if self.showTemplateError.isChecked():
                plt.setp(leg.get_texts()[1], color = 'b', alpha = 0.5)  # Adjust template error, alpha is higher to make more readable
                plt.setp(leg.get_texts()[2], color = 'r', alpha = 0.75) # Adjust spectrum label
            else:
                plt.setp(leg.get_texts()[1], color = 'r', alpha = 0.75) # Adjust spectrum table
        else:
            plt.setp(leg.get_texts()[0], color = 'r', alpha = 0.6)

        # *** Set Plot Spacing ***
        
        plt.subplots_adjust(left = 0.143, right = 0.927, top = 0.816, bottom = 0.194)

        # *** Set Plot Limits ***

        ax.set_xlim([3000,11000])               # Set x axis limits to constant value
        self.toolbar.update()                   # Clears out view stack
        self.full_xlim = plt.gca().get_xlim()   # Pull out default, current x-axis limit
        self.full_ylim = plt.gca().get_ylim()   # Pull out default, current y-axis limit
        self.toolbar.push_current()             # Push the current full zoom level to the view stack
        if self.zoomed:                         # If the previous plot was zoomed in, we should zoom this too
            plt.xlim(self.zoomed_xlim)          # Set to the previous plot's zoom level
            plt.ylim(self.zoomed_ylim)          # Set to the previous plot's zoom level
            self.toolbar.push_current()         # Push the current, zoomed level to the view stack so it shows up first

        # *** Calc and update the template match metric text ***

        if templateFile is not None:
            m = min(len(self.specObj.wavelength), len(hdulist[1].data['loglam']))
            dist = round(np.sqrt(np.nansum([(t-s)**2 for t,s in zip(hdulist[1].data['flux'][:m],self.specObj.flux[:m])])),2)
            dist = '{:.2f}'.format(dist)
        else:
            dist = 'None'
        self.distMetric.setText(dist)

        # *** Draw the Plot ***

        self.canvas.draw()
        

    ###
    # Menu Item Callback Methods
    #

    # No menu item callbacks exist currently.

    ###
    # Main GUI Component Callback Methods
    #

    def spectrumChosen(self, val):
        """
        Description:
            Fires when the user chooses a new spectrum from the
            dropdown list of all available spectra.
        """
        self.specIndex = val    # Update the current spectrum index
        self.loadUserSpectrum() # Load the new spectrum
        self.updatePlot()       # Update the plot with the new spectrum

    def specTypeChanged(self, val):
        """
        Description:
            Fires when the the spectrum type slider has been changed
            either by the user or programmatically by the GUI
        """
        self.checkSliderStates()
        self.updatePlot()

    def specSubtypeChanged(self, val):
        """
        Description:
            Fires when the the spectrum subtype slider has been changed
            either by the user or programmatically by the GUI
        """
        self.checkSliderStates()
        self.updatePlot()

    def metallicityChanged(self, val):
        """
        Description:
            Fires when the the metallicity type slider has been changed
            either by the user or programmatically by the GUI
        """
        self.updatePlot()

    def earlierCallback(self):
        """
        Description:
            Fires when the earlier button is pressed (or the associated
            keyboard shortcut is used). Moves the template to an earlier
            spectral type and updates the plot.
        """
        curSpec = self.specTypeSlider.sliderPosition()
        curSub  = self.subTypeSlider.sliderPosition()
        # If user hasn't selected "O" spectral type and they're
        # currently selected zero sub type, we need to loop around
        # to the previous spectral type
        if curSpec != 0 and curSub == 0:
            # Set the sub spectral type, skipping over K8 and K9
            # since they don't exist.
            self.updateSlider(self.subTypeSlider, 7 if curSpec == 6 else 9)
            # Decrease the spectral type
            self.updateSlider(self.specTypeSlider, curSpec - 1)
        else:
            # Just decrease sub spectral type
            self.updateSlider(self.subTypeSlider, curSub - 1)

        # Now check our current slider states to make sure
        # they're valid and then update the plot.
        self.checkSliderStates()
        self.updatePlot()

    def laterCallback(self):
        """
        Description:
            Fires when the later button is pressed (or the associated
            keyboard shortcut is used). Moves the template to a later
            spectral type and updates the plot.
        """
        curSpec = self.specTypeSlider.sliderPosition()
        curSub  = self.subTypeSlider.sliderPosition()
        # If the user hasn't selected "L" spectral type and
        # they're currently selecting "9" spectral sub type
        # (or 7 if spec type is "K"), we need to loop around
        # to the next spectral type
        if curSpec != 7 and (curSub == 9 or (curSpec == 5 and curSub == 7)):
            self.updateSlider(self.specTypeSlider, curSpec + 1)
            self.updateSlider(self.subTypeSlider, 0)
        else:
            # Just increase the sub spectral type
            self.updateSlider(self.subTypeSlider, curSub + 1)

        # Now check our current slider states to make sure
        # they're valid and then update the plot.
        self.checkSliderStates()
        self.updatePlot()

    def lowerMetalCallback(self):
        """
        Description:
            Fires when the later metallicity button is pressed (or the
            associated keyboard shortcut is used). Moves the template to
            a lower metallicity (if possible) and updates the plot.
        """
        curMetal = self.metalSlider.sliderPosition()
        if curMetal != 0:
            self.updateSlider(self.metalSlider, curMetal - 1)
            self.updatePlot()

    def higherMetalCallback(self):
        """
        Description:
            Fires when the higher metallicity button is pressed (or the
            associated keyboard shortcut is used). Moves the template to
            a higher metallicity (if possible) and updates the plot.
        """
        curMetal = self.metalSlider.sliderPosition()
        if curMetal != 6:
            self.updateSlider(self.metalSlider, curMetal + 1)
            self.updatePlot()

    def oddCallback(self):
        """
        Description:
            Fires when the odd button is pressed (or the associated
            keyboard shortcut is used). Brings up the Odd GUI by using
            a class from the gui_utils to allow the user to select a non-
            standard spectrum choice.
        """
        option = OptionWindow(self, ['Wd', 'Wdm', 'Carbon', 'Gal', 'Unknown'], instruction = 'Pick an odd type')
        if option.choice is not None:
            # Store the user's respose in the outData
            self.outData[self.specIndex,5] = option.choice
            self.outData[self.specIndex,6] = 'nan'
            # Move to the next spectrum
            self.moveToNextSpectrum()

    def badCallback(self):
        """
        Description:
            Fires when the bad button is pressed (or the associated
            keyboard shortcut is used). Simply sets the spectrum choice
            as "BAD" and moves on to the next spectrum.
        """
        # Store BAD as the user's choices
        self.outData[self.specIndex,5] = 'BAD'
        self.outData[self.specIndex,6] = 'BAD'
        # Move to the next spectra
        self.moveToNextSpectrum()

    def previousCallback(self):
        """
        Description:
            Fires when the previous button is pressed (or the associated
            keyboard shortcut is used). Moves back to the previous user's
            spectrum.
        """
        self.moveToPreviousSpectrum()

    def nextCallback(self):
        """
        Description:
            Fires when the next button is pressed (or the associated
            keyboard shortcut is used). Stores the current spectrum's
            choice and moves forward to the next user's spectrum.
        """
        # Store the choice for the current spectra
        self.outData[self.specIndex,5] = self.specType[self.specTypeSlider.sliderPosition()] + str(self.subTypeSlider.sliderPosition())
        self.outData[self.specIndex,6] = self.metalType[self.metalSlider.sliderPosition()]
        # Move to the next spectra
        self.moveToNextSpectrum()

    def callback_hammer_time(self):
        timeCalled = time()
        if self.pPressTime == 0 or timeCalled - self.pPressTime > 1.5:
            # Reset
            self.pPressTime = timeCalled
            self.pPressNum = 1
            return
        else:
            self.pPressNum += 1

        if self.pPressNum == 5:
            chrList = [(10,1),(32,18),(46,1),(39,1),(47,1),(32,26),(10,1),(32,1),(42,1),(32,3),(39,1),(42,1),(32,10),(47,1),(32,1),(40,1),(95,11),
                       (46,1),(45,12),(46,1),(32,2),(10,1),(32,9),(42,1),(32,7),(91,1),(32,1),(93,1),(95,11),(124,1),(47,2),(80,1),(121,1),(72,1),
                       (97,1),(109,2),(101,1),(114,1),(47,2),(124,1),(32,2),(10,1),(32,14),(42,1),(32,2),(41,1),(32,1),(40,1),(32,11),(39,1),(45,12),
                       (39,1),(32,2),(10,1),(32,17),(39,1),(45,1),(39,1),(32,1),(42,1),(32,25),(10,1),(32,13),(42,1),(32,33),(10,1),(32,19),(42,1),(32,27)]
            MessageBox(self, ''.join([chr(c[0])*c[1] for c in chrList]), fontFamily = 'courier')
    
    ###
    # Utility Methods
    #

    def checkSliderStates(self):
        """
        Description:
            This method is used whenever the spectrum type sliders
            are updated. It will ensure that the user cannot choose
            certain spectrum types because they are invalid.
        """
        
        # Check to see if the spectral slider is on the K type.
        # If it is, turn off the option to pick K8 and K9
        # since those don't exist. Otherwise, just turn those
        # sub spectral type labels on.
        if self.specTypeSlider.sliderPosition() == 5:
            self.subTypeLabel[-1].setDisabled(True)
            self.subTypeLabel[-2].setDisabled(True)
            if self.subTypeSlider.sliderPosition() in [8,9]:
                self.updateSlider(self.subTypeSlider, 7)
        else:
            self.subTypeLabel[-1].setEnabled(True)
            self.subTypeLabel[-2].setEnabled(True)

    def moveToNextSpectrum(self):
        """
        Description:
            This method handles moving to the next spectrum. All it really
            does is determines if the user is at the end of the list of
            spectrum, and, if so, asks if they're done. If they aren't at
            the end, it moves to the next spectrum (by incrementing self.specIndex)
            and calling self.loadUserSpectrum.
        """
        if self.specIndex+1 >= len(self.outData):
            QApplication.beep() # Use the system beep to notify the user
            msg =  MessageBox(self, "You've classified all the spectra. Are you finished?",
                              buttons = QMessageBox.Yes|QMessageBox.No)
            if msg.reply == QMessageBox.Yes:
                self._cleanUpAndClose()
        else:
            self.specIndex += 1
            self.loadUserSpectrum()
            self.updatePlot()

    def moveToPreviousSpectrum(self):
        """
        Description:
            This method handles moving to the previous spectrum. It will simply
            decrement the self.specIndex variable if they're not already on
            the first index and call self.loadUserSpectrum.
        """
        if self.specIndex > 0:
            self.specIndex -= 1
            self.loadUserSpectrum()
            self.updatePlot()

    def splitSpecType(self, s):
        head = s.rstrip('0123456789')
        tail = s[len(head):]
        return head, tail

    def loadUserSpectrum(self):
        """
        Description:
            This handles loading a new spectrum based on the self.specIndex variable
            and updates the GUI components accordingly
        """
        
        # Read in the spectrum file indicated by self.specIndex
        fname = self.outData[self.specIndex,0]
        ftype = self.outData[self.specIndex,1]
        self.specObj.readFile(self.options['spectraPath']+fname, ftype) # Ignore returned values
        self.specObj.normalizeFlux()
        
        # Set the spectrum entry field to the new spectrum name
        self.spectrumList.setCurrentIndex(self.specIndex)

        # Set the sliders to the new spectrum's auto-classified choices
        specTypePostSplit,  specSubTypePostSplit = self.splitSpecType(self.outData[self.specIndex,3])

        self.updateSlider( self.specTypeSlider, self.specType.index(specTypePostSplit) )
        self.updateSlider( self.subTypeSlider,  self.subType.index(specSubTypePostSplit)  )
        self.updateSlider( self.metalSlider,    self.metalType.index(self.outData[self.specIndex,4])   )
        
        # Reset the indicator for whether the plot is zoomed. It should only stay zoomed
        # between loading templates, not between switching spectra.
        self.full_xlim = None
        self.full_ylim = None
        self.zoomed = False
        
        # Reset the smooth state to be unsmoothed, unless the user chose to lock the state
        if not self.lockSmoothState.isChecked():
            self.smoothSpectrum.setChecked(False)

    def getTemplateFile(self, specState = None, subState = None, metalState = None):
        """
        Description:
            This will determine the filename for the template which matches the
            current template selection. Either that selection will come from
            current slider positions, or else from input to this function. This
            will search for filenames matching a specific format. The first attempt
            will be to look for a filename of the format "SS_+M.M_Dwarf.fits",
            where the SS is the spectral type and subtype and +/-M.M is the [Fe/H]
            metallicity. The next next format it will try (if the first doesn't
            exist) is "SS_+M.M.fits". After that it will try "SS.fits".
        """
        # If values weren't passed in for certain states, assume we should
        # use what is chosen on the GUI sliders
        if specState is None: specState = self.specTypeSlider.sliderPosition()
        if subState is None: subState = self.subTypeSlider.sliderPosition()
        if metalState is None: metalState = self.metalSlider.sliderPosition()

        # Try using the full name, i.e., SS_+M.M_Dwarf.fits
        filename = self.specType[specState] + str(subState) + '_' + self.metalType[metalState] + '_Dwarf'

        fullPath = os.path.join(self.templateDir, filename + '.fits')

        if os.path.isfile(fullPath):
            return fullPath

        # Try using only the spectra and metallicity in the name, i.e., SS_+M.M.fits
        filename = filename[:7]

        fullPath = os.path.join(self.templateDir, filename + '.fits')

        if os.path.isfile(fullPath):
            return fullPath
        
        # Try to use just the spectral type, i.e., SS.fits
        #filename = filename[:2]
        filename = self.specType[specState] + str(subState)

        fullPath = os.path.join(self.templateDir, filename + '.fits')
        
        if os.path.isfile(fullPath):
            return fullPath

        # Return None if file could not be found
        return None

    def updateSlider(self, slider, value):
        slider.blockSignals(True)
        slider.setValue(value)
        slider.setSliderPosition(value)
        slider.blockSignals(False)

    def closeEvent(self, event):
        """
        Description:
            This method is the window's closeEvent method and is here to
            override the QMainWindow closeEvent method. Effectively, if the
            user want's to quit the program and they trigger the close
            event, this will catch that event and ask them if they're sure
            they want to close first. If they respond with yes, this will
            run the _writeOutDataToFile function which saves the data the
            user has produced and then calls the parent close method to handle
            the actual close process. If they respond no, it just ignores the
            close event and continues running the GUI.
        """
        # Ask the user if they're sure they actually want to quit
        msg = MessageBox(self, 'Are you sure you want to exit PyHammer?', title = 'Quit',
                         buttons = QMessageBox.Yes|QMessageBox.No)
        if msg.reply == QMessageBox.Yes:
            self._writeOutDataToFile()
            event.accept()
        else:
            event.ignore()

    def _cleanUpAndClose(self):
        """
        Description:
            This method is one of the available close methods of the GUI. It
            simply performs the process of outputing the spectra data to
            the output file and quitting. Note that the process of quitting
            involved is to force quit the entire QApplication, not just this
            QMainWindow object. This is because of the fact that we don't want
            to trigger the closeEvent method of the QMainWindow object.
        """
        self._writeOutDataToFile()
        qApp.quit()

    def _writeOutDataToFile(self):
        """
        Description:
            Writes all the output data to the output file. This method is used
            before any quit procedures so save the data recorded by the user
            before closing the GUI.
        """
        with open(self.options['outfile'], 'w') as outfile:
            outfile.write('#Filename,File Type,Radial Velocity (km/s),Guessed Spectral Type,Guessed [Fe/H],User Spectral Type,User [Fe/H]\n')
            for i, spectra in enumerate(self.outData):
                for j, col in enumerate(spectra):
                    outfile.write(col)
                    if j < 6: outfile.write(',')
                if i < len(self.outData)-1: outfile.write('\n')
        
