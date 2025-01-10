"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

from PIL import ImageTk


class Turbine:
    """Turbine graphics object
    Stores and manipulates graphics data of the turbine"""

    def __init__(self, canvas, data_arcade):
        # Handles
        self.canvas = canvas
        self.data_arcade = data_arcade

        # Variables
        self.turbine_count = 0
        self.turbine_state = 0

        # Images
        self.IMG_blade_top = ImageTk.PhotoImage(file='modules/gui/imgs/blade_top.png', master=self.canvas)
        self.IMG_ID_blade_top = self.canvas.create_image(175, 101, image=self.IMG_blade_top)
        self.IMG_blade_bot = ImageTk.PhotoImage(file='modules/gui/imgs/blade_bot.png', master=self.canvas)
        self.IMG_ID_blade_bot = self.canvas.create_image(175, 293, image=self.IMG_blade_bot)
        self.IMG_blade_h_top = ImageTk.PhotoImage(file='modules/gui/imgs/blade_h_top.png', master=self.canvas)
        self.IMG_ID_blade_h_top = self.canvas.create_image(175, 125, image=self.IMG_blade_h_top)
        self.IMG_blade_h_bot = ImageTk.PhotoImage(file='modules/gui/imgs/blade_h_bot.png', master=self.canvas)
        self.IMG_ID_blade_h_bot = self.canvas.create_image(175, 270, image=self.IMG_blade_h_bot)
        self.IMG_blade_cent = ImageTk.PhotoImage(file='modules/gui/imgs/blade_cent.png', master=self.canvas)
        self.IMG_ID_blade_cent = self.canvas.create_image(175, 200, image=self.IMG_blade_cent)

    def rotate(self):
        if self.turbine_count >= self.data_arcade.next_rotation:
            if self.turbine_state == 0:
                self.canvas.itemconfig(self.IMG_ID_blade_top, state='normal')
                self.canvas.itemconfig(self.IMG_ID_blade_h_top, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_blade_cent, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_blade_h_bot, state='normal')
                self.canvas.itemconfig(self.IMG_ID_blade_bot, state='hidden')
                self.turbine_state += 1
            elif self.turbine_state == 1:
                self.canvas.itemconfig(self.IMG_ID_blade_top, state='normal')
                self.canvas.itemconfig(self.IMG_ID_blade_h_top, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_blade_cent, state='normal')
                self.canvas.itemconfig(self.IMG_ID_blade_h_bot, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_blade_bot, state='normal')
                self.turbine_state += 1
            elif self.turbine_state == 2:
                self.canvas.itemconfig(self.IMG_ID_blade_top, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_blade_h_top, state='normal')
                self.canvas.itemconfig(self.IMG_ID_blade_cent, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_blade_h_bot, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_blade_bot, state='normal')
                self.turbine_state += 1
            elif self.turbine_state == 3:
                self.canvas.itemconfig(self.IMG_ID_blade_top, state='normal')
                self.canvas.itemconfig(self.IMG_ID_blade_h_top, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_blade_cent, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_blade_h_bot, state='hidden')
                self.canvas.itemconfig(self.IMG_ID_blade_bot, state='normal')
                self.turbine_state = 0
            self.turbine_count = 0
        self.turbine_count += 2
