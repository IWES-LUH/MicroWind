"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import time
from interface.modules.gui.main_window import MainWindow
from interface.modules.arcade_game import ArcadeGame
from interface.modules.windprofile import WindProfile, RandomWind


class GUIManager:
    """MicoWind GUI Manager
    Runs the loop to execute data transfer, calculations and refreshing of the graphs
    """

    def __init__(self, root, driver, logger):
        # CONSTANTS
        self.REFRESH_RATE = 50
        self.REFRESH_ARCADE = 50

        # Handles
        self.driver = driver
        self.logger = logger

        # Flags
        self.start_flag = False
        self.aerodynamics_flag = False
        self.wind_profile_run_flag = False
        self.arcade_flag = False
        self.run_flag = True
        self.pause_charts_flag = True

        # Variables
        self.last_loop = 0
        self.chart_update = 0

        # Objects
        self.arcade_game = None
        self.C1 = None
        self.C2 = None
        self.C3 = None
        self.C4 = None
        self.wind_profile = None
        self.controller = None

        # Start main window
        self.window = MainWindow(root, self)

        # Initialize random wind object
        self.RandomWind = RandomWind()

    def run(self):
        if self.arcade_flag:
            # Run arcade game
            self.arcade_game = ArcadeGame(self)
            self.arcade_game.run()
            return

        if self.run_flag:
            # Run the main loop
            self.window.window.after(self.REFRESH_RATE, self.run)
        else:
            self.close_program()
            return

        # Track cycle times
        self.driver.dt_cycle = time.time() - self.last_loop
        self.last_loop = time.time()

        if self.driver.arduino_connected:
            # Read from arduino
            self.driver.read_from_arduino()

        # Set wind speed depending on mode
        if self.window.var_radio_wind.get() == 1:
            # Random
            self.driver.v_set = self.RandomWind.calc(self.driver.v_1, self.window.var_wind.get())
        elif self.window.var_radio_wind.get() == 2:
            # Manually
            self.driver.v_set = self.window.var_wind.get() / 100
        elif self.window.var_radio_wind.get() == 3:
            # Profile
            if self.wind_profile_run_flag:
                self.driver.v_set = self.wind_profile.calc()

        # Set pitch and torque depending on mode
        if self.driver.rot_turb > self.driver.ROT_MAX:
            # Emergency shut down
            self.window.notification.configure(text='Speed limit')
            self.window.var_radio_turbine.set(2)
            self.driver.beta_set = self.driver.PITCH_IDLE
            self.window.var_pitch.set(self.driver.PITCH_IDLE)
            self.driver.torque_level = self.driver.TORQUE_LEVEL_MAX
            self.window.var_torque.set(self.driver.TORQUE_LEVEL_MAX)
        elif self.window.var_radio_turbine.get() == 1:
            # External controller
            self.window.notification.configure(text=' ')
            [pitch, torque_level] = self.controller.calc(self.driver.v_1,
                                                         self.driver.rot_turb,
                                                         self.driver.power_turb,
                                                         self.driver.torque,
                                                         self.driver.thrust_force,
                                                         self.driver.tip_speed_ratio,
                                                         self.driver.dt_cycle)
            self.driver.beta_set = pitch
            self.driver.torque_level = torque_level
        elif self.window.var_radio_turbine.get() == 2:
            # Manually
            self.window.notification.configure(text=' ')
            self.driver.beta_set = self.window.var_pitch.get()
            self.driver.torque_set = self.window.var_torque.get() / 100
            self.window.label_torque_value.configure(text=str(int(self.driver.torque*100)/100))

        if self.driver.rot_turb == 0:
            # Enable start button only if turbine stands still
            self.window.button_turbine_start.configure(state='normal')
            if self.start_flag:
                self.driver.torque_level = -1
        else:
            self.start_flag = False
            self.window.button_turbine_start.configure(state='disabled')

        # Print to terminal
        self.driver.print_values()

        if self.driver.arduino_connected:
            # Write to arduino
            self.driver.write_to_arduino()

        if self.logger.active:
            # Log data to text file
            self.logger.log(self.driver)
        else:
            self.window.button_data_logger.configure(text='Log data')

        if self.chart_update == 0:
            if self.C1.active:
                self.C1.update(self.driver)
            if self.C3.active:
                self.C3.update(self.driver)
            self.chart_update = 1
        elif self.chart_update == 1:
            if self.C2.active:
                self.C2.update(self.driver)
            if self.C4.active:
                self.C4.update(self.driver)
            self.chart_update = 0

    def open_wind_profile(self, file):
        print('open wind profile')
        self.wind_profile = WindProfile(file)

    def close_program(self):
        if self.driver.arduino_connected:
            self.driver.read_from_arduino()
            self.driver.v_set = 0
            self.driver.torque_level = 0
            self.driver.beta_set = self.driver.PITCH_IDLE
            self.driver.write_to_arduino()
            self.driver.port.close()
        if self.logger.active:
            self.logger.end()

        self.window.window.destroy()
        self.window.window.quit()
