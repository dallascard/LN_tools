# -*- coding: utf-8 -*-
"""
This script takes a json file of case_ids and converts the corresponding original articles
(located into the json_dir) to shortened versions (written to output_dir)

The csv file should have the case_ids in the first column

The json files to be converted come from parse_LN_to_JSON.py

@author: dcard
"""

# import modules
import os
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
    all_short_dir = project_dir + '/all_short/'

    if not path.exists(json_dir):
        exit("Error: json directory not found: " + json_dir)
        
    if not path.exists(all_short_dir):
        os.makedirs(all_short_dir)

    files = glob.glob(json_dir + '*.json')
    files.sort()

    print("Saving all")

    count = 0
    for json_filename in files:
        #json_filename = json_dir + '/' + json_prefix + case_id + '.json'
        basename = os.path.basename(json_filename)
        prefix = os.path.splitext(basename)[0]
        case_id = prefix[len(json_prefix):]

        # open the json file, read it in, and unpack it
        json_file = codecs.open(json_filename, encoding = 'utf-8')
        json_text = json_file.read()
        json_file.close()
        doc = loads(json_text, encoding='utf-8')

        output_file_name = all_short_dir + json_prefix + case_id + '_short'+ '.txt'
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

