# Other modules #
from bbcflib.track.test_variables import track_collections

# Internal modules #
from .. import genomic_manip
from .tests import run_one

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

################################################################################### 
class Test(unittest.TestCase):
    def runTest(self):
        self.maxDiff = None

        tests = [
                {'fn':     genomic_manip.basic.bounded(),
                 'input':  {'min_bound': 0, 'max_bound': 45},
                 'tracks': {'X': [(-2,10),(20,30),(26,23),(40,50)]},
                 'expected': [(0,10),(20,30),(40,45)]}
                ,
                {'fn':     genomic_manip.basic.concatenate(),
                 'input':  {'list_of_tracks': [track_collections['Validation'][1]['path_sql'],
                                               track_collections['Validation'][4]['path_sql']]},
                 'expected': [
                             ( 0,   10, u'Validation feature 1',  10.0),
                             ( 2,    8, u'Validation feature 2',   0.0),
                             (10,   20, u'Lorem',                  1.0, 1),
                             (20,   30, u'Validation feature 3',  10.0),
                             (25,   30, u'Validation feature 4',   0.0),
                             (30,   40, u'Ipsum',                  2.0, 1),
                             (40,   45, u'Validation feature 5',   0.0),
                             (40,   50, u'Validation feature 6',  10.0),
                             (60,   70, u'Validation feature 7',  10.0),
                             (70,   80, u'Validation feature 8',  10.0),
                             (90,  100, u'Validation feature 9',  10.0),
                             (90,  110, u'Validation feature 10', 10.0),
                             (120, 130, u'Validation feature 11', 10.0),
                             (125, 135, u'Validation feature 12',  5.0)]}
                 ,
                 {'fn':     genomic_manip.basic.concatenate(),
                 'input':  {'list_of_tracks': [[(0,10),(0,10),(5,10)],
                                               [(0,5),(0,12),(5,8)]]},
                 'expected': [(0,5),(0,10),(0,10),(0,12),(5,8),(5,10)]}
                 ]

        for t in tests: run_one(self, t)

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
