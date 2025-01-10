"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import time
from random import randint


class WindProfile:
    """Wind Profile
    Class to open a text file and read wind speeds"""

    def __init__(self, file):
        self.wind_profile_start = time.time()
        self.wind_profile_time = list()
        self.wind_profile_speed = list()
        self.v_set = 0
        for i in range(8):
            file.readline()
        while True:
            line = file.readline()
            if not line:
                break
            self.wind_profile_time.append(float(line.split(',')[0]))
            self.wind_profile_speed.append(float(line.split(',')[1]))

    def stop(self):
        self.wind_profile_time = list()
        self.wind_profile_speed = list()

    def calc(self):
        if len(self.wind_profile_time) > 0:
            if time.time()-self.wind_profile_start > self.wind_profile_time[0]:
                self.v_set = self.wind_profile_speed[0]
                del self.wind_profile_time[0]
                del self.wind_profile_speed[0]

        else:
            self.v_set = 0

        return self.v_set


class RandomWind:
    def __init__(self):
        self.dv = 0.01
        self.v_min = 0.8
        self.v_set = 0
        self.v_target = 0

    def calc(self, v, v_slider):
        if v_slider < self.v_min * 100:
            v_slider = self.v_min * 100
        if abs(v-self.v_target) < self.dv:
            self.v_target = randint(int(self.v_min*100), int(v_slider)) / 100
        if self.v_set < self.v_target:
            self.v_set += self.dv
        elif self.v_set > self.v_target:
            self.v_set -= self.dv

        return self.v_set
