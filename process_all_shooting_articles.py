import os
import glob

from optparse import OptionParser

import file_handling as fh
from parse_LN_to_JSON import parse_LN_to_JSON

def main():
    usage = "%prog stanford_dir output_dir"
    parser = OptionParser(usage=usage)
    #parser.add_option('-n', dest='n', default=100,
    #                  help='Number of words per topic: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()
    stanford_dir = args[0]
    output_dir = args[1]

    input_dirs = glob.glob(os.path.join(stanford_dir, '*'))

    for d in input_dirs:
        basename = os.path.basename(d)
        print(basename)
        #parse_LN_to_JSON(input_dir, output_dir, output_prefix, start, write_files)


if __name__ == '__main__':
    main()
