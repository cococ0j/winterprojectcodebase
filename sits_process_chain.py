#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
This script is to concatenate all three process stages.
"""



import time
import os
import os.path
import lxml.etree as ET
import optparse
import sys
import datetime



from config_sen2cor import *
from sen2cor_process import *
import logging



class OptionParser (optparse.OptionParser):

    def check_required(self, opt):
        option = self.get_option(opt)

        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)


def print_config(sen2cor_xml_path=None, maja_xml_path=None):

    sen2cor_tag = ['Nr_Processes', 'Aerosol_Type', 'Mid_Latitude', 'Ozone_Content', 'WV_Correction', 'VIS_Update_Mode', 'WV_Watermask' \
        'Cirrus_Correction', 'BRDF_Correction', 'BRDF_Lower_Bound']

    maja_tag = []

    if sen2cor_xml_path is not None:

        tree1 = ET.parse(sen2cor_xml_path)
        root1 = tree1.getroot()

        for elem in root1.iter():
            if elem.tag in sen2cor_tag:
                print elem.tag + ' ' + ':' + ' ' + elem.text

    if maja_xml_path is not None:

        tree2 = ET.parse(maja_xml_path)
        root2 = tree2.getroot()

        for elem in root2.iter():
            if elem.tag in maja_tag:
                print elem.tag + ' ' + ':' + ' ' + elem.text


def compare_dict(d1,d2):
    d3 = {}
    existed = []
    for t1, l1 in d1.iteritems():
        if t1 in d2:
            for v1 in l1:
                keyword_v1 = v1[:3] + v1[11:]
                for v2 in d2[t1]:
                    keyword_v2 = v2[:3] + v2[11:]
                    if keyword_v1 == keyword_v2:
                        existed.append(v1)
                        break
            temp = [v3 for v3 in l1 if v3 not in existed]
            if len(temp) != 0:
                d3[t1] = temp

        else:
            d3[t1] = l1
    return d3





#==================
#parse command line
#==================
if len(sys.argv) == 1:
    prog = os.path.basename(sys.argv[0])
    print '      '+sys.argv[0]+' [options]'
    print "     Aide : ", prog, " --help"
    print "        ou : ", prog, " -h"
    print "example 1 : python %s -t [54HYE,54HBV] -d 2018-04-01 -f 2018-05-31 -w /Users/jibusi/Downloads/winterproject/data/test" %sys.argv[0]
    print "example 2 : python %s -t [54HYE,54HBV] -d 2018-04-01 -f 2018-05-31 -w /Users/jibusi/Downloads/winterproject/data/test --s1 TRUE --s2 TRUE --lp sen2cor --up 95"%sys.argv[0]
    sys.exit(-1)
else :
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage)

    parser.add_option("-t","--tilelist", dest="tile_list", action="store", type="string",
            help="a list of tiles you are going to process, delimit by comma",default=None)

    parser.add_option("-d", "--start_date", dest="start_date", action="store", type="string",
                      help="start date, fmt('2015-12-22')", default=None)

    parser.add_option("-f", "--end_date", dest="end_date", action="store", type="string",
                      help="end date, fmt('2015-12-23')", default=None)

    parser.add_option("-w", "--write_dir", dest="write_dir", action="store", type="string",
                      help="Path of main directory of this process", default=None)

    parser.add_option("--s1", "--save_l1c",dest="save_l1c",action="store",type="string",
                      help="The choice of saving L1C files or not, default is TRUE ", default='TRUE')

    parser.add_option("--s2", "--save_l2a", dest="save_l2a", action="store", type="string",
                      help="The choice of saving L2A files or not, default is TRUE ", default='TRUE')

    parser.add_option("--lp","--l2a_processor",dest="l2a_processor",action='store',type="string",
                      help="Choose processors from sen2cor or maja. Default is sen2cor.", default='sen2cor')

    # Add option of choose cloudCover
    parser.add_option("--ll", "--lower_limit", dest="lower_limit", action="store", type="float",
                      help="lower limit in cloud cover", default=0)
    parser.add_option("--ul", "--upper_limit", dest="upper_limit", action="store", type="float",
                      help="upper limit in cloud cover", default=95)

    # Add two process flags
    parser.add_option("--fs", "--first_step", dest="first_step", action="store", type="string",
                      help="Whether running peps download or not, default is TRUE ", default='TRUE')

    parser.add_option("--ls", "--last_step", dest="last_step", action="store", type="string",
                      help="Whether running iota2 processing or not, default is TRUE ", default='TRUE')

    (options, args) = parser.parse_args()



if options.tile_list is None or options.start_date is None or options.end_date is None or options.write_dir is None:
    print 'Please make enter all necessary parameters, including tile_list,  start_date, end_date and write_dir'
    sys.exit(-1)

# list all parameters
tile_list = [i.strip() for i in options.tile_list.lstrip('[').rstrip(']').split(',')]
start_date = options.start_date
end_date = options.end_date
l2a_processor = options.l2a_processor

save_l1c = options.save_l1c.lower() == 'true'
save_l2a = options.save_l2a.lower() == 'true'

# two flags
first_step = options.first_step.lower() == 'true'
last_step = options.last_step.lower() == 'true'

# cloud cover parameters of catalog request
lower_limit = options.lower_limit
upper_limit = options.upper_limit

# list all path
# check saving directory exist, if not create these directories

execute_time = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

# Main path
write_dir = options.write_dir
if not os.path.exists(write_dir):
    os.system('mkdir %s' %(write_dir))

# Main L1C path
l1c_dir = options.write_dir + '/' + 'L1C'

# Main L2A path
l2a_dir = options.write_dir + '/' + "L2A"

# Main GAP path
gap_dir = options.write_dir + '/' + "GAP"

# Main AUX path
aux_dir = options.write_dir + '/' + 'AUX'
if not os.path.exists(aux_dir):
    os.system('mkdir %s'%(aux_dir))

# Copy L2A_GIPP.xml to aux_dir
os.system('cp L2A_GIPP.xml %s'%(aux_dir))

sen2cor_xml_path = aux_dir + '/' + 'L2A_GIPP.xml'


# Create log
log_file = aux_dir + '/' + execute_time + '.log'
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
logging.info('Tile list: %s', options.tile_list)
logging.info('Start date: %s', start_date)
logging.info('End date: %s', end_date)
logging.info('L2A Processor: %s', l2a_processor)
logging.info("Cloud covering: [%s, %s]", options.lower_limit, options.upper_limit)
logging.info('Save L1C: %s', options.save_l1c)
logging.info('Save L2A: %s', options.save_l2a)

############################################
############### Configuration ##############

if l2a_processor == 'sen2cor':

    # configure sen2cor
    config_sen2cor(sen2cor_xml_path)

    # Print Sen2Cor configuration
    print '###########################################################'
    print '################## Sen2Cor configuration ##################'
    print_config(sen2cor_xml_path)
    print '###########################################################'

if l2a_processor == 'maja':
    pass



############################################
############ PEPS Download process #########

# if choosing to running peps download step.
if first_step:

    # Download process
    # Create main l1c product directory
    if not os.path.exists(l1c_dir):
        os.system('mkdir %s' % (l1c_dir))

    # Update log file
    logging.info("The following are peps download records. ")
    cur_work_dir = os.getcwd()
    peps_dir = cur_work_dir + '/' + 'peps_download.py'


    for tile in tile_list:

        # l1c product folder path by tiles
        l1c_tile_dir = l1c_dir + "/" + 'T' + tile
        if not os.path.exists(l1c_tile_dir):
            os.system('mkdir %s' % (l1c_tile_dir))

        # list of existing files
        cur_num_files_in_tile_dir = os.listdir(l1c_tile_dir)

        peps_command = 'python %s -t %s -a peps.txt -d %s -f %s -c S2ST --ll %d --ul %d -w %s 2>&1 | tee -a %s' % (
        peps_dir, tile, start_date, end_date,
        lower_limit, upper_limit, l1c_tile_dir, log_file)
        os.system(peps_command)

        # Delete tmp files
        delete_tmp = 'find %s -type f -name "*tmp" -delete' % (l1c_tile_dir)
        os.system(delete_tmp)

        # Delete .DS_Store for macOS
        # os.system('rm %s/.DS_Store' % (l1c_tile_dir))

        # list of files after downloading
        after_num_files_in_tile_dir = os.listdir(l1c_tile_dir)

        # check whether there is no data for current tile or no new data for current tile
        if len(after_num_files_in_tile_dir) == 0:
            logging.error("Error: There is no data for tile %s on date from %s to %s.", tile, start_date, end_date)
            print "Error: There is no data for tile %s on date from %s to %s." % (tile, start_date, end_date)
            print "*******************************************************************"
            remove_empty_tile_dir = "rm -r %s" %(l1c_tile_dir)
            os.system(remove_empty_tile_dir)
            continue

        if len(cur_num_files_in_tile_dir) == len(after_num_files_in_tile_dir):
            logging.warning("Warning: There is no new data for tile %s on date from %s to %s.", tile, start_date, end_date)
            print "Warning: There is no new data for tile %s on date from %s to %s." % (tile, start_date, end_date)
            print "*******************************************************************"
            continue

        logging.info('The following is unzipping %s data.', tile)
        print "############### Unzip SAFE folders ################ "
        # Unzip SAVE folders
        unzip_command = 'cd %s && unzip \'*.zip\' 2>&1 | tee -a %s' % (l1c_tile_dir, log_file)
        os.system(unzip_command)
        print "############### Unzip finished ################ "

        # Delete zip files
        delete_zip = 'find %s -type f -name "*.zip" -delete' % (l1c_tile_dir)
        os.system(delete_zip)





############################################
#########  Atmospheric Correction ##########

# Record tiles in L1C folder
if not os.path.exists(l1c_dir):

    print "Please provide at least one L1C product in your L1C directory before running Atmospheric Correction"
    print "****************************************************************************************************"
    logging.error(
        "Error: Please provide at least one L1C product in your L1C directory before running Atmospheric Correction")
    sys.exit(-2)

else:
    l1c_dir_tiles_list = os.listdir(l1c_dir)  # for linux
    # l1c_dir_tiles_list = [i for i in os.listdir(l1c_dir) if i != '.DS_Store']  # For macOS

    if len(l1c_dir_tiles_list) == 0:
        logging.error("Error: Please provide at least one L1C product in your L1C directory before running Atmospheric Correction")
        print "Error: Please provide at least one L1C product in your L1C directory before running Atmospheric Correction"
        print "***********************************************************************************************************"
        os.system('rm -r %s' % l1c_dir)
        sys.exit(-2)

    l1c_data_existing = {}

    for l1c_dir_tile in l1c_dir_tiles_list:
        l1c_dir_tile_dir = l1c_dir + '/' + l1c_dir_tile
        l1c_data_existing[l1c_dir_tile] = os.listdir(l1c_dir_tile_dir) # for linux
        # l1c_data_existing[l1c_dir_tile] = [i for i in os.listdir(l1c_dir_tile_dir) if i != '.DS_Store']  # for macOS

    # Check whether L2A the folder exist
    if not os.path.exists(l2a_dir):

        # if l2a_dir doesn't exist, make l2a_dir, and run sen2cor without consideration of existing L2A products
        os.system('mkdir %s' % (l2a_dir))

        l1c_data_waiting_process = l1c_data_existing

        print "************ L1C data list for Atmospheric Correction *************"
        logging.info("L1C data list for Atmospheric Correction as follows:")
        for tile_name, safe_folder_names_list in l1c_data_waiting_process.iteritems():
            logging.info("Tile: %s", tile_name)
            print "Tile: %s" % (tile_name)
            for safe_folder_name in safe_folder_names_list:
                logging.info("L1C product: %s", safe_folder_name)
                print "L1C product: %s" % (safe_folder_name)
        print "*******************************************************************"

        if l2a_processor == 'sen2cor':

            # Sen2cor process
            logging.info('The following is the log of Sen2Cor Atmospheric Correction')
            print "************* Sen2Cor Atmospheric Correction *************"


            for l1c_dir_tile, l1c_dir_tiles_list in l1c_data_waiting_process.iteritems():
                l1c_dir_tile_dir = l1c_dir + '/' + l1c_dir_tile
                l2a_dir_tile_dir = l2a_dir + '/' + l1c_dir_tile
                if not os.path.exists(l2a_dir_tile_dir):
                    os.system("mkdir %s" % l2a_dir_tile_dir)
                for l1c_dir_tile_dir_safe in l1c_dir_tiles_list:
                    l1c_dir_tile_dir_safe_path = l1c_dir_tile_dir + '/' + l1c_dir_tile_dir_safe
                    sen2cor_process(sen2cor_xml_path, l1c_dir_tile_dir_safe_path, l2a_dir_tile_dir, log_file)

            print "************ Atmospheric Correction Finished *************"
            logging.info('Sen2cor Atmospheric Correction Finished')


        if l2a_processor == 'maja':
            # MAJA process
            pass


    else:
        # if l2a_dir exists, we should find out how many new l2a products are waiting for processing.
        l2a_dir_tiles_list = os.listdir(l2a_dir) # For linux
        # l2a_dir_tiles_list = [i for i in os.listdir(l2a_dir) if i != '.DS_Store'] # for macOS
        l2a_data_existing = {}
        for l2a_dir_tile in l2a_dir_tiles_list:
            l2a_dir_tile_dir = l2a_dir + '/' + l2a_dir_tile
            l2a_data_existing[l2a_dir_tile] = os.listdir(l2a_dir_tile_dir)  # For linux
            # l2a_data_existing[l2a_dir_tile] = [i for i in os.listdir(l2a_dir_tile_dir) if i != '.DS_Store']  # For macOS

        # Compare l1c_data_existing and l2a_data_existing to find out how many l1c data to process. And also record to log file and display
        l1c_data_waiting_process = compare_dict(l1c_data_existing, l2a_data_existing)


        print "************ L1C data list for Atmospheric Correction *************"
        logging.info("L1C data list for Atmospheric Correction as follows:")
        for tile_name, safe_folder_names_list in l1c_data_waiting_process.iteritems():
            logging.info("Tile: %s",tile_name)
            print "Tile: %s" %(tile_name)
            for safe_folder_name in safe_folder_names_list:
                logging.info("L1C product: %s",safe_folder_name)
                print "L1C product: %s" %(safe_folder_name)
        print "*******************************************************************"

        if l2a_processor == "sen2cor":

            # Sen2cor process
            print "************  Sen2Cor Atmospheric Correction   *************"
            logging.info("The following is the log of Sen2Cor Atmospheric Correction")
            for l1c_dir_tile, l1c_dir_tiles_list in l1c_data_waiting_process.iteritems():
                l1c_dir_tile_dir = l1c_dir + '/' + l1c_dir_tile
                l2a_dir_tile_dir = l2a_dir + '/' + l1c_dir_tile
                if not os.path.exists(l2a_dir_tile_dir):
                    os.system("mkdir %s" % l2a_dir_tile_dir)
                for l1c_dir_tile_dir_safe in l1c_dir_tiles_list:
                    l1c_dir_tile_dir_safe_path = l1c_dir_tile_dir + '/' + l1c_dir_tile_dir_safe
                    sen2cor_process(sen2cor_xml_path, l1c_dir_tile_dir_safe_path, l2a_dir_tile_dir, log_file)
            print "************  Sen2Cor Atmospheric Correction Finished *************"
            logging.info("Sen2Cor Atmospheric Correction Finished")

        if l2a_processor == "maja":
            # MAJA process
            pass




# Delete L1C files
if not save_l1c:
    #delete_l1c = 'find %s -type d -name "*.SAFE" -exec rm -r {} +'%(l1c_dir)
    delete_l1c = 'rm -r %s' %(l1c_dir)
    os.system(delete_l1c)


# IOTA2 process
# Update log file
# if last_step:
#    pass
#if not os.path.exists(gap_dir):
#    os.system('mkdir %s'%(gap_dir))
