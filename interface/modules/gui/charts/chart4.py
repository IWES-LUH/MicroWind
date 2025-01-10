"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import tkinter as TK
import tkinter.ttk as ttk
import numpy as np
from math import cos, sin
from interface.modules.gui.charts.chart import Chart
from interface.modules.gui.charts.anti_aliasing_line import AntiAliasingLine
import interface.modules.gui.gui_colors as color


class Chart4(Chart):
    """Chart4 Aerodynamics
    Chart to display inflow and resulting forces at the blade tip"""

    def __init__(self, canvas):
        super().__init__(canvas,
                         name='aerodynamics',
                         x_label="Tip speed (m/s)",
                         y_label="Wind speed (m/s)",
                         x_left=14,
                         x_right=-22,
                         y_bottom=6,
                         y_top=-16,
                         x_grid=[24, 22, 20, 18, 16, 14, 12, 10, 8, 6, 4, 2, 0],
                         y_grid=[6, 5, 4, 3, 2, 1, 0],
                         legend=True)

        self.LINE_WIDTH = 2
        self.X_LEFT_MIN = 8
        self.X_RIGHT_MAX = -6

        self.pitch_last = 0

        self.profile_coordinates = np.loadtxt('data/profile.txt', skiprows=0, dtype=float)
        self.profile_coordinates[:, 0] = -(self.profile_coordinates[:, 0] - 0.25)
        self.profile_coordinates[:, 1] = -(self.profile_coordinates[:, 1] - 0.05)
        self.profile_coordinates = self.profile_coordinates * 6
        self.profile = []
        for i in range(self.profile_coordinates[:, 0].size - 1):
            self.profile.append(AntiAliasingLine(self.canvas, length=1, color=color.BLACK, width=2))

        self.v_2 = AntiAliasingLine(self.canvas, length=1, color=color.BLUE, width=self.LINE_WIDTH, arrow='last')
        self.v_rot = AntiAliasingLine(self.canvas, length=1, color=color.BLUE, width=self.LINE_WIDTH, arrow='last')
        self.v_rel = AntiAliasingLine(self.canvas, length=1, color=color.GREEN, width=self.LINE_WIDTH, arrow='last')
        self.F_l = AntiAliasingLine(self.canvas, length=1, color=color.RED, width=self.LINE_WIDTH, arrow='last')
        self.F_d = AntiAliasingLine(self.canvas, length=1, color=color.RED, width=self.LINE_WIDTH, arrow='last')
        self.F_R = AntiAliasingLine(self.canvas, length=1, color=color.PURPLE, width=self.LINE_WIDTH, arrow='last')
        self.F_T = AntiAliasingLine(self.canvas, length=1, color=color.AQUA, width=self.LINE_WIDTH, arrow='last')
        self.F_Q = AntiAliasingLine(self.canvas, length=1, color=color.AQUA, width=self.LINE_WIDTH, arrow='last')

        self.show_v = TK.BooleanVar(value=True)
        self.show_v_rel = TK.BooleanVar(value=True)
        self.show_lift_drag = TK.BooleanVar(value=False)
        self.show_resultant = TK.BooleanVar(value=False)
        self.show_force = TK.BooleanVar(value=False)

        ttk.Checkbutton(self.frame_legend, text="v_2, v_rot", variable=self.show_v,
                        style='Switch_blue').pack(side='top', pady=5, padx=5, anchor='w')

        ttk.Checkbutton(self.frame_legend, text="v_rel", variable=self.show_v_rel,
                        style='Switch_green').pack(side='top', pady=5, padx=5, anchor='w')

        ttk.Checkbutton(self.frame_legend, text="F_l, F_d", variable=self.show_lift_drag,
                        style='Switch_red').pack(side='top', pady=5, padx=5, anchor='w')

        ttk.Checkbutton(self.frame_legend, text="F_R", variable=self.show_resultant,
                        style='Switch_purple').pack(side='top', pady=5, padx=5, anchor='w')

        ttk.Checkbutton(self.frame_legend, text="F_Q, F_T", variable=self.show_force,
                        style='Switch_aqua').pack(side='top', pady=5, padx=5, anchor='w')

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
        self.draw_vectors(data)

    def resize_specific(self, data):
        w_canvas = self.canvas.winfo_width()
        w_legend = self.frame_legend.winfo_width()
        h_legend = self.frame_legend.winfo_height()
        self.canvas.coords(self.frame_legend_id, w_canvas-w_legend/2-self.R-10, h_legend/2+self.T+10)
        self.draw_profile(data)

    def draw_profile(self, data):
        theta = -np.deg2rad(data.beta_set)
        rot = np.asarray([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
        profile_rotated = np.dot(self.profile_coordinates, rot)
        if not self.x_right == self.X_RIGHT_MAX:
            profile_rotated *= 0.5
        x_positions = self.x_to_pos(profile_rotated[:, 0])
        y_positions = self.y_to_pos(profile_rotated[:, 1])

        for i in range(x_positions.size-1):
            if not (np.any(x_positions[i:i+2] == -1) or np.any(y_positions[i:i+2] == -1)):
                self.profile[i].update_coordinates((x_positions[i], y_positions[i],
                                                    x_positions[i+1], y_positions[i+1]))
            else:
                self.profile[i].hide()

    def draw_vectors(self, data):
        x_pos_cent = self.x_to_pos(0)
        y_pos_cent = self.y_to_pos(0)

        x_pos = self.x_to_pos(0)
        y_pos = self.y_to_pos(data.v_2)
        if not y_pos == -1 and self.show_v.get():
            self.v_2.update_coordinates((x_pos, y_pos, x_pos_cent, y_pos_cent))
        else:
            self.v_2.hide()

        x_pos = self.x_to_pos(data.v_rot)
        y_pos = self.y_to_pos(0)
        if not x_pos == -1 and self.show_v.get():
            self.v_rot.update_coordinates((x_pos, y_pos, x_pos_cent, y_pos_cent))
        else:
            self.v_rot.hide()

        x_pos = self.x_to_pos(data.v_rot)
        y_pos = self.y_to_pos(data.v_2)
        if not x_pos == -1 and not y_pos == -1 and self.show_v_rel.get():
            self.v_rel.update_coordinates((x_pos, y_pos, x_pos_cent, y_pos_cent))
        else:
            self.v_rel.hide()

        x_pos = self.x_to_pos(data.lift_force[0]/10)
        y_pos = self.y_to_pos(-data.lift_force[1]/10)
        if not x_pos == -1 and not y_pos == -1 and self.show_lift_drag.get():
            self.F_l.update_coordinates((x_pos_cent, y_pos_cent, x_pos, y_pos))
        else:
            self.F_l.hide()

        x_pos = self.x_to_pos(data.drag_force[0]/10)
        y_pos = self.y_to_pos(-data.drag_force[1]/10)
        if not x_pos == -1 and not y_pos == -1 and self.show_lift_drag.get():
            self.F_d.update_coordinates((x_pos_cent, y_pos_cent, x_pos, y_pos))
        else:
            self.F_d.hide()

        x_pos = self.x_to_pos(data.res_force[0]/10)
        y_pos = self.y_to_pos(-data.res_force[1]/10)
        if not x_pos == -1 and not y_pos == -1 and self.show_resultant.get():
            self.F_R.update_coordinates((x_pos_cent, y_pos_cent, x_pos, y_pos))
        else:
            self.F_R.hide()

        x_pos = self.x_to_pos(0)
        y_pos = self.y_to_pos(-data.thrust_force/10)
        if not x_pos == -1 and not y_pos == -1 and self.show_force.get():
            self.F_T.update_coordinates((x_pos_cent, y_pos_cent, x_pos, y_pos))
        else:
            self.F_T.hide()

        x_pos = self.x_to_pos(data.torque_force/10)
        y_pos = self.y_to_pos(0)
        if not x_pos == -1 and not y_pos == -1 and self.show_force.get():
            self.F_Q.update_coordinates((x_pos_cent, y_pos_cent, x_pos, y_pos))
        else:
            self.F_Q.hide()
