#! /usr/bin/env python
# -*- coding: UTF-8 -*-

'''
This script that take a the satellite data folder name as an input, and the outputs are as follows:
- a text file with all the acquisition dates in ascending order (format yyyymmdd); one date by line
- a bar chart with the acquisition date on the horizontal axis, and the estimated cloud cover in the vertical line. You may

The cloud covering is the 'Cloud_Coverage_Assessment' tag found in the xml file of each SAFE folder:
 <Cloud_Coverage_Assessment>86.49903571428571</Cloud_Coverage_Assessment>

Sample commond:
python extractTempoalDistribution.py -i /Users/jibusi/Downloads/winterproject/data/Bendigo2 -o /Users/jibusi/Downloads/winterproject/data -p /Users/jibusi/Downloads/winterproject/data

'''

import os
import sys
import getopt
import re
import lxml
from xml.etree.ElementTree import iterparse
import re
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

############################################################################


def permute(l, p):
    # assert(len(l) == len(p))
    pofl = [None] * len(l)  # p(l)
    for i in range(0, len(l)):
        pofl[i] = l[p[i]]
    return pofl


############################################################################
def SortDatesPermutation(dates):
    p = [i for i in range(len(dates))]
    dates = list(dates)   # we replace the original with a copy

    for fillslot in range(len(dates) - 1, 0, -1):
        positionOfMax = 0
        for location in range(1, fillslot + 1):
            if dates[location] > dates[positionOfMax]:
                positionOfMax = location

        temp = dates[fillslot]
        dates[fillslot] = dates[positionOfMax]
        dates[positionOfMax] = temp

        # we do the same on p
        temp = p[fillslot]
        p[fillslot] = p[positionOfMax]
        p[positionOfMax] = temp

    return p


############################################################################
def parsexml(xmlfile):

    year = None
    month = None
    day = None
    cloudcover = 0

    # Use iterparse to save memory.
    for event, elem in iterparse(xmlfile):

        if elem.tag == "PRODUCT_START_TIME":

            year = elem.text[0:4]
            month = elem.text[5:7]
            day = elem.text[8:10]
            elem.clear()

        if elem.tag == 'Cloud_Coverage_Assessment':
            cloudcover = float(elem.text)
            elem.clear()
            break

    #date = year + '-' + month + '-' + day
    date = int(year + month + day)

    return date, cloudcover


############################################################################
def plot_cloudcover(dates, cloudcovers, plotfile):

    dates = [pd.to_datetime(d, format='%Y%m%d', errors='ignore') for d in dates]

    plt.ylim((-1, 100))  # set limit of y axis
    plt.bar(dates, cloudcovers, color='orange', alpha=0.6)   # plot bar chart
    plt.scatter(dates, cloudcovers, c='blue', alpha=1)    # plot scatter

    # Customize ticks
    plt.yticks(np.arange(0, 110, 10),
               ('0 %', '10 %', '20 %', '30 %', '40 %', '50 %',
                '60 %', '70 %', '80 %', '90 %', '100 %', '110 %'))
    plt.xticks(rotation=45)
    plt.xlabel('Acquistion Dates')
    plt.ylabel('Cloud Covering')
    plt.savefig(plotfile + '/' + 'figure.pdf', dpi=300, bbox_inches='tight')
    plt.show()


############################################################################
#######################       Main fuction      ############################
############################################################################


# Initialize
inputfile = None
outputfile = None
plotfile = None

# Assess parameters
try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:p:", ["infile=", "outfile=", "plotfile="])
except getopt.GetoptError:
    print 'Error: test_arg.py -i <inputfile> -o <outputfile>'
    print '   or: test_arg.py --infile=<inputfile> --outfile=<outputfile>'
    sys.exit(2)

for opt, arg in opts:

    if opt == "-h":
        print 'test_arg.py -i <inputfile> -o <outputfile>'
        print 'or: test_arg.py --infile=<inputfile> --outfile=<outputfile>'
        sys.exit()

    elif opt in ("-i", "--infile"):
        inputfile = arg

    elif opt in ("-o", "--outfile"):
        outputfile = arg

    elif opt in ("-p", "--plotfile"):
        plotfile = arg

# Main process
if outputfile != None and inputfile != None:

    folder_path = inputfile

    # set default written destination of plot to be the same as the text file path
    if plotfile == None:
        plotfile = outputfile

    sub_folder_list = os.listdir(folder_path)

    # In order to solve duplication of dates, we create a dictionary to store date, cloud covering pairs
    d = {}

    # Each sub-folder represents a satellite product extracted from PEPS
    # In each sub-folder, we collect two information:
    #         1 Acquisition date
    #         2 Cloud covering
    for sub_folder in sub_folder_list:

        if os.path.isdir(folder_path + '/' + sub_folder):

            files = os.listdir(folder_path + '/' + sub_folder)

            for file in files:

                if re.match(r'.*(MTD).*(\.xml)$', file):
                    f = folder_path + "/" + sub_folder + "/" + file
                    date, cloudcover = parsexml(f)
                    if date in d:
                        d[date].append(cloudcover)
                    else:
                        d[date] = [cloudcover]
                    break

    # Create date-cloud list
    dates = []
    cloudcovers = []

    for date, cloudcover in d.iteritems():
        dates.append(date)

        # Take average of cloudcovers in the same day.
        cloudcovers.append(np.mean(cloudcover))

    # Sort dates in ascending order.
    p = SortDatesPermutation(dates)
    dates_sorted = permute(dates, p)
    cloudcovers_sorted = permute(cloudcovers, p)

    # Write dates into destination folder
    write_folder_path = outputfile + '/' + 'acquisition_dates.txt'
    with open(write_folder_path, "w") as output:
        for date in dates_sorted:
            #output.write(date + '\n')
            output.write(str(date) + '\n')
        output.close()

    # plot the cloud covering of the corresponding acquisition date
    plot_cloudcover(dates_sorted, cloudcovers_sorted, plotfile)

    print 'Dates file has been saved to ' + write_folder_path
    print 'Plot has been saved to ' + plotfile + '/' + 'figure.pdf'
