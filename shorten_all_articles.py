import os
import re
import glob
import subprocess

from optparse import OptionParser

def main():
    usage = "%prog project_dir"
    parser = OptionParser(usage=usage)
    parser.add_option('-n', dest='n', default=2000,
                      help='Shorten to this many words: default=%default')
    #parser.add_option('--boolarg', action="store_true", dest="boolarg", default=False,
    #                  help='Keyword argument: default=%default')

    (options, args) = parser.parse_args()
    project_dir = args[0]
    n = int(options.n)

    input_dirs = glob.glob(os.path.join(project_dir, '*'))
    input_dirs.sort()

    for d in input_dirs:
        basename = os.path.basename(d)
        basename = re.sub(r'\s', '_', basename)
        print(basename)
        command = ["python", "shorten_articles.py", d, basename + "-", "-w", str(n)]
        print(" ".join(command))
        subprocess.call(command)


if __name__ == '__main__':
    main()
