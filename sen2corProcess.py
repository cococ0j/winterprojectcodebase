#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is to execute sen2cor processing.
"""


import os
import sys
import re
from lxml import etree
import xml.etree.cElementTree as ET
import getopt
import numpy as np
import pandas as pd

# not offer -h --help option as it is useless in whole process chain.

def modify_ozone(xmlfile,ozone):

    alter = False

    tree = ET.parse(xmlfile)
    root = tree.getroot()

    for elem in root.iter():
        if elem.tag == 'Ozone_Content':
            old_ozone = int(elem.text)

            if old_ozone != ozone:
                elem.text = str(ozone)
                alter = True

    tree.write(xmlfile)

    return alter


def sen2cor_process(sen2cor_xml_path, l1c_product_path):

    # path of L2A_GIPP.xml
    l2a_gipp = sen2cor_xml_path

    # Read OzoneLUT.csv
    ozone_LUT = pd.read_csv('OzoneLUT.csv')

    # Get current input directory of L1C product.
    folder_path = l1c_product_path
    # Get a list of L1C files
    sub_folder_list = os.listdir(folder_path)

    for sub_folder in sub_folder_list:
        # Process one by one using sen2cor with user's configuration
        tile_folder = folder_path + '/' + sub_folder

        if os.path.isdir(tile_folder):

            # Recognise Date
            date = re.findall(r'\d{8}', sub_folder)[0]
            month = int(date[4, 6])
            day = int(date[6:])
            ozone = ozone_LUT.loc[(ozone_LUT.month == month) & (ozone_LUT.day == day), 'roundOzone']

            # Alter the L2A_GIPP.xml
            alter = modify_ozone(l2a_gipp, ozone)

            # if Ozone_content is modified
            if alter:
                sen2cor_command = "python L2A_Process %s --resolution=10  --refresh --GIP_L2A %s" %(tile_folder,sen2cor_xml_path)

            # if Ozone_content keeps the same as last file.
            else:
                sen2cor_command = "python L2A_Process %s --resolution=10 --GIP_L2A %s" %(tile_folder,sen2cor_xml_path)

            os.system(sen2cor_command)


    print '############################################################'
    print 'L1C to L2A processing done.'
    print '############################################################'



