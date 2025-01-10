"""
This file is part ot the MicroWind software to control and plot data of a wind tunnel including a miniature wind turbine
Copyright (c) 2024 Institute for Wind Energy Systems, Leibniz University Hannover
The MicroWind software is licensed under GPLv3
Authors: Felix Prigge
"""

from tkinter import Tk
import sys
import os
import pathlib
# Set working directory to interface
os.chdir(str(pathlib.Path(__file__).parent.resolve()))
# Add parent directory to search path so modules can be imported with absolute paths
sys.path.append(str(pathlib.Path(__file__).parent.parent.resolve()))
from interface.modules.gui_manager import GUIManager
from interface.modules.driver import Driver
from interface.modules.logger import Logger


def main():
    """MicroWind Interface
    This function initializes and runs the interface to control the turbine and visualize the data
    """
    root = Tk()
    driver = Driver()
    logger = Logger()
    manager = GUIManager(root, driver, logger)

    # handle window exit
    def set_close_flag():
        manager.run_flag = False
    root.protocol("WM_DELETE_WINDOW", set_close_flag)

    # zoom window
    if sys.platform == 'win32':
        root.state('zoomed')

    # run loop
    root.after(1, manager.run)
    root.mainloop()
    return


if __name__ == '__main__':
    main()
