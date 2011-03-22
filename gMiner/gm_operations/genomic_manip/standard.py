# Modules #
import sys

# Importing #
from . import gmManipulation
from ... import gm_common as gm_com

#-------------------------------------------------------------------------------------------#   
class complement(gmManipulation):
    '''Complement'''
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start', 'end']}]
    input_constraints  = []
    input_other        = []
    input_extras       = [{'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return gm_com.gmCollapse.by_appending(*args) 
    
    def generate(self, X, stop_val):
        '''The result consists of all spaces that were not
        covered by a feature in the original track'''
        last_end = 0
        for x in X:
            if x[0] > last_end:
                yield (last_end, x[0], None, None, '.')
                last_end = x[1]
            else:
                last_end = max(x[1], last_end)
        if last_end < stop_val:
            yield (last_end, stop_val, None, None, '.')

#-------------------------------------------------------------------------------------------#   
class overlap_track(gmManipulation):
    '''Overlap by track'''
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']},
                          {'type': 'track', 'name': 'Y', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    input_constraints  = ['ordered']
    input_other        = []
    input_extras       = []
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return gm_com.gmCollapse.by_intersection(*args) 
   
    def generate(self, X, Y):
        '''Computes the overlap of the first track against the second track
           returning only complete features from the first track'''
        sentinel = [sys.maxint, sys.maxint]
        X = gm_com.sentinelize(X, sentinel)
        Y = gm_com.sentinelize(Y, sentinel)
        x = X.next()
        y = Y.next()
        if x == sentinel or y == sentinel: continue_loop = False
        else: continue_loop = True
        while continue_loop:
            open_window = y[0]
            close_window = y[1]
            # Extend the y window as long as possible #
            while True:
                if y == sentinel: break
                y = Y.next()
                if y[0] > close_window: break
                if y[1] > close_window: close_window = y[1]
            # Read features from X until overshooting the y window #
            while True:
                if x[0] >= close_window: break
                if x[1] > open_window: yield x
                x = X.next()
                if x == sentinel:
                    continue_loop = False
                    break        
