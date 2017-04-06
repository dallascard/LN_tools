import os
import json
import codecs
import pandas as pd
from optparse import OptionParser

def main():
    usage = "%prog summary.csv output_dir"
    parser = OptionParser(usage=usage)
    #parser.add_option('--keyword', dest='key', default=None,
    #                  help='Keyword argument: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')


    (options, args) = parser.parse_args()
    input_file = args[0]
    output_dir = args[1]

    df = pd.read_csv(input_file)

    summary = {}

    for i in df.index:
        row = df.loc[i]
        key = os.path.splitext(row['filename'])[0]
        fulldate = int(row['fulldate'])
        year = int(row['year'])
        month = int(row['month'])
        day = int(row['day'])
        source = row['source']

        summary[key] = {'source': source, 'day': day, 'month': month, 'year': year, 'fulldate': fulldate}

    with codecs.open(os.path.join(output_dir, 'summary.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)


if __name__ == '__main__':
    main()
