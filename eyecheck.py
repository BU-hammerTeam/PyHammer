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


def keyPressed(event, specState, subState):
    """
    This function is bound to the root window of this GUI and
    is called when a key is pressed while the window is in focus.
    """
    
    # Pull out the character that was pressed
    char = event.char

    # Set up an if-elif statement to respond to different key presses
    if (char == '\x1b[D'):
        callback_earlier(specState, subState)
    elif (char == '\x1b[C'):
        callback_later(specState, subState)
    # Example
    # if (char == 'q'):
    #    print('You pressed q')
    # elif(char == 'e'):
    #    print('You pressed e')
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

def callback_radioSpec(specState, subState, subButts):
    if specState.get() == 5:
        subButts[-1].configure(state='disabled')
        subButts[-2].configure(state='disabled')
        if subState.get() == 8 or subState.get() == 9:
            subState.set(7)
    else:
        subButts[-1].configure(state='normal')
        subButts[-2].configure(state='normal')
    
def main():

    # Set up the root window
    root = tk.Tk()
    root.title('PyHammer Plot Options')
    root.iconbitmap(r'resources\sun.ico')
    root.resizable(False, False)
    root.geometry('+100+100')
    
    # Define some useful quantities and variables
    specType   = np.array(['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'T', 'Y'])
    subType    = np.array(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

    ### DUMMY CODE ###
    specState  = tk.IntVar()     # Define a int to keep track of state
    subState   = tk.IntVar()
    specState.set(0)            # Set the first radio button to be ticked
    subState.set(0)
    subButtons = []
    # Define the radio buttons:
    for ind, sub in enumerate(subType):
        subButtons.append(ttk.Radiobutton(root, text=sub, variable=subState, value=ind))
        subButtons[-1].grid(row=1, column=ind, sticky='nsew')
    for ind, spec in enumerate(specType):
        ttk.Radiobutton(root, text=spec, variable=specState, value=ind, command= lambda: callback_radioSpec(specState, subState, subButtons)).grid(row=0, column=ind, sticky='nsew')
    
    # Define the buttons for interacting with the data (e.g., flag it, done, back):
    ttk.Button(root, text='Odd', command=callback_odd).grid(row=2, column=0, columnspan=2, sticky='nsew')
    ttk.Button(root, text='Bad', command=callback_bad).grid(row=2, column=2, columnspan=2, sticky='nsew')
    ttk.Button(root, text='Smooth', command=callback_smooth).grid(row=2, column=4, columnspan=2, sticky='nsew')
    ttk.Button(root, text='Done', command=callback_done).grid(row=2, column=6, columnspan=2, sticky='nsew')
    ttk.Button(root, text='Back', command=callback_back).grid(row=2, column=8, columnspan=2, sticky='nsew')
    ttk.Button(root, text='Earlier', command= lambda: callback_earlier(specState, subState)).grid(row=3, column=0, columnspan=5, sticky='nsew')
    ttk.Button(root, text='Later', command= lambda: callback_later(specState, subState)).grid(row=3, column=5, columnspan=5, sticky='nsew')
    
    #root.geometry('500x300')
    ### DUMMY CODE ###
    
    root.bind_all('<Key>', lambda event, specstate=specState, substate=subState: keyPressed(event, specstate, substate))
    root.mainloop() 
