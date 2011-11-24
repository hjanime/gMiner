# coding: utf-8

################################# Description ##################################
label           = 'complement'
short_name      = 'Complement'
long_name       = 'Complement (boolean NOT)'
input_tracks    = [{'key':'X', 'position':1, 'kind':'single', 'fields':['start','end']}]
input_args      = []
input_meta      = [{'key':'l', 'position':2, 'type': int, 'kind':'chrom_len'}]
output_tracks   = [{'position':1, 'fields': ['start','end']}]
tracks_collapse = None
chroms_collapse = None

################################ Documentation #################################
tooltip = \
"""
    The ``complement`` manipulation takes only one track
for input. The output consists of all intervals that
were not covered by a feature in the input track.
This corresponds to the boolean NOT operation.
"""

################################## Examples ####################################
numeric_example = \
"""
X: (10,20) (30,40)
R: ( 0,10) (20,30) (40,100)
"""

visual_example = \
u"""
X: ──────█████─────────█████──────
R: ██████─────█████████─────██████
"""

#################################### Tests #####################################
from track.test import samples
tests = [
    {'tracks':   [samples['small_features'][1]['sql']],
     'args':     {'l':200},
     'expected': [('chr1',  10, 20, '', 0.0, 0),
                  ('chr1',  30, 40, '', 0.0, 0),
                  ('chr1',  50, 60, '', 0.0, 0),
                  ('chr1',  80, 90, '', 0.0, 0),
                  ('chr1', 110, 120,'', 0.0, 0),
                  ('chr1', 135, 200,'', 0.0, 0)]}]

############################### Implementation #################################
def generate(manip, X, l):
    end = 0
    for x in X:
        if x['start'] > end:
            yield (end, x['start'])
            end = x['end']
        else:
            end = max(x['start'], end)
    if end < l:
        yield (end, l)
