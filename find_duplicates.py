# -*- coding: utf-8 -*-
"""
This script looks through the JSON files created by parse_LN_to_JSON.py and looks
for duplicates using the Jaccard Coefficient f k-grams of the article text (body).

It creates a CSV file with all of the cases listed and duplicates marked, and 
optionally stores the same information in a JSON file for use by make_sample.py

@author: dcard
"""

#import modules
from os import path, makedirs
from optparse import OptionParser
from json import loads, dump
import codecs
import re
import glob
import csv
import datetime


# This function updates a dictionary if the given value is greater than the present value
# Inputs:
#   d: a dictionary
#   key: a key for the new dictionary
#   value: a value to insert at that key (if it's bigger than the current value)
def insert_max(d, key, value):
    # check to see if the key exists
    if d.has_key(key):
        # if it does, check the value
        if value > d[key]:
            # if the new value is bigger, update
            d[key] = value
    # if it doesn't exist, just store the value
    else:
        d[key] = value
        

# This function compares two sets of n-grams and reterns the Jaccard Coefficient
# Inputs:
#   i_shingles, j_shingles: sets of n-grams
def compare_shingles(i_shingles,j_shingles):
    # take the intersection between i and j
    shared_shingles = i_shingles.intersection(j_shingles)
    # get the size of the intesection
    shared_count = len(shared_shingles)
    # divide the sum of the individual counts by the shared count (unless 0)
    total_count = len(i_shingles) + len(j_shingles) - shared_count
    if total_count > 0:
        JC = float(shared_count) / float(total_count)
    else:
        JC = 0
    # return the Jaccard Coefficient
    return JC
    
    
# This function is called when duplicates are found to update a dictionary
# which stores the case ids of all associate duplictes (including itself)
# Inputs:
#   duplicates: a dictionary of duplicates
#   i_id, j_id: case_ids of the two duplicates
def store_duplicates(duplicates, i_id, j_id):
    # start with case_id i
    # if the dictionary already has it as a duplicate then update the set
    dup_i = set()
    dup_j = set()    
    if duplicates.has_key(i_id):
        dup_i = duplicates[i_id]        
    else:
        dup_i = {i_id,j_id}
    if duplicates.has_key(j_id):
        dup_j = duplicates[j_id]        
    else:
        dup_j = {i_id,j_id}
        
    new_dup = dup_i.union(dup_j)
    new_dup = new_dup.union({i_id, j_id})
    for d in new_dup:
        if duplicates.has_key(d):
            duplicates[d].update(new_dup)
        else:
            duplicates[d] = new_dup

    # return the modified dictionary
    return duplicates


### MAIN ###

# set up an options parser
usage = "\n%prog project_dir [options]"
parser = OptionParser(usage=usage)
parser.add_option('-k', help='use K-grams for deduplication [default = %default]', metavar='K', default=4)
parser.add_option('-r', help='range (in days) over which to look for duplicates [default = %default]', metavar='RANGE', default = 62)
parser.add_option('-t', help='Threshold above which to consider similar articles as duplicates [default = %default]', metavar='THRESH', default=0.2)

# make a dictionary of months to look for
MONTHS = {u'january':1, u'february':2, u'march':3, u'april':4, u'may':5, u'june':6, u'july':7, u'august':8, u'september':9, u'october':10, u'november':11, u'december':12}

(options, args) = parser.parse_args()

if len(args) < 1:
	exit("Error: Please provide a project directory")

# Make sure we can find the input directory
project_dir = args[0]
if not path.exists(project_dir):
    exit("Error: Cannot find project directory")

input_dir = project_dir + '/json/'
output_dir = project_dir + '/metadata/'

if not path.exists(output_dir):
	makedirs(output_dir)

# Open the csv file for writing
csv_file_name = output_dir + 'duplicates.csv'
csv_file = open(csv_file_name, 'wb')
writer = csv.writer(csv_file)

# Get a list of all the files in the input directory
files = glob.glob(input_dir + '/*.json')
files.sort()

print "Found", len(files), " files."

date_hash = {}              # a dictionary of files (articles) indexed by date
case_years = {}             # a dictionary of yeas, indexed by case id
shingle_k = int(options.k)       # the size of shingles to use (k in k-grams)
shingle_thresh = float(options.t)  # the threshold for the JC above which to consider duplicates
date_range = int(options.r)      # the range (in days) over which to look for duplicates

# Start an empty list of case_ids
case_ids = []

# Go through all the files one by one
count = 0
for f in files:
    # open the file and unpack the json object into  dictionary
    input_file_name = f
    name_parts = input_file_name.split('/')
    file_name = name_parts[-1]
    
    input_file = codecs.open(input_file_name, encoding='utf-8')
    input_text = input_file.read()
    input_file.close()
    
    doc = loads(input_text, encoding='utf-8')

    # set default (blank) values for various strings
    case_id = u''       # case_id
    orig_date = u''     # the date string as written in the article
    day = u''           # the day from the date string
    month = u''         # the month from the date string
    year = u''          # the year from the date string
    fulldate = u''      # the date in the format YYYYMMDD

    # Look for the case_id from this file and add it to the list
    if doc.has_key(u'CASE_ID'):
        case_id = doc[u'CASE_ID'] 
        case_ids.append(case_id)

    # Look for the date from this file and parse it
    if doc.has_key(u'DATE'):
        orig_date = doc[u'DATE']
        year = doc[u'YEAR']
        month = doc[u'MONTH']
        if doc.has_key(u'DAY'):        
            day = doc[u'DAY']
        else:
            day = 0
        if day == 0:
            day = 15;
        date = datetime.date(int(year), int(month), int(day))        
      
        # store this file in the dictionary of files indexed by date
        if date_hash.has_key(date):
            # if the date exists as a key, add this file to the list at that key
            file_list = list(date_hash[date])
            file_list.append(file_name)
            date_hash[date] = file_list
        else:
            # otherwise, start a new list
            date_hash[date] = [file_name]
        
        # also store the year of this article
        case_years[case_id] = int(year)

    # keep a count for user feedback
    count += 1
    if (count%1000 == 0):
        print "Processed", count, "files."

