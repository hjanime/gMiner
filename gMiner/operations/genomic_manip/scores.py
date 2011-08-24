"""
Manipulations that deal with or only make sense with quantitative information.
"""

# Built-in modules #
import sys

# Internal modules #
from . import Manipulation as Manip
from ... import common

################################################################################
class merge_scores(Manip):
    '''Merges N quantitative streams using some average function.
       If the boolean value `geometric` is false, the arithmetic mean
       is used, otherwise the geometric mean is used.'''

    def __init__(self):
        self.name               = 'Merge scores'
        self.input_tracks       = [{'type':'list of tracks', 'name':'list_of_tracks', 'kind':'quantitative', 'fields':['start','end','score']}]
        self.input_constraints  = []
        self.input_request      = [{'type': bool, 'key': 'geometric', 'name': 'geometric', 'default': False}]
        self.input_special      = []
        self.input_by_chrom     = []
        self.output_tracks      = [{'type': 'track', 'kind': 'quantitative', 'fields': ['start','end','score']}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_union(*args)

    def __call__(self, list_of_tracks, geometric=False):
        # Get all iterators #
        sentinel = (sys.maxint, sys.maxint, 0.0)
        tracks = [common.sentinelize(x, sentinel) for x in list_of_tracks]
        elements = [x.next() for x in tracks]
        # Declare meaning functions #
        def arithmetic_mean(scores): return sum(scores)*tracks_denom
        def geometric_mean(scores):  return sum(scores)**tracks_denom
        tracks_denom = 1.0/len(tracks)
        # Choose meaning function #
        if not geometric: mean_fn = arithmetic_mean
        else:             mean_fn = geometric_mean
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

#-------------------------------------------------------------------------------------------#
class mean_score_by_feature(Manip):
    '''Given a quantitative stream "X" and a qualitative stream "Y"
       computes the mean of scores of every of Y's features in X.
       The output consists of a qualitative stream similar to Y but
       with a new score value property for every feature.'''

    def __init__(self):
        self.name               = 'Mean score by feature'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'quantitative', 'fields': ['start','end','score']},
                                   {'type': 'track', 'name': 'Y', 'kind': 'qualitative',  'fields': ['start','end','name','score','strand']}]
        self.input_constraints  = []
        self.input_request      = []
        self.input_special      = []
        self.input_by_chrom     = []
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start','end','name','score','strand']}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_union(*args)

    def __call__(self, X, Y):
        # Sentinel #
        sentinel = (sys.maxint, sys.maxint, 0.0)
        X = common.sentinelize(X, sentinel)
        # Growing and shrinking list of features in X #
        F = [(-sys.maxint, -sys.maxint, 0.0)]
        # --- Core loop --- #
        for y in Y:
            # Check that we have all the scores necessary #
            while F[-1][0] < y[1]: F.append(X.next())
            # Throw away the scores that are not needed anymore #
            while True:
                if F[0][1] <= y[0]: F.pop(0)
                else: break
            # Compute the average #
            score = 0.0
            for f in F:
                if y[1] <= f[0]: continue
                if f[0] <  y[0]: start = y[0]
                else:            start = f[0]
                if y[1] <  f[1]: end   = y[1]
                else:            end   = f[1]
                score += (end-start) * f[2]
            # Emit a feature #
            yield y[0:3]+(score/(y[1]-y[0]),)+y[4:]

#-------------------------------------------------------------------------------------------#
class threshold(Manip):
    '''Given a stream "X", a real number "s" and an optional output datatype
       defaulting to the input datatype (`quantitative` or `qualitative`),
       will threshold the stream according to the scores of every feature
       and base pair. Four behaviors are possible:

       * The input is `quantitative` and the output should be `quantitative`:
            Any base pair having a score below `s` is set to a score of 0.0.

       * The input is `quantitative` and the output should be `qualitative`:
            The result is a stream where continuous regions which had
            a score equal or above `s` become a feature that has a score
            equal to the mean of the scores in that region weighted
            by base pair.

       * The input is `qualitative` and the output should be `qualitative`:
            Features having a score below `s` are removed.

       * The input is `qualitative` and the output should be `quantitative`:
            Features having a score below `s` are removed. Remaining features
            are converted to regions with a score equal to the score of the
            feature. Where features overlap, the mean of the scores of every
            feature is computed on a per base pair basis.
     '''

    def __init__(self):
        self.name               = 'Threshold with a value'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'any', 'fields': ['start','end','score', '...']}]
        self.input_constraints  = []
        self.input_request      = [{'type': int, 'key': 'threshold', 'name': 's'}]
        self.input_special      = [{'type': 'in_datatype', 'name': 'in_type'},
                                   {'type': 'out_datatype', 'name': 'out_type', 'fields': {'same': 0}}]
        self.input_by_chrom     = []
        self.output_tracks      = [{'type': 'track', 'kind': 'various'}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_union(*args)

    def qual_to_qual(self, X, s):
        for x in X:
            if x[2] >= s: yield x

    def qual_to_quan(self, X, s):
        #TODO (carefull with overlap zones)
        for x in []: yield x

    def quan_to_quan(self, X, s):
        for x in X:
            if x[2] >= s: yield x

    def quan_to_qual(self, X, s):
        from .standard import merge
        for x in merge().quan(self.quan_to_quan(X, s)): yield x

#-------------------------------------------------------------------------------------------#
class window_smoothing(Manip):
    '''Given a quantitative stream and a window size in base pairs,
       will output a new quantitative stream with, at each position
       p, the mean of the scores in the window [p-L, p+L].
       Border cases are handled by zero padding and the signal's
       support is invariant.'''

    def __init__(self):
        self.name               = 'Smooth scores'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'quantitative', 'fields': ['start','end','score']}]
        self.input_constraints  = []
        self.input_request      = [{'type': int, 'key': 'window_size', 'name': 'L', 'default': 200}]
        self.input_special      = []
        self.input_by_chrom     = [{'type': 'stop_val', 'name': 'stop_val'}]
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'score']}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_union(*args)

    def __call__(self, X, L, stop_val):
        # Sentinel #
        sentinel = (sys.maxint, sys.maxint, 0.0)
        X = common.sentinelize(X, sentinel)
        # Growing and shrinking list of features around our moving window #
        F = []
        # Current position counting on nucleotides (first nucleotide is zero) #
        p = -L-2
        # Position since which the mean hasn't changed #
        same_since = -L-3
        # The current mean and the next mean #
        curt_mean = 0
        next_mean = 0
        # Multipication factor instead of division #
        f = 1.0 / (2*L+1)
        # First feature if it exists #
        F.append(X.next())
        if F == [sentinel]: return
        # --- Core loop --- #
        while True:
            # Advance one #
            p += 1
            # Window start and stop #
            s = p-L
            e = p+L+1
            # Scores entering window #
            if F[-1][1] < e: F.append(X.next())
            if F[-1][0] < e: next_mean += F[-1][2] * f
            # Scores exiting window #
            if F[ 0][1] < s: F.pop(0)
            if F[ 0][0] < s: next_mean -= F[ 0][2] * f
            # Border condition on the left #
            if p < 0:
                curt_mean = 0
                same_since = p
                continue
            # Border condition on the right #
            if p == stop_val:
                if curt_mean != 0: yield (same_since, p, curt_mean)
                break
            # Maybe emit a feature #
            if next_mean != curt_mean:
                if curt_mean != 0: yield (same_since, p, curt_mean)
                curt_mean  = next_mean
                same_since = p

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
