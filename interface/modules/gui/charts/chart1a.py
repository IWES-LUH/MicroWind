"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import numpy as np
from interface.modules.gui.charts.anti_aliasing_line import AntiAliasingLine
from interface.modules.gui.charts.chart1 import Chart1
import interface.modules.gui.gui_colors as color


class Chart1a(Chart1):
    """Chart1a Power curve
    Chart to display power vs wind speed in the bottom left area"""

    def __init__(self, canvas):
        super().__init__(canvas,
                         name='power_v1',
                         x_label="Wind speed (m/s)",
                         y_label="Turbine power (mW)",
                         x_left=0,
                         x_right=6,
                         y_bottom=0,
                         y_top=140,
                         x_grid=[0, 1, 2, 3, 4, 5, 6],
                         y_grid=[0, 20, 40, 60, 80, 100, 120, 140])

        # Power curve
        self.pc_cin = AntiAliasingLine(self.canvas, length=1, color=color.GRAY, width=self.LINE_WIDTH)
        self.pc_opt = AntiAliasingLine(self.canvas, length=4, color=color.GRAY, width=self.LINE_WIDTH, smooth=True)
        self.pc_max = AntiAliasingLine(self.canvas, length=2, color=color.GRAY, width=self.LINE_WIDTH)

    def update(self, data, force_resize=False):
        # Check if chart needs resizing
        if not self.width == self.canvas.winfo_width() \
                or not self.height == self.canvas.winfo_height()\
                or force_resize:
            self.width = self.canvas.winfo_width()
            self.height = self.canvas.winfo_height()
            self.resize_axes()
            self.resize_dots()
            self.resize_specific(data)

        self.update_dots(data)

    def resize_specific(self, data):
        # Power curve
        power_factor = data.POWER_RATED/data.WIND_RATED**3
        x = np.linspace(data.WIND_IN, data.WIND_RATED, 5)
        y = power_factor * x**3
        self.pc_cin.update_coordinates((self.x_to_pos(data.WIND_IN), self.y_to_pos(0),
                                        self.x_to_pos(data.WIND_IN), self.y_to_pos(y[0])))
        self.pc_opt.update_coordinates((self.x_to_pos(x[0]), self.y_to_pos(y[0]),
                                        self.x_to_pos(x[1]), self.y_to_pos(y[1]),
                                        self.x_to_pos(x[2]), self.y_to_pos(y[2]),
                                        self.x_to_pos(x[3]), self.y_to_pos(y[3]),
                                        self.x_to_pos(x[4]), self.y_to_pos(y[4])))
        self.pc_max.update_coordinates((self.x_to_pos(data.WIND_RATED), self.y_to_pos(data.POWER_RATED),
                                        self.x_to_pos(data.WIND_OUT_1), self.y_to_pos(data.POWER_RATED),
                                        self.x_to_pos(data.WIND_OUT_2), self.y_to_pos(0)))
