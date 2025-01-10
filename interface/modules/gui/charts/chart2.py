"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import tkinter as TK
import tkinter.ttk as ttk
import numpy as np
import time
from interface.modules.gui.charts.chart import Chart
from interface.modules.gui.charts.anti_aliasing_line import AntiAliasingLine
import interface.modules.gui.gui_colors as color


class Chart2(Chart):
    """Chart2 time series of measurements
    Chart to display the history of various measurements"""

    def __init__(self, canvas):
        super().__init__(canvas,
                         name='time_series',
                         x_label="Time (s)",
                         y_label="Normalized values",
                         x_left=0,
                         x_right=6,
                         y_bottom=0,
                         y_top=3,
                         x_grid=[0, 1, 2, 3, 4, 5, 6],
                         y_grid=[0, 0.5, 1, 1.5, 2, 2.5, 3],
                         legend=True)

        self.LINE_WIDTH = 2
        self.LINE_SEGMENTS = 50

        self.last_time = time.time()

        self.power_line = []
        self.rotation_line = []
        self.wind_line = []
        self.thrust_line = []
        self.torque_line = []
        self.anemometer_line = []

        self.power_line = AntiAliasingLine(self.canvas, length=self.LINE_SEGMENTS,
                                           color=color.BLUE, width=self.LINE_WIDTH)
        self.rotation_line = AntiAliasingLine(self.canvas, length=self.LINE_SEGMENTS,
                                              color=color.GREEN, width=self.LINE_WIDTH)
        self.wind_line = AntiAliasingLine(self.canvas, length=self.LINE_SEGMENTS,
                                          color=color.RED, width=self.LINE_WIDTH)
        self.thrust_line = AntiAliasingLine(self.canvas, length=self.LINE_SEGMENTS,
                                            color=color.PURPLE, width=self.LINE_WIDTH)
        self.torque_line = AntiAliasingLine(self.canvas, length=self.LINE_SEGMENTS,
                                            color=color.ORANGE, width=self.LINE_WIDTH)
        self.anemometer_line = AntiAliasingLine(self.canvas, length=self.LINE_SEGMENTS,
                                                color=color.AQUA, width=self.LINE_WIDTH)

        self.x_values = np.zeros(self.LINE_SEGMENTS+1)
        self.power_values = np.zeros(self.LINE_SEGMENTS+1)
        self.rotation_values = np.zeros(self.LINE_SEGMENTS+1)
        self.wind_values = np.zeros(self.LINE_SEGMENTS+1)
        self.thrust_values = np.zeros(self.LINE_SEGMENTS+1)
        self.torque_values = np.zeros(self.LINE_SEGMENTS+1)
        self.anemometer_values = np.zeros(self.LINE_SEGMENTS+1)

        self.show_power = TK.BooleanVar(value=True)
        self.show_rotation = TK.BooleanVar(value=True)
        self.show_wind = TK.BooleanVar(value=False)
        self.show_thrust = TK.BooleanVar(value=False)
        self.show_torque = TK.BooleanVar(value=False)
        self.show_anemometer = TK.BooleanVar(value=False)

        ttk.Checkbutton(self.frame_legend, text="Power", variable=self.show_power,
                        style='Switch_blue').pack(side='top', pady=5, padx=5, anchor='w')

        ttk.Checkbutton(self.frame_legend, text="Rotation speed", variable=self.show_rotation,
                        style='Switch_green').pack(side='top', pady=5, padx=5, anchor='w')

        ttk.Checkbutton(self.frame_legend, text="Wind speed", variable=self.show_wind,
                        style='Switch_red').pack(side='top', pady=5, padx=5, anchor='w')

        ttk.Checkbutton(self.frame_legend, text="Thrust force", variable=self.show_thrust,
                        style='Switch_purple').pack(side='top', pady=5, padx=5, anchor='w')

        ttk.Checkbutton(self.frame_legend, text="Torque", variable=self.show_torque,
                        style='Switch_orange').pack(side='top', pady=5, padx=5, anchor='w')

        ttk.Checkbutton(self.frame_legend, text="Anemometer", variable=self.show_anemometer,
                        style='Switch_aqua').pack(side='top', pady=5, padx=5, anchor='w')

    def update(self, data):
        # Check if chart needs resizing
        if not self.width == self.canvas.winfo_width() or not self.height == self.canvas.winfo_height():
            self.width = self.canvas.winfo_width()
            self.height = self.canvas.winfo_height()
            self.resize_axes()
            self.resize_specific()
        self.update_lines(data)

    def resize_specific(self):
        w_canvas = self.canvas.winfo_width()
        w_legend = self.frame_legend.winfo_width()
        h_legend = self.frame_legend.winfo_height()
        self.canvas.coords(self.frame_legend_id, w_canvas-w_legend/2-self.R-10, h_legend/2+self.T+10)

    def update_lines(self, data):
        self.x_values = self.x_values + time.time() - self.last_time
        self.last_time = time.time()
        self.x_values = np.roll(self.x_values, 1)
        self.x_values[0] = 0

        self.power_values = np.roll(self.power_values, 1)
        self.rotation_values = np.roll(self.rotation_values, 1)
        self.wind_values = np.roll(self.wind_values, 1)
        self.thrust_values = np.roll(self.thrust_values, 1)
        self.torque_values = np.roll(self.torque_values, 1)
        self.anemometer_values = np.roll(self.anemometer_values, 1)

        self.x_values[self.x_values > self.x_right] = self.x_right

        self.power_values[0] = self.limit_y(data.power_turb / data.POWER_RATED)
        self.rotation_values[0] = self.limit_y(data.rot_turb / data.ROT_RATED)
        self.wind_values[0] = self.limit_y(data.v_1 / data.WIND_RATED)
        self.thrust_values[0] = self.limit_y(data.thrust_force / data.THRUST_RATED)
        self.torque_values[0] = self.limit_y(data.torque / data.TORQUE_RATED)
        self.anemometer_values[0] = self.limit_y(data.v_anem / data.WIND_RATED)

        x_pos = self.x_to_pos(self.x_values)
        power_pos = self.y_to_pos(self.power_values)
        rotation_pos = self.y_to_pos(self.rotation_values)
        wind_pos = self.y_to_pos(self.wind_values)
        thrust_pos = self.y_to_pos(self.thrust_values)
        torque_pos = self.y_to_pos(self.torque_values)
        anemometer_pos = self.y_to_pos(self.anemometer_values)

        if self.show_power.get():
            t = tuple(np.stack((x_pos, power_pos)).flatten('F'))
            self.power_line.update_coordinates(t)
        else:
            self.power_line.hide()

        if self.show_rotation.get():
            t = tuple(np.stack((x_pos, rotation_pos)).flatten('F'))
            self.rotation_line.update_coordinates(t)
        else:
            self.rotation_line.hide()

        if self.show_wind.get():
            t = tuple(np.stack((x_pos, wind_pos)).flatten('F'))
            self.wind_line.update_coordinates(t)
        else:
            self.wind_line.hide()

        if self.show_thrust.get():
            t = tuple(np.stack((x_pos, thrust_pos)).flatten('F'))
            self.thrust_line.update_coordinates(t)
        else:
            self.thrust_line.hide()

        if self.show_torque.get():
            t = tuple(np.stack((x_pos, torque_pos)).flatten('F'))
            self.torque_line.update_coordinates(t)
        else:
            self.torque_line.hide()

        if self.show_anemometer.get():
            t = tuple(np.stack((x_pos, anemometer_pos)).flatten('F'))
            self.anemometer_line.update_coordinates(t)
        else:
            self.anemometer_line.hide()

    def limit_y(self, value):
        if value > self.y_top:
            value = self.y_top
        elif value < self.y_bottom:
            value = self.y_bottom

        return value
