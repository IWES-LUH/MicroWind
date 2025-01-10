"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import tkinter as TK
import tkinter.ttk as ttk


class GameOverWindow:
    """Game over window for arcade game
    Starts the game over window for name input
    """

    def __init__(self, handler):
        # CONSTANTS
        self.UNI_BLUE = '#2155CD'
        self.LIGHT_BLUE = '#99d9ea'
        self.GRAY_BLUE = '#7092be'
        self.GREEN = '#22b14c'
        self.LIGHT_GREEN = '#b5e61d'
        self.RED = '#ed1c24'
        self.BACKGROUND = self.GRAY_BLUE

        # Handles
        self.handler = handler

        # Variables
        self.letter = 0

        # Initialize and configure window
        self.window = TK.Tk()
        self.window.title("MicroWind Arcade, Leibniz Universität Hannover, Institut für Windenergiesysteme")
        self.window.config(padx=50, pady=50, bg=self.BACKGROUND)
        self.window.geometry('1000x800+460+140')
        self.window.attributes("-topmost", True)
        self.window.overrideredirect(True)

        self.window.tk.call('source', 'modules/gui/arcade_theme/arcade.tcl')
        style = ttk.Style(self.window)
        style.theme_use('arcade')
        style.configure('TButton', font=('FixedSys', 22))
        style.configure('TButton', foreground='black')
        style.configure('TLabelframe', background=self.BACKGROUND)
        style.configure('TLabelframe.Label', background=self.BACKGROUND)
        style.configure('TLabelframe.Label', font=('FixedSys', 22))

        # Fill window
        name = TK.StringVar()
        score = int(self.handler.score)
        TK.Label(self.window, text="Congratulations!", font='FixedSys 40',
                 bg=self.BACKGROUND, fg='white').pack(side='top')
        TK.Label(self.window, text="You genenerated", font='FixedSys 20',
                 bg=self.BACKGROUND, fg=self.LIGHT_GREEN).pack(side='top')
        TK.Label(self.window, text=str(score)+' mWs', font='FixedSys 40',
                 bg=self.BACKGROUND, fg='white').pack(side='top')
        TK.Label(self.window, text="of clean energy", font='FixedSys 20',
                 bg=self.BACKGROUND, fg=self.LIGHT_GREEN).pack(side='top')
        TK.Label(self.window, text=" ", font='FixedSys 20',
                 bg=self.BACKGROUND, fg=self.LIGHT_GREEN).pack(side='top')
        TK.Label(self.window, text="Please enter your name", font='FixedSys 20',
                 bg=self.BACKGROUND, fg='white').pack(side='top', pady=15)
        self.entry_name = ttk.Entry(self.window, textvariable=name, font='FixedSys 20')
        self.entry_name.pack(side='top', padx=10, pady=10)

        # Play again button
        def play_again():
            self.handler.add_entry(self.entry_name.get(), score)
            self.handler.arcade_window.fill_score_table()
            self.window.destroy()
            self.handler.arcade_window.window.attributes('-topmost', True)
            self.handler.idle()

            print(name.get())

        self.button_play_again = ttk.Button(self.window, text="Enter", command=play_again, width=10)
        self.button_play_again.pack(side='top', padx=10, pady=30)

        # Keyboard
        self.frame_keyboard = TK.Frame(self.window, background=self.GRAY_BLUE)
        self.frame_keyboard.pack(side='top')

        keys = [['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '<-'],
                ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '*'],
                ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', '+', '#'],
                ['Z', 'X', 'C', 'V', 'B', 'N', 'M', '>', '<', '_', ' ']]

        def key_clicked(key_c):
            if key_c == '<-':
                # Remove letter
                if self.letter >= 1:
                    self.letter -= 1
                    self.entry_name.delete(self.letter)
            else:
                if self.letter <= 19:
                    # Append letter
                    self.letter += 1
                    self.entry_name.insert(self.letter, str(key_c))

        # Keyboard buttons
        for i, key_row in enumerate(keys):
            for j, key in enumerate(key_row):
                button_key = ttk.Button(self.frame_keyboard, text=key,
                                        command=lambda value=key: key_clicked(value), width=3)
                button_key.grid(row=i, column=j, padx=5, pady=5)


