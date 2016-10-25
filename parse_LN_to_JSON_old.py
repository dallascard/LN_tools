"""
parse_LN.py

Parse a single file or a directory of raw files from Lexis-Nexis,
which come as text files containing a block of news articles concatenated into one file.

Objective is to split articles into individual files and extract relevant
information

In general, the articles have:
a source (newspaper name)
a well-defined date
sometimes a title after the date
some possible top tags, including author (byline) and length
some paragraphs of text (usually)
many possible end tags (some of which include relvance percentages)
a copyright (usually)

Also, all tags will (usually) be in the form 'TAG: content'

Unfortunately, there is a lot that can go wrong, including missing sections,
broken lines, unusually formats, strangely converted characters, 
and randomly copied text. We do the best we can.


"""

# import modules
from optparse import OptionParser
from os import path, makedirs
from json import dump
from unicodedata import normalize
import codecs
import re
import glob

# This function writes an individual article to a text file, unchanged
# Yes, it works purely on global variables...
def write_text_file():
    if doc.has_key(u'CASE_ID'):
        output_file_name = output_dir + '/' + prefix + str(doc[u'CASE_ID']) + '.txt'
        output_file = codecs.open(output_file_name, mode='w', encoding='utf-8')
        output_file.writelines(output_text)
        output_file.close()

# This function writes a parsed version of an article as a JSON object
# It too relies on global variables...
def write_json_file():
    # assume we have a dictionary named doc
    # it should have a case_id
    if doc.has_key(u'CASE_ID'):

        # get the top tags, and put them in a dictionary
        top = {}
        for t in top_tags:
            # split the tag into TAG and TEXT (at the colon)
            index = t.find(':')
            tag = t[:index]
            text = t[index+1:]
            # strip off whitespace
            text = text.lstrip()
            top[tag] = text

        # store the top tags and anything else from the top section which didn't fit
        top[u'TOP_MISC'] = top_misc
        doc[u'TOP'] = top

        # store the paragraphs of body text in BODY
        doc[u'BODY'] = paragraphs
        
        # get the bottom tags and put them in a dictionary, as with top tags
        bottom = {}        
        for t in end_tags:
            index = t.find(':')
            tag = t[:index]
            text = t[index+1:]
            text = text.lstrip()
            bottom[tag] = text
        bottom[u'BOTTOM_MISC'] = end_misc
        doc[u'BOTTOM'] = bottom

        # output the overall dictionary as a json file
        output_file_name = json_dir + '/' + prefix + str(doc[u'CASE_ID']) + '.json'
        output_file = codecs.open(output_file_name, mode='w', encoding='utf-8')
        dump(doc, output_file, ensure_ascii=False, indent=2)
        output_file.close()
    

# Tags used at the top and bottom of L-N files
TOP_TAGS = [u'BYLINE:', u'DATELINE:', u'HIGHLIGHT:', u'LENGTH:', u'SECTION:', u'SOURCE:', u'E-mail:', ]
END_TAGS = [u'CATEGORY:', u'CHART:', u'CITY:', u'COMPANY:', u'CORRECTION-DATE:', u'COUNTRY:', u'CUTLINE:', u'DISTRIBUTION:', u'DOCUMENT-TYPE:', u'ENHANCEMENT:', u'GEOGRAPHIC:',  u'GRAPHIC:', u'INDUSTRY:', u'JOURNAL-CODE:', u'LANGUAGE:', u'LOAD-DATE:', u'NOTES:', u'ORGANIZATION:', u'PERSON:', u'PHOTO:', u'PHOTOS:', u'PUBLICATION-TYPE:', u'SERIES:', u'STATE:', u'SUBJECT:', u'TICKER:', u'TYPE:', u'URL:']
MONTHS = {u'january':1, u'february':2, u'march':3, u'april':4, u'may':5, u'june':6, u'july':7, u'august':8, u'september':9, u'october':10, u'november':11, u'december':12}

# set up an options parser  
usage = 'usage %prog [options] (must specify -f OR -d)'
parser = OptionParser(usage=usage)
parser.add_option('-f', help='read in FILE', metavar='FILE')
parser.add_option('-d', help='read in in ALL files in INDIR', metavar='INDIR')
parser.add_option('-o', help='output individual files to DIR', metavar='DIR', default='./temp/text/')
parser.add_option('-j', help='output individal xml files to JDIR', metavar='JDIR', default='./temp/json/')
parser.add_option('-p', help='prefix for output text files [default = %default]', metavar='PRE', default='prefx.0-')
parser.add_option("-w", action="store_true", dest="write_files", default=False,
                  help="Write individual .txt files [default = %default]")

(options, args) = parser.parse_args()

case_id = 0                 # unique id for each article (doc)
total_expected_docs = 0     # total numbe of artcles we expect to get from all L-N files
total_docs_found = 0        # running count of listed numbers of docs

tag_counts = {}             # counts of how many times we see each tag
first_tag_counts = {}       # counts of how any times we see each tag as the first tag

