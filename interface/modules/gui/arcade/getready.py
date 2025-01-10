"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

from PIL import ImageTk
import time


class GetReady:
    """GetReady graphics object
    Stores and manipulates graphics data"""

    def __init__(self, canvas):
        # Handles
        self.canvas = canvas

        # Variables
        self.time = time.time()
        self.state = 0

        # Images
        self.IMG_GR1 = ImageTk.PhotoImage(file='modules/gui/imgs/GR1.png', master=self.canvas)
        self.IMG_ID_GR1 = self.canvas.create_image(700, 250, image=self.IMG_GR1)
        self.IMG_GR2 = ImageTk.PhotoImage(file='modules/gui/imgs/GR2.png', master=self.canvas)
        self.IMG_ID_GR2 = self.canvas.create_image(700, 250, image=self.IMG_GR2)
        self.IMG_GR3 = ImageTk.PhotoImage(file='modules/gui/imgs/GR3.png', master=self.canvas)
        self.IMG_ID_GR3 = self.canvas.create_image(700, 250, image=self.IMG_GR3)
        self.IMG_GR4 = ImageTk.PhotoImage(file='modules/gui/imgs/GR4.png', master=self.canvas)
        self.IMG_ID_GR4 = self.canvas.create_image(700, 250, image=self.IMG_GR4)

        self.hide()

    def show(self):
        if time.time() - self.time > 1:
            self.time = time.time()
            if self.state == 0:
                self.canvas.itemconfig(self.IMG_ID_GR1, state='normal')
                self.canvas.itemconfig(self.IMG_ID_GR2, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GR3, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GR4, state='hidden')
                self.state = 1
            elif self.state == 1:
                self.canvas.itemconfig(self.IMG_ID_GR1, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GR2, state='normal')
                self.canvas.itemconfig(self.IMG_ID_GR3, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GR4, state='hidden')
                self.state = 2
            elif self.state == 2:
                self.canvas.itemconfig(self.IMG_ID_GR1, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GR2, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GR3, state='normal')
                self.canvas.itemconfig(self.IMG_ID_GR4, state='hidden')
                self.state = 3
            elif self.state == 3:
                self.canvas.itemconfig(self.IMG_ID_GR1, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GR2, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GR3, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_GR4, state='normal')
                self.state = 0

    def hide(self):
        self.canvas.itemconfig(self.IMG_ID_GR1, state='hidden')
        self.canvas.itemconfig(self.IMG_ID_GR2, state='hidden')
        self.canvas.itemconfig(self.IMG_ID_GR3, state='hidden')
        self.canvas.itemconfig(self.IMG_ID_GR4, state='hidden')

        self.state = 0
