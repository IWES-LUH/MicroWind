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
print("*** You are running the MicroWind thrust calibration script ***")
print("")
print("This setup will help to measure the calibration factor of the load cell. ")

inp = input("Continue calibration? <y/n>\n")
while not inp == 'y':
    inp = input("Continue calibration? <y/n>\n")
    if inp == 'n':
        print("exit calibration script")
        sys.exit()

print("")
print("Step 1: Leave the wind turbine untouched.")
[] = input("Press any key to continue")
load_cell_zero = 0
for i in range(10):
    driver.read_from_arduino()
    driver.write_to_arduino()
    load_cell_zero += driver.thrust
    time.sleep(0.1)
load_cell_zero /= 10


print("Step 2: Pull the nacelle back with 100mN.")
[] = input("Press any key o continue")
load_cell_100 = 0
for i in range(50):
    driver.read_from_arduino()
    driver.write_to_arduino()
    load_cell_100 += driver.thrust
    time.sleep(0.1)
load_cell_100 /= 50

thrust_factor = 100 / (load_cell_100 - load_cell_zero)

print("Calibration factor: " + str(thrust_factor) + " mN/-")

replace_line(16, 'THRUST_FACTOR = ' + str(thrust_factor) + '  # [mN/-] / Calculated by calibrate_thrust.py')
print("")
print("The file /data/calibration.py has been updated")
print("Calibration finished")

fig, ax = plt.subplots()
x = np.asarray([0, 100])
y = x / THRUST_FACTOR
ax.plot(x, y)
ax.set_xlabel("Thrust force [mN]")
ax.set_ylabel("Thrust signal [-]")
ax.set_title("Thrust calibration")
plt.show()