"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

from PIL import ImageTk


class GameOver:
    """GameOver graphics object
    Stores and manipulates graphics data"""

    def __init__(self, canvas):
        # Handles
        self.canvas = canvas

        # Variables
        self.state = 1
        self.count = 0

        # Images
        self.IMG_GO1 = ImageTk.PhotoImage(file='modules/gui/imgs/GO1.png', master=self.canvas)
        self.IMG_ID_GO1 = self.canvas.create_image(700, 250, image=self.IMG_GO1)
        self.IMG_GO2 = ImageTk.PhotoImage(file='modules/gui/imgs/GO2.png', master=self.canvas)
        self.IMG_ID_GO2 = self.canvas.create_image(700, 250, image=self.IMG_GO2)
        self.IMG_GO3 = ImageTk.PhotoImage(file='modules/gui/imgs/GO3.png', master=self.canvas)
        self.IMG_ID_GO3 = self.canvas.create_image(700, 250, image=self.IMG_GO3)

        self.hide()

    def show(self):
        if self.count == 10:
            if self.state == 0:
                self.canvas.itemconfig(self.IMG_ID_GO1, state='normal')
                self.canvas.itemconfig(self.IMG_ID_GO2, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GO3, state='hidden')
                self.state = 1
            elif self.state == 1:
                self.canvas.itemconfig(self.IMG_ID_GO1, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GO2, state='normal')
                self.canvas.itemconfig(self.IMG_ID_GO3, state='hidden')
                self.state = 2
            elif self.state == 2:
                self.canvas.itemconfig(self.IMG_ID_GO1, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GO2, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GO3, state='normal')
                self.state = 0
            self.count = 0
        self.count += 1

    def hide(self):
        self.canvas.itemconfig(self.IMG_ID_GO1, state='hidden')
        self.canvas.itemconfig(self.IMG_ID_GO2, state='hidden')
        self.canvas.itemconfig(self.IMG_ID_GO3, state='hidden')
