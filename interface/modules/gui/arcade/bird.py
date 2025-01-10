"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

from PIL import ImageTk


class Bird:
    """Bird graphics object
    Stores and manipulates graphics data of the bird"""

    def __init__(self, canvas, data_arcade):
        # CONSTANTS
        self.POS_Y = 250

        # Handles
        self.canvas = canvas
        self.data_arcade = data_arcade

        # Variables
        pos_x = self.data_arcade.bird_pos
        self.wing_position = 0
        self.wing_count = 0

        self.speed = self.data_arcade.BIRD_SPEED

        # Images
        self.sprite_top = ImageTk.PhotoImage(file='modules/gui/imgs/bird_top.png', master=self.canvas)
        self.sprite_mid = ImageTk.PhotoImage(file='modules/gui/imgs/bird_mid.png', master=self.canvas)
        self.sprite_bot = ImageTk.PhotoImage(file='modules/gui/imgs/bird_bot.png', master=self.canvas)
        self.sprite_GO = ImageTk.PhotoImage(file='modules/gui/imgs/bird_GO.png', master=self.canvas)
        self.bird_top = self.canvas.create_image(pos_x, self.POS_Y-14, image=self.sprite_top)
        self.bird_mid = self.canvas.create_image(pos_x, self.POS_Y, image=self.sprite_mid)
        self.bird_bot = self.canvas.create_image(pos_x, self.POS_Y+10, image=self.sprite_bot)
        self.bird_GO = self.canvas.create_image(pos_x, self.POS_Y+10, image=self.sprite_GO)
        self.canvas.itemconfig(self.bird_GO, state='hidden')

    def move(self):
        self.data_arcade.bird_pos -= self.data_arcade.BIRD_SPEED
        if self.data_arcade.bird_pos < -100:
            self.reset()

        self.canvas.move(self.bird_top, -self.speed, 0)
        self.canvas.move(self.bird_mid, -self.speed, 0)
        self.canvas.move(self.bird_bot, -self.speed, 0)
        self.canvas.move(self.bird_GO, -self.speed, 0)

        self.wing_count += 1

        if self.wing_count == 10:
            if self.wing_position == 0:
                self.canvas.itemconfig(self.bird_top, state='normal')
                self.canvas.itemconfig(self.bird_mid, state='hidden')
                self.canvas.itemconfig(self.bird_bot, state='hidden')
                self.wing_position += 1
            elif self.wing_position == 1:
                self.canvas.itemconfig(self.bird_top, state='hidden')
                self.canvas.itemconfig(self.bird_mid, state='normal')
                self.canvas.itemconfig(self.bird_bot, state='hidden')
                self.wing_position += 1
            elif self.wing_position == 2:
                self.canvas.itemconfig(self.bird_top, state='hidden')
                self.canvas.itemconfig(self.bird_mid, state='hidden')
                self.canvas.itemconfig(self.bird_bot, state='normal')
                self.wing_position += 1
            elif self.wing_position == 3:
                self.canvas.itemconfig(self.bird_top, state='hidden')
                self.canvas.itemconfig(self.bird_mid, state='normal')
                self.canvas.itemconfig(self.bird_bot, state='hidden')
                self.wing_position = 0

            self.wing_count = 0

    def hit(self):
        self.canvas.itemconfig(self.bird_top, state='hidden')
        self.canvas.itemconfig(self.bird_mid, state='hidden')
        self.canvas.itemconfig(self.bird_bot, state='hidden')
        self.canvas.itemconfig(self.bird_GO, state='normal')

    def reset(self):
        self.canvas.itemconfig(self.bird_GO, state='hidden')
        pos_x = self.data_arcade.BIRD_START - self.data_arcade.bird_pos
        self.canvas.move(self.bird_top, pos_x, 0)
        self.canvas.move(self.bird_mid, pos_x, 0)
        self.canvas.move(self.bird_bot, pos_x, 0)
        self.canvas.move(self.bird_GO, pos_x, 0)
        self.data_arcade.bird_pos = self.data_arcade.BIRD_START
