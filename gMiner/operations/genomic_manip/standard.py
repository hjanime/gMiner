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
        '''The result consists of all intervals that were not
           covered by a feature in the original track'''
        last_end = 0
        for x in X:
            if x[0] > last_end:
                yield (last_end, x[0], None, None, 0)
                last_end = x[1]
            else:
                last_end = max(x[1], last_end)
        if last_end < stop_val:
            yield (last_end, stop_val, None, None, 0)

#-------------------------------------------------------------------------------------------# 
class internal_merge(gmManipulation):
    '''Internal merge'''
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    input_constraints  = []
    input_other        = []
    input_extras       = [{'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return gm_com.gmCollapse.by_appending(*args) 
    
    def generate(self, X, stop_val):
        '''Merges features that are adjacent or overlapping in one track'''
        sentinel = (sys.maxint, sys.maxint)
        X = gm_com.sentinelize(X, sentinel)
        x = X.next()
        if x != sentinel:
            while True:
                x_next = X.next()
                if x_next == sentinel:
                    yield tuple(x)
                    break
                if (x_next[0] <= x[1]):
                    x = list(x)
                    x[1] = max(x[1], x_next[1])
                    x[2] = x[2] + ' + ' + x_next[2]
                    x[3] = x[3] + x_next[3]
                    x[4] = x[4] == x_next[4] and x[4] or 0
                else:
                    yield tuple(x) 
                    x = x_next

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
        sentinel = (sys.maxint, sys.maxint)
        X = gm_com.sentinelize(X, sentinel)
        Y = gm_com.sentinelize(Y, sentinel)
        x = X.next()
        y = Y.next()
        if x == sentinel or y == sentinel: continue_loop = False
        else:                              continue_loop = True
        while continue_loop:
            open_window  = y[0]
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
                if x[1] >  open_window:  yield x
                x = X.next()
                if x == sentinel:
                    continue_loop = False
                    break       

#-------------------------------------------------------------------------------------------#
class overlap_pieces(gmManipulation):
    '''Overlap by pieces'''
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']},
                          {'type': 'track', 'name': 'Y', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    input_constraints  = ['ordered']
    input_other        = []
    input_extras       = [{'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return gm_com.gmCollapse.by_intersection(*args) 
    
    def generate(self, X, Y, stop_val):
        '''Computes the overlap between both tracks returning
           new features that exacly match the overlaping zones'''
        def scan(f, Wf, g, Wg, lastPick):
            g_index = 0
            while g_index < len(Wg):
                g_current = Wg[g_index]
                if left_of(g_current, f):
                    Wg.pop(g_index)
                else:
                    g_index += 1
                    if overlaps(g_current, f):
                        yield (max(f[0],g_current[0]), min(f[1],g_current[1]), f[2] + " with " + g_current[2], 0.0, 0)
            if not left_of(f, g):
                Wf.append(f)
        def left_of(a, b):
            return (a[1] < b[0])
        def overlaps(a, b):
            return min(a[1],b[1]) - max(a[0],b[0]) > 0
        # fjoin: Simple and Efficient Computation of Feature Overlap #
        # J. Comp. Bio., 13(8), Oct. 2006, pp 1457-1464. #
        sentinel = (sys.maxint, sys.maxint)
        X = gm_com.sentinelize(X, sentinel)
        Y = gm_com.sentinelize(Y, sentinel)
        x = X.next()
        y = Y.next()
        Wx = []
        Wy = []
        while x[0] != sentinel or y[0] != sentinel:
            if x[0] < y[0]:
                for z in scan(x, Wx, y, Wy, 0): yield z
                x = X.next()
            else:
                for z in scan(y, Wy, x, Wx, 1): yield z 
                y = Y.next()      

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
