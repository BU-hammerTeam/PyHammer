import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
import time
import os
import csv
import pdb

class Eyecheck(object):

    def __init__(self, specObj, options):
        # Store input variables
        self.specObj = specObj
        self.options = options
        # Open the infile and read it into a list
        self.inData = []
        with open(options['infile'], 'r') as file:
            for line in file:
                self.inData.append(line.strip().rsplit(' ',1))
        # Open the outfile and read it into a list
        with open(options['outfile'], 'r') as file:
            reader = csv.reader(file)
            self.outData = list(reader)[1:] # Ignore the header line
        # Define User's spectrum data
        self.specIndex = 0
        self.specObj.readFile(options['spectraPath']+self.inData[self.specIndex][0],
                              self.inData[self.specIndex][1]) # Ignore returned values
        # Useful information
        self.specType  = ['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L']
        self.subType   = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        self.metalType = ['-2.0', '-1.5', '-1.0', '-0.5', '+0.0', '+0.5', '+1.0']
        self.templates = ['O5', 'O7', 'O8', 'O9', 'B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B8', 'B9', 'A0', 'A1', 'A3-1.0', 'A3-0.5', 'A3+0.0', 'A3+0.5', 'A4-1.0', 'A6-2.0', 'A6-1.5', 'A6-1.0', 'A6-0.5', 'A6+0.0', 'A6+0.5', 'A7-2.0', 'A7-1.5', 'A7-1.0', 'A7-0.5', 'A7+0.0', 'A7+0.5', 'A8-1.5', 'A8-1.0', 'A8-0.5', 'A8+0.5', 'A9-2.0', 'A9-1.5', 'A9-1.0', 'A9-0.5', 'A9+0.0', 'A9+0.5', 'F0-2.0', 'F0-1.5', 'F0-1.0', 'F0+0.0', 'F0+0.5', 'F1-2.0', 'F1-1.5', 'F1-1.0', 'F1-0.5', 'F2-2.0', 'F2-1.5', 'F2-1.0', 'F2-0.5', 'F2+0.0', 'F3-2.0', 'F3-1.5', 'F3-1.0', 'F3-0.5', 'F3+0.0', 'F4-2.0', 'F4-1.5', 'F4-1.0', 'F4-0.5', 'F4+0.0', 'F5-2.0', 'F5-1.5', 'F5-1.0', 'F5-0.5', 'F6-2.0', 'F6-1.5', 'F6-1.0', 'F6-0.5', 'F6+0.0', 'F7-2.0', 'F7-1.5', 'F7-1.0', 'F7-0.5', 'F7+0.0', 'F8-2.0', 'F8-1.5', 'F8-1.0', 'F8-0.5', 'F8+0.0', 'F9-2.0', 'F9-1.5', 'F9-1.0', 'F9-0.5', 'F9+0.0', 'G0-2.0', 'G0-1.5', 'G0-1.0', 'G0-0.5', 'G0+0.0', 'G1-2.0', 'G1-1.5', 'G1-1.0', 'G1-0.5', 'G1+0.0', 'G2-2.0', 'G2-1.0', 'G2-0.5', 'G2+0.0', 'G3-2.0', 'G3-1.5', 'G3-1.0', 'G3-0.5', 'G3+0.0', 'G4-2.0', 'G4-1.5', 'G4-1.0', 'G4-0.5', 'G4+0.0', 'G5-2.0', 'G5-1.5', 'G5-1.0', 'G5-0.5', 'G5+0.0', 'G5+0.5', 'G6-2.0', 'G6-1.5', 'G6-1.0', 'G6-0.5', 'G6+0.0', 'G6+0.5', 'G7-1.0', 'G7-0.5', 'G7+0.0', 'G7+0.5', 'G8-2.0', 'G8-1.5', 'G8-1.0', 'G8-0.5', 'G8+0.0', 'G8+0.5', 'G9-2.0', 'G9-1.5', 'G9-1.0', 'G9-0.5', 'G9+0.0', 'G9+0.5', 'K0-1.0', 'K0-0.5', 'K0+0.0', 'K1-2.0', 'K1-1.0', 'K1-0.5', 'K1+0.0', 'K1+0.5', 'K2-1.5', 'K2-1.0', 'K2-0.5', 'K2+0.0', 'K2+0.5', 'K3-2.0', 'K3-1.5', 'K3-1.0', 'K3-0.5', 'K3+0.0', 'K3+0.5', 'K4-1.0', 'K4-0.5', 'K4+0.0', 'K4+0.5', 'K5-2.0', 'K5-1.0', 'K5-0.5', 'K5+0.0', 'K5+0.5', 'K7-1.0', 'K7-0.5', 'K7+0.0', 'K7+0.5', 'K7+1.0', 'M0-0.5', 'M0+0.0', 'M0+0.5', 'M0+1.0', 'M1-1.0', 'M1-0.5', 'M1+0.0', 'M1+0.5', 'M2-1.0', 'M2-0.5', 'M2+0.0', 'M2+0.5', 'M3-1.0', 'M3-0.5', 'M3+0.0', 'M3+0.5', 'M4+0.0', 'M4+0.5', 'M5-0.5', 'M5+0.0', 'M5+0.5', 'M6-0.5', 'M6+0.0', 'M6+0.5', 'M7-0.5', 'M7+0.0', 'M7+0.5', 'M8-0.5', 'M8+0.0', 'M9', 'L0', 'L1', 'L2', 'L3', 'L6']
        self.templateDir = os.path.join(os.path.split(__file__)[0], 'resources', 'templates')
        # GUI Components
        self.root = tk.Tk()
        self.spectrumEntry = tk.StringVar(value = os.path.basename(self.inData[self.specIndex][0]))
        self.specState  = tk.IntVar(value = self.specType.index(self.outData[self.specIndex][2][0]))
        self.subState   = tk.IntVar(value = int(self.outData[self.specIndex][2][1]))
        self.metalState = tk.IntVar(value = self.metalType.index(self.outData[self.specIndex][3]))
        self.subButtons = []            # We keep track of these radio buttons so
        self.metalButtons = []          # they can be enabled and disabled if need be
        # Figure Components
        plt.ion()
        plt.style.use('ggplot')         # Just makes it look nice
        self.full_xlim = None           # Store these to keep track of zooming
        self.full_ylim = None
        self.zoomed_xlim = None
        self.zoomed_ylim = None
        self.zoomed = False
        self.updatePlot()               # Create the plot
        
        # Call the method for setting up the GUI layout
        self.setupGUI()

        # Run the GUI
        self.root.mainloop()

    def _exit(self):
        # Write the outData to the output file
        with open(options['outfile'], 'w') as outfile:
            outfile.write('#Filename,Radial Velocity (km/s),Guessed Spectral Type,Guessed Metallicity,User Spectral Type,User Metallicity\n')
            for i, spectra in enumerate(self.outData):
                for j, col in enumerate(spectra):
                    outfile.write(col)
                    if j < 5: outfile.write(',')
                if i < len(self.outData)-1: outfile.write('\n')
        # Close down the GUI and plot window
        self.root.destroy()
        plt.close('all')

    def setupGUI(self):
        # Set the root window properties
        self.root.title('PyHammer Eyecheck')
        self.root.iconbitmap(r'resources\sun.ico')
        self.root.resizable(False, False)
        self.root.geometry('+100+100')

        # Define the menubar
        menubar = tk.Menu()

        fileMenu = tk.Menu(menubar, tearoff = 0)
        fileMenu.add_command(label = 'Quit', command = self._exit)

        aboutMenu = tk.Menu(menubar, tearoff = 0)
        aboutMenu.add_command(label = 'Help', command = self.callback_help)
        aboutMenu.add_command(label = 'About', command = self.callback_about)

        menubar.add_cascade(label = 'File', menu = fileMenu)
        menubar.add_cascade(label = 'About', menu = aboutMenu)
        self.root.config(menu = menubar)
        
        # Define the labels in the GUI
        for i, name in enumerate(['Spectra', 'Type', 'Subtype', 'Metallicity', 'Change Type', 'Change Metallicity', 'Options']):
            ttk.Label(self.root, text = name).grid(row = i, column = 0, stick = 'e',
                                                   pady = (10*(i==4),10*(i==0)))

        # Define the entry box and relevant widgets for indicating the spectrum
        ttk.Entry(self.root, textvariable = self.spectrumEntry).grid(row = 0, column = 1, columnspan = 9, pady = (0,10), sticky = 'nesw')
        ttk.Button(self.root, text = 'Go', width = 3, command = self.jumpToSpectrum).grid(row = 0, column = 10, pady = (0,10))

        # Define the radio buttons
        # First the radio buttons for the spectral type
        for ind, spec in enumerate(self.specType):
            temp = ttk.Radiobutton(self.root, text = spec, variable = self.specState, value = ind,
                                   command = lambda: self.callback_specRadioChange(True))
            temp.grid(row = 1, column = ind+1, sticky = 'nesw')
        # Now the sub spectral type radio buttons
        for ind, sub in enumerate(self.subType):
            self.subButtons.append(ttk.Radiobutton(self.root, text = sub, variable = self.subState, value = ind,
                                                   command = lambda: self.callback_subRadioChange(True)))
            self.subButtons[-1].grid(row = 2, column = ind+1, sticky = 'nesw')
        # Finally the radio buttons for the metallicities
        for ind, metal in enumerate(self.metalType):
            self.metalButtons.append(ttk.Radiobutton(self.root, text = metal, variable = self.metalState, value = ind,
                                                     command = lambda: self.callback_metalRadioChange(True)))
            self.metalButtons[-1].grid(row = 3, column = ind+1, sticky = 'nesw')
            
        # Define the buttons for interacting with the data (e.g., flag it, next, back):
        ttk.Button(self.root, text = 'Earlier', command = self.callback_earlier).grid(row = 4, column = 1, columnspan = 5, sticky = 'nesw', pady = (10,0))
        ttk.Button(self.root, text = 'Later', command = self.callback_later).grid(row = 4, column = 6, columnspan = 5, sticky = 'nesw', pady = (10,0))
        ttk.Button(self.root, text = 'Lower', command = self.callback_lower).grid(row = 5, column = 1, columnspan = 5, sticky = 'nesw')
        ttk.Button(self.root, text = 'Higher', command = self.callback_higher).grid(row = 5, column = 6, columnspan = 5, sticky = 'nesw')
        ttk.Button(self.root, text = 'Odd', underline = 0, command = self.callback_odd).grid(row = 6, column = 1, columnspan = 2, sticky = 'nesw')
        ttk.Button(self.root, text = 'Bad', underline = 0, command = self.callback_bad).grid(row = 6, column = 3, columnspan = 2, sticky = 'nesw')
        ttk.Button(self.root, text = 'Smooth', underline = 0, command = self.callback_smooth).grid(row = 6, column = 5, columnspan = 2, sticky = 'nesw')
        ttk.Button(self.root, text = 'Back', underline = 3, command = self.callback_back).grid(row = 6, column = 7, columnspan = 2, sticky = 'nesw')
        ttk.Button(self.root, text = 'Next', command = self.callback_next).grid(row = 6, column = 9, columnspan = 2, sticky = 'nesw')

        # Set the key bindings
        self.root.bind('o', lambda event: self.callback_odd())
        self.root.bind('b', lambda event: self.callback_bad())
        self.root.bind('s', lambda event: self.callback_smooth())
        self.root.bind('<Return>', lambda event: self.callback_next())
        self.root.bind('k', lambda event: self.callback_back())
        self.root.bind('<Left>', lambda event: self.callback_earlier())
        self.root.bind('<Right>', lambda event: self.callback_later())
        self.root.bind('<Down>', lambda event: self.callback_lower())
        self.root.bind('<Up>', lambda event: self.callback_higher())

        # Set the close protocol to call this class' personal exit function
        self.root.protocol('WM_DELETE_WINDOW', self._exit)

        # Force the GUI to appear as a top level window, on top of all other windows
        self.root.lift()
        self.root.call('wm', 'attributes', '.', '-topmost', True)
        self.root.after_idle(self.root.call, 'wm', 'attributes', '.', '-topmost', False)

    def updatePlot(self):
        # Before updating the plot, check the current axis limits. If they're
        # set to the full limit values, then the plot wasn't zoomed in on when
        # they moved to a new plot. If the limits are different, they've zoomed
        # in and we should store the current plot limits so we can set them
        # to these limits at the end.
        if self.full_xlim is not None:
            if (self.full_xlim == plt.gca().get_xlim() and
                self.full_ylim == plt.gca().get_ylim()):
                self.zoomed = False
            else:
                self.zoomed = True
                self.zoomed_xlim = plt.gca().get_xlim()
                self.zoomed_ylim = plt.gca().get_ylim()
        
        # Do some initial plotting tasks
        fig = plt.figure('Pyhammer Spectrum Matching', figsize = (12,6))
        plt.cla()   # Clear the plot
        if plt.get_current_fig_manager().toolbar._active != 'ZOOM':
            # Make it so the zoom button is selected by default
            plt.get_current_fig_manager().toolbar.zoom()
            
        # Determine which, if any, template file to load
        templateFile = self.getTemplateFile()

        # Plot the template
        if templateFile is not None:
            hdulist = fits.open(templateFile)
            self.templateLoglam = hdulist[1].data['loglam']
            self.templateFlux = hdulist[1].data['flux']
            #self.templateStd = hdulist[1].data['std']

            plt.plot(self.templateLoglam[::10], self.templateFlux[::10], '-k', label = 'Template')
            templateName = os.path.split(templateFile)[1][:-5].replace('_','\;')
        else:
            plt.plot([],[], '-k', label = 'Template')
            templateName = 'N/A'
        # Plot the user's data
        plt.plot(self.specObj.loglam, self.specObj.normFlux, '-r', label = 'Your Spectrum')
        spectraName = os.path.basename(self.inData[self.specIndex][0])[:-5]

        # Set some axis settings
        plt.xlabel(r'$\mathrm{log_{10}(wavelength / \mathring{A})}$', fontsize = 16)
        plt.ylabel(r'$\mathrm{Normalized\;Flux}$', fontsize = 16)
        plt.title(r'$\mathrm{Template:\;' + templateName + '}$\n$\mathrm{Spectrum:\;' + spectraName + '}$', fontsize = 16)
        plt.xlim([3.5,4.05])
        plt.legend(loc = 0).get_frame().set_alpha(0)
        plt.subplots_adjust(left = 0.075, right = 0.975, top = 0.9, bottom = 0.15)
        # Set the plot limits
        self.full_xlim = plt.gca().get_xlim()
        self.full_ylim = plt.gca().get_ylim()
        fig.canvas.toolbar.push_current()       # Push the current full zoom level to the stack
        if self.zoomed:                         # If the previous plot was zoomed in, we should zoom this too
            plt.xlim(self.zoomed_xlim)          # Set to the previous plot's zoom level
            plt.ylim(self.zoomed_ylim)          # Set to the previous plot's zoom level
            fig.canvas.toolbar.push_current()   # Push the current, zoomed level to the stack so it shows up first

        plt.draw()
        

    ##
    # Menu Item Callbacks
    #
    
    def callback_help(self):
        helpStr = \
            'Welcome to the main GUI for spectral typing your spectra.\n\n' \
            'Each spectra in your spectra list file will be loaded in\n' \
            'sequence and shown on top of the template it was matched\n' \
            'to. From here, fine tune the spectral type by comparing\n ' \
            'your spectrum to the templates and choose "Done" when\n' \
            "you've landed on the correct choice. Continue through each\n" \
            'spectrum until finished.'
        self.showInfoWindow('Pyhammer Help', helpStr)

    def callback_about(self):
        aboutStr = \
            'This project was developed by a select group of graduate students\n' \
            'at the Department of Astronomy at Boston University. The project\n' \
            'was lead by Aurora Kesseli with development help and advice provided\n' \
            'by Mark Veyette, Dylan Morgan, Andrew West, Brandon Harrison, and\n' \
            'Dan Feldman. Contributions were further provided by Chris Theissan.\n\n' \
            'See the acompanying paper Kesseli et al. (2016) for further details.'
        self.showInfoWindow('Pyhammer About', aboutStr)

    def showInfoWindow(self, title, text):
        """
        showHelpWindow(root, helpText)

        Description:
            This brings up a new window derived from root
            that displays helpText and has a button to close
            the window when user is done.

        Input:
            text: This should be a string to display
        """
        
        infoWindow = tk.Toplevel(self.root)
        infoWindow.title(title)
        infoWindow.iconbitmap(r'resources\sun.ico')
        infoWindow.resizable(False, False)
        infoWindow.geometry('+%i+%i' % (self.root.winfo_rootx(), self.root.winfo_rooty()))
        
        label = ttk.Label(infoWindow, text = text, font = '-size 10')
        label.grid(row = 0, column = 0, padx = 2, pady = 2)
        but = ttk.Button(infoWindow, text = 'OK', command = infoWindow.destroy)
        but.grid(row = 1, column = 0, sticky = 'nsew', padx = 2, pady = 5)
        infoWindow.rowconfigure(1, minsize = 40)


    ##
    # Button and Key Press Callbacks
    #
    
    def callback_odd(self):
        # Store the custom name designation from the user
        choice = OddWindow(self.root, ['Wd', 'Wdm', 'Carbon', 'Gal', 'Unknown'])
        self.root.wait_window(choice.oddWindow)
        self.outData[self.specIndex][4] = choice.name
        self.outData[self.specIndex][5] = 'nan'
        # Move to the next spectra
        self.moveToNextSpectrum()
        
    def callback_bad(self):
        # Store BAD as the user's choices
        self.outData[self.specIndex][4] = 'BAD'
        self.outData[self.specIndex][5] = 'BAD'
        # Move to the next spectra
        self.moveToNextSpectrum()
        
    def callback_smooth(self):
        print('Someone pushed a smooth button.')
        
    def callback_next(self):
        # Store the choice for the current spectra
        self.outData[self.specIndex][4] = self.specType[self.specState.get()] + str(self.subState.get())
        self.outData[self.specIndex][5] = self.metalType[self.metalState.get()]
        # Move to the next spectra
        self.moveToNextSpectrum()
        
    def callback_back(self):
        self.moveToPreviousSpectrum()
    
    def callback_earlier(self):
        curSub  = self.subState.get()
        curSpec = self.specState.get()
        # If user hasn't selected "O" spectral type and they're
        # currently selected zero sub type, we need to loop around
        # to the previous spectral type
        if curSpec != 0 and curSub == 0:
            # Set the sub spectral type, skipping over K8 and K9
            # since they don't exist.
            self.subState.set(7 if curSpec == 6 else 9)
            # Decrease the spectral type
            self.specState.set(curSpec - 1)
        else:
            # Just decrease sub spectral type
            self.subState.set(curSub - 1)

        # Call the spectral and sub spectral type radio
        # button change callbacks as if the user changed
        # the buttons themselves
        self.callback_specRadioChange(True)
        self.callback_subRadioChange(False)

    def callback_later(self):
        curSub  = self.subState.get()
        curSpec = self.specState.get()
        # If the user hasn't selected "L" spectral type and
        # they're currently selecting "9" spectral sub type
        # (or 7 if spec type is "K"), we need to loop around
        # to the next spectral type
        if curSpec != 7 and (curSub == 9 or (curSpec == 5 and curSub == 7)):
            self.specState.set(curSpec + 1)
            self.subState.set(0)
        else:
            # Just increase the sub spectral type
            self.subState.set(curSub + 1)

        # Call the spectral and sub spectral type radio
        # button change callbacks as if the user changed
        # the buttons themselves.
        self.callback_specRadioChange(True)
        self.callback_subRadioChange(False)

    def callback_higher(self):
        curMetal = self.metalState.get()
        # If the user isn't at the max metallicity option,
        # then increase the metallicity
        if curMetal != 6:
            self.metalState.set(curMetal + 1)
        # Call the metallicity radio button change callback
        # as if the user changed the button themselves.
        self.callback_metalRadioChange(True)

    def callback_lower(self):
        curMetal = self.metalState.get()
        # If the user isn't at the min mellaticity option,
        # then decrease the metallicity
        if curMetal != 0:
            self.metalState.set(curMetal - 1)
        # Call the metallicity radio button change callback
        # as if the user changed the button themselves.
        self.callback_metalRadioChange(True)

    ##
    # Radiobutton Selection Change Callbacks
    #

    def callback_specRadioChange(self, callUpdatePlot):
        # If the spectral type radio button has changed,
        # check to see if the user switched to a "K" type.
        # If they have, turn off the option to pick K8 and K9
        # Since those don't exist. Otherwise, just turn those
        # sub spectral type buttons on.
        if self.specState.get() == 5:
            self.subButtons[-1].configure(state = 'disabled')
            self.subButtons[-2].configure(state = 'disabled')
            if self.subState.get() == 8 or self.subState.get() == 9:
                self.subState.set(7)
        else:
            self.subButtons[-1].configure(state = 'normal')
            self.subButtons[-2].configure(state = 'normal')
            
        if callUpdatePlot: self.updatePlot()

    def callback_subRadioChange(self, callUpdatePlot):
        if callUpdatePlot: self.updatePlot()

    def callback_metalRadioChange(self, callUpdatePlot):
        if callUpdatePlot: self.updatePlot()

    ##
    # Utility Methods
    #

    def moveToNextSpectrum(self):
        if self.specIndex+1 >= len(self.inData):
            modal = ModalWindow(self.root, 'PyHammer', "You've classified all the spectra. Are you finished?")
            self.root.wait_window(modal.modalWindow)
            if modal.choice == 'Yes':
                self._exit()
        else:
            self.specIndex += 1
            self.getUserSpectrum()

    def moveToPreviousSpectrum(self):
        if self.specIndex > 0:
            self.specIndex -= 1
            self.getUserSpectrum()

    def jumpToSpectrum(self):
        spectrumFound = False
        for i, spectrum in enumerate(self.inData):
            if os.path.basename(self.spectrumEntry.get()) == os.path.basename(spectrum[0]):
                self.specIndex = i
                spectrumFound = True
                break
        if not spectrumFound:
            message = 'The spectrum you input could not be matched\n' \
                      'to one of the spectrum in your list. Check\n' \
                      'your input and try again.'
            self.showInfoWindow('PyHammer Error', message)
        else:
            self.getUserSpectrum()

    def getUserSpectrum(self):
        # Read in the next spectrum file
        self.specObj.readFile(options['spectraPath']+self.inData[self.specIndex][0],
                              self.inData[self.specIndex][1]) # Ignore returned values from readFile
        # Set the spectrum entry field
        self.spectrumEntry.set(os.path.basename(self.inData[self.specIndex][0]))
        # Set the radio button selections
        self.specState.set(self.specType.index(self.outData[self.specIndex][2][0]))
        self.subState.set(int(self.outData[self.specIndex][2][1]))
        self.metalState.set(self.metalType.index(self.outData[self.specIndex][3]))
        # Update the plot
        self.updatePlot()

    def getTemplateFile(self, specState = None, subState = None, metalState = None):
        # If values weren't passed in for certain states, assume we should
        # use what is chosen on the GUI
        if specState is None: specState = self.specState.get()
        if subState is None: subState = self.subState.get()
        if metalState is None: metalState = self.metalState.get()
        
        # Try to use just the spectral type and subtype for the name first
        filename = self.specType[specState] + str(subState)

        fullPath = os.path.join(self.templateDir, filename + '.fits')
        
        if os.path.isfile(fullPath):
            return fullPath

        # Try adding the current metallicity choice
        filename += '_' + self.metalType[metalState]

        fullPath = os.path.join(self.templateDir, filename + '.fits')

        if os.path.isfile(fullPath):
            return fullPath

        # Try adding the word Dwarf to the name
        filename += '_Dwarf'

        fullPath = os.path.join(self.templateDir, filename + '.fits')

        if os.path.isfile(fullPath):
            return fullPath

        # Return None if file could not be found
        return None


