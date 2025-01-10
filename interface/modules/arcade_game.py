"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import time
import datetime
import pandas as pd
from interface.modules.gui.arcade.arcade_window import ArcadeWindow
from interface.modules.gui.arcade.gameover_window import GameOverWindow
from interface.modules.windprofile import WindProfile


class ArcadeGame:
    """MicoWind Arcade Game
    Runs the loop to execute data transfer, calculations and refreshing of the arcade game
    """

    def __init__(self, main_manager):
        # CONSTANTS
        self.REFRESH = 50

        self.WIND_MIN = 1
        self.WIND_MAX = 3
        self.SPEED_R = 420
        self.DAMAGE_STATIC_INC = 0.5
        self.DAMAGE_EXP = 1.04
        self.DAMAGE_MAX = 100
        self.POWER_MAX = 30
        self.BIRD_START = 3000
        self.BIRD_SPEED = 10
        self.BIRD_COLLISION_MAX = 250
        self.BIRD_COLLISION_MIN = 100
        self.BIRD_ROT_LIMIT = 70
        self.NEW_GAME_DELAY = 4

        # Handles
        self.driver = main_manager.driver
        self.main_manager = main_manager

        # Variables
        self.last_loop = time.time()
        self.game_over_time = time.time()
        self.game_stop_time = time.time()
        self.dt = 0
        self.power = 0
        self.score = 0
        self.damage = 0
        self.bird_pos = self.BIRD_START
        self.last_loop = 0
        self.next_rotation = 0
        self.todays_high_score = None
        self.total_high_score = None

        self.wind_profile = None

        # Flags
        self.game_run_flag = False
        self.game_over_flag = False
        self.game_restart_flag = False
        self.name_input_flag = False
        self.bird_hit_flag = False

        # Load highscore from database
        self.read_database()

        self.arcade_window = ArcadeWindow(self)

    def run(self):
        if self.main_manager.arcade_flag:
            # Run arcade window loop
            self.arcade_window.window.after(self.REFRESH, self.run)
        else:
            print("return to main manager")
            self.arcade_window.window.destroy()
            self.main_manager.run()
            return

        if self.driver.arduino_connected:
            # Read from arduino
            self.driver.read_from_arduino()

        # Calculate input
        self.calculate()
        if self.game_run_flag:
            self.increment_score()

        # Set pitch angle from potentiometer
        self.driver.beta_set = self.driver.beta_potentiometer

        if self.game_run_flag:
            # Set wind speed
            self.driver.v_set = self.wind_profile.calc()

        if self.driver.arduino_connected:
            self.driver.write_to_arduino()

        # Refresh widgets
        self.arcade_window.move_cloud()
        self.arcade_window.rotate_turbine()
        self.arcade_window.update_bars()
        if self.game_run_flag:
            self.driver.led = True
            self.arcade_window.update_damage()
            self.arcade_window.update_score()
            if not self.bird_hit_flag:
                self.arcade_window.move_bird()
            self.arcade_window.hide_get_ready()
            self.arcade_window.hide_game_over()
        else:
            self.driver.led = False
            if self.game_over_flag or self.game_restart_flag:
                if self.game_over_flag:
                    self.arcade_window.show_game_over()
                if self.game_restart_flag:
                    self.arcade_window.show_get_ready()
                if time.time() - self.game_stop_time > self.NEW_GAME_DELAY:
                    self.game_over_flag = False
                    if self.name_input_flag:
                        # Open window for name input
                        self.name_input_flag = False
                        self.arcade_window.graphics_game_over.hide()
                        GameOverWindow(self)
                    else:
                        self.start_game()

        # Check for bird collision
        if self.bird_pos < self.BIRD_COLLISION_MAX:
            if self.bird_pos > self.BIRD_COLLISION_MIN:
                if self.driver.rot_turb > self.BIRD_ROT_LIMIT:
                    if self.game_run_flag:
                        print('bird collision detected')
                        self.arcade_window.graphics_bird.hit()
                        self.name_input_flag = True
                        self.stop_game()

        # Check for damage limit
        if self.damage >= self.DAMAGE_MAX:
            if self.game_run_flag:
                self.name_input_flag = True
                self.stop_game()

    def idle(self):
        self.arcade_window.graphics_bird.reset()
        self.score = 0
        self.damage = 0
        self.arcade_window.update_damage()
        self.arcade_window.update_score()

    def stop_game(self):
        self.driver.v_set = self.WIND_MIN
        self.game_stop_time = time.time()
        self.game_run_flag = False
        self.game_over_flag = True

    def restart_game(self):
        self.driver.v_set = self.WIND_MIN
        self.game_stop_time = time.time()
        self.game_run_flag = False
        self.game_restart_flag = True

    def start_game(self):
        self.game_over_flag = False
        self.game_restart_flag = False
        self.game_run_flag = True
        self.score = 0
        self.arcade_window.graphics_bird.reset()
        self.damage = 0
        with open('wind/arcade.txt', 'rt') as file:
            self.open_wind_profile(file)

    def open_wind_profile(self, file):
        self.wind_profile = WindProfile(file)

    def increment_score(self):
        self.score += self.power * self.dt

    def calculate(self):
        # Internal calculations
        self.dt = time.time()-self.last_loop
        self.last_loop = time.time()
        speed_over = self.driver.rot_turb - self.SPEED_R
        self.damage += self.DAMAGE_STATIC_INC * self.dt
        if speed_over > 0:
            self.damage += (self.DAMAGE_EXP ** speed_over - 1) * self.dt

        if self.driver.rot_turb > 60:
            self.next_rotation = int(3 * self.SPEED_R / self.driver.rot_turb)
        else:
            self.next_rotation = 15

        self.driver.torque_level = 5
        if self.driver.rot_turb < 420:
            self.driver.torque_level = 8
        if self.driver.rot_turb < 300:
            self.driver.torque_level = 6
        if self.driver.rot_turb < 200:
            self.driver.torque_level = 4
        if self.driver.rot_turb < 100:
            self.driver.torque_level = 2
        if self.driver.rot_turb < 50:
            self.driver.torque_level = 0

        self.power = 0.9 * self.power + 0.1 * self.driver.power_turb

    def read_database(self):
        try:
            self.todays_high_score = pd.read_csv('data/highscores/'
                                                 + datetime.date.today().strftime('%Y-%m-%d') + '.csv')
        except:
            self.todays_high_score = pd.DataFrame({'Name': ['Empty1', 'Empty2', 'Empty3', 'Empty4', 'Empty5'],
                                                   'Score': [0, 0, 0, 0, 0],
                                                   'Time': ['00:00', '00:01', '00:02', '00:03', '00:04']})
        self.total_high_score = pd.read_csv('data/highscores/total.csv')

        self.todays_high_score.sort_values(by=['Score'], ascending=False, inplace=True)
        self.total_high_score.sort_values(by=['Score'], ascending=False, inplace=True)

    def save_database(self):
        self.todays_high_score.to_csv('data/highscores/' + datetime.datetime.now().strftime('%Y-%m-%d') + '.csv',
                                      index=False)
        self.total_high_score.to_csv('data/highscores/total.csv', index=False)

    def add_entry(self, name, score):
        clock_time = datetime.datetime.now().strftime('%H:%M')
        entry = {'Name': name, 'Score': score, 'Time': clock_time}
        self.todays_high_score.loc[len(self.todays_high_score)] = entry
        self.todays_high_score.sort_values(by=['Score'], ascending=False, inplace=True, ignore_index=True)
        self.todays_high_score = self.todays_high_score.head(50)
        date = datetime.datetime.now().strftime('%d.%m.%Y')
        entry['Date'] = date
        self.total_high_score.loc[len(self.total_high_score)] = entry
        self.total_high_score.sort_values(by=['Score'], ascending=False, inplace=True, ignore_index=True)
        self.total_high_score = self.total_high_score.head(50)

        print(self.total_high_score)
