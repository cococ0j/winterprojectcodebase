#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is to execute sen2cor processing.
"""


import os
import re
import lxml.etree as ET
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




def sen2cor_process(sen2cor_xml_path, l1c_product_path, l2a_product_path, log_file):

    # path of L2A_GIPP.xml
    l2a_gipp = sen2cor_xml_path

    # Get current input directory of L1C product.
    safe_folder_path = l1c_product_path


    # Parse ozone parameter
    tree = ET.parse(l2a_gipp)
    root = tree.getroot()

    for elem in root.iter():
        if elem.tag == 'Ozone_Content':
            old_ozone = int(elem.text)
        if elem.tag == 'Target_Directory':
            elem.text = l2a_product_path
    tree.write(l2a_gipp)


    if old_ozone == -1:
        # if user set ozone to -1, the following code collects ozone information from OzoneLUT.csv and modify ozone
        # parameter for each L1C product.
        # Read OzoneLUT.csv
        ozone_LUT = pd.read_csv('OzoneLUT.csv')

        # Recognise Date
        date = re.findall(r'\d{8}', safe_folder_path[-66:-1])[0]
        month = int(date[4:6])
        day = int(date[6:])
        ozone = int(ozone_LUT.loc[(ozone_LUT.month == month) & (ozone_LUT.day == day), 'roundOzone'])


        # Alter the L2A_GIPP.xml
        alter = modify_ozone(l2a_gipp, ozone)
        # if Ozone_content is modified
        if alter:
            sen2cor_command = "L2A_Process %s --resolution=10 --refresh --GIP_L2A %s 2>&1 | tee -a %s" % (
                safe_folder_path, sen2cor_xml_path, log_file)

        # if Ozone_content keeps the same as last file.
        else:
            sen2cor_command = "L2A_Process %s --resolution=10 --GIP_L2A %s 2>&1 | tee -a %s" % (
                safe_folder_path, sen2cor_xml_path, log_file)
        os.system(sen2cor_command)
        print '############################################################'

    else:
        # if user set ozone to one number other than -1, ozone will keep using the same Ozone throughout all L1C products.
        sen2cor_command = "L2A_Process %s --resolution=10 --refresh --GIP_L2A %s 2>&1 | tee -a %s" % (
                safe_folder_path,  sen2cor_xml_path, log_file)

        os.system(sen2cor_command)
        print '############################################################'





