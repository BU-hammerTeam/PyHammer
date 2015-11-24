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


def keyPressed(event):
    """
    This function is bound to the root window of this GUI and
    is called when a key is pressed while the window is in focus.
    """
    
    # Pull out the character that was pressed
    char = event.char

    # Set up an if-elif statement to respond to different key presses

    # Example
    # if (char == 'q'):
    #    print('You pressed q')
    # elif(char == 'e'):
    #    print('You pressed e')

def main():

    # Set up the root window
    root = tk.Tk()
    root.title('PyHammer')
    root.iconbitmap(r'resources\sun.ico')
    root.resizable(False, False)
    root.geometry('+100+100')
    root.bind_all('<Key>', keyPressed)
    
    # Define some useful quantities and variables
    specType = np.array(['O', 'B', 'A', 'F', 'G', 'K', 'M', 'L', 'T', 'Y'])
    subType = np.array(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

    ### DUMMY CODE ###
    ttk.Label(text = 'A dummy label').pack()
    root.geometry('500x300')
    ### DUMMY CODE ###
    
    root.mainloop() 
