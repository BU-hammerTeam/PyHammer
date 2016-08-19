import tkinter as tk
from tkinter import ttk
import os

###
# This module defines several useful classes that create basic GUI components used
# used throughout the PyHammer interface. Defined are are GUIs for opening an info
# window to inform the user of information, a modal window for asking a yes/no
# question, an option window for asking the user to pick a choice, and a tooltip
# class to creating tooltips that are bound to widgets.
#


class InfoWindow(object):
    """
    Description:
        This brings up a new window derived from root
        that displays info and has a button to close
        the window when user is done. This optionally can
        display the multiple sets of text in multiple tabs
        so as to not have a huge, long window and to keep
        the information more organized.
        
    Input:
        args: This will be a set of arguments supplying what should be
            put into the info window. If the user wants a basic window
            with simple text, then just supply a string with that text.
            However, the user can also specify multiple arguments where
            each argument will be its own tab in a notebook on the window.
            Each argument in this case should be a tuple containing first
            the name that will appear on the tab, and second, the text to
            appear inside the tab.
        parent: The root window to potentially derive this one from. If
            nothing is provided, this will create a new window from scratch.
        title: The title to display on the window
        height: The height of the window, in lines. More height provides a
            taller window.
        width: The width of the window, in characters.
        fontFamily: A valid, specific font family to use, if desired.
            
    Example:
        This brings up a simple GUI with basic text in it. It derives from a
        top level root window named 'root'

        InfoWindow('This is an example\ninfo window.', parent = root, title = 'A GUI title')
        
        This brings up a GUI with multiple tabs and different
        text in each tab. This is not derived from a root.
        
        InfoWindow(('Tab 1', 'Text in tab 1'), ('Tab 2', 'Some more text'), title = 'Title')
        
    """

    def __init__(self, *args, parent = None, title = 'PyHammer', height = 6, width = 50, fontFamily = None):
        # Setup the window
        if parent is None:
            # If no top level was provided, define the window as the top level
            self.infoWindow = tk.Tk()
        else:
            # If a top level was provided, derive a new window from it
            self.infoWindow = tk.Toplevel(parent)
            self.infoWindow.grab_set()  # Make the root window non-interactive
            self.infoWindow.geometry('+%i+%i' % (parent.winfo_rootx(), parent.winfo_rooty()))
        self.infoWindow.title(title)
        self.infoWindow.iconbitmap(os.path.join(os.path.split(__file__)[0],'resources','sun.ico'))
        self.infoWindow.resizable(False, False)

        # Define the window contents
        if len(args) == 1:
            self.defineTab(self.infoWindow, args[0], height, width, fontFamily)
        else:
            notebook = ttk.Notebook(self.infoWindow)
            for a in args:
                tab = tk.Frame(notebook)
                notebook.add(tab, text = a[0])
                self.defineTab(tab, a[1], height, width, fontFamily)
            notebook.pack()
        if parent is None: self.infoWindow.mainloop()

    def defineTab(self, parent, text, height, width, fontFamily):
        # Create the Text widget which displays the text
        content = tk.Text(parent, height = height, width = width, background = parent.cget('background'),
                          relief = tk.FLAT, wrap = tk.WORD, font = '-size 10')
        if fontFamily is not None: content.configure(font = '-family ' + fontFamily +' -size 10')
        content.grid(row = 0, column = 0, padx = 2, pady = 2)
        content.insert(tk.END, text)
        # Create the Scrollbar for the Text widget
        scrollbar = ttk.Scrollbar(parent, command = content.yview)
        scrollbar.grid(row = 0, column = 1, sticky = 'ns')
        # Link the Text widget to the Scrollbar
        content.config(state = tk.DISABLED, yscrollcommand = scrollbar.set)
        # Add the OK button at the bottom for quitting out
        but = ttk.Button(parent, text = 'OK', command = self.infoWindow.destroy)
        but.grid(row = 1, column = 0, columnspan = 2, sticky = 'nsew', padx = 2, pady = 5)
        parent.rowconfigure(1, minsize = 40)


