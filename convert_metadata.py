import csv
import json
import codecs
import os.path
from optparse import OptionParser

import sources

def main():

    usage = "%prog metadata.csv metadata.json"
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()

    output = args[1]

    metadata = {}
    SOURCES = sources.SOURCES
    sources_found = set()
    
    csv_filename = args[0]
    if os.path.exists(csv_filename):
        with codecs.open(csv_filename, 'rU') as csv_file:
            reader = csv.reader(csv_file)
            row_count = 0
            for row in reader:
                # read header
                if row_count == 0:
                    pass
                else:
                    filename = row[1]
                    key = os.path.splitext(filename)[0]
                    source = row[4]
                    if source not in SOURCES:
                        raise Exception("Source not found:" + source)
                    source = SOURCES[source]
                    if source not in sources_found:
                        sources_found.add(source)
                    year = int(row[5])
                    month = int(row[6])
                    day = int(row[7])
                    fulldate = int(row[8])
                    metadata[key] = {'source':source, 'year':year, 'month':month, 'day':day, 'fulldate':fulldate}
                row_count += 1
    print "read", row_count, "rows"

    print sources_found

    #sources_filename = 'sources.json'
    #with codecs.open(sources_filename, 'w', encoding='utf-8') as sources_file:
    #    json.dump(list(sources), sources_file, indent=2)
    
    """
    articles_by_year = {}
    keys = metadata.keys()
    for k in keys:
        year = metadata[k]['year']
        if articles_by_year.has_key(year):
            articles_by_year[year] += 1
        else:
            articles_by_year[year] = 1
            
    keys = articles_by_year.keys()
    keys.sort()
    for k in keys:
        print k, articles_by_year[k]
    """
    
    json_filename = output
    with codecs.open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(metadata, json_file, indent=2)
        
    print "Done!"

if __name__ == '__main__':
    main()
