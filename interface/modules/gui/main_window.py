"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge, Mohammadsadegh Saei Esfahani
"""

import tkinter as TK
import tkinter.ttk as ttk
import os
import importlib
from interface.modules.gui.charts.chart1a import Chart1a
from interface.modules.gui.charts.chart1b import Chart1b
from interface.modules.gui.charts.chart2 import Chart2
from interface.modules.gui.charts.chart3 import Chart3
from interface.modules.gui.charts.chart4 import Chart4
import interface.modules.gui.gui_colors as color


class MainWindow:
    """GUI window
    Initializes the tkinter widgets and assembles the main window
    """

    def __init__(self, window, manager):
        # CONSTANTS
        self.PAD_X_BIAS = 10

        # Handles
        self.window = window
        self.manager = manager

        # Flag
        self.fullscreen = False

        # Initialize the gui window
        self.window.title('MicroWind')
        self.window.config(padx=5, pady=5)
        self.window.resizable(True, True)
        # self.window.iconbitmap('modules/gui/imgs/wind-turbine.ico')

        #  changing the theme
        style = ttk.Style(window)
        self.window.tk.call('source', 'modules/gui/azure_iwes_theme/azure.tcl')
        style.theme_use('azure')

        # Frame layout
        """
        Monitor:  Aerodynamics=False
        | -----------------------------------|
        | Logo         Game                  |
        | -----------------------------------|
        |   frame       |    frame           |
        |   control     |    chart3          |
        |               |                    |
        | --------------|--------------------|
        |   frame       |    frame           |
        |   chart1      |    chart2          |
        |               |                    |
        | --------------|--------------------|
        
        Aerodynamics:  Aerodynamics=True
        | -----------------------------------|
        | Logo         Game                  |
        | -----------------------------------|
        |   frame       |    frame           |
        |   control     |    chart4          |
        |               |                    |
        | --------------|                    |
        |   frame       |                    |
        |   chart1      |                    |
        |               |                    |
        | --------------|--------------------|
        """

        # Initialize frames
        self.frame_head = TK.Frame(self.window, highlightthickness=0)
        self.frame_control = TK.Frame(self.window, highlightthickness=0)
        self.frame_chart1 = TK.Frame(self.window, highlightthickness=0)
        self.frame_chart3 = TK.Frame(self.window, highlightthickness=0)
        self.frame_chart2 = TK.Frame(self.window, highlightthickness=0)
        self.frame_chart4 = TK.Frame(self.window, highlightthickness=0)

        self.frame_head.grid(row=0, column=0, padx=5, pady=5, columnspan=2, sticky='we')
        self.frame_control.grid(row=1, column=0, padx=0, pady=5, sticky=TK.NW)
        self.frame_chart1.grid(row=2, column=0)
        self.frame_chart2.grid(row=2, column=1)
        self.frame_chart3.grid(row=1, column=1)
        self.frame_chart4.grid(row=1, column=1, rowspan=2)
        self.frame_chart4.grid_remove()
        self.frame_chart4.active = False

        self.window.grid_columnconfigure(0, weight=0)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=0)
        self.window.grid_rowconfigure(1, weight=0)
        self.window.grid_rowconfigure(2, weight=1)

        # Fill frames
        [self.notification, self.button_data_logger] = self.head()
        [self.var_wind_sel, self.var_controller_sel] = self.profile_and_controller_selection()
        [self.var_radio_wind, self.var_wind] = self.wind_control()
        [self.var_radio_turbine, self.var_pitch, self.label_pitch_value, self.var_torque, self.label_torque_value, self.button_turbine_start] = self.turbine_control()
        self.vertical_space()
        self.canvas_chart1 = self.charts()

    def head(self):
        label_micro = ttk.Label(self.frame_head, text='Micro', font='Bahnschrift 30 bold', foreground='#888888')
        label_micro.pack(side='left')
        label_wind = ttk.Label(self.frame_head, text='Wind', font='Bahnschrift 30 bold', foreground='#000000')
        label_wind.pack(side='left')

        # GUI control buttons
        frame_buttons = TK.Frame(self.frame_head)
        frame_buttons.pack(side='right', padx=0)

        # Chart type selection button: monitor or aerodynamics
        def switch_chart_type():
            if self.manager.aerodynamics_flag:
                self.manager.aerodynamics_flag = False
                button_charts.configure(text='Aerodynamics')
                self.frame_chart2.grid()
                self.frame_chart3.grid()
                self.manager.C2.active = True
                self.manager.C3.active = True
                self.frame_chart4.grid_remove()
                self.manager.C4.active = False
            else:
                self.manager.aerodynamics_flag = True
                button_charts.configure(text='Monitor')
                self.frame_chart2.grid_remove()
                self.frame_chart3.grid_remove()
                self.manager.C2.active = False
                self.manager.C3.active = False
                self.frame_chart4.grid()
                self.manager.C4.active = True

        button_charts = ttk.Button(frame_buttons, text="Aerodynamics", command=switch_chart_type,
                                   takefocus=False, width=14)
        button_charts.pack(side='left', padx=5)

        # Pause charts button
        def fullscreen():
            if self.fullscreen:
                self.window.overrideredirect(False)
                self.fullscreen = False
            else:
                self.window.overrideredirect(True)
                self.fullscreen = True

        button_fullscreen = ttk.Button(frame_buttons, text="Fullscreen", command=fullscreen,
                                         takefocus=False, width=14)
        button_fullscreen.pack(side='left', padx=5)

        # Data logger button
        def start_stop_logger():
            if not self.manager.logger.active:
                self.manager.logger.start()
                button_data_logger.configure(text='Stop log')
            else:
                self.manager.logger.end()
                button_data_logger.configure(text='Log data')

        button_data_logger = ttk.Button(frame_buttons, text="Log data", command=start_stop_logger, takefocus=False)
        button_data_logger.pack(side='left', padx=5)

        def start_game():
            self.manager.arcade_flag = True

        button_game = ttk.Button(frame_buttons, text="Game", command=start_game, takefocus=False)
        button_game.pack(side='right', padx=5)

        # Notification
        notification = ttk.Label(self.frame_head, text="Speed Limit Reached",
                                 font='Bahnschrift 30 bold', justify=TK.CENTER, foreground=color.RED)
        notification.pack(side='left', expand=True)
        return [notification, button_data_logger]

    def profile_and_controller_selection(self):
        # Wind profile text box
        text_wind_profile = TK.Text(self.frame_control, height=6, width=29, bg=color.TEXT_BOX_COLOR)
        text_wind_profile.grid(row=1, column=0, padx=self.PAD_X_BIAS, sticky=TK.NW, rowspan=2)

        # Wind profile selection
        def update_wind_profile_info(*args):
            with open('wind/' + var_wind_sel.get() + '.txt', 'rt') as file_wind:
                file_wind.readline()
                file_wind.readline()
                text_wind_profile.delete(1.0, TK.END)
                text_wind_profile.insert(1.0, file_wind.readline()[1:])
                text_wind_profile.insert(2.0, file_wind.readline()[1:])
                text_wind_profile.insert(3.0, file_wind.readline()[1:])
                text_wind_profile.insert(4.0, file_wind.readline()[1:])
                text_wind_profile.insert(5.0, file_wind.readline()[1:])
                text_wind_profile.insert(6.0, file_wind.readline()[1:])

        # Wind profile drop down
        list_wind = os.listdir("wind/")
        for i in range(len(list_wind)):
            list_wind[i] = list_wind[i][:-4]

        var_wind_sel = TK.StringVar(self.window)
        var_wind_sel.set(list_wind[0])  # starts with the first element of the list
        menu_wind = ttk.OptionMenu(self.frame_control, var_wind_sel, list_wind[0], *list_wind,
                                   command=update_wind_profile_info)
        menu_wind.config(width=24)
        menu_wind.grid(row=0, column=0, sticky=TK.W, padx=self.PAD_X_BIAS)
        update_wind_profile_info(list_wind[0])

        # Controller text box
        text_controller = TK.Text(self.frame_control, height=12, width=29, bg=color.TEXT_BOX_COLOR)
        text_controller.grid(row=4, column=0, padx=self.PAD_X_BIAS, sticky=TK.NW, rowspan=5)

        # Controller selection
        def update_controller_info(*args):
            module = importlib.import_module('controller.'+var_controller_sel.get())
            controller = getattr(module, var_controller_sel.get())()
            description = controller.description
            self.manager.controller = controller
            text_controller.delete(1.0, TK.END)
            text_controller.insert(1.0, description[0] + '\n')
            text_controller.insert(2.0, description[1] + '\n')
            text_controller.insert(3.0, description[2] + '\n')
            text_controller.insert(4.0, description[3] + '\n')
            text_controller.insert(5.0, description[4] + '\n')
            text_controller.insert(6.0, description[5] + '\n')
            text_controller.insert(7.0, description[6] + '\n')
            text_controller.insert(8.0, description[7] + '\n')
            text_controller.insert(9.0, description[8] + '\n')
            text_controller.insert(10.0, description[9] + '\n')
            text_controller.insert(11.0, description[10] + '\n')
            text_controller.insert(12.0, description[11] + '\n')

        # Controller drop down
        list_controller = os.listdir('controller/')
        for i in range(len(list_controller)):
            list_controller[i] = list_controller[i][:-3]

        var_controller_sel = TK.StringVar(self.window)
        var_controller_sel.set(list_controller[0])  # starts with the second element of the list
        menu_controller = ttk.OptionMenu(self.frame_control, var_controller_sel, list_controller[0], *list_controller,
                                         command=update_controller_info)
        menu_controller.config(width=24)
        menu_controller.grid(row=3, column=0, sticky=TK.W, padx=self.PAD_X_BIAS)
        update_controller_info(list_controller[0])

        return var_wind_sel, var_controller_sel

    def wind_control(self):
        # Wind speed label
        label_wind = TK.Label(self.frame_control, text="Wind speed:", font='Arial 12 bold', justify=TK.LEFT)
        label_wind.grid(row=0, column=1, sticky=TK.W, columnspan=3)

        # Wind speed radio buttons
        frame_radio_wind = TK.Frame(self.frame_control)
        frame_radio_wind.grid(row=1, column=1, columnspan=3, sticky=TK.W)
        var_radio_wind = TK.IntVar()

        # Wind speed random radio button
        def sel_random_wind():
            slider_wind.configure(state='normal')
            button_wind_profile_start.configure(state='disabled')

        radio_wind_random = ttk.Radiobutton(frame_radio_wind, text="Random", variable=var_radio_wind,
                                            value=1, command=sel_random_wind)
        radio_wind_random.grid(row=0, column=0, sticky=TK.W, pady=0)

        # Wind speed constant radio button
        def sel_constant_wind():
            slider_wind.configure(state='normal')
            button_wind_ll.configure(state='normal')
            button_wind_l.configure(state='normal')
            button_wind_m.configure(state='normal')
            button_wind_mm.configure(state='normal')
            button_wind_profile_start.configure(state='disabled')

        radio_wind_constant = ttk.Radiobutton(frame_radio_wind, text="Constant", variable=var_radio_wind,
                                              value=2, command=sel_constant_wind)
        radio_wind_constant.grid(row=0, column=1, sticky=TK.W, padx=10)
        var_radio_wind.set(2)

        # Wind speed profile radio button
        def sel_profile_wind():
            slider_wind.configure(state='disabled')
            button_wind_ll.configure(state='disabled')
            button_wind_l.configure(state='disabled')
            button_wind_m.configure(state='disabled')
            button_wind_mm.configure(state='disabled')
            button_wind_profile_start.configure(state='normal')

        radio_wind_profile = ttk.Radiobutton(frame_radio_wind, text="Profile", variable=var_radio_wind,
                                             value=3, command=sel_profile_wind)
        radio_wind_profile.grid(row=0, column=2, sticky=TK.W, padx=10)
        var_radio_wind.set(2)

        # Wind speed profile start button
        def start_wind_profile():
            if not self.manager.wind_profile_run_flag:
                with open('wind/' + self.var_wind_sel.get() + '.txt', 'rt') as FILE_Wind:
                    self.manager.open_wind_profile(FILE_Wind)
                self.manager.wind_mode = 3
                button_wind_profile_start.configure(text="Stop")
                self.manager.wind_profile_run_flag = True
            else:
                self.manager.wind_profile.stop()
                self.manager.wind_profile_run_flag = False
                button_wind_profile_start.configure(text="Start")

        button_wind_profile_start = ttk.Button(self.frame_control, text="Start profile", command=start_wind_profile,
                                               takefocus=False, state='disabled')
        button_wind_profile_start.grid(row=1, column=4, sticky=TK.E, pady=5, padx=2)

        # Wind speed value label
        label_wind_value = ttk.Label(self.frame_control, text='%', width=4)
        label_wind_value.grid(row=2, column=1, sticky=TK.W, pady=0, padx=3)

        # Wind speed slider
        var_wind = TK.IntVar()
        var_wind.set(0)
        label_wind_value.configure(text=str(var_wind.get()/100))

        def update_wind_label(i):
            var_wind.set(i)
            if var_wind.get() < 40:
                var_wind.set(0)
            label_wind_value.configure(text=str(var_wind.get()/100))

        slider_wind = ttk.Scale(self.frame_control, from_=39, to=600, length=180, orient=TK.HORIZONTAL,
                                variable=var_wind, command=update_wind_label, takefocus=False)
        slider_wind.grid(row=2, column=2, sticky=TK.W, padx=0, pady=0)

        # Wind speed change buttons
        frame_change_wind = TK.Frame(self.frame_control)
        frame_change_wind.grid(row=2, column=3, columnspan=2, sticky=TK.E, padx=0, pady=0)

        def decrease_wind():
            if slider_wind.get() > 39:
                slider_wind.set(int(slider_wind.get()-40))
            else:
                slider_wind.set(0)
            label_wind_value.configure(text=str(var_wind.get()/100))

        button_wind_ll = ttk.Button(frame_change_wind, text="<<", command=decrease_wind, takefocus=False, width=3)
        button_wind_ll.grid(row=0, column=0, sticky=TK.W, padx=2)

        def decrease_wind_little():
            if slider_wind.get() > 4:
                slider_wind.set(int(slider_wind.get()-5))
            label_wind_value.configure(text=str(var_wind.get()/100))

        button_wind_l = ttk.Button(frame_change_wind, text="<", command=decrease_wind_little, takefocus=False, width=2)
        button_wind_l.grid(row=0, column=1, sticky=TK.W, padx=2)

        def increase_wind_little():
            if slider_wind.get() < 596:
                slider_wind.set(int(slider_wind.get()+5))
            if slider_wind.get() == 0:
                slider_wind.set(int(slider_wind.get()+40))
            label_wind_value.configure(text=str(var_wind.get()/100))

        button_wind_m = ttk.Button(frame_change_wind, text=">", command=increase_wind_little, takefocus=False, width=2)
        button_wind_m.grid(row=0, column=2, sticky=TK.W, padx=2)

        def increase_wind():
            if slider_wind.get() < 571:
                slider_wind.set(int(slider_wind.get()+30))
            else:
                slider_wind.set(600)
            if slider_wind.get() == 0:
                slider_wind.set(int(slider_wind.get()+40))
            label_wind_value.configure(text=str(var_wind.get()/100))

        button_wind_mm = ttk.Button(frame_change_wind, text=">>", command=increase_wind, takefocus=False, width=3)
        button_wind_mm.grid(row=0, column=3, sticky=TK.W, padx=2)

        return var_radio_wind, var_wind

    def turbine_control(self):
        # Turbine label
        label_turbine = TK.Label(self.frame_control, text="Turbine:", font='Arial 12 bold', justify=TK.LEFT)
        label_turbine.grid(row=3, column=1, sticky=TK.W, columnspan=2)

        # Pitch angle radio buttons:
        frame_radio_turbine = TK.Frame(self.frame_control)
        frame_radio_turbine.grid(row=4, column=1, columnspan=3, sticky=TK.W)
        var_radio_turbine = TK.IntVar()

        # Pitch angle from controller radio button
        def sel_pitch_by_controller():
            slider_pitch.configure(state='disabled')
            button_pitch_ll.configure(state='disabled')
            button_pitch_l.configure(state='disabled')
            button_pitch_m.configure(state='disabled')
            button_pitch_mm.configure(state='disabled')
            slider_torque.configure(state='disabled')
            button_torque_l.configure(state='disabled')
            button_torque_m.configure(state='disabled')
            button_turbine_start.configure(state='disabled')

        radio_turbine_controller = ttk.Radiobutton(frame_radio_turbine, text="Auto (controller)",
                                                   variable=var_radio_turbine, value=1,
                                                   command=sel_pitch_by_controller)
        radio_turbine_controller.grid(row=0, column=0, sticky=TK.W, pady=0)

        # Pitch angle manual radio button
        def sel_pitch_manually():
            slider_pitch.configure(state='normal')
            button_pitch_ll.configure(state='normal')
            button_pitch_l.configure(state='normal')
            button_pitch_m.configure(state='normal')
            button_pitch_mm.configure(state='normal')
            slider_torque.configure(state='normal')
            button_torque_l.configure(state='normal')
            button_torque_m.configure(state='normal')
            button_turbine_start.configure(state='normal')

        radio_turbine_manual = ttk.Radiobutton(frame_radio_turbine, text="Manually", value=2,
                                               variable=var_radio_turbine,
                                               command=sel_pitch_manually)
        radio_turbine_manual.grid(row=0, column=1, sticky=TK.W, pady=0)

        var_radio_turbine.set(2)

        # Turbine start button
        def start_turbine():
            button_turbine_start.configure(state='disabled')
            self.manager.start_flag = True

        button_turbine_start = ttk.Button(self.frame_control, text="Start turbine", command=start_turbine,
                                          takefocus=False, state='normal')
        button_turbine_start.grid(row=4, column=4, sticky=TK.E, pady=5, padx=2)

        # Pitch angle label
        label_pitch = TK.Label(self.frame_control, text="Pitch angle:", font='Arial 10 bold', justify=TK.LEFT)
        label_pitch.grid(row=5, column=1, sticky=TK.W, columnspan=2)

        # Pitch angle value label
        label_pitch_value = ttk.Label(self.frame_control, text="", width=4)
        label_pitch_value.grid(row=6, column=1, sticky=TK.W, pady=0, padx=3)

        # Pitch angle slider
        var_pitch = TK.IntVar()
        var_pitch.set(45)
        label_pitch_value.configure(text=str(var_pitch.get()) + "°")

        def update_pitch_label(i):
            var_pitch.set(i)
            label_pitch_value.configure(text=str(var_pitch.get()) + "°")

        slider_pitch = ttk.Scale(self.frame_control, from_=-5, to=85, length=180,
                                 orient=TK.HORIZONTAL, command=update_pitch_label,
                                 variable=var_pitch, takefocus=False)
        slider_pitch.grid(row=6, column=2, sticky=TK.W, padx=0, pady=0)

        # Pitch angle change buttons
        frame_change_pitch = TK.Frame(self.frame_control)
        frame_change_pitch.grid(row=6, column=3, columnspan=2, sticky=TK.E, padx=0, pady=0)

        def decrease_pitch():
            if slider_pitch.get() > 4:
                slider_pitch.set(int(slider_pitch.get()-5))
            else:
                slider_pitch.set(0)
            label_pitch_value.configure(text=str(var_pitch.get())+"°")

        button_pitch_ll = ttk.Button(frame_change_pitch, text="<<", command=decrease_pitch, takefocus=False, width=3)
        button_pitch_ll.grid(row=0, column=0, sticky=TK.W, padx=2)

        def decrease_pitch_little():
            if slider_pitch.get() > 0:
                slider_pitch.set(int(slider_pitch.get()-1))
            label_pitch_value.configure(text=str(var_pitch.get())+"°")

        button_pitch_l = ttk.Button(frame_change_pitch, text="<", command=decrease_pitch_little,
                                    takefocus=False, width=2)
        button_pitch_l.grid(row=0, column=1, sticky=TK.W, padx=2)

        def increase_pitch_little():
            if slider_pitch.get() < 85:
                slider_pitch.set(int(slider_pitch.get()+1))
            label_pitch_value.configure(text=str(var_pitch.get())+"°")

        button_pitch_m = ttk.Button(frame_change_pitch, text=">", command=increase_pitch_little,
                                    takefocus=False, width=2)
        button_pitch_m.grid(row=0, column=2, sticky=TK.W, padx=2)

        def increase_pitch():
            if slider_pitch.get() < 81:
                slider_pitch.set(int(slider_pitch.get()+5))
            else:
                slider_pitch.set(85)
            label_pitch_value.configure(text=str(var_pitch.get())+"°")

        button_pitch_mm = ttk.Button(frame_change_pitch, text=">>", command=increase_pitch, takefocus=False, width=3)
        button_pitch_mm.grid(row=0, column=3, sticky=TK.W, padx=2)

        # Torque factor Label
        label_torque = TK.Label(self.frame_control, text="Torque:", font='Arial 10 bold', justify=TK.LEFT)
        label_torque.grid(row=7, column=1, sticky=TK.W, columnspan=2)

        # Torque factor value label
        label_torque_value = ttk.Label(self.frame_control, text="", width=4)
        label_torque_value.grid(row=8, column=1, sticky=TK.W, pady=0, padx=3)

        # Torque factor slider
        var_torque = TK.IntVar()
        var_torque.set(0)
        label_torque_value.configure(text=str(var_torque.get()))

        def update_torque_label(i):
            var_torque.set(i)
            label_torque_value.configure(text=str(var_torque.get()/100))

        slider_torque = ttk.Scale(self.frame_control, from_=0, to=240, length=180,
                                  orient=TK.HORIZONTAL, command=update_torque_label,
                                  variable=var_torque, takefocus=False)
        slider_torque.grid(row=8, column=2, sticky=TK.W, padx=0, pady=0)

        # Torque change buttons
        frame_change_torque = TK.Frame(self.frame_control)
        frame_change_torque.grid(row=8, column=3, columnspan=2, sticky=TK.E, padx=0)

        def decrease_torque():
            if slider_torque.get() > 0:
                slider_torque.set(int(slider_torque.get()-5))
            label_torque_value.configure(text=str(var_torque.get()/100))

        button_torque_l = ttk.Button(frame_change_torque, text="<", command=decrease_torque, takefocus=False, width=7)
        button_torque_l.grid(row=0, column=0, sticky=TK.W, padx=2)

        def increase_torque():
            if slider_torque.get() < 240:
                slider_torque.set(int(slider_torque.get()+5))
            label_torque_value.configure(text=str(var_torque.get()/100))

        button_torque_m = ttk.Button(frame_change_torque, text=">", command=increase_torque, takefocus=False, width=7)
        button_torque_m.grid(row=0, column=1, sticky=TK.W, padx=2)

        return var_radio_turbine, var_pitch, label_pitch_value, var_torque, label_torque_value, button_turbine_start

    def vertical_space(self):
        TK.Label(self.frame_control, text=' ', fg='white').grid(row=9, column=0, columnspan=2)

    def charts(self):
        # Control widgets for chart1
        var_radio_chart1 = TK.IntVar()
        var_radio_chart1.set(1)
        frame_radio_chart1 = TK.Frame(self.frame_chart1, height=100)
        frame_radio_chart1.pack(side='top', anchor='e', padx=10)

        def sel_chart1_type():
            self.canvas_chart1.delete('all')
            dots = self.manager.C1.save_dots
            if var_radio_chart1.get() == 1:
                self.manager.C1 = Chart1a(self.canvas_chart1)
            else:
                self.manager.C1 = Chart1b(self.canvas_chart1)

            self.manager.C1.save_dots = dots
            self.manager.C1.redraw_dots()
            self.manager.C1.update(self.manager.driver, force_resize=True)

        def take_data_point():
            self.manager.C1.take_save_dot(self.manager.driver, var_radio_chart1_color.get())

        def clear_dots():
            for d in self.manager.C1.save_dots:
                d.clear()

        radio_chart1_power = ttk.Radiobutton(frame_radio_chart1, text="Power curve", variable=var_radio_chart1,
                                             value=1, command=sel_chart1_type)
        radio_chart1_power.grid(row=0, column=0, sticky=TK.W, padx=0, pady=0)

        radio_chart1_lambda = ttk.Radiobutton(frame_radio_chart1, text="c_P Lambda", variable=var_radio_chart1,
                                              value=2, command=sel_chart1_type)
        radio_chart1_lambda.grid(row=0, column=1, sticky=TK.W, padx=0, pady=0)

        label_chart1_color = ttk.Label(frame_radio_chart1, text="    Color:")
        label_chart1_color.grid(row=0, column=2, sticky=TK.W, padx=0, pady=0)

        var_radio_chart1_color = TK.StringVar()
        var_radio_chart1_color.set(color.BLUE)
        radio_chart1_red = ttk.Radiobutton(frame_radio_chart1, text="r", variable=var_radio_chart1_color,
                                           value=color.RED)
        radio_chart1_red.grid(row=0, column=3, sticky=TK.W, padx=0, pady=0)
        radio_chart1_blue = ttk.Radiobutton(frame_radio_chart1, text="b", variable=var_radio_chart1_color,
                                            value=color.BLUE)
        radio_chart1_blue.grid(row=0, column=4, sticky=TK.W, padx=0, pady=0)
        radio_chart1_green = ttk.Radiobutton(frame_radio_chart1, text="g", variable=var_radio_chart1_color,
                                             value=color.GREEN)
        radio_chart1_green.grid(row=0, column=5, sticky=TK.W, padx=0, pady=0)

        button_chart1_data_point = ttk.Button(frame_radio_chart1, text="Take point", command=take_data_point,
                                              takefocus=False)
        button_chart1_data_point.grid(row=0, column=6, sticky=TK.W, padx=0, pady=0)

        button_chart1_clear = ttk.Button(frame_radio_chart1, text="Clear", command=clear_dots,
                                         takefocus=False)
        button_chart1_clear.grid(row=0, column=7, sticky=TK.W, padx=10, pady=0)
        TK.Canvas(frame_radio_chart1, height=30, width=5, background='white').grid(row=0, column=8)

        canvas_chart1 = TK.Canvas(self.frame_chart1, height=1000, width=611, highlightthickness=0)
        canvas_chart1.pack(side='top')

        self.manager.C1 = Chart1a(canvas_chart1)

        canvas_chart2 = TK.Canvas(self.frame_chart2, height=1000, width=2000, highlightthickness=0)
        canvas_chart2.pack(side='top')

        self.manager.C2 = Chart2(canvas_chart2)

        canvas_chart3 = TK.Canvas(self.frame_chart3, height=334, width=2000, highlightthickness=0)
        canvas_chart3.pack(side='top')

        self.manager.C3 = Chart3(canvas_chart3)

        canvas_chart4 = TK.Canvas(self.frame_chart4, height=2000, width=2000, highlightthickness=0)
        canvas_chart4.pack(side='top')

        self.manager.C4 = Chart4(canvas_chart4)
        self.manager.C4.active = False

        return canvas_chart1
