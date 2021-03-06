#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import inspect
import logging
from game_of_hit.data  import DataManager
from game_of_hit       import transform
from game_of_hit.utils import downsample

logger = logging.getLogger(__name__)

class DatasetPreprocess:

    def __init__(self, config_dataset): 
        self.config_dataset = config_dataset
        self.get_panel()

        logger.info(f"___/ Preprocess Settings \___")


    def get_panel(self):
        config_dataset = self.config_dataset

        data_manager = DataManager(config_dataset)

        records = data_manager.get_records()

        panel = data_manager.get_img_by_record(records[0][0])

        ## # Get panel size...
        ## with SPIPanelDataset(config_dataset) as spipanel:
        ##     panel = spipanel.get_panel_and_label(0)[0]

        self.panel = panel

        return None


    def get_panelsize(self):
        self.get_panel()

        return self.panel.shape


    def apply_mask(self):
        panel = self.panel
        size_y, size_x = panel.shape

        # Create a raw mask...
        mask = np.ones_like(panel)

        # Mask out the top 20%...
        top = 0.2
        h_false = int(top * size_y)
        mask_false_area = (slice(0, h_false), slice(0, size_x))
        mask[mask_false_area[0], mask_false_area[1]] = 0

        # Fetch the value...
        self.mask = mask

        logger.info(f"Apply mask.")

        return None


    def apply_augmentation(self):
        ## # Random rotation...
        ## angle = None
        ## center = (524, 506)
        ## trans_random_rotate = transform.RandomRotate(angle = angle, center = center)

        # Random patching...
        num_patch = 5
        ## size_patch_y, size_patch_x = 40, 200
        size_patch_y, size_patch_x = 20, 80
        trans_random_patch  = transform.RandomPatch(num_patch             , size_patch_y     , size_patch_x, 
                                                    var_patch_y    = 0.2  , var_patch_x    = 0.2, 
                                                    is_return_mask = False, is_random_flip = True)
        ## trans_list = [trans_random_rotate, trans_random_patch]
        trans_list = [trans_random_patch]

        # Add augmentation to dataset configuration...
        self.trans_random = trans_list

        logger.info(f"Apply random patching.")

        return None


    def apply_crop(self):
        panel = self.panel
        crop_orig = 250, 250
        crop_end  = panel.shape

        trans_crop = transform.Crop(crop_orig, crop_end)

        self.trans_crop = trans_crop

        logger.info(f"Apply cropping.")

        return None



    def apply_downsample(self):
        resize_y, resize_x = 6, 6
        resize = (resize_y, resize_x) if not None in (resize_y, resize_x) else ()

        self.resize = resize

        logger.info(f"Apply downsampling.")

        return None


    def apply_standardize(self):
        self.trans_standardize = { 1 : transform.hflip, 3 : transform.hflip }

        logger.info(f"Apply standardization.")

        return None


    def apply_zoom(self):
        panel = self.panel
        size_y, size_x = panel.shape

        ## low = 0
        ## high = int(0.6 * size_y)
        mid  = int(0.5 * size_y)
        low  = int(mid - 0.05 * size_y)
        high = int(mid + 0.05 * size_y)

        trans_zoom = transform.RandomPanelZoom(low = low, high = high)

        self.trans_zoom = trans_zoom

        logger.info(f"Apply random zooming. low = {low}, high = {high}.")

        return None


    def apply_noise_poisson(self):
        self.noise_poisson = transform.noise_poisson

        logger.info("Apply Poisson noise. ")

        return None


    def apply_noise_gaussian(self):
        ## scale = 1.0
        scale = 100.0
        sigma = scale * 0.15

        def _noise_gaussian(img):
            return transform.noise_gaussian(img, sigma)

        self.noise_gaussian = _noise_gaussian

        logger.info(f"Apply Gaussian noise. sigma = {sigma}.")

        return None


    def trans(self, img, **kwargs):
        """ The function consumed by dataset class.  
        """
        # Apply mask...
        if getattr(self, "mask", None) is not None: img *= self.mask

        # Apply transformation for standardizing image: low-right corner is the center...
        id_panel = kwargs.get("id_panel")
        if getattr(self, "trans_standardize", None) is not None:
            if id_panel in self.trans_standardize:
                trans = self.trans_standardize[id_panel]
                if inspect.isfunction(trans): img = trans(img)

        # Apply random transform if available???
        if getattr(self, "trans_random", None) is not None:
            for trans in self.trans_random:
                if isinstance(trans, (transform.RandomRotate, transform.RandomPatch)): img = trans(img)

        # Apply crop...
        if getattr(self, "trans_crop", None) is not None: img = self.trans_crop(img)

        # Apply zoom...
        if getattr(self, "trans_zoom", None) is not None: img = self.trans_zoom(img)
        if getattr(self, "RandomPanelZoom", None) is not None: img = self.trans_zoom(img)

        # Resize images...
        if getattr(self, "resize", None) is not None:
            bin_row, bin_col = self.resize
            img = downsample(img, bin_row, bin_col, mask = None)

        # Apply Poisson noise...
        if getattr(self, "noise_poisson", None) is not None:
            img = self.noise_poisson(img)

        # Apply Guassian noise...
        if getattr(self, "noise_gaussian", None) is not None:
            img = self.noise_gaussian(img)

        return img


    def apply(self):
        self.apply_noise_poisson()
        self.apply_noise_gaussian()

        ## self.apply_mask()
        self.apply_standardize()
        ## self.apply_augmentation()
        ## self.apply_crop()
        self.apply_zoom()
        self.apply_downsample()

        self.config_dataset.trans = self.trans

        return None


