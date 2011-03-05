#!/usr/bin/env python
#
# Calls Echo Nest Remix API to analyze all mp3 files in a directory. This
# modifies the ID3 tags to include bpm/key information. Full analysis results
# are stored in a "shelve database" and a key to the results are stored in the
# ID3 tags as well.
#
# Author: Yacin Nadji <yacin@gatech.edu>
#

import sys
from optparse import OptionParser
import shelve
from time import sleep
from random import randint

from mutagen.id3 import ID3, TKEY, TBPM, TXXX
from mutagen.easyid3 import EasyID3
import echonest.audio as audio
from pyechonest.track import track_from_id

sys.path.append('wulib')
from wulib import rwalk

# Not sure if this is "music theory" correct, but I'm pretty sure this is what
# the mapping is according to Echo Nest Remix.
keymap = {
    0:  'C',
    1:  'C#',
    2:  'D',
    3:  'D#',
    4:  'E',
    5:  'F',
    6:  'F#',
    7:  'G',
    8:  'G#',
    9:  'A',
    10: 'A#',
    11: 'B'
}

modemap = {
    0:  'm',
    1:  ''
}

def key(echosong):
    return u'%s%s' % (keymap[echosong.analysis.key['value']],
                      modemap[echosong.analysis.mode['value']])

def main(argv):
    """main function for standalone usage"""
    usage = "usage: %prog [options] dir dbfile"
    parser = OptionParser(usage=usage)
    parser.add_option('-r', '--replace', help='Replace existing BPM/key ID3 tags',
            default=False, action='store_true')

    (options, args) = parser.parse_args(argv)

    if len(args) != 2:
        parser.print_help()
        return 2

    # do stuff
    mp3s = rwalk(args[0], '*.mp3')

    # Initialize shelve db. Check for existing 'maxkey'.
    db = shelve.open(args[1])
    try:
        idx = db['maxkey']
    except KeyError:
        idx = u'0'

    for mp3 in mp3s:
        tags = ID3(mp3)
        # Skip already analyzed files
        if not options.replace and 'TXXX:mashupid' in tags:
            continue

        echosong = audio.LocalAnalysis(mp3)
        moreinfo = track_from_id(echosong.analysis.identifier)

        # Add main tags
        tags.add(TBPM(encoding=1, text=unicode(round(echosong.analysis.tempo['value']))))
        try:
            tags.add(TKEY(encoding=1, text=key(echosong)))
        except KeyError:
            sys.stderr.write('Incorrect key info; key: %d, mode: %d\n' %
                    (echosong.analysis.key['value'], echosong.analysis.mode['value']))
        tags.add(TXXX(encoding=3, desc=u'danceability', text=unicode(moreinfo.danceability)))
        tags.add(TXXX(encoding=3, desc=u'energy', text=unicode(moreinfo.energy)))
        tags.add(TXXX(encoding=3, desc=u'loudness', text=unicode(moreinfo.loudness)))

        # Create ID and insert into db
        tags.add(TXXX(encoding=3, desc=u'mashupid', text=idx))
        tags.save()

        db[idx] = echosong
        idx = unicode(int(idx) + 1)

        # So we don't hammer their servers
        print('Finished analyzing %s, sleeping...' % mp3)
        sleep(randint(0, 3))

    # Update 'maxkey'.
    db['maxkey'] = idx

    db.close()
    print('Done!')

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
