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
                {'fn':     genomic_manip.boolean.bool_and(),
                 'tracks': {'X': track_collections['Validation'][2]['path_sql'],
                            'Y': track_collections['Validation'][3]['path_sql']},
                 'expected': [( 15,  20, u'NameA with Name1',  0.1,  1),
                              ( 32,  38, u'NameB with Name2',  0.2,  1),
                              ( 95, 100, u'NameD with Name5',  0.0,  1),
                              (110, 115, u'Name6 with NameD',  0.2,  1),
                              (130, 135, u'Name7 with NameE',  0.4,  1),
                              (140, 145, u'NameF with Name7',  0.4,  1),
                              (185, 190, u'NameG with Name8',  0.2,  1),
                              (185, 195, u'NameG with Name9',  0.2,  1),
                              (210, 215, u'Name10 with NameH', 0.45-5e-17, 1),
                              (215, 220, u'NameI with Name10', 0.25, 1),
                              (235, 240, u'NameJ with Name11', 0.1,  1),
                              (250, 254, u'Name12 with NameJ', 0.15+2e-17, 1),
                              (252, 258, u'NameK with Name12', 0.25, 1),
                              (256, 260, u'NameL with Name12', 0.2,  1),
                              (270, 275, u'Name13 with NameL', 0.1,  1)]}
                 ,
                {'fn':     genomic_manip.boolean.bool_or(),
                 'tracks': {'X': track_collections['Validation'][2]['path_sql'],
                            'Y': track_collections['Validation'][3]['path_sql']},

                 'expected': [( 10,  25, u'Name1 + NameA',          0.2, 1),
                              ( 30,  40, u'Name2 + NameB',          0.4, 1),
                              ( 50,  80, u'Name3 + NameC + Name4',  0.4, 1),
                              ( 90, 120, u'Name5 + NameD + Name6',  0.4, 1),
                              (125, 150, u'NameE + Name7 + NameF',  1.2+2e-16, 1),
                              (180, 200, u'Name8 + Name9 + NameG',  0.5, 1),
                              (205, 225, u'NameH + Name10 + NameI', 1.2, 1),
                              (230, 280, u'Name11 + NameJ + Name12 + NameK + NameL + Name13', 0.9-1e-16, 1),
                              (290, 300, u'Name14', 0.7, 1),
                              (310, 330, u'NameM',  0.3, 1)]} 
                 ]

        for t in tests: run_one(self, t)
