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
        def make_feature(a, b):
            return (max(a[0],b[0]),
                    min(a[1],b[1]),
                    make_name(a[2], b[2]),
                    (a[3]+b[3])/2.0,
                    a[4]==b[4] and b[4] or 0)
        # Preparation #
        sentinel = (sys.maxint, sys.maxint)
        X = common.sentinelize(X, sentinel)
        Y = common.sentinelize(Y, sentinel)
        x = X.next()
        y = Y.next()
        Wx = []
        Wy = []
        # Core loop stops when both x and y are at the sentinel
        while x[0] != sentinel or y[0] != sentinel:
            # Take the leftmost current feature and scan it against the other window
            if x[0] < y[0]:
                # Remove features from the y window that are left of x
                Wy = [f for f in Wy if f[1] > x[0]]
                # Yield new features with all overlaps of x in Wy
                for f in [f for f in Wy if f[1] > x[0] and x[1] > f[0]]: yield make_feature(x, f)
                # Put x in the window only if it is not left of y
                if x[1] >= y[0]: Wx.append(x)
                # Advance current x feature
                x = X.next()
            else:
                # Remove features from the x window that are left of y
                Wx = [f for f in Wx if f[1] > y[0]]
                # Yield new features with all overlaps of y in Wx
                for f in [f for f in Wx if f[1] > y[0] and y[1] > f[0]]: yield make_feature(y, f)
                # Put y in the window only if it is not left of x
                if y[1] >= x[0]: Wy.append(y)
                # Advance current y feature
                y = Y.next()
        # Inspired from: #
        # fjoin: Simple and Efficient Computation of Feature Overlap #
        # Journal of Computational Biology, 13(8), Oct. 2006, pp 1457-1464. #

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
        self.input_tracks       = [{'type':'track','name':['X1','X2'], 'kind':'qualitative', 'fields':['start','end','name','score','strand']},
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

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
