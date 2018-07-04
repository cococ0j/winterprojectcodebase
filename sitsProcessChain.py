#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
This script is to concatenate all three process stages.
'''




import re
from lxml import etree
import xml.etree.cElementTree as ET
import getopt
import numpy as np
import pandas as pd
import time
import os, os.path, optparse, sys
from datetime import date


from peps_download import *
from configureSen2cor import *
from sen2corProcess import *



class OptionParser (optparse.OptionParser):

    def check_required (self, opt):
        option = self.get_option(opt)

        # Assumes the option's 'default' is set to None!
        if getattr(self.values, option.dest) is None:
            self.error("%s option not supplied" % option)


def print_config(sen2cor_xml_path = None,maja_xml_path = None):

    sen2cor_tag = ['Target_Directory','Aerosol_Type','mid_Latitude', 'Ozone_Content', 'WV_Correction', 'VIS_Update_Mode', 'WV_ Watermask' \
        'Cirrus_Correction', 'BRDF_Correction', 'BRDF_Lower_bound']

    maja_tag = []

    if sen2cor_xml_path is not None:

        tree1 = ET.parse(sen2cor_xml_path)
        root1 = tree1.getroot()

        for elem in root1.iter():
            if elem in sen2cor_tag:
                print elem.tag + ' ' + ':' + ' ' + elem.text

    if maja_xml_path is not None:

        tree2 = EF.parse(maja_xml_path)
        root2 = tree2.getroot()

        for elem in root2.iter():
            if elem in maja_tag:
                print elem.tag + ' ' + ':' + ' ' + elem.text


#==================
#parse command line
#==================
if len(sys.argv) == 1:
    prog = os.path.basename(sys.argv[0])
    print '      '+sys.argv[0]+' [options]'
    print "     Aide : ", prog, " --help"
    print "        ou : ", prog, " -h"
    print "example 1 : python %s -l 'Toulouse' -a peps.txt -d 2016-12-06 -f 2017-02-01 -c S2ST" %sys.argv[0]
    print "example 2 : python %s --lon 1 --lat 44 -a peps.txt -d 2015-11-01 -f 2015-12-01 -c S2"%sys.argv[0]
    print "example 3 : python %s --lonmin 1 --lonmax 2 --latmin 43 --latmax 44 -a peps.txt -d 2015-11-01 -f 2015-12-01 -c S2"%sys.argv[0]
    print "example 4 : python %s -l 'Toulouse' -a peps.txt -c SpotWorldHeritage -p SPOT4 -d 2005-11-01 -f 2006-12-01"%sys.argv[0]
    print "example 5 : python %s -c S1 -p GRD -l 'Toulouse' -a peps.txt -d 2015-11-01 -f 2015-12-01"%sys.argv[0]
    sys.exit(-1)
else :
    usage = "usage: %prog [options] "
    parser = OptionParser(usage=usage)

    parser.add_option("-t","--tilelist", dest="tile_list", action="store", type="string", \
            help="a list of tiles you are going to process, delimit by comma",default=None)

    parser.add_option("-d", "--start_date", dest="start_date", action="store", type="string", \
                      help="start date, fmt('2015-12-22')", default=None)

    parser.add_option("-f", "--end_date", dest="end_date", action="store", type="string", \
                      help="end date, fmt('2015-12-23')", default=None)

    parser.add_option("-w", "--write_dir", dest="write_dir", action="store", type="string", \
                      help="Path of main directory of this process", default=None)

    parser.add_option("-c", "--l1c_dir", dest="l1c_dir", action="store", type="string", \
                      help="Path of L1C products", default='L1C')

    parser.add_option("-a", "--l2a_dir", dest="l2a_dir", action="store", type="string", \
                      help="Path of L2A products", default='L2A')

    parser.add_option("-g", "--gap_dir", dest="gap_dir", action="store", type="string", \
                      help="Path of final data after gap-filling", default='GAP')

    parser.add_option("--s1", "--save_l1c",dest="save_l1c",action="store",type="string",
                      help="The choice of saving L1C files or not, default is TRUE ", default='TRUE')

    parser.add_option("--s2", "--save_l2a", dest="save_l2a", action="store", type="string",
                      help="The choice of saving L2A files or not, default is TRUE ", default='TRUE')

    parser.add_option("-p","--processor",dest="processor",action='store',type="string",
                      help="Choose processors from sen2cor or maja. Default is sen2cor.", default='sen2cor')

    (options, args) = parser.parse_args()

if options.tile_list is None or options.start_date is None or options.end_date is None or options.write_dir is None:
    print 'Please make enter all necessary parameters, including tile_list,  start_date, end_date and write_dir'
    sys.exit(-1)

# list all parameters
tile_list = options.tile_list.lstrip('[').rstrip(']').split(',')
start_date = options.start_date
end_date = options.end_date
processor = options.processor

save_l1c = options.save_l1c.lower() == 'true'
save_l2a = options.save_l2a.lower() == 'true'

# list all path
# check saving directory exist, if not create these directories
# main path
write_dir = options.write_dir
if not os.path.exists(write_dir):
    os.system('mkdir %s'%(write_dir))

# L1C path
if options.l1c_dir[0] == '.':
    l1c_dir = option.write_dir + options.l1c_dir[1:]
else:
    l1c_dir = option.write_dir + '/' + options.l1c_dir
if not os.path.exists(l1c_dir):
    os.system('mkdir %s'%(l1c_dir))

# L2A path
if options.l2a_dir[0] == '.':
    l2a_dir = option.write_dir + options.l2a_dir[1:]
else:
    l2a_dir = options.write_dir + '/' + options.l2a_dir
if not os.path.exists(l2a_dir):
    os.system('mkdir %s'%(l2a_dir))

# GAP path
if options.gap_dir[0] == '.':
    gap_dir = option.write_dir + options.gap_dir[1:]
else:
    gap_dir = options.write_dir + '/' + options.gap_dir
if not os.path.exists(gap_dir):
    os.system('mkdir %s'%(gap_dir))

# AUX path
aux_dir = options.write_dir + '/' + 'AUX'
if not os.path.exists(aux_dir):
    os.system('mkdir %s'%(aux_dir))

# Copy L2A_GIPP.xml to aux_dir
os.system('cp L2A_GIPP.xml %s'%(aux_dir))

sen2cor_xml_path = aux_dir + '/' + 'L2A_GIPP.xml'



# configure sen2cor
config_sen2cor(sen2cor_xml_path, l2a_dir)


# Print all configuration for this process chain.
# Peps configuration

# Sen2Cor configuration
print '###########################################################'
print '################## Sen2Cor configuration ##################'
print '\n'
print_config(sen2cor_xml_path)

# MAJA configuration
#print '###########################################################'
#print '################## MAJA configuration ##################'
#print '\n'
#print_config(maja_config_path)

# IOTA2 configuration

############################################
############ Main Processing Loop ##########

# Download process
# Update log file

# Sen2cor process
# check whether the folder exist
# Update log file

# MAJA process
# Update log file

# IOTA2 process
# Update log file