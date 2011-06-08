# Modules #
import sys

# Importing #
from . import Manipulation as Manip
from ... import common

#-------------------------------------------------------------------------------------------#
class complement(Manip):
    '''The result consists of all intervals that were not
       covered by a feature in the original stream'''

    def __init__(self): 
        self.name               = 'Complement'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start','end']}]
        self.input_constraints  = []
        self.input_request      = []
        self.input_special      = []
        self.input_by_chrom     = [{'type': 'stop_val', 'name': 'stop_val'}]
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start','end','name','score','strand']}]
        self.output_constraints = []
        self.output_other       = []

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
class merge(Manip):
    '''Merges features that are adjacent or overlapping in one stream'''

    def __init__(self): 
        self.name               = 'Internal merge'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start','end', '...']}]
        self.input_constraints  = []
        self.input_request      = []
        self.input_special      = [{'type': 'in_datatype', 'name': 'in_type'}]
        self.input_by_chrom     = []
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': {'same': 0}}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_appending(*args) 
   
    def quan(self, X):
        # Setup #
        for x in X: break
        if 'x' not in locals(): return
        # Core loop #
        for y in X:
            if y[0] == x[1]:
                x = list(x)
                l_x = x[1] - x[0]
                l_y = y[1] - y[0]
                x[2] = (l_x*x[2] + l_y*y[2])  / (l_x+l_y) 
                x[1] = y[1]
            else:
                yield tuple(x)
                x = y
        # Last feature #
        yield tuple(x)
        
    def qual(self, X):
        # Setup #
        for x in X: break
        if 'x' not in locals(): return
        # Core loop #
        for y in X:
            if y[0] == x[1]:
                x = list(x)
                x[1] = max(x[1], y[1])
                x[2] = x[2] + ' + ' + y[2]
                x[3] = x[3] + y[3]
                x[4] = x[4] == y[4] and x[4] or 0
            else:
                yield tuple(x)
                x = y
        # Last feature #
        yield tuple(x)

#-------------------------------------------------------------------------------------------# 
class overlap(Manip):
    '''Computes the overlap of the first stream against the second stream
       returning only complete features from the first stream'''

    def __init__(self): 
        self.name               = 'Overlap by track'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'qualitative', 'fields': ['start','end','name','score','strand']},
                                   {'type': 'track', 'name': 'Y', 'kind': 'qualitative', 'fields': ['start','end']}]
        self.input_constraints  = ['ordered']
        self.input_request      = []
        self.input_special      = []
        self.input_by_chrom     = []
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start', 'end', 'name', 'score', 'strand']}]
        self.output_constraints = []
        self.output_other       = []

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
class neighborhood(Manip):
    '''Given a stream of features and four integers `before_start`, `after_end`,
       `after_start` and `before_end`, this manipulation will output,
       for every feature in the input stream, one or two features
       in the neighboorhod of the orginal feature.

       * Only `before_start` and `after_end` are given::

             (start, end, ...) -> (start+before_start, end+after_end, ...)

       * Only `before_start` and `after_start` are given::

             (start, end, ...) -> (start+before_start, start+after_start, ...)

       * Only `after_end` and `before_end` are given::

             (start, end, ...) -> (end+before_end, end+after_end, ...)

       * If all four parameters are given, a pair of features is outputed::

             (start, end, ...) -> (start+before_start, start+after_start, ...)
                                  (end+before_end, end+after_end, ...)

       * If the boolean parameter `on_strand` is set to True,
         features on the negative strand are inverted as such::

             (start, end, ...) -> (start-after_end, start-before_end, ...)
                                  (end-after_start, end-before_start, ...)

       * If the inputed stream is quantitative, only `before_start` and `after_end`
         are taken into consideration and must be equal.'''

    def __init__(self): 
        self.name               = 'Neighborhood regions'
        self.input_tracks       = [{'type': 'track', 'name': 'X', 'kind': 'any', 'fields': ['start','end', '...']}]
        self.input_constraints  = []
        self.input_request      = [{'type': int, 'key': 'before_start', 'name': 'before_start', 'default': None},
                                   {'type': int, 'key': 'after_end',    'name': 'after_end',    'default': None},
                                   {'type': int, 'key': 'after_start',  'name': 'after_start',  'default': None},
                                   {'type': int, 'key': 'before_end',   'name': 'before_end',   'default': None}]
        self.input_special      = [{'type': 'in_datatype', 'name': 'in_type'}]
        self.input_by_chrom     = [{'type': 'stop_val', 'name': 'stop_val'}]
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': {'same': 0}}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_appending(*args)

    def qual(self, stop_val, **kwargs):
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
        from .basic import bounded
        for x in bounded()(X, 0, stop_val): yield x

    def quan(self, stop_val, **kwargs):
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
        from .basic import bounded
        for x in bounded()(X, 0, stop_val): yield x

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
