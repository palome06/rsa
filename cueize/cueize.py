import sys
import getopt
from song import Song
import type_a
import type_b

if __name__ == '__main__':
    try:
        options, args = getopt.getopt(sys.argv[1:], 'hj:r:w:', ['help', 'job_type=', 'root=', 'wiki='])
    except getopt.GetoptError:
        sys.exit()
    job_type = 'A'
    root_path = '.'
    wiki_path = 'wikipedia.txt'
    for name, value in options:
        if name in ('-h', '--help'):
            print('play.py [--job_type|--root|--wiki|--help]')
            exit(0)
        elif name in ('-j', '--job_type'):
            job_type = value.upper()
        elif name in ('-r', '--root'):
            root_path = value
        elif name in ('-w', '--wiki'):
            wiki_path = value
    if job_type == 'A':
        type_a.run(wiki_path=wiki_path, root_path=root_path)
    elif job_type == 'B':
        type_b.run(wiki_path=wiki_path, root_path=root_path)
    # deal_with_all_files_type_b(r'D:\PlatWorld\STDownloads\Baidu\2nd Album - 革命の丘')

# load format: single format, album format threater format
# wave format:
# cue format: 