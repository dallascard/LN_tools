# -*- coding: utf-8 -*-
"""
This script reads in all the JSON files, parses them, and writes a summary to a CSV file


"""
# import modules
from os import path, makedirs
from sys import exit
from optparse import OptionParser
from json import loads
import codecs
import re
import glob
import csv
import operator


TOP_TAGS = [u'BYLINE', u'DATELINE', u'GUESTS', u'HIGHLIGHT', u'LENGTH', u'SECTION', u'SOURCE', u'E-mail']
END_TAGS = [u'CATEGORY', u'CHART', u'CITY', u'COMPANY', u'CORRECTION', u'CORRECTION-DATE', u'COUNTRY', u'CUTLINE', u'DISTRIBUTION', u'DOCUMENT-TYPE', u'ENHANCEMENT', u'GEOGRAPHIC',  u'GRAPHIC', u'INDUSTRY', u'JOURNAL-CODE', u'LANGUAGE', u'LOAD-DATE', u'NAME', u'NOTES', u'ORGANIZATION', u'PERSON', u'PHOTO', u'PHOTOS', u'PUBLICATION-TYPE', u'SERIES', u'STATE', u'SUBJECT', u'TICKER', u'TRANSCRIPT', u'TYPE', u'URL']

# make an option parser
usage = "\n%prog json_dir output_file [options]"
parser = OptionParser(usage=usage)


(options, args) = parser.parse_args()

if len(args) < 1:
	exit("Error: Please provide a project directory")


# Make a list of tags to look for
# TODO: Add an option to allow users to add additional tag pairs

#TAGS = [(u'COUNTRY', 'UNITED STATES'),
#        (u'GEOGRAPHIC', u'UNITED STATES'),
#        (u'SUBJECT', u'SMOKING'),
#        (u'SUBJECT', u'TOBACCO PRODUCTS'),
#        (u'SUBJECT', u'TOBACCO MFG')]
#        (u'SUBJECT', u'IMMIGRATION'),
#        (u'SUBJECT', u'ILLEGAL IMMIGRANTS'),
#        (u'SUBJECT', u'IMMIGRATION LAW')]

#TAGS = [(u'COUNTRY', 'UNITED STATES')]

tags_dict = {}      # a dictionary of tags we see

# Look for the input directory
json_dir = args[0]
if not path.exists(json_dir):
    exit("Cannot find json directory " + json_dir)

csv_filename = args[1]
csv_file = open(csv_filename, 'wb')
writer = csv.writer(csv_file)


# Write a header to te CSV file
row = ['caseid', 'filename', 'original file', 'original document number', 'Channel', 'Show',
         'year', 'month', 'day', 'fulldate', 'Observation', 'Speaker', 'SpeakerNum', 'Text']


header_row = row
writer.writerow(header_row)

# Get all the files in the input directory
files = glob.glob(json_dir + '/*.json')
files.sort()
print "Found", len(files), " files."

rows = {}

# Process each file, one by one
count = 0
for f in files:
    # Open the JSON file and unpack it into a dictionary
    input_file_name = f
    name_parts = input_file_name.split('/')
    file_name = name_parts[-1]
    
    input_file = codecs.open(input_file_name, encoding='utf-8')
    input_text = input_file.read()
    input_file.close()
    
    doc = loads(input_text, encoding='utf-8')
    
    # Set a list of variables to empty unicode string
    case_id = u''
    orig_file = u''
    orig_id = u''
    source = u''
    disclaimer = u''
    orig_date = u''
    date = u''
    day = u''
    month = u''
    year = u''
    fulldate = u''
    title = u''
    title_extra = u''
    show = u''
    body = u''
    
    # get the Case id
    if doc.has_key(u'CASE_ID'):
        case_id = doc[u'CASE_ID']
        
    # Get the original L-N file this article came from
    if doc.has_key(u'ORIG_FILE'):
        orig_file = doc[u'ORIG_FILE']
     
    # get the document number in the original L-N file
    if doc.has_key(u'ORIG_ID'):
        orig_id = doc[u'ORIG_ID']

    # get the source (newspaper name)
    if doc.has_key(u'SOURCE'):
        source = doc[u'SOURCE']
    
    if doc.has_key(u'DISCLAIMER'):
        disclaimer = doc[u'DISCLAIMER']

    # get the date of publication, and parse it
    if doc.has_key(u'DATE'):
        orig_date = doc[u'DATE']
    if doc.has_key(u'DAY'):
        day = doc[u'DAY']
    if doc.has_key(u'MONTH'):
        month = doc[u'MONTH']
    if doc.has_key(u'YEAR'):
        year = doc[u'YEAR']
    if doc.has_key(u'FULLDATE'):
        fulldate = doc[u'FULLDATE']    
        
    # get the article title
    if doc.has_key(u'TITLE'):
        title = doc[u'TITLE']
    if doc.has_key(u'TITLE_EXTRA'):
        title_extra = doc[u'TITLE_EXTRA']
    if doc.has_key(u'SHOW'):
        show = doc[u'SHOW']
   
           
    # get the body text and do a basic word count
    if doc.has_key(u'BODY'):
        word_count = 0
        body = doc[u'BODY']

    for paragraph in body:
        utterance = paragraph[0]
        speaker = paragraph[1]
        speaker_num = paragraph[2]
        text = paragraph[3]                
        # Write all of this information for this article to the csv file
        row = [case_id, file_name, orig_file, orig_id, source, show, year, month, day,
           fulldate, utterance, speaker, speaker_num, text]

   
    
        # encode it as ascii for excel
        for i in range(len(row)):
            if isinstance(row[i], unicode):
                row[i] = codecs.encode(row[i], 'ascii', 'ignore')

        writer.writerow(row)    

    # keep a count for user feedback
    count += 1
    if (count%1000 == 0):
        print "Processed", count, "files."

# close the csv file
csv_file.close()
    
    