# If the output directories do not exist, create them
output_dir = options.o
if not path.exists(output_dir):
    makedirs(output_dir)
    
json_dir = options.j
if not path.exists(json_dir):
    makedirs(json_dir)

# get the prefix to use when naming files
prefix = options.p

# get a list of files to parse, either a single file, or all files in a directory
files = []
input_file_name = options.f
if input_file_name == None:
    input_dir = options.d
    if path.exists(input_dir):
        files = glob.glob(input_dir + '/*')
else:
    files = [input_file_name]
            
print "Found", len(files), "files."

# sort the files and parse them one by one
files.sort()
for f in files:
    # open the next file, and read it in 
    input_file_name = f
    name_parts = input_file_name.split('/')
    orig_file_name = name_parts[-1]
    # open with utf-8-sig encoding to eat the unicode label
    input_file = codecs.open(input_file_name, encoding='utf-8-sig')
    input_text = input_file.read()
    input_file.close()

    # split the text into individual lines
    lines = input_text.split('\r\n')

    doc = {}            # store the article we are working on as a dictionary
    doc_count = 0       # count of how many articles we have found
    doc_num = 0         # document number in the original L-N file
    expected_docs = 0   # the number of articles we expect to find in this L-N file

    # process each line, one at a time
    for line in lines:
        # first, normalize the unicode (to get rid of things like \xa0)
        orig_line = line
        line = normalize('NFKD', line)     
        
        # start off looking for  new document (each of which is marked as below)
        # also, store the numbers from this pattern as groups for use below
        match = re.search(u'([0-9]+) of ([0-9]+) DOCUMENTS', line)
        
        # if we find a new article
        if match:   
            # first, save the article we are currently working on
            if doc_num > 0:
                if options.write_files:
                    # write the original file as a text file, unmodified
                    write_text_file()
                    # also write the (parsed) article as a json object
                    write_json_file()
                
            # now move on to the new artcle
            # check to see if the document numbering within the L-N file is consisent  
            # (i.e. the next document should be numbered one higher than the last)
            if int(match.group(1)) != doc_num + 1:
                print "Missed document after " + input_file_name + ' ' + str(doc_num)
            
            # if this is the first article in the L-N file, get the expected number of docs
            if expected_docs == 0:
                expected_docs = int(match.group(2))
                total_expected_docs += expected_docs
            elif (expected_docs != int(match.group(2))):
                print "Discrepant document counts after", input_file_name, str(doc_num-1)

            # get the document number from the original L-N file
            doc_num = int(match.group(1))
            # assign a new, unique, case id
            case_id += 1
            # add one to the number of documents we've seen
            doc_count += 1

            # start a new document as a dictionary
            doc = {}
            # store what we know so far
            doc[u'CASE_ID'] = case_id               # unique identifier
            doc[u'ORIG_FILE'] = orig_file_name      # filename of the original L-N file
            doc[u'ORIG_ID'] = doc_num               # document number in the L-N file
            
            current = u''       # current stores the block we are currently working on
            output_text = []    # a list of lines to write to the text file
            top_tags = []       # a list of top tags
            paragraphs = []     # a list of body paragraphs
            end_tags = []       # a list of end tags
            top_misc = u''      # things we can't parse from the top of the article
            end_misc = u''      # things we can't parse from the bottom of the article
            have_length = False
            have_section = False

        # once we've started working on a document...
        elif (doc_num > 0):   
        
            match = False
            
            # check if thee's anything on this line
            if (line != u''):
                # if so, strip the whitespace and add the current line to our working line
                temp = line.lstrip()
                temp = temp.rstrip()
                current += temp + ' '
                
            # if not, process the line(s) we've been working on...
            elif (current != u''):
                current = current.rstrip()
                
                # first check to see if this looks like a tag
                tag_match = re.search(u'^([A-Z]+[-]?[A-Z]+:)', current)
                if tag_match:
                    tag = tag_match.group(1)  
                    
                    # if we find a tag, see if it's a top tag
                    if (tag in TOP_TAGS) and (len(paragraphs) == 0):
                        if tag == u'LENGTH:':
                            if have_length == False:
                                top_tags.append(current)
                                have_length = True
                                match = True
                        elif tag == u'SECTION:':
                            if have_section == False:
                                top_tags.append(current)
                                have_section = True
                                match = True
                        else:
                            top_tags.append(current)
                            match = True
                        
                    # then see if it's a bottom tag
                    elif (tag in END_TAGS) and ((len(paragraphs)>0) or have_section or have_length):
                        # deal with it as an end tag:
                        end_tags.append(current)
                        match = True
                
                # if it's not a tag, but we already have end tags, continue with the end
                if match == False and len(end_tags) > 0:
                    # deal with this as bottom matter
                    # pick up the copyright if it's there
                    pattern = re.search(u'^Copyright ', current)
                    if pattern:
                        if not doc.has_key(u'COPYRIGHT'):
                            doc[u'COPYRIGHT'] = current
                    # otherwise, 
                    else:
                        # sometimes the end tags get split over multiple lines
                        # i.e., if this text contains '(#%)'
                        pattern = re.search(u'\([0-9]+%\)', current)
                        if pattern:
                            end_tags[-1] += ' ' + current
                        # or if the last tag was just a tag with no content
                        elif end_tags[-1] in END_TAGS:
                            end_tags[-1] += ' ' + current
                        # not foolproof... store the rest in misc
                        else:
                            end_misc += current + u' ** '   
                    match = True
    
                # then, check if it could be a date for the artcle
                if match == False and not doc.has_key(u'DATE'):
                    
                    date_match = re.search('^([a-zA-Z]*).?\s*(\d\d?).*\s*(\d\d\d\d).*', current)
                    month_yyyy_match = re.search('^([a-zA-Z]*).?\s*(\d\d\d\d).*', current)
                
                    if date_match:
                        month_name = date_match.group(1)
                        month_name = month_name.lower()
                        day = date_match.group(2)
                        year = date_match.group(3)
                        if MONTHS.has_key(month_name):
                            month = MONTHS[month_name]
                            doc[u'DATE'] = current
                            doc[u'MONTH'] = int(month)
                            doc[u'DAY'] = int(day)
                            doc[u'YEAR'] = int(year)        
                            # also store the date in the format YYYYMMDD
                            fulldate = year + str(month).zfill(2) + day.zfill(2)
                            doc[u'FULLDATE'] = fulldate
                            match = True
                    
                    # try an alternate date format
                    elif month_yyyy_match:
                        month_name = month_yyyy_match.group(1)
                        month_name = month_name.lower()
                        year = month_yyyy_match.group(2)
                        if MONTHS.has_key(month_name):
                            doc[u'DATE'] = current
                            month = MONTHS[month_name]
                            doc[u'MONTH'] = int(month)
                            doc[u'YEAR'] = int(year)        
                            match = True
                  
                # if its not a tag or date, and we don't have end tags
                if match == False:
                    # check if we have any top tags
                    if len(top_tags) == 0:
                        # if not, check if we have a date
                        if not doc.has_key(u'DATE'):
                            # if not, assume this is a part of the source
                            source = current.lower()
                            source = re.sub('^the', '', source, 1)
                            source   = source.lstrip()
                            if doc.has_key(u'SOURCE'):
                                doc[u'SOURCE'] = doc[u'SOURCE'] + u'; ' + source
                            else:
                                doc[u'SOURCE'] = source
                            match = True
                        # if we do have top tags, assume this is a title
                        else:
                            # assuming we don't already have a title
                            if not doc.has_key(u'TITLE'):
                                doc[u'TITLE'] = current
                                match = True

                # don't move onto the body until we at least one tag
                if (match == False) and (have_length == False) and (have_section == False):
                    top_misc += current + u' ** '
                    match = True
    
                # in all other cases, assume this is part of the body         
                if match == False:
                    # Try to deal with paragraphs that have been split over mutiple lines
                    # By default, assume we'll just append the current working line
                    # to the body
                    append = True
                    # if we have at least one paragraph
                    if len(paragraphs) > 0:
                        # Look at the end of the last paragraph and the start of
                        # this one to see if a line has been split.
                       
                       # First, try to join hyperlinks, email addresses and
                        # hyphenated words that have been split
                        if re.search(u'[/@-]$', paragraphs[-1]):
                            if re.search(u'^[a-z]', current):                                
                                paragraphs[-1] = paragraphs[-1] + u'' + current
                                append = False
    
                        # Also search for the symbols at the start of the next line
                        elif re.search(u'^[/@]', current):
                            paragraphs[-1] = paragraphs[-1] + 'u' + current
                            append = False
    
                        # Finally, try to join sentences that have been split
                        # i.e. the last paagraph doesn't end with an end character
                        elif not re.search(u'[\.\"\'?!:_]$', paragraphs[-1]):
                            # and the next paragraph doesn't start with a start symbol.
                            if not re.search(u'^[A-Z"\'>*-\.\(0-9=\$%_]|(http)|(www)', current):
                                paragraphs[-1] = paragraphs[-1] + u' ' + current
                                append = False
                    # in all other cases, just add the input as a new paragraph
                    if (append == True):
                        paragraphs.append(current)
                    
                # start a new working line
                current = u''


            output_text.append(orig_line + u'\r\n')
        
    total_docs_found += doc_count

    # once we reach the end of the file, output the current document    
    # and then go to the next file
    if doc_num > 0:
        if options.write_files:
            write_text_file()
            write_json_file()

    # print a summary for the L-N file
    print 'Processed', orig_file_name + ': ', 'Expected:', expected_docs, '  Found:', doc_count

# and print a final summary of everything
print 'Total number of documents expected: ' + str(total_expected_docs)
print 'Total number of documents found: ' + str(total_docs_found)

