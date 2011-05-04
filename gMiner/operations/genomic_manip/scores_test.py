# gMiner Modules #
from ..  import genomic_manip as gm_manip
from ... import gm_tests
from ...gm_tests import gm_scores

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

#--------------------------------------------------------------------------#
def flatten_score(start, stop, X):
    sentinel = [sys.maxint, sys.maxint, 0.0]
    X = gm_com.sentinelize(X, sentinel)
    x = [start-2, start-1, 0.0]
    for i in xrange(start, stop):
        if i >= x[1]: x = X.next()
        if i >= x[0]: yield x[2]
        else: yield 0.0

################################################################################### 
class Unittest_test(unittest.TestCase):
    def runTest(self):
        self.maxDiff = None
       
        #--------------------------------------------------------------------------#
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
        tests = [{'fn':    gm_manip.scores.merge_scores().generate,
                 'input':  {'stop_val': 200,
                            'list_of_tracks': [[],[]]},
                 'output': []},
                 
                 {'fn':    gm_manip.scores.merge_scores().generate,
                 'input':  {'stop_val': 200,
                            'list_of_tracks': [gm_tests.gm_track_collections['Scores']['Scores 1']['data']['chr1'],
                                               gm_tests.gm_track_collections['Scores']['Scores 2']['data']['chr1'],
                                               gm_tests.gm_track_collections['Scores']['Scores 3']['data']['chr1']]},
                 'output': [(0,    5,    2.0 + 0.6666666666666666),
                            (5,   10,    4.0),
                            (20,  30,   10.0),
                            (30,  40,   30.0),
                            (40,  50,   26.0 + 0.666666666666666),
                            (50,  60,  120.0),
                            (60,  68,  100.0),
                            (68,  70,  200.0),
                            (70,  80,  100.0),
                            (90,  110,   3.0),
                            (120, 130,  10.)]}
                 ]

        for t in tests:
            self.assertEqual(list(t['fn'](**t['input'])), t['output'])
        #--------------------------------------------------------------------------#

        tests  = [{'fn':   gm_manip.scores.mean_score_by_feature().generate,
                 'input':  {'X': gm_tests.gm_track_collections['Scores'    ]['Scores 4'    ]['data']['chr1'],
                            'Y': gm_tests.gm_track_collections['Validation']['Validation 2']['data']['chr1']},
                 'output': [(10,  20,  u'Name1',  15.0, 1),
                            (30,  40,  u'Name2',  50.0, 1),
                            (50,  60,  u'Name3',  30.0, 1),
                            (70,  80,  u'Name4',  25.0, 1),
                            (90,  100, u'Name5',   8.0, 1),
                            (110, 120, u'Name6',   0.0, 1),
                            (130, 150, u'Name7',   1.0, 1),
                            (180, 190, u'Name8',   5.0, 1),
                            (180, 200, u'Name9',   8.0, 1),
                            (210, 220, u'Name10',  0.0, 1),
                            (230, 240, u'Name11',  0.0, 1),
                            (250, 260, u'Name12',  0.0, 1),
                            (270, 280, u'Name13',  0.0, 1),
                            (290, 300, u'Name14',  0.0, 1)]}
                 ]

        for t in tests:
            self.assertEqual(list(t['fn'](**t['input'])), t['output'])

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
