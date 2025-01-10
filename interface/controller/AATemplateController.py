"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""


# Class name must equal file name!
class AATemplateController():
    # Controller class
    def __init__(self):
        self.description = [" ",
                            " ",
                            " ",
                            " ",
                            " ",
                            " ",
                            " ",
                            " ",
                            " ",
                            " ",
                            " ",
                            " "]

    def calc(self, v_anemometer, rotation_speed, power, torque, thrust_force, tip_speed_ratio, dt):
        # All controller calculations here
        turbine_start = 0

        return[0, 0]
        # [beta_set, torque_level]
