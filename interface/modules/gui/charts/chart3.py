"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import numpy as np
from math import cos, sin
from interface.modules.gui.charts.chart import Chart
from interface.modules.gui.charts.anti_aliasing_line import AntiAliasingLine
import interface.modules.gui.gui_colors as color


class Chart3(Chart):
    """Chart1b Tip Speed Ratio
    Chart to display the inflow angle and the pitch angle of the blade tip"""

    def __init__(self, canvas, chart_type=1):
        super().__init__(canvas,
                         name='tip_speed_ratio',
                         x_label="Tip speed (m/s)",
                         y_label="Wind speed (m/s)",
                         x_left=14,
                         x_right=-6,
                         y_bottom=6,
                         y_top=-2,
                         x_grid=[24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0],
                         y_grid=[6, 5, 4, 3, 2, 1, 0])

        self.X_LEFT_MIN = 8
        self.X_RIGHT_MAX = -6

        self.pitch_last = 0

        self.lambda_lines = []
        for i in range(10):
            self.lambda_lines.append(AntiAliasingLine(self.canvas, length=1, color=color.GRAY, width=1))

        labels = ["tip speed ratio = 0", "1", "2", "3", "4"]
        self.lambda_labels = []
        for i in range(len(labels)):
            self.lambda_labels.append(self.canvas.create_text((1, 1), text=labels[i], anchor='e',
                                      font='TkDefaultFont 10 bold', fill=color.COLOR_LABELS))

        self.profile_coordinates = np.loadtxt('data/profile.txt', skiprows=0, dtype=float)
        self.profile_coordinates[:, 0] = -(self.profile_coordinates[:, 0]-0.25)
        self.profile_coordinates[:, 1] = -(self.profile_coordinates[:, 1]-0.05)
        self.profile_coordinates = self.profile_coordinates * 6
        self.profile = AntiAliasingLine(self.canvas, length=len(self.profile_coordinates[:, 0]),
                                        color=color.BLUE, width=2)

        self.inflow = AntiAliasingLine(self.canvas, length=1, color=color.RED, width=2, arrow='last')

    def update(self, data):
        # Check if chart needs resizing
        if not self.width == self.canvas.winfo_width() or not self.height == self.canvas.winfo_height():
            self.width = self.canvas.winfo_width()
            self.height = self.canvas.winfo_height()
            self.x_right = self.X_RIGHT_MAX
            y_spacing = self.height / abs(self.y_top - self.y_bottom)
            self.x_left = self.width / y_spacing + self.x_right
            if self.x_left < self.X_LEFT_MIN:
                self.x_right = -1
                self.x_left = self.width / y_spacing + self.x_right
            self.resize_axes()
            self.resize_specific(data)
        if not self.pitch_last == data.beta_set:
            self.draw_profile(data)
            self.pitch_last = data.beta_set
        self.draw_inflow(data)

    def resize_specific(self, data):
        # Lambda lines
        for i in range(10):
            # calc x
            x = self.y_bottom * i
            y = self.y_bottom
            if x > self.x_left:
                x = self.x_left
                y = self.x_left / i

            self.lambda_lines[i].update_coordinates((self.x_to_pos(x), self.y_to_pos(y),
                                                     self.x_to_pos(0), self.y_to_pos(0)))
            if i < len(self.lambda_labels):
                self.canvas.coords(self.lambda_labels[i], self.x_to_pos(x+0.2), self.y_to_pos(self.y_bottom-0.4))

        self.draw_profile(data)

    def draw_profile(self, data):
        theta = -np.deg2rad(data.beta_set)
        rot = np.asarray([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
        profile_rotated = np.dot(self.profile_coordinates, rot)
        if not self.x_right == self.X_RIGHT_MAX:
            profile_rotated *= 0.5
        [profile_rotated[:, 0], profile_rotated[:, 1]] = self.limit(profile_rotated[:, 0], profile_rotated[:, 1])
        x_pos = self.x_to_pos(profile_rotated[:, 0])
        y_pos = self.y_to_pos(profile_rotated[:, 1])

        t = tuple(np.stack((x_pos, y_pos)).flatten('F'))

        self.profile.update_coordinates(t)

    def draw_inflow(self, data):
        x_pos = 0
        y_pos = 0
        x_pos_cent = self.x_to_pos(0)
        y_pos_cent = self.y_to_pos(0)

        if data.tip_speed <= self.x_left and data.v_1 <= self.y_bottom:
            x_pos = self.x_to_pos(data.tip_speed)
            y_pos = self.y_to_pos(data.v_1)
        elif data.tip_speed > self.x_left:
            x_pos = self.x_to_pos(self.x_left)
            y_pos = self.y_to_pos(data.v_1 * self.x_left / data.tip_speed)
        elif data.v_1 > self.y_bottom:
            x_pos = self.x_to_pos(data.tip_speed * self.y_bottom / data.v_1)
            y_pos = self.y_to_pos(self.y_bottom)

        self.inflow.update_coordinates((x_pos, y_pos, x_pos_cent, y_pos_cent))

    def limit(self, x_values, y_values):
        left_x = self.x_left > x_values
        right_x = x_values > self.x_right
        bottom_y = self.y_bottom > y_values
        top_y = y_values > self.y_top
        inside = np.argwhere(left_x * right_x * bottom_y * top_y).flatten()
        if len(inside) > 0:
            x_values[0:inside[0]] = x_values[inside[0]]
            y_values[0:inside[0]] = y_values[inside[0]]
            x_values[inside[-1]+1:] = x_values[inside[-1]]
            y_values[inside[-1]+1:] = y_values[inside[-1]]

        return x_values, y_values

