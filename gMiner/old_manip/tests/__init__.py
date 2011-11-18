"""
Unittesting for the various genomic manipulations.
"""

# Built-in modules #
import os

# Internal modules #
import gMiner

# Other modules #
from bbcflib import track
from bbcflib.track.track_collection import yeast_chr_file

################################################################################
def run_one(case, t):
    # Input variables #
    # Input tracks #
    if t.get('tracks'):
        for k,v in t['tracks'].items():
            if type(v) == list:
                t['tracks'][k] = iter(v)
            else:
                if t.get('fields') and t['fields'].get(k):
                    with track.load(v) as x:
                        t['tracks'][k] = iter(list(x.read('chr1', fields=t['fields'][k])))
                else:
                    with track.load(v) as x:
                        t['tracks'][k] = iter(list(x.read('chr1')))
        kwargs = t.get('input', {})
        kwargs.update(t['tracks'])
    else:
        for i,v in enumerate(t['input']['list_of_tracks']):
            if type(v) == list:
                t['input']['list_of_tracks'][i] = iter(v)
            else:
                with track.load(v) as x: t['input']['list_of_tracks'][i] = iter(list(x.read('chr1')))
        kwargs = t['input']
    # Run it #
    case.assertEqual(list(t['fn'](**kwargs)), t['expected'])

def run_request(case, t):
    files = gMiner.run(**t['kwargs'])
    with track.load(files[0], chrmeta=yeast_chr_file) as x:
        data = list(x.read('chr1'))
    os.remove(files[0])
    case.assertEqual(data, t['expected'])

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