class ModalWindow(object):

    def __init__(self, parent, title, text):
        self.choice = None

        # Setup the window
        self.modalWindow = tk.Toplevel(parent)
        self.modalWindow.title(title)
        self.modalWindow.iconbitmap(r'resources\sun.ico')
        self.modalWindow.resizable(False, False)
        self.modalWindow.geometry('+%i+%i' % (parent.winfo_rootx(), parent.winfo_rooty()))

        # Setup the widgets in the window
        label = ttk.Label(self.modalWindow, text = text, font = '-size 10')
        label.grid(row = 0, column = 0, columnspan = 2, padx = 2, pady = 2)
        
        but = ttk.Button(self.modalWindow, text = 'Yes', command = self.choiceYes)
        but.grid(row = 1, column = 0, sticky = 'nsew', padx = 2, pady = 5)

        but = ttk.Button(self.modalWindow, text = 'No', command = self.choiceNo)
        but.grid(row = 1, column = 1, sticky = 'nsew', padx = 2, pady = 5)

        self.modalWindow.rowconfigure(1, minsize = 40)

    def choiceYes(self):
        self.choice = 'Yes'
        self.modalWindow.destroy()

    def choiceNo(self):
        self.choice = 'No'
        self.modalWindow.destroy()


class OddWindow(object):

    def __init__(self, parent, choices):
        self.name = None
        self.choices = choices
        self.radioChoice = tk.IntVar(value = 0)
        self.customName = tk.StringVar()
        self.label = tk.StringVar(value = 'Choose Odd Type')

        # Setup the window
        self.oddWindow = tk.Toplevel(parent)
        self.oddWindow.title('')
        self.oddWindow.iconbitmap(r'resources\sun.ico')
        self.oddWindow.resizable(False, False)
        self.oddWindow.geometry('+%i+%i' % (parent.winfo_rootx(), parent.winfo_rooty()))

        # Setup the widgets in the window
        tk.Label(self.oddWindow, textvariable = self.label, justify = 'center').grid(row = 0, column = 0)
        
        for i, c in enumerate(choices):
            temp = ttk.Radiobutton(self.oddWindow, text = c, variable = self.radioChoice, value = i)
            temp.grid(row = i+1, column = 0, padx = 10, sticky = 'nesw')
            
        temp = ttk.Radiobutton(self.oddWindow, text = '', variable = self.radioChoice, value = i+1)
        temp.grid(row = i+2, column = 0, padx = 10, sticky = 'nesw')
        
        temp = ttk.Entry(self.oddWindow, textvariable = self.customName, width = 10)
        temp.grid(row = i+2, column = 0, padx = 30, sticky = 'w')

        but = ttk.Button(self.oddWindow, text = 'OK', command = self.done)
        but.grid(row = i+3, column = 0, sticky = 'nsew', padx = 2, pady = 5)
        self.oddWindow.rowconfigure(i+3, minsize = 40)
        self.oddWindow.columnconfigure(0, minsize = 175)

    def done(self):
        if self.radioChoice.get() < len(self.choices):
            self.name = self.choices[self.radioChoice.get()]
        else:
            if self.customName.get() == '':
                self.label.set('Enter Text for Custom Name')
                self.oddWindow.bell()
                self.oddWindow.after(1500, lambda: self.label.set('Choose Odd Type'))
                return
            else:
                self.name = self.customName.get()
        self.oddWindow.destroy()
        
