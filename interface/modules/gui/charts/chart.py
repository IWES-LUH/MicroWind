"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import tkinter as TK
import numpy as np
import interface.modules.gui.gui_colors as color


class Chart:
    """Chart master
    Class for initializing a chart drawn with tkinter.
    Contains functions for resizing and calculating pixel locations on canvas based on chart values"""

    def __init__(self, canvas, name, x_label, y_label, x_left, x_right, y_bottom, y_top, x_grid, y_grid, legend=False):
        self.L = 90  # Axes distance to frame
        self.R = 30
        self.T = 10
        self.B = 60
        self.LABEL_DIST_Y = 50  # Label distance to axes
        self.LABEL_DIST_X = 35  # Label distance to axes
        self.TICK_DIST = 5
        self.TICK_LENGTH = 5

        self.x_left = x_left
        self.x_right = x_right
        self.y_bottom = y_bottom
        self.y_top = y_top
        self.x_grid = x_grid
        self.y_grid = y_grid

        self.canvas = canvas
        self.name = name
        self.width = self.canvas.winfo_width()
        self.height = self.canvas.winfo_height()

        self.active = True

        if legend:
            self.frame_legend = TK.Frame(self.canvas, bd=2, relief='groove')
            self.frame_legend_id = self.canvas.create_window((100, 100), window=self.frame_legend)

        # Initialize lines and labels. Positions will be set at first resize command
        # Axes and labels
        self.axes = self.canvas.create_rectangle(1, 1, 1, 1, outline=color.COLOR_AXES, width=1)
        self.x_label = self.canvas.create_text((self.width-1, self.height-1), text=x_label, anchor='e',
                                               font='TkDefaultFont 14 bold', fill=color.COLOR_LABELS)
        self.y_label = self.canvas.create_text((1, 1), text=y_label, anchor='e',
                                               font='TkDefaultFont 14 bold', angle=90, fill=color.COLOR_LABELS)

        # Grid and ticks
        self.x_ticks = []
        self.x_tick_labels = []
        for i in range(len(self.x_grid)):
            if not i == 0 or not i == len(self.x_grid) - 1:
                self.x_ticks.append(self.canvas.create_line(1, 1, 1, 1, fill=color.COLOR_AXES))
            self.x_tick_labels.append(self.canvas.create_text(1, 1, text=str(self.x_grid[i]), anchor='n',
                                                              font='TkDefaultFont 10', fill=color.COLOR_TEXT_SMALL))

        self.y_ticks = []
        self.y_tick_labels = []
        for i in range(len(self.y_grid)):
            if not i == 0 or not i == len(self.y_grid) - 1:
                self.y_ticks.append(self.canvas.create_line(1, 1, 1, 1, fill=color.COLOR_AXES))
            self.y_tick_labels.append(self.canvas.create_text(1, 1, text=str(self.y_grid[i]), anchor='e',
                                                              font='TkDefaultFont 10', fill=color.COLOR_TEXT_SMALL))

    def resize_axes(self):

        # Axes and labels
        self.canvas.coords(self.axes, self.L, self.T, self.width - self.R, self.height - self.B)
        self.canvas.coords(self.x_label, self.width-self.R, self.height-self.B+self.LABEL_DIST_X)
        self.canvas.coords(self.y_label, self.L-self.LABEL_DIST_Y, self.T)

        # Grid and ticks
        for i in range(len(self.x_grid)):
            if max(self.x_right, self.x_left) >= self.x_grid[i] >= min(self.x_right, self.x_left):
                self.canvas.coords(self.x_ticks[i],
                                   self.x_to_pos(self.x_grid[i]), self.height - self.B - self.TICK_LENGTH,
                                   self.x_to_pos(self.x_grid[i]), self.height - self.B)
                self.canvas.coords(self.x_tick_labels[i], self.x_to_pos(self.x_grid[i]),
                                   self.height - self.B + self.TICK_DIST)
                self.canvas.itemconfig(self.x_ticks[i], state='normal')
                self.canvas.itemconfig(self.x_tick_labels[i], state='normal')
            else:
                self.canvas.itemconfig(self.x_ticks[i], state='hidden')
                self.canvas.itemconfig(self.x_tick_labels[i], state='hidden')

        for i in range(len(self.y_grid)):
            if max(self.y_top, self.y_bottom) >= self.y_grid[i] >= min(self.y_top, self.y_bottom):
                self.canvas.coords(self.y_ticks[i],
                                   self.L, self.y_to_pos(self.y_grid[i]),
                                   self.L + self.TICK_LENGTH, self.y_to_pos(self.y_grid[i]))
                self.canvas.coords(self.y_tick_labels[i], self.L - self.TICK_DIST, self.y_to_pos(self.y_grid[i]))
                self.canvas.itemconfig(self.y_ticks[i], state='normal')
                self.canvas.itemconfig(self.y_tick_labels[i], state='normal')
            else:
                self.canvas.itemconfig(self.y_ticks[i], state='hidden')
                self.canvas.itemconfig(self.y_tick_labels[i], state='hidden')

    def x_to_pos(self, x):
        x_pos = self.L + (self.width - self.L - self.R) / (self.x_right - self.x_left) * (x - self.x_left)

        if isinstance(x, np.ndarray):
            x_pos[x_pos < self.L - 1] = -1
            x_pos[x_pos > self.width-self.R] = -1
            return x_pos
        else:
            if x_pos < self.L - 1 or x_pos > self.width-self.R:
                return -1
            else:
                return x_pos

    def y_to_pos(self, y):
        y_pos = self.height - self.B - (self.height - self.T - self.B) \
                / (self.y_top - self.y_bottom) * (y - self.y_bottom)

        if isinstance(y, np.ndarray):
            y_pos[y_pos < self.T - 1] = -1
            y_pos[y_pos > self.height-self.B] = -1
            return y_pos
        else:
            if y_pos < self.T - 1 or y_pos > self.height-self.B:
                return -1
            else:
                return y_pos
