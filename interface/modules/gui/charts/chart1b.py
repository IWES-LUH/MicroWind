"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import numpy as np
from interface.modules.gui.charts.chart1 import Chart1
from interface.modules.gui.charts.anti_aliasing_line import AntiAliasingLine
import interface.modules.gui.gui_colors as color


class Chart1b(Chart1):
    """Chart1b c_p lambda
    Chart to display power coefiicient vs tip speed ratio in the bottom left area"""

    def __init__(self, canvas):
        super().__init__(canvas,
                         name='cp_tsr_0_deg',
                         x_label="Tip speed ratio",
                         y_label="Power coefficient",
                         x_left=0,
                         x_right=8,
                         y_bottom=0,
                         y_top=0.15,
                         x_grid=[0, 1, 2, 3, 4, 5, 6, 7, 8],
                         y_grid=[0, 0.025, 0.05, 0.075, 0.1, 0.125, 0.15])

        self.CP_CORRECTION_FACTOR = 1/1.4

        self.cp_tsr_0_deg_coordinates = np.loadtxt('data/cp_tsr_0_deg.txt', skiprows=0, dtype=float)
        self.cp_tsr_0_deg_coordinates[:, 1] *= self.CP_CORRECTION_FACTOR
        self.cp_tsr_5_deg_coordinates = np.loadtxt('data/cp_tsr_5_deg.txt', skiprows=0, dtype=float)
        self.cp_tsr_5_deg_coordinates[:, 1] *= self.CP_CORRECTION_FACTOR

        self.cp_tsr_0_deg = AntiAliasingLine(self.canvas, length=len(self.cp_tsr_0_deg_coordinates[:, 0]),
                                             color=color.GRAY, width=self.LINE_WIDTH, smooth=True)
        self.cp_tsr_5_deg = AntiAliasingLine(self.canvas, length=len(self.cp_tsr_5_deg_coordinates[:, 0]),
                                             color=color.LIGHT_GRAY, width=self.LINE_WIDTH, smooth=True)

        self.beta_label_0_deg = self.canvas.create_text((1, 1), text='beta = 0°', anchor='w',
                                                        font='TkDefaultFont 10 bold', fill=color.GRAY)
        self.beta_label_5_deg = self.canvas.create_text((1, 1), text='beta = 5°', anchor='e',
                                                        font='TkDefaultFont 10 bold', fill=color.LIGHT_GRAY)

    def update(self, data, force_resize=False):
        # Check if chart needs resizing
        if not self.width == self.canvas.winfo_width() \
                or not self.height == self.canvas.winfo_height()\
                or force_resize:
            self.width = self.canvas.winfo_width()
            self.height = self.canvas.winfo_height()
            self.resize_axes()
            self.resize_dots()
            self.resize_specific()

        self.update_dots(data)

    def resize_specific(self):
        x_pos = self.x_to_pos(self.cp_tsr_0_deg_coordinates[:, 0])
        y_pos = self.y_to_pos(self.cp_tsr_0_deg_coordinates[:, 1])
        t = tuple(np.stack((x_pos, y_pos)).flatten('F'))
        self.cp_tsr_0_deg.update_coordinates(t)
        self.canvas.coords(self.beta_label_0_deg, x_pos[0]+10, y_pos[0])

        x_pos = self.x_to_pos(self.cp_tsr_5_deg_coordinates[:, 0])
        y_pos = self.y_to_pos(self.cp_tsr_5_deg_coordinates[:, 1])
        t = tuple(np.stack((x_pos, y_pos)).flatten('F'))
        self.cp_tsr_5_deg.update_coordinates(t)
        self.cp_tsr_5_deg.update_coordinates(t)
        self.canvas.coords(self.beta_label_5_deg, x_pos[0]+10, y_pos[0]-20)
