"""
Basic manipulations that are used internally by other more complex manipulations.
"""

# Built-in modules #
import sys

# Internal modules #
from . import Manipulation as Manip
from ... import common

################################################################################
class qual_to_quan(Manip):
    '''Convert a qualitative stream to a quantitative one'''

    def __init__(self):
        self.name               = 'Flatten'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start','end','...']}]
        self.input_constraints  = []
        self.input_request      = []
        self.input_special      = []
        self.output_tracks      = [{'type': 'track', 'kind': 'quantitative', 'fields': ['start','end','score']}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_appending(*args)

    def __call__(self, X):
        # Setup #
        for x in X: break
        if 'x' not in locals(): return
        if len(x) > 2:
            yield (x[0], x[1], x[2])
            for x in X: yield (x[0], x[1], x[2])
        else:
            yield (x[0], x[1], 1.0)
            for x in X: yield (x[0], x[1], 1.0)

class quan_to_qual(Manip):
    '''Convert a quantitative stream to a qualitative one'''

    def __init__(self):
        self.name               = 'Flatten'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'quantitative', 'fields': ['start','end','score']}]
        self.input_constraints  = []
        self.input_request      = []
        self.input_special      = []
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start','end','name','score','strand']}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_appending(*args)

    def __call__(self, X):
        # Setup #
        for x in X: yield (x[0], x[1], 'Unnamed', x[2], 0)

#------------------------------------------------------------------------------#
class flatten(Manip):
    '''From a interval based format create the corresponding
       numeric vector'''

    def __init__(self):
        self.name               = 'Flatten'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'quantitative', 'fields': ['start','end','score']}]
        self.input_constraints  = []
        self.input_request      = []
        self.input_special      = []
        self.input_by_chrom     = [{'type': 'stop_val', 'name': 'stop_val'}]
        self.output_tracks      = []
        self.output_constraints = []
        self.output_other       = [list]

    def chr_collapse(self, *args): return common.collapse.by_appending(*args)

    def __call__(self, X, stop_val=None):
        # Setup #
        last_end = 0
        # Core loop #
        for x in X:
            for i in xrange(last_end, x[0]): yield 0.0
            for i in xrange(x[0],     x[1]): yield x[2]
            last_end = x[1]
        # End piece #
        if stop_val:
            for i in xrange(x[1],stop_val): yield 0.0

#------------------------------------------------------------------------------#
class bounded(Manip):
    '''Given a stream of features and two integers `min_bound`, `max_bound`,
       this manipulation will output every feature unmodified unless one of the
       features exceed the specified bounds, in which case it is cropped.'''

    def __init__(self):
        self.name               = 'Neighborhood regions'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'any', 'fields': ['start','end', '...']}]
        self.input_constraints  = []
        self.input_request      = [{'type': int, 'key': 'min_bound', 'name': 'min_bound', 'default': -sys.maxint},
                                   {'type': int, 'key': 'max_bound', 'name': 'max_bound', 'default':  sys.maxint}]
        self.input_special      = []
        self.input_by_chrom     = []
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': {'same': 0}}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_appending(*args)

    def __call__(self, X, min_bound, max_bound):
        for x in X:
            if not x[1] < min_bound and not x[0] > max_bound and x[0] < x[1]:
                yield (max(x[0],min_bound), min(x[1],max_bound)) + x[2:]

#------------------------------------------------------------------------------#
class concatenate(Manip):
    '''Concatenates N streams such as the resulting stream
       contains all the features of every inputed stream.'''

    def __init__(self):
        self.name               = 'Merge scores'
        self.input_tracks       = [{'type':'list of tracks', 'name':'list_of_tracks', 'kind':'quantitative', 'fields':['start','end','...']}]
        self.input_constraints  = []
        self.input_request      = []
        self.input_special      = []
        self.input_by_chrom     = []
        self.output_tracks      = [{'type': 'track', 'kind': 'any', 'fields': ['start','end','...']}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_union(*args)

    def __call__(self, list_of_tracks):
        # Get all iterators #
        sentinel = (sys.maxint, sys.maxint, 0.0)
        tracks   = [common.sentinelize(x, sentinel) for x in list_of_tracks]
        features = range(len(tracks))
        # Advance feature #
        def advance(i):
            features[i] = tracks[i].next()
            if features[i] == sentinel:
                tracks.pop(i)
                features.pop(i)
        # Find lowest feature #
        def get_lowest_feature():
            from operator import itemgetter
            i = min(enumerate([(f[0],f[1]) for f in features]), key=itemgetter(1))[0]
            return i, features[i]
        # Core loop #
        for i in xrange(len(tracks)-1, -1, -1): advance(i)
        while tracks:
            i,f = get_lowest_feature()
            yield f
            advance(i)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
