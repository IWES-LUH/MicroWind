"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

import tkinter as TK
import tkinter.ttk as ttk
from PIL import ImageTk
from interface.modules.gui.arcade.cloud import Cloud
from interface.modules.gui.arcade.bird import Bird
from interface.modules.gui.arcade.turbine import Turbine
from interface.modules.gui.arcade.gameover import GameOver
from interface.modules.gui.arcade.getready import GetReady


class ArcadeWindow:
    """GUI window for arcade game
    Initializes the tkinter widgets and assembles the arcade game window
    """

    def __init__(self, arcade_game):
        # CONSTANTS
        self.BLUE = '#2155CD'
        self.LIGHT_BLUE = '#99d9ea'
        self.GRAY_BLUE = '#7092be'
        self.GREEN = '#22b14c'
        self.LIGHT_GREEN = '#b5e61d'
        self.RED = '#ed1c24'
        self.SLIDER_THICKNESS = 24
        self.PAD_y = 5

        # Handles
        self.arcade_game = arcade_game
        self.driver = arcade_game.driver

        # Initialize the game window
        self.window = TK.Tk()
        self.window.title("MicroWind Arcade, Leibniz Universität Hannover, Institut für Windenergiesysteme")
        self.window.config(padx=100, pady=50, bg=self.BLUE)
        self.window.geometry('1920x1080+0+0')
        self.window.overrideredirect(True)

        # Configure style
        self.window.tk.call('source', 'modules/gui/arcade_theme/arcade.tcl')
        style = ttk.Style(self.window)
        style.theme_use('arcade')
        style.configure('TLabelframe', background=self.BLUE)
        style.configure('TLabelframe.Label', font=('FixedSys', 22))
        style.configure('TLabelframe.Label', background=self.BLUE)
        style.configure('TLabelframe.Label', foreground='white')
        style.configure('TButton', font=('FixedSys', 22))
        style.configure('TButton', foreground='black')
        style.configure('Treeview.Heading', font=('FixedSys', 16))
        style.configure('Treeview.Heading', foreground=self.BLUE)
        style.configure('Treeview.Heading', background=self.LIGHT_BLUE)
        style.configure('Treeview.Cell', background=self.LIGHT_BLUE)
        style.configure('Treeview', font=('FixedSys', 16))
        style.configure('Treeview', foreground=self.LIGHT_BLUE)
        style.configure('Treeview', background=self.BLUE)
        style.configure('Treeview', fieldbackground=self.BLUE)
        style.configure('TLabel', font=('FixedSys', 44))

        # Window size information and dimension information
        self.W = self.window.winfo_screenwidth()
        self.H = self.window.winfo_screenheight()

        # Generate widgets
        [self.label_score, self.img_title] = self.head()
        [self.canvas_damage, self.img_damage_bg, self.img_damage_bar, self.img_id_damage_bar] = self.damage_bar()
        [self.canvas_power, self.img_id_power_bg, self.img_power_bar, self.img_id_power_bar,
         self.canvas_speed, self.img_id_speed_bg, self.img_speed_bar, self.img_id_speed_bar,
         self.canvas_forecast, self.img_forecast_bg, self.graphics_turbine, self.graphics_bird,
         self.graphics_cloud, self.graphics_game_over, self.graphics_get_ready] = self.game()
        [self.tree_today, self.tree_total] = self.high_score()
        self.fill_score_table()

    def head(self):
        # Head frame
        frame_head = TK.Frame(self.window, bg=self.BLUE)
        frame_head.pack(side='top', fill='x')

        frame_buttons = ttk.Labelframe(frame_head, text='Game')
        frame_buttons.pack(side='right', fill='y', padx=10, pady=self.PAD_y)
        frame_buttons['style'] = 'TLabelframe'

        # Exit button
        def exit_arcade():
            self.arcade_game.main_manager.arcade_flag = False

        button_exit = ttk.Button(frame_buttons, text="EXIT", command=exit_arcade, width=10)
        button_exit.pack(side='right', padx=10, pady=10)

        # Restart button
        def restart():
            self.arcade_game.name_input_flag = False
            self.arcade_game.restart_game()
            button_restart.configure(state='normal')

        button_restart = ttk.Button(frame_buttons, text="RESTART", command=restart, width=10)
        button_restart.pack(side='right', padx=10, pady=10)

        frame_score = ttk.Labelframe(frame_head, text="Score")
        frame_score.pack(side='left', fill='y', padx=10, pady=self.PAD_y)

        # Score
        label_score = TK.Label(frame_score, text="     0 mWh", fg=self.LIGHT_BLUE, font='FixedSys 30 bold',
                               bg=self.BLUE, width=12, anchor='e')
        label_score.pack(side='left', padx=10, pady=10)

        # Title
        canvas_title = TK.Canvas(frame_head, height=90, width=800, bg=self.BLUE, highlightthickness=0)
        canvas_title.pack(side='right', expand=1)
        img_title = ImageTk.PhotoImage(file='modules/gui/imgs/TOA.png', master=canvas_title)
        canvas_title.create_image(400, 60, image=img_title)

        return label_score, img_title

    def damage_bar(self):
        # Damage bar
        frame_damage = ttk.Labelframe(self.window, text="Damage")
        frame_damage.pack(side='top', fill='x', padx=10, pady=self.PAD_y)
        canvas_damage = TK.Canvas(frame_damage, height=56, highlightthickness=0, bg=self.BLUE)
        canvas_damage.pack(side='top', fill='x', padx=20, pady=12)
        canvas_damage.update()
        img_damage_bg = ImageTk.PhotoImage(file='modules/gui/imgs/damage_bg.png', master=canvas_damage)
        canvas_damage.create_image(850, 28, image=img_damage_bg)
        img_damage_bar = ImageTk.PhotoImage(file='modules/gui/imgs/damage_bar.png', master=canvas_damage)
        img_id_damage_bar = canvas_damage.create_image(-800, 28, image=img_damage_bar)

        return canvas_damage, img_damage_bg, img_damage_bar, img_id_damage_bar

    def game(self):
        # Horizontal frame for power, speed and forecast
        frame_game = TK.Frame(self.window, bg=self.BLUE)
        frame_game.pack(side='top', fill='x')

        # Power bar
        frame_power = ttk.Labelframe(frame_game, text="Power")
        frame_power.pack(side='left', padx=10, pady=self.PAD_y)
        canvas_power = TK.Canvas(frame_power, height=500, width=200, bg=self.BLUE, highlightthickness=0)
        canvas_power.pack(side='left', padx=12, pady=20)
        canvas_power.update()
        img_power_bg = ImageTk.PhotoImage(file='modules/gui/imgs/power_bar.png', master=canvas_power)
        canvas_power.create_image(100, 250, image=img_power_bg)
        img_power_bar = ImageTk.PhotoImage(file='modules/gui/imgs/bar.png', master=canvas_power)
        img_id_power_bar = canvas_power.create_image(100, 400, image=img_power_bar)

        # Speed bar
        frame_speed = ttk.Labelframe(frame_game, text="Turbine speed")
        frame_speed.pack(side='left', padx=10, pady=self.PAD_y)
        canvas_speed = TK.Canvas(frame_speed, height=500, width=200, bg=self.BLUE, highlightthickness=0)
        canvas_speed.pack(side='left', padx=12, pady=20)
        canvas_speed.update()
        img_speed_bg = ImageTk.PhotoImage(file='modules/gui/imgs/speed_bar.png', master=canvas_speed)
        canvas_speed.create_image(100, 250, image=img_speed_bg)
        img_speed_bar = ImageTk.PhotoImage(file='modules/gui/imgs/bar.png', master=canvas_speed)
        img_id_speed_bar = canvas_speed.create_image(100, 340, image=img_speed_bar)

        # Forecast view
        frame_forecast = ttk.Labelframe(frame_game, text="Forecast")
        frame_forecast.pack(side='left', fill='x', expand=1, padx=10, pady=self.PAD_y)
        canvas_forecast = TK.Canvas(frame_forecast, height=500, bg=self.GRAY_BLUE, highlightthickness=0)
        canvas_forecast.pack(side='left', fill='x', expand=1, padx=20, pady=20)
        canvas_forecast.update()
        img_forecast_bg = ImageTk.PhotoImage(file='modules/gui/imgs/Background.png', master=canvas_forecast)
        canvas_forecast.create_image(1180 / 2, 250, image=img_forecast_bg)

        graphic_turbine = Turbine(canvas_forecast, self.arcade_game)

        graphic_bird = Bird(canvas_forecast, self.arcade_game)
        graphic_cloud = []
        for i in range(5):
            graphic_cloud.append(Cloud(canvas_forecast, self.arcade_game.driver))

        graphic_game_over = GameOver(canvas_forecast)
        graphic_get_ready = GetReady(canvas_forecast)

        return [canvas_power, img_power_bg, img_power_bar, img_id_power_bar,
                canvas_speed, img_speed_bg, img_speed_bar, img_id_speed_bar,
                canvas_forecast, img_forecast_bg,
                graphic_turbine, graphic_bird, graphic_cloud, graphic_game_over, graphic_get_ready]

    def high_score(self):
        # Horizontal frame for highscore tables
        frame_high_score = TK.Frame(self.window, bg=self.BLUE, width=self.W)
        frame_high_score.pack(side='left', fill='x', expand=1)

        # Todays highscore table
        frame_today = ttk.Labelframe(frame_high_score, text="Today\'s high score")
        frame_today.pack(side='left', fill='y', padx=10, pady=self.PAD_y)
        columns = ('name', 'score', 'time')
        tree_today = ttk.Treeview(frame_today, columns=columns, height=18, show='headings')
        tree_today.pack(padx=10, pady=10)
        tree_today.heading('name', text="Name", anchor=TK.W)
        tree_today.column('name', width=300)
        tree_today.heading('score', text="Score", anchor=TK.W)
        tree_today.column('score', width=200)
        tree_today.heading('time', text="Time", anchor=TK.W)
        tree_today.column('time', width=200)

        # Total hoghscore table
        frame_total = ttk.Labelframe(frame_high_score, text="Total high score")
        frame_total.pack(side='right', fill='y', padx=10, pady=self.PAD_y)
        columns = ('name', 'score', 'date')
        tree_total = ttk.Treeview(frame_total, columns=columns, height=18, show='headings')
        tree_total.pack(padx=10, pady=10)
        tree_total.heading('name', text="Name", anchor=TK.W)
        tree_total.column('name', width=300)
        tree_total.heading('score', text="Score", anchor=TK.W)
        tree_total.column('score', width=200)
        tree_total.heading('date', text="Date", anchor=TK.W)
        tree_total.column('date', width=200)

        return tree_today, tree_total

    def fill_score_table(self):
        # Fill the highscore tables
        for entry in self.tree_today.get_children():
            self.tree_today.delete(entry)
        for entry in self.tree_total.get_children():
            self.tree_total.delete(entry)
        for i in range(5):
            self.tree_today.insert('', TK.END, values=[self.arcade_game.todays_high_score["Name"][i],
                                                       self.arcade_game.todays_high_score["Score"][i],
                                                       self.arcade_game.todays_high_score["Time"][i]])
            self.tree_total.insert('', TK.END, values=[self.arcade_game.total_high_score["Name"][i],
                                                       self.arcade_game.total_high_score["Score"][i],
                                                       self.arcade_game.total_high_score["Date"][i]])

    def update_score(self):
        # Update the highscore tables
        score = int(self.arcade_game.score)
        self.label_score.configure(text=str(score) + " mWs")

    def update_damage(self):
        # Update the damage bar
        w = self.canvas_damage.winfo_width() - self.SLIDER_THICKNESS
        w_ = self.img_damage_bar.width() - self.SLIDER_THICKNESS
        damage = int(self.arcade_game.damage / self.arcade_game.DAMAGE_MAX * w)
        if damage >= w:
            damage = w
        self.canvas_damage.moveto(self.img_id_damage_bar, damage - w_, 0)

    def update_bars(self):
        # Update the power bar
        h = self.canvas_power.winfo_height() - self.SLIDER_THICKNESS
        if self.arcade_game.power < self.arcade_game.POWER_MAX:
            power = self.arcade_game.power / self.arcade_game.POWER_MAX * h
        else:
            power = h
        self.canvas_power.moveto(self.img_id_power_bar, 0, h - power)

        # Update the speed bar
        h = self.canvas_speed.winfo_height() - self.SLIDER_THICKNESS
        if self.driver.rot_turb < 2 * self.arcade_game.SPEED_R:
            speed = int(self.driver.rot_turb / self.arcade_game.SPEED_R / 2 * h)
        else:
            speed = h
        self.canvas_speed.moveto(self.img_id_speed_bar, 0, h - speed)

    def move_cloud(self):
        for i in range(5):
            self.graphics_cloud[i].move()

    def move_bird(self):
        self.graphics_bird.move()

    def rotate_turbine(self):
        self.graphics_turbine.rotate()

    def show_game_over(self):
        self.graphics_game_over.show()

    def hide_game_over(self):
        self.graphics_game_over.hide()

    def show_get_ready(self):
        self.graphics_get_ready.show()

    def hide_get_ready(self):
        self.graphics_get_ready.hide()
