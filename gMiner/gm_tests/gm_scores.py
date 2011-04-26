# Modules #
import sys
from .. import gm_common as gm_com

###################################################################################
def flatten_score(start, stop, X):
    sentinel = [sys.maxint, sys.maxint, 0.0]
    X = gm_com.sentinelize(X, sentinel)
    x = [start-2, start-1, 0.0]
    for i in xrange(start, stop):
        if i >= x[1]: x = X.next()
        if i >= x[0]: yield x[2]
        else: yield 0.0

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
