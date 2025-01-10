"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import time
import sys
import os
import pathlib
import numpy as np
from matplotlib import pyplot as plt
# Set working directory to interface/
os.chdir(str(pathlib.Path(__file__).parent.resolve()))
# Add parent directory to search path so modules can be imported with absolute paths
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
from interface.modules.driver import Driver
from interface.data.calibration_data import *


def replace_line(line_num, text):
    # small helper function to replace single line in calibration_data.py
    lines = open('data/calibration_data.py', 'r').readlines()
    lines[line_num] = text + '\n'
    out = open('data/calibration_data.py', 'w')
    out.writelines(lines)
    out.close()


driver = Driver()
if not driver.arduino_connected:
    raise RuntimeError("Arduino connection required")
driver.read_from_arduino()
driver.fan_pwm = 0
driver.write_to_arduino()

print("")
print("*** You are running the MicroWind calibration script ***")
print("")
print("This setup will run the wind tunnel at different wind speeds and measure the rotation speed of the turbine")

inp = input("Continue calibration? <y/n>\n")
while not inp == 'y':
    inp = input("Continue calibration? <y/n>\n")
    if inp == 'n':
        print("exit calibration script")
        sys.exit()

print("")

print("Measure fan rotation speed and wind speed based on PWM signal")
pwm = [100, 190]
fan_speed = [0, 0]
wind_speed = [0, 0]
driver.torque_level = 0
for i in range(len(pwm)):
    print("Set fan PWM to ", pwm[i])
    driver.fan_pwm = pwm[i]
    driver.beta_set = 45
    driver.read_from_arduino()
    driver.write_to_arduino()
    time.sleep(10)
    driver.beta_set = 20
    driver.read_from_arduino()
    driver.write_to_arduino()
    time.sleep(10)

    for s in range(5):
        driver.read_from_arduino()
        driver.write_to_arduino()
        fan_speed[i] += driver.rot_fan
        wind_speed[i] += driver.rot_turb / 60 * 2 * 3.14 * 0.16 / TSR_AT_20_DEG
        time.sleep(0.5)

    fan_speed[i] /= 5
    wind_speed[i] /= 5

FAN_PWM_FACTOR = (pwm[1] - pwm[0]) / (wind_speed[1] - wind_speed[0])
FAN_PWM_BIAS = pwm[0] - FAN_PWM_FACTOR * wind_speed[0]

WIND_SPEED_FACTOR = (wind_speed[1] - wind_speed[0]) / (fan_speed[1] - fan_speed[0])
WIND_SPEED_BIAS = wind_speed[0] - WIND_SPEED_FACTOR * fan_speed[0]

print("Assuming linear relationships between PWM, fan speed and wind speed we get the following constants:")
print("PWM factor: ", FAN_PWM_FACTOR)
print("PWM bias: ", FAN_PWM_BIAS)
print("Wind speed factor: ", WIND_SPEED_FACTOR)
print("Wind speed bias: ", WIND_SPEED_BIAS)
replace_line(10, 'FAN_PWM_FACTOR = ' + str(FAN_PWM_FACTOR) + '  # [-/(m/s)] / Calculated by calibrate_wind.py')
replace_line(11, 'FAN_PWM_BIAS = ' + str(FAN_PWM_BIAS) + '  # [-] / Calculated by calibrate_wind.py')
replace_line(12, 'WIND_SPEED_FACTOR = ' + str(WIND_SPEED_FACTOR) + '  # [(m/s)/(rpm)] / Calculated by calibrate_wind.py')
replace_line(13, 'WIND_SPEED_BIAS = ' + str(WIND_SPEED_BIAS) + '  # [m/s] / Calculated by calibrate_wind.py')

driver.fan_pwm = 0
driver.read_from_arduino()
driver.write_to_arduino()
print("")
print("The file /data/calibration.py has been updated")
print("Calibration finished")

fig, ax = plt.subplots(1, 2)
x1 = np.asarray([0.8, 6])
y1 = FAN_PWM_FACTOR * x1 + FAN_PWM_BIAS
ax[0].plot(x1, y1)
ax[0].set_xlabel("Wind speed [m/s]")
ax[0].set_ylabel("PWM [/255]")
ax[0].set_title("Wind speed PWM")
y2 = np.asarray([0.8, 6])
x2 = (y2 - WIND_SPEED_BIAS) / WIND_SPEED_FACTOR
ax[1].plot(x2, y2)
ax[1].set_xlabel("Fan rotation [rpm]")
ax[1].set_ylabel("Wind speed [m/s]")
ax[1].set_title("Wind speed RPM")
plt.show()
