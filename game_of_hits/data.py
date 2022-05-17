#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import csv
import h5py
import numpy as np
import random

from game_of_hits.utils  import read_log, set_seed

class DataManager:
    def __init__(self, config_data):
        super().__init__()

        self.path_csv = config_data.path_csv
        self.path_log = config_data.path_log
        self.username = config_data.username
        self.trans    = config_data.trans
        self.seed     = config_data.seed

        set_seed(self.seed)

        self.h5_handle_dict = self.get_h5_handler_from_csv()
        self.records        = self.get_records()

        self.res_list = [ [i[0], None] for i in self.records ]    # Store results in list, modifiable by seq_idx

        self.KEY_TO_IMG = "photons"

        self.img_trans_dict = {}
        self.state_random   = [random.getstate(), np.random.get_state()]


    def get_timestamp(self):
        basename = os.path.basename(self.path_log)
        timestamp = basename[:basename.find(".")]

        return timestamp


    def get_h5_handler_from_csv(self):
        path_csv = self.path_csv

        # Read the csv and collect files to read...
        h5_handle_dict = {}
        with open(path_csv, 'r') as fh:
            lines = csv.reader(fh)

            next(lines)

            for line in lines:
                fl_base, label, drc_root = line
                basename = (fl_base, label)

                fl_h5 = f"{fl_base}.h5"
                path_h5 = os.path.join(drc_root, fl_h5)
                if not basename in h5_handle_dict:
                    h5_handle_dict[basename] = h5py.File(path_h5, 'r')    # !!!Remember to close it

        return h5_handle_dict


    def close_h5_handler(self):
        for h5_handle in self.h5_handle_dict.values(): h5_handle.close()


    def get_records(self):
        path_log = self.path_log

        # Read log file...
        log_dict = read_log(path_log)

        # Obtain history of all tests...
        records = log_dict["data"]

        return records


    def save_random_state(self):
        self.state_random = (random.getstate(), np.random.get_state())

        return None


    def set_random_state(self):
        state_random, state_numpy = self.state_random
        random.setstate(state_random)
        np.random.set_state(state_numpy)


    def get_img_by_record(self, record):
        base, seq_idx, panel_idx, label = record.split()

        basename = (base, label)
        KEY_TO_IMG = self.KEY_TO_IMG
        img = self.h5_handle_dict[basename][KEY_TO_IMG][int(seq_idx)][int(panel_idx)]

        if self.trans is not None:
            k = base, seq_idx, panel_idx, label
            ## if not k in self.img_trans_dict:
            ##     img = self.trans(img, id_panel = int(panel_idx))
            ##     self.img_trans_dict[k] = img
            ## else:
            ##     img = self.img_trans_dict[k]

            # Save random state...
            if not k in self.img_trans_dict:
                self.save_random_state()
                self.img_trans_dict[k] = self.state_random
            else:
                # Access the random state...
                self.state_random = self.img_trans_dict[k]
                self.set_random_state()

            # Process image with the right random state...
            img = self.trans(img, id_panel = int(panel_idx))

        img_norm = (img - np.mean(img)) / np.std(img)

        return img_norm


