# -*- coding: utf-8 -*-
"""
This script takes a json file of case_ids and converts the corresponding original articles
(located into the json_dir) to shortened versions (written to output_dir)

The csv file should have the case_ids in the first column

The json files to be converted come from parse_LN_to_JSON.py

@author: dcard
"""

# import modules
from os import path, makedirs
from optparse import OptionParser
from json import loads
import glob
import codecs
import csv



def main():
    # Set up an option parser  
    usage = '\n%prog project_dir file_prefix [options]'
    parser = OptionParser(usage=usage)
    parser.add_option('-w', help='Number of words at which to end article [default = %default]', metavar='WORD_COUNT', default=225)
    parser.add_option('-t', help='Topic code [default = %default]', metavar='TOPIC_CODE', default="NA")

    (options, args) = parser.parse_args()

    if len(args) < 2:
    	exit("Error: Not enough input arguments")

    project_dir = args[0]
    json_prefix = args[1]
    json_dir = project_dir + '/json/'
    output_dir = project_dir + '/partition/'
    metadata_dir = project_dir + '/metadata/'
    all_short_dir = project_dir + '/all_short/'

    if not path.exists(json_dir):
    	exit("Error: json directory not found: " + json_dir)
    	
    if not path.exists(metadata_dir):
    	exit("Error metadata dir not found: " + metadata_dir)

    if not path.exists(output_dir):
    	exit("Error: sample dir not found. Please run make_csv.py -s")

    sample_file = metadata_dir + 'sample.json'

    # read in the JSON file and unpack it
    input_file = codecs.open(sample_file, encoding='utf-8')
    input_text = input_file.read()
    input_file.close()    
    sample = loads(input_text, encoding='utf-8')

    case_ids = sample.keys()


    count = 0
    # go through each row in the json file
    for case_id in case_ids:
        # find the associated json file
        json_filename = json_dir + '/' + json_prefix + case_id + '.json'
        if not path.exists(json_filename):
            exit("Cannot find" + json_filename)
        else:


            # open the json file, read it in, and unpack it
            json_file = codecs.open(json_filename, encoding = 'utf-8')
            json_text = json_file.read()
            json_file.close()
            doc = loads(json_text, encoding='utf-8')

            # open a corresponding file for writing the output
            primary = sample[case_id][0]
            secondary = sample[case_id][1]
            sample_dir = output_dir + '/' + str(primary) + '/' + str(secondary) + '/'
            if not path.exists(sample_dir):
                makedirs(sample_dir)
            
            output_file_name = sample_dir + json_prefix + case_id + '_short'+ '.txt'

            shorten_and_save_article(case_id, doc, output_file_name, options.t, options.w)

        count += 1
        if (count%1000 == 0):
            print "Processed", count, "cases."




def shorten_and_save_article(case_id, doc, output_file_name, topic_code, max_words):

    with codecs.open(output_file_name, mode='wU', encoding='utf-8') as output_file:

        if doc.has_key(u'CASE_ID'):
            assert int(case_id) == int(doc[u'CASE_ID'])
        
        output_file.writelines(topic_code + u'-' + case_id)
        output_file.write(u'\n\n')
        output_file.writelines("PRIMARY")
        output_file.write(u'\n\n')
        
        # look for the title in the json file, and write it to the output file
        if doc.has_key(u'TITLE'):
            output_file.writelines(doc[u'TITLE'])
            output_file.write(u'\n\n')
              
        # then get the text of the article
        if doc.has_key(u'BODY'):
            body = doc[u'BODY']
            word_count = 0      # count of words found in the document
            text = []           # list of paragraphs to write
            p = 0               # paragarph number
            # go through each paragraph in the body and add it to the output
            # stop when we reach the end of the body, or we have enough words
            while (word_count < int(max_words)) and (p < len(body)):
                # grab the next paragraph
                paragraph = body[p]
                # split it into words and count them, nothing fancy
                words = paragraph.split()
                word_count += len(words)
                
                # add the paragraph to the text to be written to the output
                text.append(paragraph)
                # add newlines to separate pargraphs ### MAYBE NOT PLATFORM INDEPENDENT???
                text.append(u'\n\n')

                # go onto the next paragraph
                p += 1

            # write our pargraphs to the output
            output_file.writelines(text)
                

if __name__ == '__main__':
    main()

