# Modules #
import sys

# Importing #
from . import gmManipulation as Manip
from ... import common

#-------------------------------------------------------------------------------------------#
class merge_scores(Manip):
    '''Merges N quantitative streams using the average fucntion'''
    
    name               = 'Merge scores'
    input_tracks       = [{'type': 'list of tracks', 'name': 'list_of_tracks', 'kind': 'quantitative', 'fields': ['start', 'end', 'score']}]
    input_constraints  = []
    input_other        = []
    input_extras       = [{'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'quantitative', 'fields': ['start', 'end', 'score']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return common.collapse.by_union(*args) 
    
    def __call__(self, list_of_tracks, stop_val):
        # Get all iterators #
        sentinel = (sys.maxint, sys.maxint, 0.0)
        tracks = [common.sentinelize(x, sentinel) for x in list_of_tracks]
        elements = [x.next() for x in tracks]
        tracks_denom = 1.0/len(tracks)
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
            if scores:
                score = sum(scores)*tracks_denom
                if abs(score) > 1e-10: yield (start, end, score)
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
    '''Given a quantitative stream "X" and a qualititive stream "Y"
       computes the mean of scores in X for every feature in Y.
       The output consits of a qualitative stream simliar to Y but
       with a new score value proprety for every feature.'''

    name               = 'Mean score by feature'
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'quantitative', 'fields': ['start', 'end', 'score']},
                          {'type': 'track', 'name': 'Y', 'kind': 'qualitative',  'fields': ['start', 'end', 'name', 'score', 'strand']}]
    input_constraints  = []
    input_other        = []
    input_extras       = []
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    output_constraints = []
    output_other       = []
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
            yield (y[0], y[1], y[2], score/(y[1]-y[0]), y[4])

#-------------------------------------------------------------------------------------------#
class window_smoothing(Manip):
    '''Given a quantiative stream and a window size in base pairs,
       will output a new quantiative stream with, at each position
       p, the mean of the scores in the window [p-L, p+L].
       Border cases are handled by zero padding and the signal's
       support is invariant.'''

    name               = 'Smooth scores'
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'quantiative', 'fields': ['start', 'end', 'score']}]
    input_constraints  = []
    input_other        = [{'type': int, 'key': 'window_size', 'name': 'L', 'default': 200}]
    input_extras       = [{'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'score']}]
    output_constraints = []
    output_other       = []
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

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
