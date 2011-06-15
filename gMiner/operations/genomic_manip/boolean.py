# Modules #
import sys

# Importing #
from . import Manipulation as Manip
from ... import common

#-------------------------------------------------------------------------------------------#
class bool_not(Manip):
    '''The result consists of all intervals that were not
       covered by a feature in the original stream'''

    def __init__(self): 
        self.name               = 'Boolean NOT'
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
                yield (last_end, x[0], '', 0.0, 0)
                last_end = x[1]
            else:
                last_end = max(x[1], last_end)
        if last_end < stop_val:
            yield (last_end, stop_val, '', 0.0, 0)

#-------------------------------------------------------------------------------------------#
class bool_and(Manip):
    '''Computes the overlap between both streams returning
       new features that exacly match the overlaping zones.
       This is equivalent to the boolean `AND` operation.'''

    def __init__(self): 
        self.name               = 'Boolean AND'
        self.input_tracks       = [{'type':'track', 'name':'X', 'kind':'qualitative', 'fields':['start','end','name','score','strand']},
                                   {'type':'track', 'name':'Y', 'kind':'qualitative', 'fields':['start','end','name','score','strand']}]
        self.input_constraints  = []
        self.input_request      = []
        self.input_special      = []
        self.input_by_chrom     = []
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start','end','name','score','strand']}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_intersection(*args) 
    
    def __call__(self, X, Y):
        def make_name(a, b):
            if a and b: return a + ' + ' + b
            elif a: return a
            return b
        def scan(f, Wf, g, Wg, lastPick):
            g_index = 0
            while g_index < len(Wg):
                g_current = Wg[g_index]
                if left_of(g_current, f):
                    Wg.pop(g_index)
                else:
                    g_index += 1
                    if overlaps(g_current, f):
                        yield (max(f[0],g_current[0]),
                               min(f[1],g_current[1]),
                               make_name(f[2], g_current[2]),
                               (f[3]+g_current[3])/2.0,
                               f[4] and g_current[4] or 0)
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
class bool_or(Manip):
    '''Concatenates two streams together and subsequently performs
       the merge operation on the result.
       This is equivalent to the boolean `OR` operation.'''

    def __init__(self): 
        self.name               = 'Boolean OR'
        self.input_tracks       = [{'type':'track', 'name':'X', 'kind':'qualitative', 'fields':['start','end','name','score','strand']},
                                   {'type':'track', 'name':'Y', 'kind':'qualitative', 'fields':['start','end','name','score','strand']}]
        self.input_constraints  = []
        self.input_request      = []
        self.input_special      = []
        self.input_by_chrom     = []
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start','end','name','score','strand']}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_intersection(*args) 
    
    def __call__(self, X, Y):
        from .basic import concatenate
        from .standard import merge
        for x in merge().qual(concatenate()([X,Y])): yield x

#-------------------------------------------------------------------------------------------#
class bool_xor(Manip):
    '''Concatenates two streams together and subsequently performs
       the merge operation on the result. Form this result is removed
       any regions that were present in both of the original streams.
       This is equivalent to the boolean `XOR` operation.'''

    def __init__(self):
        self.name               = 'Boolean XOR'
        self.input_tracks       = [{'type':'track','name':['X1','X2'],'kind':'qualitative','fields':['start','end','name','score','strand']},
                                   {'type':'track','name':['Y1','Y2'], 'kind':'qualitative', 'fields':['start','end','name','score','strand']}]
        self.input_constraints  = []
        self.input_request      = []
        self.input_special      = []
        self.input_by_chrom     = [{'type': 'stop_val', 'name': 'stop_val'}]
        self.output_tracks      = [{'type': 'track', 'kind': 'qualitative', 'fields': ['start','end','name','score','strand']}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_intersection(*args) 
    
    def __call__(self, X1, X2, Y1, Y2, stop_val):
        a = bool_and()
        o = bool_or()
        n = bool_not()
        for x in a(o(X1,Y1), n(a(X2,Y2), stop_val)): yield x
