# gMiner Modules #
from ..  import genomic_manip as gm_manip
from ... import gm_tests
from ...gm_tests import gm_scores

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

################################################################################### 
class Unittest_test(unittest.TestCase):
    def runTest(self):
        self.maxDiff = None
       
        #--------------------------------------------------------------------------#
        tests  = [{'fn':   gm_manip.scores.window_smoothing().generate,
                 'input':  {'stop_val': 9,
                            'L': 2,
                            'X': [[0,2,10],
                                  [2,4,20],
                                  [6,8,10]]},
                 'output': [(0,  1,   8.0),
                            (1,  3,  12.0),
                            (3,  5,  10.0),
                            (5,  6,   8.0),
                            (6,  9,   4.0),]}
                 ]
       
        def smooth_signal(data, L):
            import numpy
            window = L*2+1
            weightings    = numpy.repeat(1.0, window) / window
            extended_data = numpy.hstack([[0] * L, data, [0] * L])
            smoothed = numpy.convolve(extended_data, weightings)[window-1:-(window-1)]
            return smoothed.tolist()

        def check_both_methods():
            computed_output      = list(gm_manip.scores.window_smoothing().generate(stop_val=stop_val, L=L, X=X))
            self.assertEqual(computed_output, expected_output)
            flat_X               = list(gm_scores.flatten_score(0, stop_val, X.__iter__()))
            flat_expected_output = list(gm_scores.flatten_score(0, stop_val, expected_output.__iter__()))
            flat_computed_output = smooth_signal(flat_X, L) 
            self.assertEqual(flat_computed_output, flat_expected_output)

        stop_val = 9
        L = 2
        X = [[0,2,10],[2,4,20],[6,8,10]]
        expected_output = [(0,  1,   8.0),
                           (1,  3,  12.0),
                           (3,  5,  10.0),
                           (5,  6,   8.0),
                           (6,  9,   4.0),]
        check_both_methods()

        stop_val = 12
        expected_output = [(0,  1,   8.0),
                           (1,  3,  12.0),
                           (3,  5,  10.0),
                           (5,  6,   8.0),
                           (6,  9,   4.0),
                           (9,  10,  2.0),]
        check_both_methods()

        #--------------------------------------------------------------------------#
        tests  = [{'fn':   gm_manip.scores.merge_scores().generate,
                 'input':  {'stop_val': 200,
                            'list_of_tracks': [[],[]]},
                 'output': []}
                 ]

        for t in tests:
            self.assertEqual(list(t['fn'](**t['input'])), t['output'])

        #--------------------------------------------------------------------------#
