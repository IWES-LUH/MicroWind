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
# stop fan
driver.fan_pwm = 0
driver.write_to_arduino()


print("")
print("*** You are running the MicroWind pitch calibration script ***")
print("")
print("This setup will help to calibrate pitch limits. ")
inp = input("Continue calibration? <y/n>\n")
while not inp == 'y':
    inp = input("Continue calibration? <y/n>\n")
    if inp == 'n':
        print("exit calibration script")
        sys.exit()

print("")
print("Increasing the pitch angle, until the pitch slider touches the main bearing")
initial_servo_time = 1200
driver.servo_time = initial_servo_time
driver.read_from_arduino()
driver.write_to_arduino()
servo_time = initial_servo_time
while True:
    inp = input("increase, decrease or set <++/+/-/--/set>")
    if inp == '++':
        servo_time -= 25
        driver.servo_time = servo_time
        driver.read_from_arduino()
        driver.write_to_arduino()
    if inp == '+':
        servo_time -= 5
        driver.servo_time = servo_time
        driver.read_from_arduino()
        driver.write_to_arduino()
    if inp == '--':
        servo_time += 25
        driver.servo_time = servo_time
        driver.read_from_arduino()
        driver.write_to_arduino()
    if inp == '-':
        servo_time += 5
        driver.servo_time = servo_time
        driver.read_from_arduino()
        driver.write_to_arduino()
    if inp == 'set':
        break
servo_time_min = servo_time
print("The current angle is set to ", ANGLE_AT_BACK_LIMIT, "°. Servo time: ", servo_time_min)
time.sleep(0.5)
print("Now increase the pitch until pitch slider touches the hub")
initial_servo_time = 1200
driver.servo_time = initial_servo_time
driver.read_from_arduino()
driver.write_to_arduino()
servo_time = initial_servo_time
while True:
    inp = input("increase, decrease or set <++/+/-/--/set>")
    if inp == '++':
        servo_time -= 25
        driver.servo_time = servo_time
        driver.read_from_arduino()
        driver.write_to_arduino()
    if inp == '+':
        servo_time -= 5
        driver.servo_time = servo_time
        driver.read_from_arduino()
        driver.write_to_arduino()
    if inp == '--':
        servo_time += 25
        driver.servo_time = servo_time
        driver.read_from_arduino()
        driver.write_to_arduino()
    if inp == '-':
        servo_time += 5
        driver.servo_time = servo_time
        driver.read_from_arduino()
        driver.write_to_arduino()
    if inp == 'set':
        break
servo_time_max = servo_time
print("The current angle is set to ", ANGLE_AT_FRONT_LIMIT, "°. Servo time: ", servo_time_max)
print("Assuming linear relation we get the following coefficients for calculating the servo duration:")
SERVO_TIME_FACTOR = (servo_time_min - servo_time_max) / (ANGLE_AT_BACK_LIMIT - ANGLE_AT_FRONT_LIMIT)
SERVO_TIME_BIAS = servo_time_max + SERVO_TIME_FACTOR * (0 - ANGLE_AT_FRONT_LIMIT)
print("Factor: ", SERVO_TIME_FACTOR)
print("Bias: ", SERVO_TIME_BIAS)
print("")
replace_line(5, "SERVO_TIME_FACTOR = " + str(SERVO_TIME_FACTOR) + "  # [us/deg] / Calculated by calibrate_pitch.py")
replace_line(6, "SERVO_TIME_BIAS = " + str(SERVO_TIME_BIAS) + "  # [us] / Calculated by calibrate_pitch.py")
print("")
print("The file /data/calibration.py has been updated")
print("Calibration finished")

fig, ax = plt.subplots()
x = np.asarray([ANGLE_AT_FRONT_LIMIT, ANGLE_AT_BACK_LIMIT])
y = SERVO_TIME_FACTOR * x + SERVO_TIME_BIAS
ax.plot(x, y)
ax.set_xlabel("Pitch angle [deg]")
ax.set_ylabel("Servo pulse duration [us]")
ax.set_title("Servo calibration")
plt.show()
