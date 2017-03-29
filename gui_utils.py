from pyhamimports import *


class MessageBox(QMessageBox):

    def __init__(self, parent, text, title = 'PyHammer', buttons = QMessageBox.Ok, details = None, fontFamily = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setText(text)
        self.setStandardButtons(buttons)
        if details is not None:
            self.setDetailedText(details)
        if fontFamily is not None:
            font = self.font()
            font.setFamily(fontFamily)
            self.setFont(font)

        self.reply = self.exec_()


class OptionWindow(QDialog):

    def __init__(self, parent, choices, title = 'PyHammer', instruction = 'Pick a choice'):
        super().__init__(parent)
        self.setWindowTitle(title)

        # *** Setup and layout the GUI ***
        
        grid = QGridLayout()

        # Add the instruction label at the top of the window
        self.instruction = instruction
        self.instructionLabel = QLabel(self.instruction, alignment = Qt.AlignCenter)
        grid.addWidget(self.instructionLabel, 0, 0, 1, 2)

        # Define a radio button and label choice for each of the
        # users input choices
        self.radioButton = []
        for i, c in enumerate(choices):
            self.radioButton.append(QRadioButton(''))
            grid.addWidget(self.radioButton[-1], i+1, 0)
            grid.addWidget(QLabel(c), i+1, 1)
            if i == 0:
                self.radioButton[0].setChecked(True)

        # Define a special radio button accompanied by
        # a text edit field so they can supply a custom
        # choice
        self.radioButton.append(QRadioButton(''))
        grid.addWidget(self.radioButton[-1], i+2, 0)
        self.custom = QLineEdit(placeholderText = 'Custom...')
        self.custom.setMinimumWidth(150)
        self.custom.textEdited.connect(lambda: self.radioButton[-1].setChecked(True))
        grid.addWidget(self.custom, i+2, 1)

        # Provide the okay button at the bottom and
        # connect it to the QDialog done method, which
        # we override to first get the selected choice
        ok = QPushButton('Ok')
        ok.clicked.connect(self.done)
        grid.addWidget(ok, i+3, 0, 1, 2)

        # Set the current grid layout as the main window
        # layout and set the window to be fixed to the
        # grid size
        self.setLayout(grid)
        self.setFixedSize(grid.minimumSize())

        # Create some variables
        choices.append('')
        self.choices = choices
        self.choice = None

        # Run the GUI
        self.exec_()

    def done(self, i):
        """Overrides the QDialog done method to first store which choice the user selected"""
        self.choices[-1] = self.custom.text()
        for r, c in zip(self.radioButton,self.choices):
            if r.isChecked():
                self.choice = c
                break

        if r is self.radioButton[-1] and self.choice == '':
            self.instructionLabel.setText('Enter Text for Custom Name')
            QApplication.beep() # Use the system error beep to indicate a problem
            QTimer.singleShot(1500, lambda: self.instructionLabel.setText(self.instruction))
            return

        super().done(i)

    def closeEvent(self, event):
        super().close()
