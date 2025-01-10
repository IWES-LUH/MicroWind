"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

from math import cos, sin, atan
from scipy.interpolate import interp1d
import numpy as np
import time
import serial
import serial.tools.list_ports
import warnings
import interface.data.calibration_data as cal


class Driver:
    """MicroWind driver class
    Stores all data, performs internal calculations and is responsible for communication with the arduino.
    Can be used as a standalone command line control tool.
    """

    def __init__(self):
        # CONSTANTS
        self.AIR_DENS = 1.225
        self.ROTOR_RADIUS = 0.16
        self.ROTOR_INERTIA = 0.2  # Just a rough guess but seems to be ok
        self.PITCH_IDLE = 45
        self.ROT_MAX = 1200
        self.ROT_RATED = 600
        self.POWER_RATED = 75
        self.WIND_IN = 1
        self.WIND_RATED = 2.5
        self.WIND_OUT_1 = 5.5
        self.WIND_OUT_2 = 5.7
        self.THRUST_RATED = 100
        self.TORQUE_RATED = 1.2
        # Servo time limits
        self.SERVO_T_MIN = 1000  # Standard min pulse for servo
        self.SERVO_T_MAX = 2000  # Standard max pulse for servo
        # Fan PWM limits
        self.FAN_PWM_MIN = 6
        self.FAN_PWM_MAX = 255
        # Min max value of pitch
        self.PITCH_MIN = -5
        self.PITCH_MAX = 85
        # Min max value of wind speed
        self.V_MIN = 0.4
        self.V_MAX = 6
        # Min max value of torque levels
        self.TORQUE_LEVEL_MIN = -1
        self.TORQUE_LEVEL_MAX = 13

        # Input variables
        self.fan_pwm = self.FAN_PWM_MIN  # Protected property. Uses setter method for safety
        self.v_set = self.V_MIN  # Protected property. Uses setter method for safety
        self.servo_time = self.SERVO_T_MIN  # Protected property. Uses setter method for safety
        self.beta_set = self.PITCH_IDLE  # Protected property. Uses setter method for safety
        self.torque_level = 0  # Protected property. Uses setter method for safety
        self.led = True

        # Output variables
        self.time_last = time.time()
        self.dt = 1
        self.dt_rw = 0
        self.dt_r = 0
        self.rot_fan = 0
        self.rot_turb = 0
        self.rot_turb_last = 0
        self.current = 0
        self.voltage = 0
        self.thrust = 0
        self.anemometer = 0
        self.potentiometer = 0
        self.beta_potentiometer = 0
        self.tip_speed = 0
        self.power_turb = 0
        self.power_aero = 0
        self.power_wind = 0
        self.v_1 = 0
        self.v_anem = 0
        self.c_p = 0
        self.c_p_aero = 0
        self.v_2 = 0
        self.v_rot = 0
        self.v_rel = 0
        self.phi = 0
        self.torque = 0
        self.torque_force = 0
        self.res_force = np.asarray([0, 0])
        self.lift_force = np.asarray([0, 0])
        self.drag_force = np.asarray([0, 0])
        self.thrust_force = 0
        self.tip_speed_ratio = 0
        self.print_counter = 0

        # Interpolation for thermal anemometer
        self.interp_anemometer = interp1d(cal.ANEMOMETER_READ, cal.ANEMOMETER_WIND,
                                          kind='quadratic', fill_value='extrapolate')

        # Initialize serial communication to arduino
        self.port = serial.Serial()
        self.arduino_connected = False
        self.data_received = False
        self.torque_flip = 0.5
        self.attach_arduino()

    # Data transfer
    # Initialize serial connection
    def attach_arduino(self):
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if 'Arduino' in p.description]
        try:
            self.port = serial.Serial(arduino_ports[0], baudrate=38400)
            self.port.flushInput()
            self.port.flushOutput()
            time.sleep(2)
            self.arduino_connected = True
        except:
            warnings.warn('Arduino not connected', TransmissionWarning)

    # Receive data
    def read_from_arduino(self):
        try:
            if not self.data_received:
                self.port.write((1).to_bytes(1, byteorder='little'))
                read_data = self.port.read(16)
                self.port.flushInput()
                self.rot_fan = int.from_bytes(read_data[0:2], byteorder='little')
                self.rot_turb = int.from_bytes(read_data[2:4], byteorder='little')
                self.current = int.from_bytes(read_data[4:6], byteorder='little', signed=True)
                self.voltage = int.from_bytes(read_data[6:8], byteorder='little', signed=True)
                self.thrust = int.from_bytes(read_data[8:11], byteorder='little', signed=True)
                self.anemometer = int.from_bytes(read_data[12:14], byteorder='little')
                self.potentiometer = int.from_bytes(read_data[14:16], byteorder='little')
                self.data_received = True
            else:
                warnings.warn('No data received. Transmit first.', TransmissionWarning)
        except:
            warnings.warn('serial connection lost during receiving', TransmissionWarning)
            self.port.close()
            self.arduino_connected = False
        self.__calculate_input()

    # Transmit data
    def write_to_arduino(self):
        try:
            if self.data_received:
                self.port.write(self.fan_pwm.to_bytes(1, byteorder='little'))
                self.port.write(self.servo_time.to_bytes(2, byteorder='little'))
                self.port.write(self.torque_level.to_bytes(1, byteorder='little', signed=True))
                self.port.write(self.led.to_bytes(1, byteorder='little'))
                self.port.flushOutput()
                self.data_received = False
            else:
                warnings.warn('No data transmitted. Receive first.', TransmissionWarning)
        except:
            warnings.warn('serial connection lost during transmitting', TransmissionWarning)
            self.port.close()
            self.arduino_connected = False

    # Input values
    def __calculate_input(self):
        self.dt = time.time() - self.time_last
        self.time_last = time.time()
        # Tip speed
        self.tip_speed = self.rot_turb / 60 * 2 * 3.14 * self.ROTOR_RADIUS
        self.v_rot = self.tip_speed

        # because current measurement is extremely noisy,
        # calculate current based on torque level and rotation speed
        if self.torque_level >= 0:
            self.torque = cal.DRIVETRAIN_FACTOR[self.torque_level] * self.rot_turb \
                          + cal.DRIVETRAIN_BIAS[self.torque_level]
        else:
            self.torque = 0
        # Power
        self.power_turb = 2 * 3.14 * self.rot_turb / 60 * self.torque

        # Far field wind speed v_1
        self.v_1 = cal.WIND_SPEED_FACTOR * self.rot_fan + cal.WIND_SPEED_BIAS
        if self.v_1 < 0:
            self.v_1 = 0

        # Thermal anemometer wind speed
        v_anem = (self.interp_anemometer(self.anemometer) + self.v_anem) / 2
        self.v_anem = 0.1 * v_anem + 0.9 * self.v_anem

        # Turbine power
        self.power_wind = 0.5 * self.AIR_DENS * self.v_1 ** 3 * 3.14 * self.ROTOR_RADIUS ** 2 * 1000

        # Aerodynamic rotor power. Compensated by inertia * acceleration
        self.power_aero = (0.5 * self.power_aero
                           + 0.5 * self.power_turb
                           + self.ROTOR_INERTIA * (self.rot_turb-self.rot_turb_last)/self.dt)

        # Power coefficient c_p
        if self.power_wind <= 0:
            self.c_p = 0
            self.c_p_aero = 0
        else:
            self.c_p = self.power_turb / self.power_wind
            self.c_p_aero = self.power_aero / self.power_wind

        # Tip speed ratio
        if self.v_1 == 0:
            self.tip_speed_ratio = 0
        else:
            self.tip_speed_ratio = self.tip_speed / self.v_1

        # Rotor thrust force
        self.thrust_force = self.thrust * cal.THRUST_FACTOR  # milli Newton

        # Theoretical rotor plane wind speed v_2
        if self.thrust_force > 0:
            if self.v_1**2-(2 * self.thrust_force / 1000 / self.AIR_DENS / 3.14 / self.ROTOR_RADIUS ** 2) > 0:
                self.v_2 = ((self.v_1 ** 2
                             - (2 * self.thrust_force / 1000 / self.AIR_DENS / 3.14 / self.ROTOR_RADIUS ** 2)) ** 0.5
                            + self.v_1) / 2
            else:
                self.v_2 = 0

            if self.v_2 < 0.5*self.v_1:
                self.v_2 = 0.5*self.v_1

        # Relative wind speed at blade tip
        self.v_rel = (self.v_2 ** 2 + self.tip_speed ** 2) ** 0.5

        # Inflow angle phi
        if self.tip_speed > 0:
            self.phi = atan(self.v_2 / self.tip_speed)
        else:
            self.phi = 0

        # Rotor torque force concentrated at blade tip
        if self.rot_turb > 0:
            self.torque_force = 60 * self.power_aero / self.rot_turb / 3.14 / 2 / self.ROTOR_RADIUS
        else:
            self.torque_force = 0

        # Resultant rorce concentrated at tip as vector
        self.res_force = np.asarray([self.torque_force, self.thrust_force])

        rot = np.asarray([[cos(-self.phi), -sin(-self.phi)], [sin(-self.phi), cos(-self.phi)]])
        res_force_rot = np.dot(self.res_force, rot)

        # Airfoil lift and drag concentrated at blade tip as vectors
        rot = np.asarray([[cos(self.phi), -sin(self.phi)], [sin(self.phi), cos(self.phi)]])
        self.lift_force = np.dot(np.asarray([0, res_force_rot[1]]), rot)
        self.drag_force = np.dot(np.asarray([res_force_rot[0], 0]), rot)

        # Update last rotation speed for gradient calculation
        self.rot_turb_last = self.rot_turb

        # Pitch potentiometer value
        self.beta_potentiometer = cal.POTENTIOMETER_FACTOR * self.potentiometer + cal.POTENTIOMETER_BIAS

    # Print to terminal
    def print_values(self):
        if self.print_counter == 19:
            print('\n\nList of variables:')
            print(f' Set wind speed (m/s):       {self.v_set:>10.2f}   |  ', end='')
            print(f' Fan PWM (0-255):            {self.fan_pwm:>10.2f}')
            print(f' Fan speed (rpm):            {self.rot_fan:>10.2f}   |  ', end='')
            print(f' Wind speed v1 (m/s):        {self.v_1:>10.2f}')
            print(f' Wind speed v2 (m/s):        {self.v_2:>10.2f}   |  ', end='')
            print(f' Anemometer wind speed (m/s):{self.v_anem:>10.2f}')
            print(f' Tip speed(m/s):             {self.tip_speed:>10.2f}   |  ', end='')
            print(f' Tip speed ratio ():         {self.tip_speed_ratio:>10.2f}')
            print(f' Inflow angle phi (°):       {self.phi:>10.2f}   |  ', end='')
            print(f' Power coefficient ():       {self.c_p:>10.2f}')
            print(f' Power wind (mW):            {self.power_wind:>10.2f}   |  ', end='')
            print(f' Power turbine (mW):         {self.power_turb:>10.2f}')
            print(f' Current (mA):               {self.current:>10.2f}   |  ', end='')
            print(f' Voltage (mW):               {self.voltage:>10.2f}')
            print(f' Thrust force (mN):          {self.thrust_force:>10.2f}   |  ', end='')
            print(f' Torque (mNm):               {self.torque:>10.2f}')
            print(f' Turbine speed (rpm):        {self.rot_turb:>10.2f}   |  ', end='')
            print(f' Torque level ():            {self.torque_level:>10.2f}')
            print(f' Beta set (°):               {self.beta_set:>10.2f}   |  ', end='')
            print(f' Servo time (ms):            {self.servo_time:>10.2f}')
            print(f' Thrust readout ():          {self.thrust:>10.2f}   |  ', end='')
            print(f' Anemometer readout ():      {self.anemometer:>10.2f}')
            print(f' dt cycle (ms):              {self.dt*1000:>10.2f}   |  ', end='')
            print(f' potentiometer:              {self.potentiometer:>10.2f}')

            self.print_counter = 0
        self.print_counter += 1

    @property
    def beta_set(self):
        return self._beta_set

    @beta_set.setter
    def beta_set(self, beta):
        if beta < self.PITCH_MIN:
            self._beta_set = self.PITCH_MIN
        elif beta > self.PITCH_MAX:
            self._beta_set = self.PITCH_MAX
        else:
            self._beta_set = beta

        self.servo_time = cal.SERVO_TIME_FACTOR * self.beta_set + cal.SERVO_TIME_BIAS

    @property
    def servo_time(self):
        return self._servo_time

    @servo_time.setter
    def servo_time(self, servo_time):
        if servo_time < self.SERVO_T_MIN:
            self._servo_time = int(self.SERVO_T_MIN)
        elif servo_time > self.SERVO_T_MAX:
            self._servo_time = int(self.SERVO_T_MAX)
        else:
            self._servo_time = int(round(servo_time))


    @property
    def v_set(self):
        return self._v_set

    @v_set.setter
    def v_set(self, v):
        if v < self.V_MIN:
            self._v_set = self.V_MIN
        elif v > self.V_MAX:
            self._v_set = self.V_MAX
        else:
            self._v_set = v

        self.fan_pwm = cal.FAN_PWM_FACTOR * self.v_set + cal.FAN_PWM_BIAS

    @property
    def fan_pwm(self):
        return self._fan_pwm

    @fan_pwm.setter
    def fan_pwm(self, pwm):
        if pwm < 0:
            self._fan_pwm = 0
        elif pwm > 255:
            self._fan_pwm = 255
        else:
            self._fan_pwm = int(round(pwm))

    @property
    def torque_set(self):
        return self._torque_set

    @torque_set.setter
    def torque_set(self, torque):
        if torque < 0:
            self._torque_set = 0
        else:
            self._torque_set = torque
        possible_t = np.asarray(cal.DRIVETRAIN_FACTOR) * self.rot_turb + np.asarray(cal.DRIVETRAIN_BIAS)
        self.torque_level = np.interp(torque, possible_t, np.arange(0, len(possible_t)))

    @property
    def torque_level(self):
        return self._torque_level

    @torque_level.setter
    def torque_level(self, level):
        if level < self.TORQUE_LEVEL_MIN:
            self._torque_level = int(self.TORQUE_LEVEL_MIN)
        elif level > self.TORQUE_LEVEL_MAX:
            self._torque_level = int(self.TORQUE_LEVEL_MAX)
        else:
            self._torque_level = int(round(level))


class TransmissionWarning(UserWarning):
    pass
