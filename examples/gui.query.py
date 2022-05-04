#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from pyqtgraph.Qt import QtGui

from game_of_hit.layout import MainLayout
from game_of_hit.window import Window
from game_of_hit.data   import DataManager

from simulated_pnccd_panel_preprocess import DatasetPreprocess
import socket


def run(config_data):
    # Main event loop
    app = QtGui.QApplication([])

    # Layout
    layout = MainLayout()

    # Data
    data_manager = DataManager(config_data)

    # Window
    win = Window(layout, data_manager)
    win.config()
    win.show()

    sys.exit(app.exec_())


class ConfigData:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        for k, v in kwargs.items(): setattr(self, k, v)

config_data = ConfigData( path_csv = "/reg/data/ana03/scratch/cwang31/spi/simulated.pnccd_panel.v2.datasets.csv",
                          path_log = "/reg/data/ana03/scratch/cwang31/spi/logs/2022_0423_0016_57.validate.query.test.log", 
                          username = os.environ.get('USER'),
                          seed     = 0,
                          trans    = None, )

# Preprocess dataset...
# Data preprocessing can be lengthy and defined in dataset_preprocess.py
dataset_preproc = DatasetPreprocess(config_data)
dataset_preproc.apply()

run(config_data)