class ModalWindow(object):
    """
    Description:
        This brings up a new window, potentially derived
        from a top level root window that displays a question
        and asks the user to choose yes or no. At the termination
        of this window, one can look at the attribute choice
        to determine which button was pressed by the user. If the
        user X's out without choosing an option, then the choice
        will be equal to None.

    Input:
        text: The question to display to the user.
        parent: The root window to potentially derive this one from. If
            nothing is provided, this will create a new window from scratch.
        title: The title to display on the window. Default is "PyHammer".

    Output:
        choice: The user's choice is recorded in the object's choice variable.
            This variable will be set to either 'yes' if they chose the yes
            button, 'no' if they chose the no button, or None if they
            X'ed out.

    Example:
        To properly use this window, you must create a new object and
        assign it to a variable. This will bring up the window. You
        must then wait for the window to be closed before moving on in
        your code. This can be acheived in a manner similar to the following:

        modal = ModalWindow('Is the answer to this question no?', parent = self.root)
        self.root.wait_window(modal.modalWindow)

        After this, one can inspect modal.choice.

        If you are not deriving this window from a top level window, then
        you do not need the wait_window call and you can simply use:

        modal = ModalWindow('Is the answer to this question no?')
    """

    def __init__(self, text, parent = None, title = 'PyHammer'):
        self.choice = None

        # Setup the window
        if parent is None:
            # If no top level was provided, define the window as the top level
            self.modalWindow = tk.Tk()
        else:
            # If a top level was provided, derive a new window from it
            self.modalWindow = tk.Toplevel(parent)
            self.modalWindow.grab_set() # Make the root window non-interactive
            self.modalWindow.geometry('+%i+%i' % (parent.winfo_rootx(), parent.winfo_rooty()))
        self.modalWindow.title(title)
        self.modalWindow.iconbitmap(os.path.join(os.path.split(__file__)[0],'resources','sun.ico'))
        self.modalWindow.resizable(False, False)

        # Setup the widgets in the window
        label = ttk.Label(self.modalWindow, text = text, font = '-size 10')
        label.grid(row = 0, column = 0, columnspan = 2, padx = 2, pady = 2)
        
        but = ttk.Button(self.modalWindow, text = 'Yes', command = self.choiceYes)
        but.grid(row = 1, column = 0, sticky = 'nsew', padx = 2, pady = 5)

        but = ttk.Button(self.modalWindow, text = 'No', command = self.choiceNo)
        but.grid(row = 1, column = 1, sticky = 'nsew', padx = 2, pady = 5)

        self.modalWindow.rowconfigure(1, minsize = 40)

        if parent is None: self.modalWindow.mainloop()

    def choiceYes(self):
        self.choice = 'yes'
        self.modalWindow.destroy()

    def choiceNo(self):
        self.choice = 'no'
        self.modalWindow.destroy()


