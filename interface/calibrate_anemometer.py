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
print("*** You are running the MicroWind anemometer calibration script ***")
print("")
print("This setup will run the wind tunnel at different wind speeds to calibrate the anemometer ")

inp = input("Continue calibration? <y/n>\n")
while not inp == 'y':
    inp = input("Continue calibration? <y/n>\n")
    if inp == 'n':
        print("exit calibration script")
        sys.exit()

print("")

# Perform loop over different wind speeds
for i in range(len(ANEMOMETER_WIND)):
    print("Change wind speed to ", ANEMOMETER_WIND[i], "m/s")
    driver.beta_set = 75
    driver.torque_level = 0
    driver.v_set = ANEMOMETER_WIND[i]
    driver.read_from_arduino()
    driver.write_to_arduino()
    time.sleep(10)
    for s in range(50):
        driver.read_from_arduino()
        driver.write_to_arduino()
        ANEMOMETER_READ[i] += driver.anemometer
        time.sleep(0.1)
        print(driver.anemometer)
    ANEMOMETER_READ[i] /= 50
driver.v_set = 0
driver.read_from_arduino()
driver.write_to_arduino()
print("Because anemometer has no linear behavior store anemometer values and wind speeds for later quadratic exreapolation")
print("Wind speeds: ", ANEMOMETER_WIND)
print("Anemometer reads: ", ANEMOMETER_READ)

replace_line(14, 'ANEMOMETER_READ = ' + str(ANEMOMETER_READ) + '  # [-] / Calculated by calibrate_anemometer.py')
replace_line(15, 'ANEMOMETER_WIND = ' + str(ANEMOMETER_WIND) + '  # [m/S] / Calculated by calibrate_anemometer.py')

driver.fan_pwm = 0
driver.read_from_arduino()
driver.write_to_arduino()
print("")
print("The file /data/calibration.py has been updated")
print("Calibration finished")

fig, ax = plt.subplots()
x = np.asarray(ANEMOMETER_WIND)
y = np.asarray(ANEMOMETER_READ)
ax.plot(x, y)
ax.set_xlabel("Wind speed [m/s]")
ax.set_ylabel("Analog read [/1024]")
ax.set_title("Anemometer calibration")
plt.show()