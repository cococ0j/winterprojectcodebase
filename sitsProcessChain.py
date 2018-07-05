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
from configSen2cor import *
from sen2corProcess import *



class OptionParser (optparse.OptionParser):

    def check_required(self, opt):
        option = self.get_option(opt)

        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)


def print_config(sen2cor_xml_path=None, maja_xml_path=None):

    sen2cor_tag = ['Nr_Processes','Target_Directory', 'Aerosol_Type', 'Mid_Latitude', 'Ozone_Content', 'WV_Correction', 'VIS_Update_Mode', 'WV_Watermask' \
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


#==================
#parse command line
#==================
if len(sys.argv) == 1:
    prog = os.path.basename(sys.argv[0])
    print '      '+sys.argv[0]+' [options]'
    print "     Aide : ", prog, " --help"
    print "        ou : ", prog, " -h"
    print "example 1 : python %s -t [54HYE,54HBV] -d 2018-04-01 -f 2018-05-31 -w /Users/jibusi/Downloads/winterproject/data/test" %sys.argv[0]
    print "example 2 : python %s -t [54HYE,54HBV] -d 2018-04-01 -f 2018-05-31 -w /Users/jibusi/Downloads/winterproject/data/test -c L1C_test1 -a L2A_test1 -" \
          "-g GAP_test1 --s1 TRUE --s2 TRUE --lp sen2cor --up 95"%sys.argv[0]
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

    parser.add_option("-c", "--l1c_dir", dest="l1c_dir", action="store", type="string",
                      help="Path of L1C products", default='L1C')

    parser.add_option("-a", "--l2a_dir", dest="l2a_dir", action="store", type="string",
                      help="Path of L2A products", default='L2A')

    parser.add_option("-g", "--gap_dir", dest="gap_dir", action="store", type="string",
                      help="Path of final data after gap-filling", default='GAP')

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

    (options, args) = parser.parse_args()

if options.tile_list is None or options.start_date is None or options.end_date is None or options.write_dir is None:
    print 'Please make enter all necessary parameters, including tile_list,  start_date, end_date and write_dir'
    sys.exit(-1)

# list all parameters
tile_list = options.tile_list.lstrip('[').rstrip(']').split(',')
start_date = options.start_date
end_date = options.end_date
l2a_processor = options.l2a_processor

save_l1c = options.save_l1c.lower() == 'true'
save_l2a = options.save_l2a.lower() == 'true'

# cloud cover parameters of catalog request
lower_limit = options.lower_limit
upper_limit = options.upper_limit

# list all path
# check saving directory exist, if not create these directories

execute_time = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")

# main path
write_dir = options.write_dir
if not os.path.exists(write_dir):
    os.system('mkdir %s' %(write_dir))

# L1C path
if options.l1c_dir == 'L1C':   # use default value
    l1c_dir = options.write_dir + '/' + options.l1c_dir + '_' + execute_time
else:  # user defined
    if options.l1c_dir[0] == '.':                  # if relative path
        l1c_dir = options.write_dir + options.l1c_dir[1:]
    else:
        l1c_dir = options.write_dir + '/' + options.l1c_dir
if not os.path.exists(l1c_dir):
    os.system('mkdir %s'%(l1c_dir))

# L2A path
if options.l2a_dir == 'L2A':  # use default value
    l2a_dir = options.write_dir + '/' + options.l2a_dir + '_' + execute_time
else:  # user defined
    if options.l2a_dir[0] == '.':                  # if relative path
        l2a_dir = options.write_dir + options.l2a_dir[1:]
    else:
        l2a_dir = options.write_dir + '/' + options.l2a_dir
if not os.path.exists(l2a_dir):
    os.system('mkdir %s'%(l2a_dir))

# GAP path
if options.gap_dir == 'GAP':
    gap_dir = options.write_dir + '/' + options.gap_dir + '_' + execute_time
else:    # user defined
    if options.gap_dir[0] == '.':   # relative path
        gap_dir = options.write_dir + options.gap_dir[1:]
    else:
        gap_dir = options.write_dir + '/' + options.gap_dir
if not os.path.exists(gap_dir):
    os.system('mkdir %s'%(gap_dir))

# AUX path
aux_dir = options.write_dir + '/' + 'AUX' + '_' + execute_time
if not os.path.exists(aux_dir):
    os.system('mkdir %s'%(aux_dir))

# Copy L2A_GIPP.xml to aux_dir
os.system('cp L2A_GIPP.xml %s'%(aux_dir))

sen2cor_xml_path = aux_dir + '/' + 'L2A_GIPP.xml'



# configure sen2cor
if l2a_processor == 'sen2cor':
    config_sen2cor(sen2cor_xml_path, l2a_dir)

    # Print Sen2Cor configuration
    print '###########################################################'
    print '################## Sen2Cor configuration ##################'
    print_config(sen2cor_xml_path)
    print '###########################################################'

"""
#Print all configuration for this process chain.
#Peps configuration
#MAJA configuration
print '###########################################################'
print '################## MAJA configuration ##################'
print '\n'
print_config(maja_config_path)
# IOTA2 configuration
"""

############################################
############ Main Processing Loop ##########

# Download process
# Update log file
cur_work_dir = os.getcwd()
peps_dir = cur_work_dir + '/' + 'pepsDownload.py'
for tile in tile_list:
    peps_command = 'python %s -t %s -a peps.txt -d %s -f %s -c S2ST --ll %d --ul %d -w %s' %(peps_dir, tile,start_date,end_date,
                                                                                                        lower_limit,upper_limit,l1c_dir)
    os.system(peps_command)

# Unzip SAVE folders
print "############### Unzip SAFE folders ################ "
unzip_command = 'cd %s && unzip \'*.zip\''%(l1c_dir)
os.system(unzip_command)
print "############### Unzip finished ################ "

# Sen2cor process
# check whether the folder exist
# Update log file

if l2a_processor == 'sen2cor':
    print "************* Sen2Cor Atomspheric Correction *************"
    sen2cor_process(sen2cor_xml_path, l1c_dir)



# MAJA process
# Update log file

# IOTA2 process
# Update log file
