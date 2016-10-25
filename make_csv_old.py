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


TOP_TAGS = [u'BYLINE', u'DATELINE', u'HIGHLIGHT', u'LENGTH', u'SECTION', u'SOURCE', u'E-mail']
END_TAGS = [u'CATEGORY', u'CHART', u'CITY', u'COMPANY', u'CORRECTION', u'CORRECTION-DATE', u'COUNTRY', u'CUTLINE', u'DISTRIBUTION', u'DOCUMENT-TYPE', u'ENHANCEMENT', u'GEOGRAPHIC',  u'GRAPHIC', u'INDUSTRY', u'JOURNAL-CODE', u'LANGUAGE', u'LOAD-DATE', u'NAME', u'NOTES', u'ORGANIZATION', u'PERSON', u'PHOTO', u'PHOTOS', u'PUBLICATION-TYPE', u'SERIES', u'STATE', u'SUBJECT', u'TICKER', u'TYPE', u'URL']


# make an option parser
usage = "\n%prog project_dir [options]"
parser = OptionParser(usage=usage)
parser.add_option("-m", action="store_true", dest="make_dirs", default=False,
                  help="Make directories for sampling [default = %default]")


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

TAGS = [(u'COUNTRY', 'UNITED STATES')]

tags_dict = {}      # a dictionary of tags we see

# Look for the input directory
project_dir = args[0]
json_dir = project_dir + '/json/'
if not path.exists(json_dir):
    exit("Cannot find json directory " + json_dir)

metadata_dir = project_dir + '/metadata/'
if not path.exists(metadata_dir):
    exit("Cannot find metadata directory!")
    
if options.make_dirs:
	sample_dir = project_dir + '/sample/'
	if not path.exists(sample_dir):
		makedirs(sample_dir)
		
# open the csv file for writing
csv_filename = metadata_dir + 'summary.csv'
csv_file = open(csv_filename, 'wb')
writer = csv.writer(csv_file)

sample_file = metadata_dir + 'sample.json'
include_samples = False
if path.exists(sample_file):
    # read in the JSON file and unpack it
    input_file = codecs.open(sample_file, encoding='utf-8')
    input_text = input_file.read()
    input_file.close()    
    sample = loads(input_text, encoding='utf-8')
    include_samples = True

duplicates_file = metadata_dir + 'duplicates.json'
include_duplicates = False
if path.exists(duplicates_file):
    # read in the JSON file and unpack it
    input_file = codecs.open(duplicates_file, encoding='utf-8')
    input_text = input_file.read()
    input_file.close()    
    duplicates = loads(input_text, encoding='utf-8')
    include_duplicate = True


# Write a header to te CSV file
row = ['caseid', 'filename', 'original file', 'original document number', 'source',
         'year', 'month', 'day', 'fulldate', 'byline', 'section',
         'page', 'length (given)', 'word count']
for t in TAGS:
    row.append(t[0]+':'+t[1])
row.append('title')
row.append('p1')

if include_duplicates:
    row.append('duplicates')
if include_samples:
    row.append('primary')
    row.append('secondary')
    
