# General modules #
import sys, numpy

# Internal modules #
from ... import common
from .. import genomic_manip

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

#----------------------------------------------------------------------------------#
def flatten_score(start, stop, X):
    sentinel = [sys.maxint, sys.maxint, 0.0]
    X = common.sentinelize(X, sentinel)
    x = [start-2, start-1, 0.0]
    for i in xrange(start, stop):
        if i >= x[1]: x = X.next()
        if i >= x[0]: yield x[2]
        else: yield 0.0

def smooth_signal(data, L):
    window = L*2+1
    weightings    = numpy.repeat(1.0, window) / window
    extended_data = numpy.hstack([[0] * L, data, [0] * L])
    smoothed = numpy.convolve(extended_data, weightings)[window-1:-(window-1)]
    return smoothed.tolist()

def check_both_smooths(self, X, L, stop_val, expected_output):
    computed_output      = list(genomic_manip.scores.window_smoothing()(stop_val=stop_val, L=L, X=X))
    self.assertEqual(computed_output, expected_output)
    flat_X               = list(flatten_score(0, stop_val, X.__iter__()))
    flat_expected_output = list(flatten_score(0, stop_val, expected_output.__iter__()))
    flat_computed_output = smooth_signal(flat_X, L) 
    self.assertEqual(flat_computed_output, flat_expected_output)

################################################################################### 
class Test(unittest.TestCase):
    def test_window_smoothing(self):
        stop_val = 9
        L = 2
        X = [[0,2,10],[2,4,20],[6,8,10]]
        expected_output = [(0,  1,   8.0),
                           (1,  3,  12.0),
                           (3,  5,  10.0),
                           (5,  6,   8.0),
                           (6,  9,   4.0),]
        check_both_smooths(self, X, L, stop_val, expected_output)

        stop_val = 12
        expected_output = [(0,  1,   8.0),
                           (1,  3,  12.0),
                           (3,  5,  10.0),
                           (5,  6,   8.0),
                           (6,  9,   4.0),
                           (9,  10,  2.0),]
        check_both_smooths(self, X, L, stop_val, expected_output)
