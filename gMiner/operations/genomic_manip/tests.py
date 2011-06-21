# General modules #
import os

# Other modules #
from bbcflib.track import Track
from bbcflib.track.test_variables import yeast_chr_file

# Internal modules #
import gMiner

###################################################################################
def run_one(case, t):
    # Input variables #
    # Input tracks #
    if t.get('tracks'):
        for k,v in t['tracks'].items():
            if type(v) == list:
                t['tracks'][k] = iter(v)
            else:
                if t.get('fields') and t['fields'].get(k):
                    with Track(v) as x:
                        t['tracks'][k] = iter(list(x.read('chr1', fields=t['fields'][k])))
                else:
                    with Track(v) as x:
                        t['tracks'][k] = iter(list(x.read('chr1')))
        kwargs = t.get('input', {})
        kwargs.update(t['tracks'])
    else:
        for i,v in enumerate(t['input']['list_of_tracks']):
            if type(v) == list:
                t['input']['list_of_tracks'][i] = iter(v)
            else:
                with Track(v) as x: t['input']['list_of_tracks'][i] = iter(list(x.read('chr1')))
        kwargs = t['input']
    # Run it #
    case.assertEqual(list(t['fn'](**kwargs)), t['expected'])

def run_request(case, t):
    files = gMiner.run(**t['kwargs'])
    with Track(files[0], chrfile=yeast_chr_file) as x:
        data = list(x.read('chr1'))
    os.remove(files[0])
    case.assertEqual(data, t['expected'])

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
