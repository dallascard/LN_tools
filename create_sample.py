# -*- coding: utf-8 -*-
"""

This file contains some general tools for sampling, splitting, shortening and
summarizing  articles from Lexis Nexis. In all cases, it takes as input json
files produced by parse_LN_to_JSON.py and duplication information from
find_duplicates.py

"""

# import modules
from os import path, makedirs
from optparse import OptionParser
from json import loads, dump
import codecs
import numpy
import csv
import re
import glob
import operator


usage = "\n%prog project_dir [options]"
parser = OptionParser(usage=usage)
parser.add_option('-s', help='sample SIZE [default = %default]', metavar='sample_size', default=500)
parser.add_option('-n', help='secondary sample SIZE [default = %default]', metavar='secondary_size', default=100)
parser.add_option('-f', help='Ignore documents before this number [default = %default]', metavar='start', default=None)
parser.add_option('-i', help='Initial folder number [default = %default]', metavar='init', default=1)

(options, args) = parser.parse_args()

if len(args) < 1:
	sys.exit("Error: Please provide a project directory")

project_dir = args[0]
metadata_dir = project_dir + '/metadata/'
duplicates_file = metadata_dir + 'duplicates.json'
csv_file_name = metadata_dir + 'sample.csv'
json_file_name = metadata_dir + 'sample.json'
	
sample_size = int(options.s)
subsample_size = int(options.n)
nSubsamples = int(sample_size / subsample_size)
start = options.f
if start is not None:
    start = int(start)
init_folder = int(options.i)

# read in the JSON file and unpack it
input_file = codecs.open(duplicates_file, encoding='utf-8')
input_text = input_file.read()
input_file.close()    
doc = loads(input_text, encoding='utf-8')

cases_by_year = {}      # a dictionary of case ids indexed by year
case_years = {}         # a dictionary of years indexed by case ids
duplicates = {}         # a dictionary of duplicates indexed by case id

# convert the json keys (strings) into case ids (ints)
case_ids = []
keys = doc.keys()
for k in keys:
    if int(k) >= start:
        case_ids.append(int(k))

# for each case, get the year and duplicates
nCases = len(case_ids)
for c in case_ids:
    # get the data associated with this case id from the json object
    data = doc[str(c)]
    # year is the first thing in the list
    year = data[0]
    # a list of duplicates is the second thing in the list
    duplicates[c] = data[1]
    # add the year and case combinations to the two dictionaries
    case_years[c] = year
    if cases_by_year.has_key(year):
        cases_by_year[year].append(c)
    else:
        cases_by_year[year] = [c]

exclusion = set()               # establish a set for cases to exclude

sample_size = int(options.s)    # get the desired sample size from the options

# get a random array of values of the same length as the list of ids
vals = numpy.random.rand(len(case_ids))
# do an argsort to get the cases with the highest random numbers
indices = vals.argsort()    

sample = {}
primary_by_case = {}
secondary_by_case = {}

p = init_folder
i = 0

# begin by excluding new articles that are duplicates with old articles
while i < nCases:
    # get the case_id associate with the next highest random value
    case_id = case_ids[indices[i]]
    # check for duplicates associated with this case id
    if duplicates.has_key(case_id):
        # if there are any, add them to the exclusion set
        for d in duplicates[case_id]:
            if int(d) < start:
                exclusion.add(case_id)

while i < nCases:
    count = 0
    # keep going until we have the desired number of samples
    while (count < sample_size) and (i < nCases):
        # get the case_id associate with the next highest random value
        case_id = case_ids[indices[i]]
        # check to see if it has been excluded because of a duplicate
        if not case_id in exclusion:
            # assign the case to the current sample
            sample[case_id] = (p, (count % nSubsamples) + 1)
            # increase the count by one
            count += 1
            # check for duplicates associated with this case id
            if duplicates.has_key(case_id):
                # if there are any, add them to the exclusion set
                for d in duplicates[case_id]:
                    exclusion.add(d)
               
        # increase the counter
        i += 1
    p += 1

    
    # set up the csv file for writing
    csv_file = open(csv_file_name, 'wb')
    writer = csv.writer(csv_file)

    for c in case_ids:
        primary = u''
        secondary = u''
        if sample.has_key(c):
            primary = sample[c][0]
            secondary = sample[c][1]
        row = [c, primary, secondary]
        writer.writerow(row)
    
    csv_file.close()

    # save the output to a json file
    output_file = codecs.open(json_file_name, mode='w', encoding='utf-8')
    dump(sample, output_file, ensure_ascii=False, indent=2)
    output_file.close()


    # keep a count for user feedback
    print "Processed", p, "samples."