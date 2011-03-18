#!/usr/bin/env python
#
# Create a list of candidates for mashups given a folder of music that has been
# tagged with analyze.py.
#
# The basic algorithm for grouping songs is as follows:
# * For all songs, generate the set of all "reasonable" BPMs. This is
# essentially the bpm +/- some number n where we also include doubles and
# halves of the song's BPM that fall within a certain range.
# * Create a histogram of these reasonable BPMs.
# * Allow the user to either:
# ** dump out a file of all the mappings, or
# ** query the histogram for song matches.
# * The above is done with or without using key.
#
# Author: Yacin Nadji <yacin@gatech.edu>
#

import sys
from optparse import OptionParser
from functools import partial
from collections import defaultdict

from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.easyid3 import EasyID3

sys.path.append('wulib')
from wulib import flatten, rwalk

def goodbpm(bpm, minbpm=60, maxbpm=190):
    return bpm > minbpm and bpm < maxbpm

def poweroftwos(bpm):
    return [bpm / x for x in range(2, 8, 2)] + \
           [bpm] + \
           [bpm * x for x in range(2, 8, 2)]

def allbpms(bpm, maxdiff=5, minbpm=60, maxbpm=190):
    doubles = poweroftwos(bpm)
    bpms = []
    for dbl in doubles:
        bpms.append([dbl - x for x in range(1, maxdiff + 1)])
        bpms.append([dbl])
        bpms.append([dbl + x for x in range(1, maxdiff + 1)])

    isgood = partial(goodbpm, minbpm=minbpm, maxbpm=maxbpm)
    return filter(isgood, flatten(bpms))

def gettag(tags, tagname):
    try:             return tags[tagname][0]
    except KeyError: return ''

def artist(query):
    """Interactive search function. Search by artist."""
    pass

def title(query):
    """Interactive search function. Search by title."""
    pass

def bpm(query):
    """Interactive search function. Search by bpm."""
    pass

def interact(interactlocals):
    import IPython.ipapi
    IPython.ipapi.launch_new_instance(interactlocals)

def main(argv):
    """main function for standalone usage"""
    usage = "usage: %prog [options] dir"
    parser = OptionParser(usage=usage)
    parser.add_option('-f', '--full', default=False, action='store_true',
                      help='Dump ALL groups')

    (options, args) = parser.parse_args(argv)

    if len(args) != 1:
        parser.print_help()
        return 2

    # do stuff
    mp3s = rwalk(args[0], '*.mp3')
    bpms = defaultdict(list)
    for mp3 in mp3s:
        try:
            tags = ID3(mp3)
            easytags = EasyID3(mp3)
        except ID3NoHeaderError:
            continue

        if 'TXXX:mashupid' in tags:
            for pitchedbpm in allbpms(int(float(tags.get('TBPM').text[0]))):
                bpms[pitchedbpm].append((mp3, gettag(easytags, 'artist'),
                                        gettag(easytags, 'title'),
                                        gettag(easytags, 'genre')))

    bpmgroups = sorted(bpms.keys())
    if options.full:
        for bpm in bpmgroups:
            print('BPM: %d\n' % bpm)
            for path, artist, title, genre in bpms[bpm]:
                print('File: %s' % path)
                print('Artist: %s' % artist)
                print('Title: %s' % title)
                print('Genre: %s' % genre)
    else:
        interact()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
