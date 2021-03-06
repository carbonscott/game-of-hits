#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from pyqtgraph          import LayoutWidget, ImageView, PlotItem
from pyqtgraph.Qt       import QtGui
from pyqtgraph.dockarea import DockArea, Dock

class MainLayout(QtGui.QWidget):
    def __init__(self):
        super().__init__()

        self.area      = DockArea()
        self.dock_dict = self.config_dock()

        self.btn_prev_qry, self.btn_next_qry, self.btn_perf = self.config_button_qry()
        self.btn_prev_cmp, self.btn_next_cmp, self.btn_chos = self.config_button_cmp()

        # Update images in child's class
        self.viewer_qry = self.config_image_qry()
        self.viewer_cmp = self.config_image_cmp()

        return None


    def config_dock(self):
        # Define Docks in main window...
        setup_dict = {
            "ImgQry"       : (500, 300),
            "ImgCmp"       : (500, 300),
            "ImgQryButton" : (1, 1),
            "ImgCmpButton" : (1, 1),
        }

        # Instantiate docks...
        dock_dict = {}
        for k, v in setup_dict.items(): dock_dict[k] = Dock(k, size = v)

        # Config layout...
        self.area.addDock(dock_dict["ImgQry"]  , "left")
        self.area.addDock(dock_dict["ImgCmp"], "right")

        self.area.addDock(dock_dict["ImgQryButton"]  , "bottom", dock_dict["ImgQry"])
        self.area.addDock(dock_dict["ImgCmpButton"], "bottom", dock_dict["ImgCmp"])

        # Hide titles...
        for v in dock_dict.values(): v.hideTitleBar()

        return dock_dict


    def config_status_qry(self):
        # Biolerplate code to start widget config
        wdgt = LayoutWidget()

        # Set up label...
        label = QtGui.QLabel("XXXX")

        wdgt.addWidget(label, row = 0, col = 0)
        self.dock_dict["ImgQryStatus"].addWidget(wdgt)

        return label


    def config_status_cmp(self):
        # Biolerplate code to start widget config
        wdgt = LayoutWidget()

        # Set up label...
        label = QtGui.QLabel("XXXX")

        wdgt.addWidget(label, row = 0, col = 0)
        self.dock_dict["ImgCmpStatus"].addWidget(wdgt)

        return label


    def config_button_qry(self):
        ''' Dock of ImgQry displays one image, three buttons, and one status.
        '''
        # Biolerplate code to start widget config
        wdgt = LayoutWidget()

        # Set up buttons...
        btn_prev = QtGui.QPushButton('Prev')
        btn_next = QtGui.QPushButton('Next')
        btn_perf = QtGui.QPushButton('Calculate performance')
        btn_save = QtGui.QPushButton('Save state')

        wdgt.addWidget(btn_prev, row = 0, col = 0)
        wdgt.addWidget(btn_next, row = 0, col = 1)
        wdgt.addWidget(btn_perf, row = 0, col = 2)

        self.dock_dict["ImgQryButton"].addWidget(wdgt)

        return btn_prev, btn_next, btn_perf


    def config_button_cmp(self):
        ''' Dock of ImgCmp displays one image, three buttons, and one status.
        '''
        # Biolerplate code to start widget config
        wdgt = LayoutWidget()

        # Set up buttons...
        btn_prev = QtGui.QPushButton('Prev')
        btn_next = QtGui.QPushButton('Next')
        btn_chos = QtGui.QPushButton('Choose')
        btn_load = QtGui.QPushButton('Load state')

        wdgt.addWidget(btn_prev, row = 0, col = 0)
        wdgt.addWidget(btn_next, row = 0, col = 1)
        wdgt.addWidget(btn_chos, row = 0, col = 2)

        self.dock_dict["ImgCmpButton"].addWidget(wdgt)

        return btn_prev, btn_next, btn_chos


    def config_image_qry(self):
        ''' Display qry image.
        '''
        # Biolerplate code to start widget config
        wdgt = ImageView(view = PlotItem())

        self.dock_dict["ImgQry"].addWidget(wdgt)

        return wdgt


    def config_image_cmp(self):
        ''' Display cmp image.
        '''
        # Biolerplate code to start widget config
        wdgt = ImageView(view = PlotItem())

        self.dock_dict["ImgCmp"].addWidget(wdgt)

        return wdgt


