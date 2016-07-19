import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt

##
# [Brandon] This is the main GUI for the program. I highly suggest 
# doing something that invovles embedding the matplotlib graphic
# into the GUI rather than having a plotting window and a GUI up
# separately. I've also already set up a method to respond to key
# presses so the user can use the keys. Since the original program
# allowed the user to either use keys or not, we can potentially add
# a small button or menu option or something where they can turn off
# this ability. Some users might like that as bumping the keyboard
# could do something they don't want.
#
# Another note, always use ttk objects when possible as they automatically
# use the user's default UI and will look better on their native computer.
#

### Callback functions:
def callback_odd():                                            
    print('Someone pushed an odd button.')
    
def callback_bad(): 
    print('Someone pushed a bad button.')
    
def callback_smooth():
    print('Someone pushed a smooth button.')
    
def callback_done():                                            
    print('Someone pushed a done button.')
    
def callback_back():                                           
    print('Someone pushed a back button.') 
    
def callback_earlier(specState, subState):                                            
    currentSub = subState.get()
    currentSpec= specState.get()
    if currentSub == 0:
        if currentSpec != 0:
            specState.set(specState.get() - 1)
            if specState.get() == 5:
                subState.set(7)
            else:
                subState.set(9)
    else:
        subState.set(currentSub - 1) 

def callback_later(specState, subState):                                             
    currentSub = subState.get()
    currentSpec= specState.get()
    if currentSub == 9 or (currentSpec == 5 and currentSub == 7):
        if currentSpec != 9:
            specState.set(specState.get() + 1)
            subState.set(0)
    else:
        subState.set(currentSub + 1)

def callback_lower(specState, subState):
    print('Someone pushed a lower button.') 

def callback_higher(specState, subState):
    print('Someone pushed a higher button.') 

def callback_radioSpec(specState, subState, subButts):
    if specState.get() == 5:
        subButts[-1].configure(state='disabled')
        subButts[-2].configure(state='disabled')
        if subState.get() == 8 or subState.get() == 9:
            subState.set(7)
    else:
        subButts[-1].configure(state='normal')
        subButts[-2].configure(state='normal')

### Main GUI loop:    
def main():

    # Set up the root window
    root = tk.Tk()
    root.title('PyHammer Plot Options')
    root.iconbitmap(r'resources\sun.ico')
    root.resizable(False, False)
    root.geometry('+100+100')
    
    # Define some useful quantities and variables
    specType   = np.array(['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L'])
    subType    = np.array(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
    metalType  = np.array(['-2.0', '-1.5', '-1.0', '-0.5', '0.0', '0.5', '1.0'])

    # Define the labels in the GUI:
    for i, name in enumerate(['Type', 'Subtype', 'Metallicity', 'Change Type', 'Change Metallicity', 'Options']):
        ttk.Label(root, text=name).grid(row=i, column=0, stick='ws')
    
    # Define states for the different variables:
    specState  = tk.IntVar()     # Define a int to keep track of state
    subState   = tk.IntVar()
    metalState = tk.IntVar()
    specState.set(0)            # Set the first radio button to be ticked
    subState.set(0)
    metalState.set(0)
    subButtons = []
    metalButtons = []           # List of actual radio button objects
    # Define the radio buttons:
    # We define the subtype buttons first because we need the subButtons done so callback_radioSpec() knows which buttons it should turn off at what time.
    for ind, metal in enumerate(metalType):
        metalButtons.append(ttk.Radiobutton(root, text=metal, variable=metalState, value=ind))
        metalButtons[-1].grid(row=2, column=ind+1, sticky='nsew')
    for ind, sub in enumerate(subType):
        subButtons.append(ttk.Radiobutton(root, text=sub, variable=subState, value=ind))
        subButtons[-1].grid(row=1, column=ind+1, sticky='nsew')
    for ind, spec in enumerate(specType):
        ttk.Radiobutton(root, text=spec, variable=specState, value=ind, command= lambda: callback_radioSpec(specState, subState, subButtons)).grid(row=0, column=ind+1, sticky='nsew')
    
    # Define the buttons for interacting with the data (e.g., flag it, done, back):
    ttk.Button(root, text='Odd', underline=0, command=callback_odd).grid(row=5, column=1, columnspan=2, sticky='nsew')
    ttk.Button(root, text='Bad', underline=0, command=callback_bad).grid(row=5, column=3, columnspan=2, sticky='nsew')
    ttk.Button(root, text='Smooth', underline=0, command=callback_smooth).grid(row=5, column=5, columnspan=2, sticky='nsew')
    ttk.Button(root, text='Done', command=callback_done).grid(row=5, column=7, columnspan=2, sticky='nsew')
    ttk.Button(root, text='Back', underline=3, command=callback_back).grid(row=5, column=9, columnspan=2, sticky='nsew')
    ttk.Button(root, text='Earlier', command= lambda: callback_earlier(specState, subState)).grid(row=3, column=1, columnspan=5, sticky='nsew', pady=(10,0))
    ttk.Button(root, text='Later', command= lambda: callback_later(specState, subState)).grid(row=3, column=6, columnspan=5, sticky='nsew', pady=(10,0))
    ttk.Button(root, text='Lower', command= lambda: callback_lower(specState, subState)).grid(row=4, column=1, columnspan=5, sticky='nsew')
    ttk.Button(root, text='Higher', command= lambda: callback_higher(specState, subState)).grid(row=4, column=6, columnspan=5, sticky='nsew')
    
    #root.geometry('500x300')
    ### DUMMY CODE ###
    root.bind('o', lambda event: callback_odd())
    root.bind('b', lambda event: callback_bad())
    root.bind('s', lambda event: callback_smooth())
    root.bind('<Return>', lambda event: callback_done())
    root.bind('k', lambda event: callback_back())
    root.bind('<Left>', lambda event, specstate=specState, substate=subState: callback_earlier(specstate, substate))
    root.bind('<Right>', lambda event, specstate=specState, substate=subState: callback_later(specstate, substate))
    root.bind('<Down>', lambda event, specstate=specState, substate=subState: callback_lower(specstate, substate))
    root.bind('<Up>', lambda event, specstate=specState, substate=subState: callback_higher(specstate, substate))
    root.mainloop() 
