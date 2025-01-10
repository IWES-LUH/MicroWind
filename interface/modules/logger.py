"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import time


class Logger:
    """Data logger
    Handles file and writes data stream"""

    def __init__(self):
        self.active = None
        self.counter = 0
        self.auto_stop = -1
        self.file = None

    def start(self):
        self.active = True
        self.counter = 0
        file = open('log.txt', 'a')
        file.write('time, ')
        file.write('v_set, ')
        file.write('v_act, ')
        file.write('v_2, ')
        file.write('anemometer, ')
        file.write('power_wind, ')
        file.write('tip_speed_ratio, ')
        file.write('beta_set, ')
        file.write('rot_turb, ')
        file.write('torque, ')
        file.write('torque level, ')
        file.write('current, ')
        file.write('voltage, ')
        file.write('power_turb, ')
        file.write('thrust_force, ')
        file.write('c_pitch_p, ')
        file.write('c_pitch_i, ')
        file.write('c_pitch_d')
        file.write('\t\n')
        self.file = file

    def end(self):
        self.active = False
        self.file.close()

    def log(self, data):
        self.file.write(str(time.time()) + ', ')
        self.file.write(str(data.v_set) + ', ')
        self.file.write(str(data.v_1) + ', ')
        self.file.write(str(data.v_2) + ', ')
        self.file.write(str(data.anemometer) + ', ')
        self.file.write(str(data.power_wind) + ', ')
        self.file.write(str(data.tip_speed_ratio) + ', ')
        self.file.write(str(data.beta_set) + ', ')
        self.file.write(str(data.rot_turb) + ', ')
        self.file.write(str(data.torque) + ', ')
        self.file.write(str(data.torque_level) + ', ')
        self.file.write(str(data.current) + ', ')
        self.file.write(str(data.voltage) + ', ')
        self.file.write(str(data.power_turb) + ', ')
        self.file.write(str(data.thrust_force) + ', ')
        self.file.write(str(data.c_pitch_p) + ', ')
        self.file.write(str(data.c_pitch_i) + ', ')
        self.file.write(str(data.c_pitch_d) + ', ')
        self.file.write('\t\n')

        self.counter += 1
        if self.counter == self.auto_stop:
            self.end()

    def __del__(self):
        if self.active:
            self.file.close()
