"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""


class DataPoint:
    """ Data Point
    Class that stores positional data of dots and prints them on a canvas.
    This way, dots can be restored after changing the chart type
    """

    def __init__(self, data, color):
        self.SIZE = 7

        # Store the data
        self.color = color
        self.v_1 = data.v_1
        self.power = data.power_turb
        self.tsr = data.tip_speed_ratio
        self.c_p = data.c_p

        # Initialize
        self.chart = None
        self.dot = None

    def draw(self, chart):
        # Create a dot on the canvas based on the current chart type
        self.chart = chart
        self.dot = self.chart.canvas.create_oval(1, 1, 1, 1, fill=self.color, outline='white')
        self.update_coordinates()

    def update_coordinates(self):
        # Only update the coordinates of en existing dot.
        [x, y] = self.calc_xy_positions()
        self.chart.canvas.coords(self.dot, x-self.SIZE, y-self.SIZE, x+self.SIZE, y+self.SIZE)

    def calc_xy_positions(self):
        # Calculate the x and y positions of the dot on the canvas
        if self.chart.name == 'power_v1':
            x = self.v_1
            y = self.power
        elif self.chart.name == 'cp_tsr_0_deg':
            x = self.tsr
            y = self.c_p
        else:
            x = 0
            y = 0

        return [self.chart.x_to_pos(x), self.chart.y_to_pos(y)]

    def clear(self):
        # Remove dot from canvas
        self.chart.canvas.delete(self.dot)



