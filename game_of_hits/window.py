#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pickle

from pyqtgraph         import LabelItem
from pyqtgraph.Qt      import QtGui, QtWidgets, QtCore
from game_of_hits.utils import PerfMetric

class Window(QtGui.QMainWindow):
    def __init__(self, layout, data_manager):
        super().__init__()

        self.createAction()
        self.createMenuBar()
        self.connectAction()

        self.layout       = layout
        self.data_manager = data_manager

        self.timestamp = self.data_manager.get_timestamp()
        self.username  = self.data_manager.username

        self.num_qry = len(self.data_manager.records)
        self.num_cmp = len(self.data_manager.records[0]) - 1    # Discount the first image, which is a query

        self.idx_qry = 0
        self.idx_cmp = 0
        self.idx_cmp_offset = 1

        self.setupButtonFunction()
        self.setupButtonShortcut()

        self.dispImg()

        return None


    def config(self):
        self.setCentralWidget(self.layout.area)
        self.resize(1400, 700)
        self.setWindowTitle(f"Game of Hit | Timestamp: {self.timestamp} | Player: {self.username}")

        return None


    def setupButtonFunction(self):
        self.layout.btn_next_qry.clicked.connect(self.nextQry)
        self.layout.btn_prev_qry.clicked.connect(self.prevQry)
        self.layout.btn_next_cmp.clicked.connect(self.nextCmp)
        self.layout.btn_prev_cmp.clicked.connect(self.prevCmp)
        self.layout.btn_perf.clicked.connect(self.dispPerf)
        self.layout.btn_chos.clicked.connect(self.updateRes)

        return None


    def setupButtonShortcut(self):
        # w/ buttons
        self.layout.btn_next_qry.setShortcut("J")
        self.layout.btn_prev_qry.setShortcut("K")
        self.layout.btn_next_cmp.setShortcut("L")
        self.layout.btn_prev_cmp.setShortcut("H")
        self.layout.btn_chos.setShortcut("C")

        # w/o buttons
        QtGui.QShortcut(QtCore.Qt.Key_G, self, self.goEventDialog)

        return None


    ###############
    ### DIPSLAY ###
    ###############
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
        self.layout.viewer_qry.setImage(img_qry, levels = [0, 1])
        self.layout.viewer_cmp.setImage(img_cmp, levels = [0, 1])
        self.layout.viewer_qry.setHistogramRange(0, 1)
        self.layout.viewer_cmp.setHistogramRange(0, 1)
        self.layout.viewer_qry.getView().autoRange()
        self.layout.viewer_cmp.getView().autoRange()

        # Display title...
        self.layout.viewer_qry.getView().setTitle(f"Sequence number: {self.idx_qry + 1}/{self.num_qry}")
        self.layout.viewer_cmp.getView().setTitle(f"Sampled image number: {self.idx_cmp + 1}/{self.num_cmp}")

        return None


    def dispCmp(self):
        # Let idx_cmp bound within reasonable range....
        self.idx_cmp = min(max(0, self.idx_cmp), self.num_cmp - 1)

        # Fetch the record by idx...
        record = self.data_manager.records[self.idx_qry]

        # Get the first record in images to cmp...
        record_cmp = record[self.idx_cmp + self.idx_cmp_offset]
        img_cmp    = self.data_manager.get_img_by_record(record_cmp)

        # Display images...
        self.layout.viewer_cmp.setImage(img_cmp, levels = [0, 1])
        self.layout.viewer_cmp.setHistogramRange(0, 1)
        ## self.layout.viewer_cmp.autoRange()
        self.layout.viewer_cmp.getView().autoRange()

        # Display title...
        self.layout.viewer_cmp.getView().setTitle(f"Sampled image number: {self.idx_cmp + self.idx_cmp_offset}/{self.num_cmp}")

        return None


    ##################
    ### NAVIGATION ###
    ##################
    def nextQry(self):
        self.idx_qry = min(self.num_qry - 1, self.idx_qry + 1)    # Right bound
        self.dispImg()

        # Restore the idx to cmp back to 0...
        self.idx_cmp = 0

        return None


    def prevQry(self):
        self.idx_qry = max(0, self.idx_qry - 1)    # Left bound
        self.dispImg()

        # Restore the idx to cmp back to 0...
        self.idx_cmp = 0

        return None


    def nextCmp(self):
        self.idx_cmp = min(self.num_cmp - 1, self.idx_cmp + 1)    # Right bound
        self.dispCmp()

        return None


    def prevCmp(self):
        self.idx_cmp = max(0, self.idx_cmp - 1)    # Left bound
        self.dispCmp()

        return None


    ###########################
    ### MEASURE PERFORMANCE ###
    ###########################
    def updateRes(self):
        res = self.data_manager.records[self.idx_qry][self.idx_cmp_offset + self.idx_cmp]
        self.data_manager.res_list[self.idx_qry][1] = res

        print(f"Choice made for event {self.idx_qry + 1}")

        return None


    def initPerf(self):
        # Fetch all labels...
        record = self.data_manager.records[0]
        labels = [ item.split()[-1].strip() for item in record[1:] ]

        # New container to store validation result (thus res_dict) for each label...
        res_dict = {}
        for label in labels: res_dict[label] = { i : [] for i in labels }

        return res_dict


    def calcPerf(self):
        # Recalculate to eliminate corruption of results
        res_dict = self.initPerf()

        is_empty = True
        for i, record in enumerate(self.data_manager.res_list):
            # Ignore unanswered tests...
            if record[1] is None: continue

            # Alright, it's not empty...
            is_empty = False

            # Extract labels
            label_qry = record[0].split()[-1].strip()
            label_res = record[1].split()[-1].strip()

            # Save it to res_dict...
            res_dict[label_qry][label_res].append( tuple(record) )

        assert not is_empty, "No results found!!!  "

        return res_dict


    def dispPerf(self):
        res_dict = self.calcPerf()
        labels   = list(res_dict.keys())

        # Get macro metrics...
        perf_metric = PerfMetric(res_dict)

        # Formating purpose...
        # Might be a bad practice to hardcode
        disp_dict = { "0" : "not sample",
                      "1" : "single hit",
                      "2" : " multi hit",
                      "9" : "background",  
                    }

        # Report multiway classification...
        msgs = []
        for label_pred in labels:
            disp_text = disp_dict[label_pred]
            msg = f"{disp_text}  |"
            for label_real in labels:
                num = len(res_dict[label_pred][label_real])
                msg += f"{num:>12d}"

            metrics = perf_metric.get_metrics(label_pred)
            for metric in metrics:
                msg += f"{metric:>12.2f}"
            msgs.append(msg)

        msg_header = " " * (msgs[0].find("|") + 1)
        for label in labels: 
            disp_text = disp_dict[label]
            msg_header += f"{disp_text:>12s}"

        for header in [ "accuracy", "precision", "recall", "specificity", "f1" ]:
            msg_header += f"{header:>12s}"
        print(msg_header)

        msg_headerbar = "-" * len(msgs[0])
        print(msg_headerbar)
        for msg in msgs:
            print(msg)

        return None


    ######################################
    ### SAVE AND RESTORE GAME PROGRESS ###
    ######################################
    def saveStateDialog(self):
        path_pickle, is_ok = QtGui.QFileDialog.getSaveFileName(self, 'Save File', f'{self.timestamp}.pickle')

        if is_ok:
            obj_to_save = ( self.data_manager.img_trans_dict,
                            self.data_manager.state_random,
                            self.data_manager.res_list,
                            self.idx_qry,
                            self.timestamp )

            with open(path_pickle, 'wb') as fh:
                pickle.dump(obj_to_save, fh, protocol = pickle.HIGHEST_PROTOCOL)

            print(f"State saved")

        return None


    def loadStateDialog(self):
        path_pickle, is_ok = QtGui.QFileDialog.getOpenFileName(self, 'Save File')

        if is_ok and os.path.exists(path_pickle):
            with open(path_pickle, 'rb') as fh:
                obj_saved = pickle.load(fh)
                self.data_manager.img_trans_dict = obj_saved[0]
                self.data_manager.state_random   = obj_saved[1]
                self.data_manager.res_list       = obj_saved[2]
                self.idx_qry                     = obj_saved[3]
                self.timestamp                   = obj_saved[4]

            self.goEvent()

        return None


    def saveState(self):
        ''' Deprecate.
        '''
        timestamp = self.timestamp

        drc_state = os.path.join(os.getcwd(), "state")
        if not os.path.exists(drc_state): os.makedirs(drc_state)

        fl_pickle = f"{timestamp}.pickle"
        path_pickle = os.path.join(drc_state, fl_pickle)
        if os.path.exists(path_pickle): os.remove(path_pickle)

        obj_to_save = ( self.data_manager.img_trans_dict,
                        self.data_manager.state_random,
                        self.data_manager.res_list,
                        self.idx_qry )

        with open(path_pickle, 'wb') as fh:
            pickle.dump(obj_to_save, fh, protocol = pickle.HIGHEST_PROTOCOL)

        print(f"State saved")

        return None


    def loadState(self):
        ''' Deprecate.
        '''
        timestamp = self.timestamp

        drc_state = os.path.join(os.getcwd(), "state")
        if not os.path.exists(drc_state): os.makedirs(drc_state)

        fl_pickle = f"{timestamp}.pickle"
        path_pickle = os.path.join(drc_state, fl_pickle)

        with open(path_pickle, 'rb') as fh:
            obj_saved = pickle.load(fh)
            self.data_manager.img_trans_dict = obj_saved[0]
            self.data_manager.state_random   = obj_saved[1]
            self.data_manager.res_list       = obj_saved[2]
            self.idx_qry                     = obj_saved[3]
            self.timestamp                   = obj_saved[4]

        self.goEvent()

        return None


    def goEvent(self):
        self.dispImg()

        # Restore the idx to cmp back to 0...
        self.idx_cmp = 0

        return None


    def goEventDialog(self):
        idx, is_ok = QtGui.QInputDialog.getText(self, "Enter the event number to go", "Enter the event number to go")

        if is_ok:
            self.idx_qry = int(idx) - 1    # seqi to python 0-based idx

            # Bound idx within a reasonable range
            self.idx_qry = min(max(0, self.idx_qry), self.num_qry - 1)

            self.dispImg()

            # Restore the idx to cmp back to 0...
            self.idx_cmp = 0

        return None


    def createMenuBar(self):
        menuBar = self.menuBar()

        # File menu
        fileMenu = QtWidgets.QMenu("&File", self)
        menuBar.addMenu(fileMenu)

        fileMenu.addAction(self.loadAction)
        fileMenu.addAction(self.saveAction)

        # Go menu
        goMenu = QtWidgets.QMenu("&Go", self)
        menuBar.addMenu(goMenu)

        goMenu.addAction(self.goAction)

        return None


    def createAction(self):
        self.loadAction = QtWidgets.QAction(self)
        self.loadAction.setText("&Load State")

        self.saveAction = QtWidgets.QAction(self)
        self.saveAction.setText("&Save State")

        self.goAction = QtWidgets.QAction(self)
        self.goAction.setText("&Event")

        return None


    def connectAction(self):
        self.saveAction.triggered.connect(self.saveStateDialog)
        self.loadAction.triggered.connect(self.loadStateDialog)

        self.goAction.triggered.connect(self.goEventDialog)

        return None


    #########################
    ### Keyboard shortcut ###
    #########################
    ## def keyPressEvent(self, event):
    ##     super().keyPressEvent(event)

    ##     if type(event) == QtGui.QKeyEvent:
    ##         if event.key() == QtCore.Qt.Key_Down : self.nextQry()
    ##         if event.key() == QtCore.Qt.Key_Up   : self.prevQry()
    ##         if event.key() == QtCore.Qt.Key_Right: self.nextCmp()
    ##         if event.key() == QtCore.Qt.Key_Left : self.prevCmp()

    ##         if event.key() == QtCore.Qt.Key_J: self.nextQry()
    ##         if event.key() == QtCore.Qt.Key_K: self.prevQry()
    ##         if event.key() == QtCore.Qt.Key_L: self.nextCmp()
    ##         if event.key() == QtCore.Qt.Key_H: self.prevCmp()

    ##         if event.key() == QtCore.Qt.Key_C: self.updateRes()
