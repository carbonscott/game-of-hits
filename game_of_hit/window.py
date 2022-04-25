#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from pyqtgraph    import LabelItem
from pyqtgraph.Qt import QtGui

class Window(QtGui.QMainWindow):
    def __init__(self, layout, data_manager):
        super().__init__()

        self.layout       = layout
        self.data_manager = data_manager

        self.timestamp = self.data_manager.get_timestamp()

        self.num_qry = len(self.data_manager.records)
        self.num_cmp = len(self.data_manager.records[0]) - 1    # Discount the first image, which is a query

        self.idx_qry = 0
        self.idx_cmp = 0

        self.setupButtonFunction()

        self.dispImg()

        return None


    def config(self):
        self.setCentralWidget(self.layout.area)
        self.resize(1400, 700)
        self.setWindowTitle(f"Game of Hit | Timestamp: {self.timestamp}")

        return None


    def dispImg(self):
        # Let idx_qry bound within reasonable range....
        self.idx_qry = min(max(0, self.idx_qry), self.num_qry - 1)

        # Fetch the record by idx_qry...
        record = self.data_manager.records[self.idx_qry]

        # Get record for the qry image...
        record_qry = record[0]
        img_qry    = self.data_manager.get_img_by_record(record_qry)

        # Get the first record in images to cmp...
        record_cmp = record[1]
        img_cmp    = self.data_manager.get_img_by_record(record_cmp)

        # Display images...
        self.layout.viewer_qry.setImage(img_qry, levels = [-1, 1])
        self.layout.viewer_cmp.setImage(img_cmp, levels = [-1, 1])
        self.layout.viewer_qry.setHistogramRange(-1, 1)
        self.layout.viewer_cmp.setHistogramRange(-1, 1)
        self.layout.viewer_qry.getView().autoRange()
        self.layout.viewer_cmp.getView().autoRange()

        # Display title...
        self.layout.viewer_qry.getView().setTitle(f"Sequence number: {self.idx_qry + 1}/{self.num_qry}")
        self.layout.viewer_cmp.getView().setTitle(f"Sampled image number: {self.idx_cmp + 1}/{self.num_cmp}")

        return None


    def setupButtonFunction(self):
        self.layout.btn_next_qry.clicked.connect(self.nextQry)
        self.layout.btn_prev_qry.clicked.connect(self.prevQry)
        self.layout.btn_next_cmp.clicked.connect(self.nextCmp)
        self.layout.btn_prev_cmp.clicked.connect(self.prevCmp)


    def nextQry(self):
        self.idx_qry = min(self.num_qry - 1, self.idx_qry + 1)    # Right bound
        self.dispImg()

        return None


    def prevQry(self):
        self.idx_qry = max(0, self.idx_qry - 1)    # Left bound
        self.dispImg()

        return None


    def dispCmp(self):
        # Let idx_cmp bound within reasonable range....
        self.idx_cmp = min(max(0, self.idx_cmp), self.num_cmp - 1)

        # Fetch the record by idx...
        record = self.data_manager.records[self.idx_qry]

        # Get the first record in images to cmp...
        record_cmp = record[self.idx_cmp + 1]
        img_cmp    = self.data_manager.get_img_by_record(record_cmp)

        # Display images...
        self.layout.viewer_cmp.setImage(img_cmp, levels = [-1, 1])
        self.layout.viewer_cmp.setHistogramRange(-1, 1)
        ## self.layout.viewer_cmp.autoRange()
        self.layout.viewer_cmp.getView().autoRange()

        # Display title...
        self.layout.viewer_cmp.getView().setTitle(f"Sampled image number: {self.idx_cmp + 1}/{self.num_cmp}")

        return None


    def nextCmp(self):
        self.idx_cmp = min(self.num_cmp - 1, self.idx_cmp + 1)    # Right bound
        self.dispCmp()

        return None


    def prevCmp(self):
        self.idx_cmp = max(0, self.idx_cmp - 1)    # Left bound
        self.dispCmp()

        return None
