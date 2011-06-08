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

        tests  = [
                {'fn':     genomic_manip.standard.complement(),
                 'input':  {'stop_val': 200},
                 'tracks': {'X': track_collections['Validation'][1]['path_sql']},
                 'expected': [(10,  20,  None, None, 0),
                              (30,  40,  None, None, 0),
                              (50,  60,  None, None, 0),
                              (80,  90,  None, None, 0),
                              (110, 120, None, None, 0),
                              (135, 200, None, None, 0)]}
                ,
                {'fn':     genomic_manip.standard.overlap(),
                 'tracks': {'X': track_collections['Validation'][2]['path_sql'],
                            'Y': track_collections['Validation'][3]['path_sql']},
                 'expected': [(10,  20,  u'Name1',  0.1, 1),
                              (30,  40,  u'Name2',  0.2, 1),
                              (90,  100, u'Name5',  0.0, 1),
                              (110, 120, u'Name6',  0.4, 1),
                              (130, 150, u'Name7',  0.4, 1),
                              (180, 190, u'Name8',  0.1, 1),
                              (180, 200, u'Name9',  0.1, 1),
                              (210, 220, u'Name10', 0.2, 1),
                              (230, 240, u'Name11', 0.1, 1),
                              (250, 260, u'Name12', 0.2, 1),
                              (270, 280, u'Name13', 0.0, 1)]}
                ,
                {'fn':     genomic_manip.standard.neighborhood(),
                 'input':  {'stop_val': 135, 'before_start':-2, 'after_end':2, 'in_type': 'qualitative'},
                 'tracks': {'X': track_collections['Validation'][1]['path_sql']},
                 'expected': [( 0,   12,  u'Validation feature 1',  10.0),
                              ( 0,   10,  u'Validation feature 2',   0.0),
                              (18,   32,  u'Validation feature 3',  10.0),
                              (23,   32,  u'Validation feature 4',   0.0),
                              (38,   47,  u'Validation feature 5',   0.0),
                              (38,   52,  u'Validation feature 6',  10.0),
                              (58,   72,  u'Validation feature 7',  10.0),
                              (68,   82,  u'Validation feature 8',  10.0),
                              (88,  102,  u'Validation feature 9',  10.0),
                              (88,  112,  u'Validation feature 10', 10.0),
                              (118, 132,  u'Validation feature 11', 10.0),
                              (123, 135,  u'Validation feature 12',  5.0)]}
                ,
                {'fn':     genomic_manip.standard.merge().quan,
                 'tracks': {'X': track_collections['Scores'][4]['path_sql']},
                 'expected': [(10,   20,   15.0),
                              (25,   35,  100.0),
                              (45,   65,   30.0),
                              (72,   77,   50.0),
                              (85,  105,    8.0),
                              (120, 122, 9000.0),
                              (130, 131,   20.0),
                              (180, 183,   10.0),
                              (188, 193,   10.0),
                              (198, 200,   40.0)]}
                ,
                {'fn':     genomic_manip.standard.merge().quan,
                 'tracks': {'X': [(10, 40, 10.0), (40, 50, 20.0)]},
                 'expected': [(10, 50, 12.5)]},
                 ]

        for t in tests: run_one(self, t)

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
