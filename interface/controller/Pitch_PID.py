"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""


# Class name must equal file name!
class Pitch_PID():
    # Controller class
    def __init__(self):
        self.description = ["Pitch ",
                            "   Controller",
                            "PID",
                            " ",
                            " ",
                            "v_in 1.0 m/s",
                            "v_r = 2.5 m/s",
                            "v_out = 5.0 m/s",
                            " ",
                            "rated speed",
                            "  600 rpm",
                            " "]
        # Controller parameter
        self.rated_speed = 600
        self.gain_pitch_p = 0.1
        self.gain_pitch_i = 0.4
        self.gain_pitch_d = 0.5

        # initializing internal variables
        self.error_speed = 0
        self.error_speed_last = 0
        self.error_tsr = 0
        self.c_pitch_p = 0
        self.c_pitch_i = 0
        self.c_pitch_d = 0
        self.v_anem_mean = 0
        self.beta_act = 40

    def calc(self, v_anemometer, rotation_speed, power, torque, thrust_force, tip_speed_ratio, dt):
        # All controller calculations here
        turbine_start = 0
        self.v_anem_mean = 0.9 * self.v_anem_mean + 0.1 * v_anemometer
        self.error_speed = rotation_speed - self.rated_speed
        if self.v_anem_mean <= 1:
            # shut down
            beta_set = 70
            torque_level = 4
        elif self.v_anem_mean >= 5:
            # shut down
            beta_set = 80
            torque_level = 13
        elif rotation_speed == 0:
            # starting turbine
            beta_set = 20
            torque_level = -1
        else:
            # normal operation
            torque_level = 12

            if rotation_speed < 420:
                torque_level = 8
            if rotation_speed < 300:
                torque_level = 6
            if rotation_speed < 200:
                torque_level = 4

            # calculate PID factors
            self.c_pitch_p = self.gain_pitch_p*self.error_speed
            self.c_pitch_i += self.gain_pitch_i*self.error_speed*dt
            self.c_pitch_d = self.gain_pitch_d*(self.error_speed-self.error_speed_last)/dt

            # Anti-integral wind up
            if self.c_pitch_i < 0:
                self.c_pitch_i = 0
            elif self.c_pitch_i > 85:
                self.c_pitch_i = 85

            # Calculate pitch
            beta_set = self.c_pitch_p+self.c_pitch_i+self.c_pitch_d

            # Limit
            if beta_set < 0:
                beta_set = 0
            elif beta_set > 85:
                beta_set = 85

        self.beta_act = beta_set
        self.error_speed_last = self.error_speed
        return[beta_set, torque_level]
