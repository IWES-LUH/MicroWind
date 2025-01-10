"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""


class AntiAliasingLine:
    """Anti-aliasing line
    class that stores two lines and draws them on top of each other.
    The bottom line has a lighter color and is wider to smooth out harsh steps"""

    def __init__(self, canvas, length, color, width, smooth=False, arrow='none'):
        self.canvas = canvas
        self.line = []
        self.line_aa = []

        if smooth:
            smooth = 'bezier'

        # Calculate rgb values from color code
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)

        r += int((255 - r) / 2)
        g += int((255 - g) / 2)
        b += int((255 - b) / 2)

        color_aa = '#%02x%02x%02x' % (r, g, b)

        # Initialize line
        init_coordinates = []
        for i in range(length+1):
            init_coordinates.append(1)
            init_coordinates.append(1)

        self.line_aa = self.canvas.create_line(*init_coordinates, fill=color_aa, width=width+0.5,
                                               smooth=smooth, arrow=arrow)
        self.line = self.canvas.create_line(*init_coordinates, fill=color, width=width,
                                            smooth=smooth, arrow=arrow)

    def update_coordinates(self, coordinates):
        # Set coordinates and show line
        self.canvas.coords(self.line, *coordinates)
        self.canvas.coords(self.line_aa, *coordinates)
        self.canvas.itemconfig(self.line, state='normal')
        self.canvas.itemconfig(self.line_aa, state='normal')

    def hide(self):
        # Hide line
        self.canvas.itemconfig(self.line, state='hidden')
        self.canvas.itemconfig(self.line_aa, state='hidden')

