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
       
     
        tests  = [{'fn':   gm_manip.scores.window_smoothing().generate,
                 'input':  {'stop_val': 20,
                            'L': 2,
                            'X': [[0,2,10],
                                  [4,6,20],
                                  [6,8,10]]},
                 'output': [(0,1, 10.0),
                           (2, 2,  8.0),
                           (3, 4, 10.0),
                           (5, 6, 12.0),
                           (7, 7,  8.0),
                           (8, 8,  4.0),
                           (9, 9, 12.0)]}
                 ]
       
        def smooth_signal(data, L):
            import numpy
            window = L*2+1
            weightings    = numpy.repeat(1.0, window) / window
            extended_data = numpy.hstack([[0] * L, data, [0] * L])
            smoothed = numpy.convolve(extended_data, weightings)[window-1:-(window-1)]
            return smoothed.tolist()

        for t in tests:
            self.assertEqual(list(t['fn'](**t['input'])), t['output'])
            L        = tests[0]['input']['L']
            stop_val = tests[0]['input']['stop_val'] 
            input    = tests[0]['input']['X'].__iter__()
            output   = tests[0]['output'].__iter__()
            real_input  = list(gm_scores.flatten_score(0, stop_val, input))
            real_output = list(gm_scores.flatten_score(0, stop_val, output))
            self.assertEqual(smooth_signal(real_input, L), real_output)

        #--------------------------------------------------------------------------#
        tests  = [{'fn':   gm_manip.scores.merge_scores().generate,
                 'input':  {'stop_val': 200,
                            'list of tracks': [[],[]]},
                 'output': []}
                 ]

        for t in tests:
            self.assertEqual(list(t['fn'](**t['input'])), t['output'])

