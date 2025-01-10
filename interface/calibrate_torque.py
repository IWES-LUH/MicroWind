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
print("*** You are running the MicroWind torque calibration script ***")
print("")
print("This setup will measure the generator current of the turbine to calculate the torque.")

inp = input("Continue calibration? <y/n>\n")
while not inp == 'y':
    inp = input("Continue calibration? <y/n>\n")
    if inp == 'n':
        print("exit calibration script")
        sys.exit()

print("")

print("Current measurement for each torque level")
torque_level = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
current_rot = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
current_factor = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
current_bias = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
turb_speed = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
print("Set pitch to 45°, then to 5°")
driver.v_set = 3
driver.beta_set = 45
driver.read_from_arduino()
driver.write_to_arduino()
time.sleep(10)
driver.beta_set = 5
driver.read_from_arduino()
driver.write_to_arduino()
time.sleep(10)
for i in range(len(torque_level)):
    driver.torque_level = torque_level[i]
    driver.read_from_arduino()
    driver.write_to_arduino()
    time.sleep(5)
    print("Torque level ", torque_level[i])
    for s in range(100):
        driver.read_from_arduino()
        driver.write_to_arduino()
        current_rot[i] += driver.current
        turb_speed[i] += driver.rot_turb
        time.sleep(0.1)

    current_rot[i] /= 100
    turb_speed[i] /= 100
    print("Current of: ", current_rot[i], "mA at rotations speed: ", turb_speed[i], "rpm")

driver.fan_pwm = 0
driver.read_from_arduino()
driver.write_to_arduino()
time.sleep(5)
print("Now without rotation...")
for i in range(len(torque_level)):
    driver.torque_level = torque_level[i]
    driver.read_from_arduino()
    driver.write_to_arduino()
    time.sleep(3)
    print("Torque level ", torque_level[i])
    for s in range(100):
        driver.read_from_arduino()
        driver.write_to_arduino()
        current_bias[i] += driver.current
        time.sleep(0.1)

    current_bias[i] /= 100
    print("Bias current of: ", current_bias[i], "mA")

print('Assuming linear relation we get the following coefficients \n'
      'for calculating the current from rotation speed and torque level:')
for i in range(len(torque_level)):
    current_factor[i] = (current_rot[i]-current_bias[i])/turb_speed[i]
    print('Torque level ', torque_level[i], ':')
    print('Factor: ', current_factor[i], 'mA/rpm')
    print('Bias: ', current_bias[i], 'mA')

DRIVETRAIN_FRICTION_TORQUE = current_bias[0] * GENERATOR_TORQUE_CONSTANT

print('This leads to the following torque / rotation speed relationships:')
for i in range(len(torque_level)):
    DRIVETRAIN_FACTOR[i] = GENERATOR_TORQUE_CONSTANT * current_factor[i]
    DRIVETRAIN_BIAS[i] = GENERATOR_TORQUE_CONSTANT * current_bias[i] - DRIVETRAIN_FRICTION_TORQUE
    print('Torque level ', torque_level[i], ':')
    print('Factor: ', DRIVETRAIN_FACTOR[i], 'mA/rpm')
    print('Bias: ', DRIVETRAIN_BIAS[i], 'mA')

print('And a drivetrain friction torque of: ')
print(DRIVETRAIN_FRICTION_TORQUE, 'mNm')

replace_line(7, 'DRIVETRAIN_FRICTION_TORQUE = '
             + str(DRIVETRAIN_FRICTION_TORQUE)
             + '  # [mNm] / Calculated by calibrate.py')
replace_line(8, 'DRIVETRAIN_FACTOR = ' + str(DRIVETRAIN_FACTOR) + '  # [mNm/rpm] / Calculated by calibrate.py')
replace_line(9, 'DRIVETRAIN_BIAS = ' + str(DRIVETRAIN_BIAS) + '  # [mNm/°] / Calculated by calibrate.py')
print("")
print("The file /data/calibration.py has been updated")
print("Calibration finished")

fig, ax = plt.subplots()
for i in range(len(DRIVETRAIN_BIAS)):
    x = np.asarray([0, 1200])
    y = DRIVETRAIN_FACTOR[i] * x + DRIVETRAIN_BIAS[i]
    if i % 2 == 0:
        if i == 0:
            ax.plot(x, y, label="Generator physical")
        else:
            ax.plot(x, y)
    else:
        if i == 1:
            ax.plot(x, y, linestyle=':', label="Generator non-physical")
        else:
            ax.plot(x, y, linestyle=':')

rot = np.arange(0, 800)
T = 4.92 * rot**2 * (2*3.14*0.16/4/60)**3 * 2 * 3.14
ax.plot(rot, T, label="Rotor (TSR = 4, c_p = 0.1)")
ax.legend()
ax.set_xlabel("Rotation speed [rpm]")
ax.set_ylabel("Torque [mNm]")
ax.set_title("Torque vs rotation speed")
plt.show()