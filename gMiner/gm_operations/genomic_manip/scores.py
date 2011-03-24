# Modules #
import sys

# Importing #
from . import gmManipulation
from ... import gm_common as gm_com

#-------------------------------------------------------------------------------------------#   
class merge_scores(gmManipulation):
    '''Merge scores'''
    input_tracks       = [{'type': 'list of tracks', 'name': 'list_of_tracks', 'kind': 'quantitative', 'fields': ['start', 'end', 'score']}]
    input_constraints  = []
    input_other        = []
    input_extras       = [{'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'quantitative', 'fields': ['start', 'end', 'score']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return gm_com.gmCollapse.by_union(*args) 
    
    def generate(self, list_of_tracks, stop_val):
        '''Merges N quantitative tracks using the average fucntion'''
        # Get all iterators #
        sentinel = [sys.maxint, sys.maxint, 0.0]
        tracks = [gm_com.sentinelize(x, sentinel) for x in list_of_tracks]
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
class mean_score_by_feature(gmManipulation):
    '''Mean score by feature'''
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'quantitative', 'fields': ['start', 'end', 'score']},
                          {'type': 'track', 'name': 'Y', 'kind': 'qualitative',  'fields': ['start', 'end', 'name', 'score', 'strand']}]
    input_constraints  = []
    input_other        = []
    input_extras       = []
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return gm_com.gmCollapse.by_union(*args) 
    
    def generate(self, X, Y):
        '''Given a quantitative track "X" and a qualititive track "Y"
           computes the mean of scores in X for every feature in Y.
           The output consits of a qualitative track simliar to Y but
           with added score values.'''
        pass #TODO

#-------------------------------------------------------------------------------------------#   
class window_smoothing(gmManipulation):
    '''Smooth scores'''
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'quantiative', 'fields': ['start', 'end', 'score']}]
    input_constraints  = []
    input_other        = [{'type': int, 'key': 'window_size', 'name': 'L', 'default': 200}]
    input_extras       = [{'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'score']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return gm_com.gmCollapse.by_union(*args) 
    
    def generate(self, X, L, stop_val):
        '''Given a quantiative track and a window size in base pairs,
           will output a new quantiative track with, at each position
           p, the mean of the scores in the window [p-L, p+L].
           Border cases are handled by signal zero padding.'''
        # Sentinel #
        sentinel = [sys.maxint, sys.maxint, 0.0]
        X = gm_com.sentinelize(X, sentinel)
        # Growing and shrinking list of features #
        F = []
        # Current position counting on nucleotides #
        p = -L-2
        # Position since which the mean hasn't changed #
        same_since = -L-3 
        # The current mean and next mean #
        curt_mean = 0
        next_mean = 0
        # Multipication factor #
        f = 1.0 / (2*L+1)
        # First feature #
        F.append(X.next())
        if F == [sentinel]: return
        # Core loop #
        while True:
            # Advance one #
            p += 1                                            #; print "p is " + str(p)
            # Window start and stop #
            s = p-L                                           #; print "s is " + str(s)
            e = p+L+1                                         #; print "e is " + str(e)
            # Scores entering window # 
            if F[-1][1] < e: F.append(X.next())               #; print "appended " + str(F[-1])
            if F[-1][0] < e: next_mean += F[-1][2] * f        #; print "adding "   + str(F[-1][2]) 
            # Scores exiting window # 
            if F[ 0][1] < s: F.pop(0)                         #; print "poped last"
            if F[ 0][0] < s: next_mean -= F[ 0][2] * f        #; print "removing " + str(F[ 0][2])
            # Border condition left #
            if p < 0:
                curt_mean = 0
                same_since = p
                continue
            # Border condition right #                                  
            if p == stop_val:
                if curt_mean != 0: yield (same_since, p, curt_mean)
                break
            # Emit feature #
            if next_mean != curt_mean:
                if curt_mean != 0: yield (same_since, p, curt_mean)
                curt_mean  = next_mean
                same_since = p
