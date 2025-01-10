"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import random
from PIL import ImageTk


class Cloud:
    """Cloud graphics object
    Stores and manipulates graphics data of the cloud"""

    def __init__(self, canvas, data):
        # Handles
        self.canvas = canvas
        self.data = data

        # Variables
        self.w = self.canvas.winfo_width()
        self.h = round(self.canvas.winfo_height()/2)
        self.pos_x = random.randint(0, self.w)
        self.pos_y = random.randint(0, self.h)
        self.speed = 4 + int(self.data.v_set*2) - round(1+3*self.pos_y/self.h)
        self.speed_rand = random.randint(1, 3)

        # Image
        self.sprite = ImageTk.PhotoImage(file='modules/gui/imgs/cloud.png', master=self.canvas)
        self.cloud = self.canvas.create_image(self.pos_x, self.pos_y, image=self.sprite)

    def move(self):
        self.speed = 4 + int(self.data.v_set*2) - round(1+3*self.pos_y/self.h)
        if self.pos_x <= -100:
            self.speed_rand = random.randint(1, 3)
            self.canvas.move(self.cloud, self.w+200, 0)
            self.pos_x += self.w+200

        self.canvas.move(self.cloud, -self.speed-self.speed_rand, 0)
        self.pos_x -= self.speed+self.speed_rand
