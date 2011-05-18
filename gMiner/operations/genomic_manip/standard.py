# Modules #
import sys

# Importing #
from . import gmManipulation as Manip
from ... import common

#-------------------------------------------------------------------------------------------#
class complement(Manip):
    '''The result consists of all intervals that were not
       covered by a feature in the original stream'''

    name               = 'Complement'
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start', 'end']}]
    input_constraints  = []
    input_other        = []
    input_extras       = [{'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return common.collapse.by_appending(*args) 
    
    def __call__(self, X, stop_val):
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
class internal_merge(Manip):
    '''Merges features that are adjacent or overlapping in one stream'''

    name               = 'Internal merge'
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    input_constraints  = []
    input_other        = []
    input_extras       = [{'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return common.collapse.by_appending(*args) 
    
    def __call__(self, X, stop_val):
        sentinel = (sys.maxint, sys.maxint)
        X = common.sentinelize(X, sentinel)
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
class overlap_track(Manip):
    '''Computes the overlap of the first stream against the second stream
       returning only complete features from the first stream'''

    name               = 'Overlap by track'
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']},
                          {'type': 'track', 'name': 'Y', 'kind': 'qualitative', 'fields': ['start', 'end']}]
    input_constraints  = ['ordered']
    input_other        = []
    input_extras       = []
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return common.collapse.by_intersection(*args) 
   
    def __call__(self, X, Y):
        sentinel = (sys.maxint, sys.maxint)
        X = common.sentinelize(X, sentinel)
        Y = common.sentinelize(Y, sentinel)
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
class overlap_pieces(Manip):
    '''Computes the overlap between both streams returning
       new features that exacly match the overlaping zones'''

    name               = 'Overlap by pieces'
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']},
                          {'type': 'track', 'name': 'Y', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    input_constraints  = ['ordered']
    input_other        = []
    input_extras       = [{'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return common.collapse.by_intersection(*args) 
    
    def __call__(self, X, Y, stop_val):
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
        X = common.sentinelize(X, sentinel)
        Y = common.sentinelize(Y, sentinel)
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

#-------------------------------------------------------------------------------------------# 
class bounded(Manip):
    '''Given a stream of features and two integers 'min_bound', 'max_bound',
       this manipulation will output every feature untouched unless one of the
       features exceeds the specified bounds, in which case it is cropped.'''

    name               = 'Neighborhood regions'
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'any', 'fields': ['start', 'end']}]
    input_constraints  = []
    input_other        = [{'type': int, 'key': 'min_bound', 'name': 'min_bound', 'default': -sys.maxint},
                          {'type': int, 'key': 'max_bound', 'name': 'max_bound', 'default':  sys.maxint}]
    input_extras       = []
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return common.collapse.by_appending(*args)

    def __call__(self, X, min_bound, max_bound):
        for x in X: 
            if not x[1] < min_bound and not x[0] > max_bound and x[0] < x[1]:
                yield (max(x[0],min_bound), min(x[1],max_bound)) + x[2:]

#-------------------------------------------------------------------------------------------# 
class neighborhood(Manip):
    '''Given a stream of features and four integers 'before_start', 'after_end',
       'after_start' and 'before_end', this manipulation will output,
       for every feature in the input stream, one or two features
       in the neighboorhod of the orginal feature.

       * Only 'before_start' and 'after_end' are given:
             (start, end, ...) -> (start+before_start, end+after_end, ...)

       * Only 'before_start' and 'after_start' are given:
             (start, end, ...) -> (start+before_start, start+after_start, ...)

       * Only 'after_end' and 'before_end' are given:
             (start, end, ...) -> (end+before_end, end+after_end, ...)

       * If all four parameters are given, a pair of features is outputed:
             (start, end, ...) -> (start+before_start, start+after_start, ...)
                                  (end+before_end, end+after_end, ...)

       * If the boolean parameter 'on_strand' is set to True,
         features on the negative strand are inverted as such:
             (start, end, ...) -> (start-after_end, start-before_end, ...)
                                  (end-after_start, end-before_start, ...)

       * If the inputed stream is quantitative, only 'before_start' and 'after_end'
         are taken into consideration and must be equal.'''

    name               = 'Neighborhood regions'
    input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'any', 'fields': ['start', 'end']}]
    input_constraints  = []
    input_other        = [{'type': int, 'key': 'before_start', 'name': 'before_start', 'default': None},
                          {'type': int, 'key': 'after_end',    'name': 'after_end',    'default': None},
                          {'type': int, 'key': 'after_start',  'name': 'after_start',  'default': None},
                          {'type': int, 'key': 'before_end',   'name': 'before_end',   'default': None}]
    input_extras       = [{'type': 'datatype', 'name': 'datatype'},
                          {'type': 'stop_val', 'name': 'stop_val'}]
    output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end']}]
    output_constraints = []
    output_other       = []
    def chr_collapse(self, *args): return common.collapse.by_appending(*args)

    def quan(self, stop_val, **kwargs):
        def generate(X, before_start=None, after_end=None, after_start=None, before_end=None, on_strand=False):
            if before_start and after_start:
                if before_start > after_start:
                    raise Exception("'before_start' cannot be larger than 'after_start'")
            if before_end and after_end:
                if before_end > after_end:
                    raise Exception("before_end cannot be larger than 'after_end'")
            if not on_strand:
                if before_start and after_end and after_start and before_end:
                    for x in X:
                        yield (x[0]+before_start, x[0]+after_start) + x[2:]
                        yield (x[1]+before_end,   x[1]+after_end) + x[2:]
                if before_start and after_start:
                    for x in X: yield (x[0]+before_start, x[0]+after_start)  + x[2:]
                if before_end and after_end:
                    for x in X: yield (x[1]+before_end,   x[1]+after_end)    + x[2:]
                if before_start and after_end:
                    for x in X: yield (x[0]+before_start, x[1]+after_end)    + x[2:]
            else:
                if before_start and after_end and after_start and before_end:
                    for x in X:
                        yield (x[0]-after_end,   x[0]-before_end) + x[2:]
                        yield (x[1]-after_start, x[1]-before_start) + x[2:]
                if before_start and after_start:
                    for x in X: yield (x[1]-after_start,  x[1]-before_start) + x[2:]
                if after_end and before_end:
                    for x in X: yield (x[0]-after_end,    x[0]-before_end) + x[2:]
                if before_start and after_end:
                    for x in X: yield (x[0]-after_end,    x[1]-before_start) + x[2:]
        X = generate(**kwargs) 
        for x in bounded()(X, 0, stop_val): yield x

    def qual(self, stop_val, **kwargs):
        def generate(X, before_start=None, after_end=None, after_start=None, before_end=None, on_strand=False):
            if on_strand:
                raise Exception("As the track is quantitative, you cannot specify 'on_strand=True'")
            if after_start:
                raise Exception("As the track is quantitative, you cannot specify a value for 'after_start'")
            if before_end:
                raise Exception("As the track is quantitative, you cannot specify a value for 'before_end'")
            if before_start != after_end:
                raise Exception("As the track is quantitative, 'before_start' and 'after_start' need to be equal")
            for x in X: yield (x[0]+before_start, x[1]+before_start) + x[2:]
        X = generate(**kwargs)
        for x in bounded()(X, 0, stop_val): yield x

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
