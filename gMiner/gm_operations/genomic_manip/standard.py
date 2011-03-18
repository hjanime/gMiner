# Importing #
from . import gmManipulation
from ... import gm_common as gm_com

#-------------------------------------------------------------------------------------------#   
class complement(gmManipulation):
    '''Complement'''
    input              = {'track': {'type': 'qualitative', 'fields': ['start', 'end']}}
    input_constraints  = []
    input_extras       = ['stop_val']
    output             = {'track': {'type': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}}
    output_constraints = []
    chr_fn             = gm_com.gmCollapse.by_appending
    def chr_collapse(self, *args): return gm_com.gmCollapse.by_intersection(*args) 
    

    def run(self, **kwargs):
        '''The result consists of all spaces that were not
        covered by a feature in the original track'''
        last_end = 0
        for x in iterable:
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
    input              = {'track': {'type': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand'], 'num': 1},
                          'track': {'type': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand'], 'num': 2}}
    input_constraints  = ['ordered']
    input_extras       = []
    output             = {'track': {'type': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}}
    output_constraints = []
    def chr_collapse(self, *args): return gm_com.gmCollapse.by_intersection(*args) 
   
    def nose_test():
        pass
    
    def run(self, **kwargs):
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
