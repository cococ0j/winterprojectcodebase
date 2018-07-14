#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is to modify the configuration file (L2A_GIPP.xml) of sen2Cor.
"""


import lxml.etree as ET


def config_sen2cor(sen2cor_xml_path):

    # Please modify available parameters below

    # 0 Nr_Processes
    nr_processes = '1'

    # 1 Target_Directory
    # -- No need to modify here --
    #target_directory = l2a_dir

    # 2 Aerosol_Type
    # -- RURAL, MARITIME, AUTO --
    aerosol_type = "RURAL"

    # 3 mid_Latitude
    # -- SUMMER, WINTER, AUTO --'
    mid_latitude = 'SUMMER'

    # 4 Ozone_Content (if it is set to -1, it will be modified automatically by ozone information collected from data.)
    """
    The atmospheric temperature profile and ozone content in Dobson Unit (DU)
    0: to get the best approximation from metadata
    (this is the smallest difference between metadata and column DU),
    else select one of:
    ==========================================
    For midlatitude summer (MS) atmosphere:
    250, 290, 331 (standard MS), 370, 410, 450
    ==========================================
    For midlatitude winter (MW) atmosphere:
    250, 290, 330, 377 (standard MW), 420, 460
    ==========================================
    """
    ozone_content = '-1'

    # 5 WV_Correction
    # -- 0: No WV correction, 1: only 940 nm bands, 2: only 1130 nm bands , 3: both regions used during wv retrieval, 4: Thermal region --
    wv_correction = '1'

    # 6 VIS_Update_Mode
    # -- 0: constant, 1: variable visibility --
    vis_update_mode = '1'

    # 7 WV_Watermask
    # -- 0: not replaced, 1: land-average, 2: line-average --
    wv_watermask = '1'

    # 8 Cirrus_Correction
    # -- FALSE: no cirrus correction applied, TRUE: cirrus correction applied --
    cirrus_correction = 'TRUE'

    # 9 BRDF_Correction
    # -- 0: no BRDF correction, 1: , 2: ,11, 12, 22, 21: see IODD for explanation --
    brdf_correction = '1'

    # 10 BRDF_Lower_bound
    # -- In most cases, g=0.2 to 0.25 is adequate, in extreme cases of overcorrection g=0.1 should be applied --
    brdf_lower_bound = '0.25'

    # Modification Ends here.
    #############################################################################################################

    # Python script to modify L2A_GIPP.xml file
    tree = ET.parse(sen2cor_xml_path)
    root = tree.getroot()

    for elem in root.iter():

        if elem.tag == 'Nr_Processes':
            elem.text = nr_processes

        #if elem.tag == 'Target_Directory':
        #   elem.text = target_directory

        if elem.tag == 'Aerosol_Type':
            elem.text = aerosol_type

        if elem.tag == 'Mid_Latitude':
            elem.text = mid_latitude

        if elem.tag == 'Ozone_Content':
            elem.text = ozone_content

        if elem.tag == 'WV_Correction':
            elem.text = wv_correction

        if elem.tag == 'VIS_Update_Mode':
            elem.text = vis_update_mode

        if elem.tag == 'WV_Watermask':
            elem.text = wv_watermask

        if elem.tag == 'Cirrus_Correction':
            elem.text = cirrus_correction

        if elem.tag == 'BRDF_Correction':
            elem.text = brdf_correction

        if elem.tag == 'BRDF_Lower_Bound':
            elem.text = brdf_lower_bound

    tree.write(sen2cor_xml_path)

    print 'Load Sen2cor configuration successfully'

"""
if __name__ == "__main__":
    sen2cor_xml_path = '/Users/jibusi/Downloads/winterproject/code/L2A_GIPP.xml'
    l2a_dir = 'test'
    config_sen2cor(sen2cor_xml_path,l2a_dir)
"""