# get all the dates for which articles exist and sort them
dates = date_hash.keys()
dates.sort()    

# set up some variables
first_date = dates[0]       # the earliest date for which we have an article
last_date = dates[-1]       # the last date for which we have an article
current_date = first_date   # the date we're currently considering     
nCases = len(case_ids)      # the total number of articles
active_dates = []           # a list of lists of cases currently comparing against
duplicates = {}             # a dictionary of duplicates, indexed by case_id
max_JCs =  {}               # the max Jaccard Coefficient (similarity) indexed by case_id
count = 0                   # the number of pairs we have processed
one_day = datetime.timedelta(1) # a constant for incrementing by one day

print first_date, last_date

print "Starting loop"
# go through every day, starting with the first
while current_date <= last_date:
    # if our list of active dates is full, pop off the first one added
    if len(active_dates) == date_range:
        # pop the oldest date
        active_dates.pop(0)

    # then add a new list for the current date
    active_dates.append([])
    # look for any files associated with the current date
    if (date_hash.has_key(current_date)):
        # start an empty list of case_ids
        cases = []
        # get all the files associatd with the current date
        files = date_hash[current_date]
        # process each file
        for f in files:
            # read in the json file and unpack it, as above
            input_file_name = input_dir + '/' + f    
            input_file = codecs.open(input_file_name, encoding='utf-8')
            input_text = input_file.read()
            input_file.close()
            doc = loads(input_text, encoding='utf-8')
        
            # get the case id
            if doc.has_key(u'CASE_ID'):
                case_id = doc[u'CASE_ID'] 
                
            # get the text of the article
            if doc.has_key(u'BODY'):
                body = doc[u'BODY']
                text = ''
                # combine the paragraphs
                for b in body:
                    text += b + u' '

                # split the text into words
                words = text.split()        
                shingles = set()           
                
                # create a set of all the n-grams in the article
                for w in range(len(words) - shingle_k + 1):
                    shingle = u''
                    # create a shingle from k words
                    for j in range(shingle_k):
                        shingle += words[w+j] + u''
                    # add it to the set
                    shingles.add(shingle)                
                   
                # add this case and its shingles to the list of cases for this date
                cases.append((case_id, shingles))
            
        # add this list of cases from this date to the list of active cases
        active_dates[-1] = cases

        # compute similarities among new cases and with old cases
        # check to see if anything was added this iteration
        new_cases = active_dates[-1]
        # if at least on case was added
        for i in range(len(new_cases)):
            # get the case_id from the tuple for this case
            i_id = new_cases[i][0]
            # get the set of shingles from the tuple for this case
            i_shingles = new_cases[i][1]
                
            # compare it to other new cases
            for j in range(i+1, len(new_cases)):
                j_id = new_cases[j][0]
                j_shingles = new_cases[j][1]
                
                # compute the Jaccard Coefficient between shingles
                JC = compare_shingles(i_shingles, j_shingles)
                
                # store the max JC for these cases
                insert_max(max_JCs, i_id, JC)
                insert_max(max_JCs, j_id, JC)

                # if the JC is above our threshold, consider these to be duplicates
                if (JC > shingle_thresh):
                    duplicates = store_duplicates(duplicates, i_id, j_id)
                    
                # keep a count for user feedback
                count += 1
                if (count%10000 == 0):
                    print "Processed", count, "pairs"

            # now compare each new case to all old cases in the active range
            # go through each date in the active range
            for k in range(len(active_dates)-1):
                # get each case associated with that date
                for j in range(len(active_dates[k])):
                    # compare as above
                    j_id = active_dates[k][j][0]
                    j_shingles = active_dates[k][j][1]
                    
                    JC = compare_shingles(i_shingles, j_shingles)

                    insert_max(max_JCs, i_id, JC)
                    insert_max(max_JCs, j_id, JC)
            
                    if (JC > shingle_thresh):
                        duplicates = store_duplicates(duplicates, i_id, j_id)

                    count += 1                    
                    if (count%10000 == 0):
                        print "Processed", count, "pairs"

    # go to the next date
    current_date = current_date + one_day

# output the results as a csv file
case_ids.sort()
# for each case write case_id, max_JC, and list of duplicates
for c in case_ids:
    row = [c]
    if max_JCs.has_key(c):
        row.append(max_JCs[c])
    if duplicates.has_key(c):
        dup_list = list(duplicates[c])
        dup_list.sort()
        row.append(dup_list)
    writer.writerow(row)
csv_file.close() 

# also write this information as a JSON object
output = {}
# for each case, save the case_id, year, and list of duplicates
for c in case_ids:
    case = []
    if case_years.has_key(c):
        case.append(case_years[c])
    else:
        case.append(0)
    if duplicates.has_key(c):
        case.append(list(duplicates[c]))
    else:
        case.append([])
    output[c] = case
    
# save the output to a json file
output_file_name = output_dir + 'duplicates.json'
output_file = codecs.open(output_file_name, mode='w', encoding='utf-8')
dump(output, output_file, ensure_ascii=False, indent=2)
output_file.close()
    