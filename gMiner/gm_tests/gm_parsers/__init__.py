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
        title, extension = name.split('.')
        def ext_to_clr(ext): return str({'bed':6,'wig':4,'gff':5}[ext])
        if expected: s = ('\033[1;37;4'+ ext_to_clr(extension) + 'm' + extension + '\033[0m' + ': ' + title).ljust(38)
        else:        s = ('\033[1;30;4'+ ext_to_clr(extension) + 'm' + extension + '\033[0m' + ': ' + title).ljust(38) 
        if status==expected:
            s += '\033[0;37m\033[42m passed the test \033[0m'
            if extra: s += ' \033[2;37m' + extra + '\033[0m'
        else:
            s += '\033[1;37m\033[41m\033[5;37m failed the test \033[0m'
            if extra: s += ' \033[1;33m' + extra + '\033[0m' 
        print s
    # Main loop #
    for path, expected in gm_tests.gm_parser_tests:
        #if not path.endswith('.wig'): continue
        #if not path.endswith('var_overwrite.wig'): continue
        name = path.split('/')[-1]
        dir  = '/'.join(path.split('/')[:-1]) + '/'
        dest = dir + name.split('.')[0] + '.sql'
        if os.path.exists(dest): os.remove(dest) 
        try:
            track = gm_tra.gmTrack.Factory({'name': name, 'location': path, 'chrs': gm_tests.yeast_chr_file}, conversion=False)
            gm_tra.gmTrackConverter.convert(track, dest , 'sql', 'qualitative', name)
        except Exception as err:
            message(path, name, False, expected, str(err))
            os.remove(dest)
            continue
        message(path, name, True, expected)

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
