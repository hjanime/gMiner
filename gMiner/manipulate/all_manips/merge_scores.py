# coding: utf-8

################################# Description ##################################
label           = 'merge_scores'
short_name      = 'Merge scores'
long_name       = 'Complement (boolean NOT)'
input_tracks    = [{'key':'n_tracks', 'position':1, 'kind': 'many', 'fields':['start','end','score']}]
input_args      = [{'key':'geometric', 'position':2, 'type': bool, 'default': False,
                    'doc':'Use the geometric mean instead of the arithmetic mean.'}]
input_meta      = []
output_tracks   = [{'position':1, 'fields': ['start','end','score']}]
tracks_collapse = None
chroms_collapse = 'union'

################################ Documentation #################################
tooltip = \
"""
    The ``merge_scores`` manipulation merges N signals
using some average function. If the boolean value ``geometric``
is true, the geometric mean is used, otherwise the arithmetic
mean is used.
"""

################################## Examples ####################################
numeric_example = \
""""""

visual_example = \
u""""""

#################################### Tests #####################################
from track.test import samples
tests = [
    {'tracks':   [samples['small_features'][1]['sql']],
     'args':     {'l':200},
     'expected': [('chr1',  10, 20,  '', 0.0, 0),
                  ('chr1',  30, 40,  '', 0.0, 0),
                  ('chr1',  50, 60,  '', 0.0, 0),
                  ('chr1',  80, 90,  '', 0.0, 0),
                  ('chr1', 110, 120, '', 0.0, 0),
                  ('chr1', 135, 200, '', 0.0, 0)]}]

############################### Implementation #################################
def generate(manip, n_tracks, geometric=False):
        # Get all iterators #
        sentinel = (sys.maxint, sys.maxint, 0.0)
        tracks = [common.sentinelize(x, sentinel) for x in n_tracks]
        elements = [x.next() for x in tracks]
        tracks_denom = 1.0/len(tracks)
        # Choose meaning function #
        if geometric: mean_fn = lambda x: sum(x)**tracks_denom
        else:         mean_fn = lambda x: sum(x)*tracks_denom
        # Check empty #
        for i in xrange(len(tracks)-1, -1, -1):
            if elements[i] == sentinel:
                tracks.pop(i)
                elements.pop(i)
        # Core loop #
        while tracks:
            # Find the next boundaries #
            start = min([x[0] for x in elements])
            end = min([x[0] for x in elements if x[0] > start] + [x[1] for x in elements])
            # Scores between boundaries #
            scores = [x[2] for x in elements if x[1] > start and x[0] < end]
            if scores: yield (start, end, mean_fn(scores))
            # Iterate over elements #
            for i in xrange(len(tracks)-1, -1, -1):
                # Change all starts #
                if elements[i][0] < end:
                    elements[i] = (end, elements[i][1], elements[i][2])
                # Advance the elements that need to be advanced #
                if elements[i][1] <= end:
                    elements[i] = tracks[i].next()
                # Pop sentinels #
                if elements[i] == sentinel:
                    tracks.pop(i)
                    elements.pop(i)
