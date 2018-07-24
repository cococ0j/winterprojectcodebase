#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is to modify the configuration file (IOTA2_Example.cfg) for IOTA2.
"""

import os
import ConfigParser

def config_iota2(iota2_config_path, tile_list, start_date, end_date):
    config = ConfigParser.RawConfigParser()

    tile_list_string = " ".join(tile_list)
    start_date_string = start_date.replace('-', '')
    end_date_string = end_date.replace('-', '')


    config.set('chain', 'outputPath', '')
    config.set('chain', 'jobsPath', '')
    config.set('chain', 'logPath', '')
    config.set('chain', 'pyAppPath', '')
    config.set('chain', 'chainName', 'OSO_chain_test')
    config.set('chain', 'nomenclaturePath', '')
    config.set('chain', 'listTile', tile_list_string)
    config.set('chain', 'featuresPath', 'None')
    config.set('chain', 'S2_S2C_Path', '')
    config.set('chain', 'regionPath', '')
    config.set('chain', 'groundTruth', '')
    config.set('chain', 'firstStep', '')
    config.set('chain', 'lastStep', '')
    config.set('chain', 'colorTable', '')

    config.set('Sentinel_2_S2C', 'startDate', start_date_string)
    config.set('Sentinel_2_S2C', 'endDate', end_date_string)
    config.set('Sentinel_2_S2C', 'temporalResolution', '5')

    config.set('GlobChain', 'proj', 'EPSG:3395')
    config.set('Sentinel_2_S2C', 'features', 'NDVI')

    with open(iota2_config_path, 'wb') as configfile:
        config.write(configfile)
