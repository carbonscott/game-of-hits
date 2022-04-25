#!/usr/bin/env python
# -*- coding: utf-8 -*-


def read_log(file):
    '''Return all lines in the user supplied parameter file without comments.
    ''' 
    # Retrieve key-value information...
    kw_kv     = "KV - " 
    kv_dict   = {}

    # Retrieve data information...
    kw_data   = "DATA - " 
    data_dict = {}
    with open(file,'r') as fh: 
        for line in fh.readlines():
            # Collect kv information...
            if kw_kv in line:
                info = line[line.rfind(kw_kv) + len(kw_kv):]
                k, v = info.split(":", maxsplit = 1)
                if not k in kv_dict: kv_dict[k.strip()] = v.strip()

            # Collect data information...
            if kw_data in line:
                info = line[line.rfind(kw_data) + len(kw_data):]
                k = info.strip().split(",")

                # Remove contents after colon...
                k[1:] = [ i[:i.rfind(":")].strip() for i in k[1:] ]

                # Convert list to tuple...
                k = tuple(k)

                if not k in data_dict: data_dict[k] = True

    ret_dict = { "kv" : kv_dict, "data" : tuple(data_dict.keys()) }

    return ret_dict
