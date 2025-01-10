"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

from interface.modules.gui.charts.chart import Chart
from interface.modules.gui.charts.data_point import DataPoint
import interface.modules.gui.gui_colors as color

class Chart1(Chart):
    """Chart1 Superclass
    Chart Superclass with functionality to take data points"""

    def __init__(self, canvas, **kwargs):
        super().__init__(canvas, **kwargs)

        self.DOT_SIZE = 7
        self.LINE_WIDTH = 2

        # Dots
        self.i_dot = 0
        self.continuous_dots = []
        self.save_dots = []

    def update_dots(self, data):
        if len(self.continuous_dots) < 10:
            self.continuous_dots.append(DataPoint(data, color.GRAY))
            self.continuous_dots[-1].draw(self)
        else:
            self.continuous_dots[self.i_dot].clear()
            self.continuous_dots[self.i_dot] = DataPoint(data, color.GRAY)
            self.continuous_dots[self.i_dot].draw(self)
            self.i_dot += 1
            if self.i_dot == 10:
                self.i_dot = 0

    def take_save_dot(self, data, color):
        self.save_dots.append(DataPoint(data, color))
        self.save_dots[-1].draw(self)

    def redraw_dots(self):
        for d in self.save_dots:
            d.draw(self)

    def resize_dots(self):
        for d in self.continuous_dots:
            d.update_coordinates()

        for d in self.save_dots:
            d.update_coordinates()


