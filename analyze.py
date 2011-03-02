#!/usr/bin/env python
#
# Perform Echo Nest Remix analysis on a folder
# of files if they are missing BPM and key tags.
#

import sys
from optparse import OptionParser
from mutagen.id3 import ID3, TKEY, TBPM
from mutagen.easyid3 import EasyID3
import echonest.audio as audio

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

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] dir"
    parser = OptionParser(usage=usage)
    parser.add_option('-r', '--replace', help='Replace existing BPM/key ID3 tags',
            default=False, action='store_true')

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    # do stuff
    mp3s = rwalk(args[0], '*.mp3')
    for mp3 in mp3s:
        tags = ID3(mp3)
        # Skip already analyzed files
        if not options.replace and 'TBPM' in tags and 'TKEY' in tags:
            continue

        echosong = audio.LocalAudioFile(mp3)
        if options.replace or 'TBPM' not in tags:
            tags.add(TBPM(encoding=1, text=unicode(round(echosong.analysis.tempo['value']))))
        if options.replace or 'TKEY' not in tags:
            try:
                tags.add(TKEY(encoding=1, text=key(echosong)))
            except KeyError:
                sys.stderr.write('Incorrect key info; key: %d, mode: %d\n' %
                        (echosong.analysis.key['value'], echosong.analysis.mode['value']))

        tags.save()

if __name__ == '__main__':
    sys.exit(main())
