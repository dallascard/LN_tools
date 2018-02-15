import os
import glob
import subprocess

from optparse import OptionParser

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
    input_dirs.sort()

    for d in input_dirs:
        basename = os.path.basename(d)
        print(basename)
        input_dir_d = d
        output_dir_d = os.path.join(output_dir, basename)
        subprocess.call(["python", "parse_LN_to_JSON.py", input_dir_d, output_dir_d, basename])


if __name__ == '__main__':
    main()