#for t in TOP_TAGS:
#    row.append(t)
#row.append('top_misc')
#for t in END_TAGS:
#    row.append(t)
#row.append('end_misc')
#row.append('disclaimer')


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
    byline = u''
    byline_extra = u''
    section_text = u''
    main_section = u''
    page = u''
    length = u''
    word_count = u''
    tags = []
    for t in TAGS:
        tags.append(u'')
    title = u''
    title_extra = u''
    graphic = u''
    cpright = u''
    top_misc = u''
    end_misc = u''
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
    
   
    # get any top tags associated with this artiicle
    if doc.has_key(u'TOP'):
        top = doc[u'TOP']
        
        # get the length and extract the number (usually wrong)
        if top.has_key(u'LENGTH'):
            length_text = top[u'LENGTH']
            length_parts = length_text.split()
            if len(length_parts) > 0:
                length = length_parts[0]
        
        # get the byline
        if top.has_key(u'BYLINE'):
            byline = top[u'BYLINE']
            
        if top.has_key(u'BYLINE_EXTRA'):
            byline_extra = top[u'BYLINE_EXTRA']
        
        # get the section and parse it into a main sectio and page number (if available)
        if top.has_key(u'SECTION'):
            section_text = top[u'SECTION']
            # convert to lower case, then convet commas and hyphens to semicolons
            section_lower = section_text.lower()
            section_lower = re.sub(',', ';', section_lower)
            section_lower = re.sub('-', '', section_lower)            
            section_parts = section_lower.split(';')

            # if there is only one section (no semicolons), search it for a page number
            if len(section_parts) == 1:
                page_search = re.search(u'([a-z]*)\s.*((page)|(pg\.))\s+([a-z]*[0-9]+[a-z]*)', section_lower)
                if page_search:
                    # if found, assume the first group is the section name
                    main_section = str(page_search.group(1))
                    # and extract the page number
                    page = str(page_search.group(5))
                else:
                    # if not found, just keep the whole thing as a section name
                    main_section = section_lower
            
            # if there's more than one part, check each one for a page number
            elif len(section_parts) > 1:
                # assume the first part is the main section name
                main_section = section_parts[0]
                page_search = re.search(u'((page)|(pg\.))\s+([a-z]*[0-9]+[a-z]*)',section_lower)
                if page_search:
                    # store the number part as the page number
                    page = str(page_search.group(4))

            # if we didn't see anything that looks like a page number, find all the numbers
            if page == u'':
                page_search = re.findall(u'([a-z]*[0-9]+[a-z]*)', section_lower)
                # if we only find one number, assume it's the pag number
                if len(page_search) == 1:
                    page = page_search[0]

            main_section = main_section.lstrip()
            main_section = main_section.rstrip()
            page = page.lstrip()
            page = page.rstrip()            
        
        # get the miscellaneous top matter
        if top.has_key(u'TOP_MISC'):
            top_misc = top[u'TOP_MISC']
            
    # get the body text and do a basic word count
    if doc.has_key(u'BODY'):
        word_count = 0
        body = doc[u'BODY']
        for b in body:
            words = b.split()            
            word_count += len(words)

    # get the bottom tags
    if doc.has_key(u'BOTTOM'):
        bottom = doc[u'BOTTOM']
        
        # search for the particular tags we're intested in (specified above in TAGS)
        for i in range(len(TAGS)):
            t = TAGS[i]            
            if bottom.has_key(t[0]):
                # if we find any of them, extract the relevance percentage
                tag = bottom[t[0]]
                search_string = t[1] + u'\s\(([0-9]+)%\)'
                pattern = re.search(search_string, tag)
                if pattern:
                    tags[i] = pattern.group(1)

        # also make a compendium of tags and categories
        # this could be useful for finding common tags
        for k in bottom.keys():
            text = bottom[k]
            # find anything that looks like a word followed by a percentage in ()
            categories = re.findall(u'([A-Z0-9\s,\(\)&]*)\([0-9]+%\)', text)
            if len(categories) > 0:
                # for each tag, store a dictionary of associated words
                if not tags_dict.has_key(k):
                    tags_dict[k] = {}
                d = tags_dict[k]
                
                # categories are all the associated words we find for this tag
                for cat in categories:
                    cat = cat.lstrip()
                    cat = cat.rstrip()
                    if d.has_key(cat):
                        d[cat] = d[cat] + 1
                    else:
                        d[cat] = 1
                
                # store the dictionary for this tag in a meta-dictionary, indexed by tag name
                tags_dict[k] = d
        
        # store the miscellaneous end matter
        if bottom.has_key(u'BOTTOM_MISC'):
            end_misc = bottom[u'BOTTOM_MISC']
                
    # Write all of this information for this article to the csv file
    row = [case_id, file_name, orig_file, orig_id, source, year, month, day,
           fulldate, byline, main_section, page, length, word_count]
    for i in range(len(TAGS)):
        row.append(tags[i])
    row.append(title)
    if word_count > 0:
        row.append(body[0])
    else:
        row.append(u' ')
   
    ucase_id = unicode(case_id)
    if include_duplicates:
        if duplicates.has_key(ucase_id):            
            dup = duplicates[ucase_id][1]
            dup.sort()
            if len(dup) > 0:
                row.append(dup)
            else:
                row.append(u' ')
        else:
            row.append(u' ')
            
    if include_samples:
        if sample.has_key(ucase_id):
            row.append(sample[ucase_id][0])
            row.append(sample[ucase_id][1])

    # get any top tags associated with this artiicle
#    if doc.has_key(u'TOP'):
#        top = doc[u'TOP']
#    else:
#        top = {}
#    for t in TOP_TAGS:
#        if top.has_key(t):
#            row.append(top[t])
#        else:
#            row.append(u'')
#    if top.has_key(u'TOP_MISC'):
#        row.append(top[u'TOP_MISC'])
#    else:
#        row.append(u'')
        
    # get any top tags associated with this artiicle
#    if doc.has_key(u'BOTTOM'):
#        bottom = doc[u'BOTTOM']
#    else:
#        bottom = {}
#    for t in END_TAGS:
#        if bottom.has_key(t):
#            row.append(bottom[t])
#        else:
#            row.append(u'')
#    if bottom.has_key(u'BOTTOM_MISC'):
#        row.append(bottom[u'BOTTOM_MISC'])
#    else:
#        row.append(u'')
#    
#    row.append(disclaimer)
    
    # encode it as ascii for excel
    for i in range(len(row)):
        if isinstance(row[i], unicode):
            row[i] = codecs.encode(row[i], 'ascii', 'ignore')

    writer.writerow(row)    

    if include_samples and options.make_dirs:
        if sample.has_key(ucase_id):
            primary = sample[ucase_id][0]
            secondary = sample[ucase_id][1]
            
            dir_name = sample_dir + '/' + str(primary) + '/'
            if not path.exists(dir_name):
                makedirs(dir_name)
                if path.exists(dir_name):
                    csv_file2 = open(dir_name + '/sample_' + str(primary) + '.csv', 'wb')
                    writer2 = csv.writer(csv_file2)
                    writer2.writerow(header_row)
                    writer2.writerow(row)
                    csv_file2.close()
            else:
                csv_file2 = open(dir_name + '/sample_' + str(primary) + '.csv', 'a')
                writer2 = csv.writer(csv_file2)
                writer2.writerow(row)
                csv_file2.close()                
    
    # keep a count for user feedback
    count += 1
    if (count%1000 == 0):
        print "Processed", count, "files."

# close the csv file
csv_file.close()
    
# display the 10 most common terms for each end tag
for i in tags_dict.items():
    print i[0]
    d = i[1]
    sorted_d = sorted(d.iteritems(), key=operator.itemgetter(1))
    sorted_d.reverse()    
    print sorted_d[:10]
    
    