class OptionWindow(object):
    """
    Description:
        This brings up a window that allows the user to choose between
        a list of radio button choices, or else enter their own choice
        in an Entry field. Once their choice is made, they hit okay.

    Input:
        choices: A list of strings which contain choices that the user
            can pick from. These will appear as a selection of radio
            buttons.
        parent: A root tkinter frame to derive this frame from. If none
            is provided, then this will become a root frame itself.
        title: The title to display on the window.
        instruction: A label to place at the top of the GUI to instruct
            the user what to do.

    Output:
        name: This will be the object's variable which stores which name
            they chose from the list, including any name they entered
            into the Entry field. This will be equal to None if they
            X'ed out of the window.

    Example:
        To properly use this window, you must create a new object and
        assign it to a variable. This will bring up the window. You
        must then wait for the window to be closed before moving on in
        your code. This can be acheived in a manner similar to the following:

        option = OptionWindow(['Dog', 'Cat', 'Bird'], parent = self.root)
        self.root.wait_window(option.optionWindow)

        After this, one can inspect option.name.

        If you are not deriving this window from a top level window, then
        you do not need the wait_window call and you can simply use:

        option = OptionWindow(['Red', 'Blue', 'Purple'])
    """

    def __init__(self, choices, parent = None, title = 'PyHammer', instruction = 'Pick a choice'):
        self.name = None
        self.choices = choices
        self.instruction = instruction

        # Setup the window
        if parent is None:
            # If no top level was provided, define the window as the top level
            self.optionWindow = tk.Tk()
        else:
            self.optionWindow = tk.Toplevel(parent)
            self.optionWindow.grab_set()   # Make the root window non-interactive
            self.optionWindow.geometry('+%i+%i' % (parent.winfo_rootx(), parent.winfo_rooty()))
        self.optionWindow.title(title)
        self.optionWindow.iconbitmap(os.path.join(os.path.split(__file__)[0],'resources','sun.ico'))
        self.optionWindow.resizable(False, False)

        # Setup some GUI parameters
        self.radioChoice = tk.IntVar(value = 0)
        self.customName = tk.StringVar()
        self.label = tk.StringVar(value = instruction)

        # Setup the widgets in the window
        tk.Label(self.optionWindow, textvariable = self.label, justify = 'center').grid(row = 0, column = 0, columnspan = 2)
        
        # Create the radio buttons for the input choices
        for i, c in enumerate(choices):
            temp = ttk.Radiobutton(self.optionWindow, text = '', variable = self.radioChoice, value = i)
            temp.grid(row = i+1, column = 0, padx = (10,0), sticky = 'nesw')
            
            temp = ttk.Label(self.optionWindow, text = c)
            temp.grid(row = i+1, column = 1, sticky = 'w')

        # Create the radio button and entry field for the user's choice
        temp = ttk.Radiobutton(self.optionWindow, text = '', variable = self.radioChoice, value = i+1)
        temp.grid(row = i+2, column = 0, padx = (10,0), sticky = 'nesw')
        
        temp = ttk.Entry(self.optionWindow, textvariable = self.customName, width = 10)
        temp.grid(row = i+2, column = 1, sticky = 'w')

        # Define the button
        but = ttk.Button(self.optionWindow, text = 'OK', command = self._exit)
        but.grid(row = i+3, column = 0, columnspan = 2, sticky = 'nsew', padx = 2, pady = 5)

        # Configure grid sizes
        self.optionWindow.rowconfigure(i+3, minsize = 40)
        self.optionWindow.columnconfigure(1, minsize = 175)

        if parent is None: self.optionWindow.mainloop()

    def _exit(self):
        """
        Description:
            This is called when the user X's out of the window or
            clicks the OK button in the window. It will check
            what choice they chose and set it as the name then
            destroy the window. It will make sure though, that the
            user has entered text into the Entry field if they
            pick that option.
        """
        if self.radioChoice.get() < len(self.choices):
            self.name = self.choices[self.radioChoice.get()]
        else:
            if self.customName.get() == '':
                # Temporarily change label to inform user of the problem.
                self.label.set('Enter Text for Custom Name')
                self.optionWindow.bell()   # Chime a bell to indicate a problem
                self.optionWindow.after(1500, lambda: self.label.set(self.instruction))
                return
            else:
                self.name = self.customName.get()
        self.optionWindow.destroy()


class ToolTip(object):
    """
    Description:
        This class allows for defining a tool tip which will pop up
        and provide a helpful hint when the user's mouse hovers
        over a given widget.

    Input:
        widget: A tkinter widget such as tk.Button or tk.Entry to
            bind the tool tip to. This will work on ttk widgets as well.
        text: The text to display in the tool tip

    Example:
        button = tk.Button('Button!')
        ToolTip(button, 'Press this!')
    """

    def __init__(self, widget, text, active = True):
        # Bind the widget mouse enter and leave callbacks
        # to the show and hide functions
        widget.bind('<Enter>', lambda event: self.showtip())
        widget.bind('<Leave>', lambda event: self.hidetip())

        # Create the derived Toplevel window and remove any
        # decorations or framing of that window
        self.tipWindow = tk.Toplevel(widget)
        self.tipWindow.wm_overrideredirect(1)
        try:
            # For Mac OS
            self.tipWindow.tk.call('::tk::unsupported::MacWindowStyle',
                                   'style', self.tipWindow._w,
                                   'help', 'noActivates')
        except tk.TclError:
            pass
        
        # Put a label into the window with the provided text
        # specify formatting
        tk.Label(self.tipWindow, text = text, justify = tk.LEFT, background='#FFFFFF',
                 relief = tk.SOLID, borderwidth = 1, font=('tahoma', '8', 'normal')).pack(ipadx = 2)
        self.tipWindow.withdraw()   # Hide the tooltip window initially

        self.widget = widget
        self.active = active

    def showtip(self):
        # Conditions to not show the tooltip
        if not self.active: return
        if str(self.widget.cget('state')) == 'disabled': return
            
        # Get widget position
        self.widget.update_idletasks()
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty()
        w = self.widget.winfo_width()
        h = self.widget.winfo_height()
        # If pointer is inside widget, define tipWindow position and display it
        if ( x <= self.widget.winfo_pointerx() <= x + w and
             y <= self.widget.winfo_pointery() <= y + h):

            self.tipWindow.wm_geometry('+{}+{}'.format(x+min(10,w/2),y+h))
            self.tipWindow.deiconify()

    def hidetip(self):
        self.tipWindow.withdraw()
