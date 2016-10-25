"""
split_LN_to_TXT.py

Split a directory of raw files from Lexis-Nexis,
which come as text files containing a block of news articles concatenated into one file,
into individual text files.

"""

# import modules
from optparse import OptionParser
from os import path, makedirs
from unicodedata import normalize
import codecs
import re
import glob

# This function writes an individual article to a text file, unchanged
# Yes, it works purely on global variables...
def write_text_file():
    if case_id != 0:
        output_file_name = output_dir + '/' + prefix + str(case_id) + '.txt'
        output_file = codecs.open(output_file_name, mode='w', encoding='utf-8')
        output_file.writelines(output_text)
        output_file.close()

# set up an options parser
usage = 'usage %prog [options] input_dir output_dir output_prefix'
parser = OptionParser(usage=usage)

(options, args) = parser.parse_args()

case_id = 0                 # unique id for each article (doc)
total_expected_docs = 0     # total numbe of artcles we expect to get from all L-N files
total_docs_found = 0        # running count of listed numbers of docs

tag_counts = {}             # counts of how many times we see each tag
first_tag_counts = {}       # counts of how any times we see each tag as the first tag

# If the output directories do not exist, create them
output_dir = args[1]
if not path.exists(output_dir):
    makedirs(output_dir)
    
# get the prefix to use when naming files
prefix = args[2]

input_dir = args[0]
if path.exists(input_dir):
    files = glob.glob(input_dir + '/*')
            
print "Found", len(files), "files."

case_id = 0
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
                # write the original file as a text file, unmodified
                write_text_file()
                
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
          
            output_text = []    # a list of lines to write to the text file

        else:
            output_text.append(orig_line + u'\r\n')
        
    total_docs_found += doc_count

    # once we reach the end of the file, output the current document    
    # and then go to the next file
    if doc_num > 0:
        write_text_file()

    # print a summary for the L-N file
    print 'Processed', orig_file_name + ': ', 'Expected:', expected_docs, '  Found:', doc_count

# and print a final summary of everything
print 'Total number of documents expected: ' + str(total_expected_docs)
print 'Total number of documents found: ' + str(total_docs_found)

