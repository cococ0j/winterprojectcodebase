#! /usr/bin/env python
# -*- coding: UTF-8 -*-


import os
import sys
import re
import lxml
import getopt

# not offer -h --help option as it is useless in whole process chain.

# Get current input directory of L1C product.
folder_path = inputdirectory
# Get a list of L1C files
sub_folder_list = os.listdir(folder_path)

for sub_folder in sub_folder_list:
    # Process one by one using sen2cor with user's configuration
    if os.path.isdir(folder_path + '/' + sub_folder):

        sen2cor_command = "python L2A_Process %s --resolution=10" % (folder_path + '/' + sub_folder)

        os.system(process_command)


# Print 'Done'
print '############################################################'
print 'L1C to L2A processing done.'
print '############################################################'
