import os
import re
import glob
import subprocess

from optparse import OptionParser

def main():
    usage = "%prog project_dir"
    parser = OptionParser(usage=usage)
    #parser.add_option('-n', dest='n', default=100,
    #                  help='Number of words per topic: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()
    project_dir = args[0]

    input_dirs = glob.glob(os.path.join(project_dir, '*'))
    input_dirs.sort()

    for d in input_dirs:
        basename = os.path.basename(d)
        basename = re.sub(r'\s', '_', basename)
        print(basename)
        csv_file = os.path.join(d, 'metadata', 'summary.csv')
        json_file = os.path.join(d, 'metadata', 'metadata.json')
        command = ["python", "convert_metadata.py", csv_file, json_file]
        print(" ".join(command))
        subprocess.call(command)


if __name__ == '__main__':
    main()
