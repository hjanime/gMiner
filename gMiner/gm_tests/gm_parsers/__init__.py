# General modules #
import os, re

# gMiner modules #
from ... import gm_tracks as gm_tra
from ... import gm_tests
from ...gm_constants import *

def parse_challange():
    # Nice color output #
    def message(path, name, status, expected, extra=None):
        if extra: extra = re.sub(' ' + path, '', extra)
        if extra: extra = re.sub(' - HTTP 400', '', extra)
        s = name.ljust(26)
        if status==expected:
            s += '\033[0;37m\033[42m passed the test \033[0m'
        else:
            s += '\033[1;37m\033[41m\033[5;37m failed the test \033[0m'
        if extra:
            s += '  (' + extra + ')' 
        print s
    # Main loop #
    for path, expected in gm_tests.gm_parser_tests:
        name = path.split('/')[-1]
        dir  = '/'.join(path.split('/')[:-1]) + '/'
        dest = dir + name.split('.')[0] + '.sql' 
        try:
            track = gm_tra.gmTrack.Factory({'name': name, 'location': path, 'chrs': gm_tests.yeast_chr_file}, conversion=False)
            gm_tra.gmTrackConverter.convert(track, dest , 'sql', 'qualitative', name)
        except Exception as err:
            message(path, name, False, expected, str(err))
            continue
        finally:
            pass
            #os.remove(dest)
        message(path, name, True, expected)
