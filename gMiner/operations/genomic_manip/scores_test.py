# General modules #
import sys, numpy

# Other modules #
from bbcflib.track import Track
from bbcflib.track.test_variables import track_collections

# Internal modules #
from ... import common
from .. import genomic_manip

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

################################################################################### 
class Test(unittest.TestCase):
    def runTest(self):
        self.maxDiff = None
       
        #--------------------------------------------------------------------------#
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

        def check_both_methods():
            computed_output      = list(genomic_manip.scores.window_smoothing().generate(stop_val=stop_val, L=L, X=X))
            self.assertEqual(computed_output, expected_output)
            flat_X               = list(flatten_score(0, stop_val, X.__iter__()))
            flat_expected_output = list(flatten_score(0, stop_val, expected_output.__iter__()))
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
        tests = [{'fn':    genomic_manip.scores.merge_scores().generate,
                 'input':  {'stop_val': 200,
                            'list_of_tracks': [[],[]]},
                 'output': []}]

        for t in tests:
            self.assertEqual(list(t['fn'](**t['input'])), t['output'])
                 
        #--------------------------------------------------------------------------#
        tests = [{'fn':    genomic_manip.scores.merge_scores().generate,
                 'input':  {'stop_val': 200,
                            'list_of_tracks': [track_collections['Scores'][1]['path_sql'],
                                               track_collections['Scores'][2]['path_sql'],
                                               track_collections['Scores'][3]['path_sql']]},
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
            for i,v in enumerate(t['input']['list_of_tracks']):
                with Track(v) as x: t['input']['list_of_tracks'][i] = list(x.read('chr1'))
            self.assertEqual(list(t['fn'](**t['input'])), t['output'])
        #--------------------------------------------------------------------------#

        tests  = [{'fn':   genomic_manip.scores.mean_score_by_feature().generate,
                 'tracks':  {'X': track_collections['Scores'    ][4]['path_sql'],
                             'Y': track_collections['Validation'][2]['path_sql']},
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
            for k,v in t['tracks'].items():
                with Track(v) as x: t['tracks'][k] = list(x.read('chr1'))
            self.assertEqual(list(t['fn'](**t['tracks'])), t['output'])

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
