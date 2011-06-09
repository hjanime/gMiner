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
                 'expected': [( 15,  20, u'NameA + Name1',  0.1,  1),
                              ( 32,  38, u'NameB + Name2',  0.2,  1),
                              ( 95, 100, u'NameD + Name5',  0.0,  1),
                              (110, 115, u'Name6 + NameD',  0.2,  1),
                              (130, 135, u'Name7 + NameE',  0.4,  1),
                              (140, 145, u'NameF + Name7',  0.4,  1),
                              (185, 190, u'NameG + Name8',  0.2,  1),
                              (185, 195, u'NameG + Name9',  0.2,  1),
                              (210, 215, u'Name10 + NameH', 0.45-5e-17, 1),
                              (215, 220, u'NameI + Name10', 0.25, 1),
                              (235, 240, u'NameJ + Name11', 0.1,  1),
                              (250, 254, u'Name12 + NameJ', 0.15+2e-17, 1),
                              (252, 258, u'NameK + Name12', 0.25, 1),
                              (256, 260, u'NameL + Name12', 0.2,  1),
                              (270, 275, u'Name13 + NameL', 0.1,  1)]}
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
                 ,
                {'fn':     genomic_manip.boolean.bool_xor(),
                 'tracks': {'X': [ (5,10,'GeneA1'),  (5,10,'GeneA2'), (5,10,'GeneA3')],
                            'Y': [(15,20,'GeneB1'),(25,35,'GeneB2'),(45,65,'GeneB3')]},
                 'expected': [(  5,  10, u'GeneA1',           0.2, 1),
                              ( 15,  20, u'GeneB1',           0.4, 1),
                              ( 20,  25, u'GeneA2 + GeneB2',  0.4, 1),
                              ( 30,  35, u'GeneA2 + GeneB2',  0.4, 1),
                              ( 40,  45, u'GeneA3 + GeneB3',  0.7, 1),
                              ( 50,  65, u'GeneA3 + GeneB3',  0.3, 1)]} 
                 ]

        for t in tests: run_one(self, t)
