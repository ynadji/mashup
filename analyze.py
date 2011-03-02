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
            tags.add(TKEY(encoding=1, text=unicode(echosong.analysis.key['value'])))

        tags.save()

if __name__ == '__main__':
    sys.exit(main())
