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
                 'expected': [(15,  20,  'NameA with Name1',  0.0, 0),
                              (32,  38,  'NameB with Name2',  0.0, 0),
                              (95,  100, 'NameD with Name5',  0.0, 0),
                              (110, 115, 'Name6 with NameD',  0.0, 0),
                              (130, 135, 'Name7 with NameE',  0.0, 0),
                              (140, 145, 'NameF with Name7',  0.0, 0),
                              (185, 190, 'NameG with Name8',  0.0, 0),
                              (185, 195, 'NameG with Name9',  0.0, 0),
                              (210, 215, 'Name10 with NameH', 0.0, 0),
                              (215, 220, 'NameI with Name10', 0.0, 0),
                              (235, 240, 'NameJ with Name11', 0.0, 0),
                              (250, 254, 'Name12 with NameJ', 0.0, 0),
                              (252, 258, 'NameK with Name12', 0.0, 0),
                              (256, 260, 'NameL with Name12', 0.0, 0),
                              (270, 275, 'Name13 with NameL', 0.0, 0)]}
                 ,
                {'fn':     genomic_manip.boolean.bool_or(),
                 'tracks': {'X': track_collections['Validation'][2]['path_sql'],
                            'Y': track_collections['Validation'][3]['path_sql']},
                 'expected': [(15,  20,  'NameA with Name1',  0.0, 0),
                              (32,  38,  'NameB with Name2',  0.0, 0),
                              (95,  100, 'NameD with Name5',  0.0, 0),
                              (110, 115, 'Name6 with NameD',  0.0, 0),
                              (130, 135, 'Name7 with NameE',  0.0, 0),
                              (140, 145, 'NameF with Name7',  0.0, 0),
                              (185, 190, 'NameG with Name8',  0.0, 0),
                              (185, 195, 'NameG with Name9',  0.0, 0),
                              (210, 215, 'Name10 with NameH', 0.0, 0),
                              (215, 220, 'NameI with Name10', 0.0, 0),
                              (235, 240, 'NameJ with Name11', 0.0, 0),
                              (250, 254, 'Name12 with NameJ', 0.0, 0),
                              (252, 258, 'NameK with Name12', 0.0, 0),
                              (256, 260, 'NameL with Name12', 0.0, 0),
                              (270, 275, 'Name13 with NameL', 0.0, 0)]}
                 ,
                {'fn':     genomic_manip.boolean.bool_xor(),
                 'tracks': {'X': track_collections['Validation'][2]['path_sql'],
                            'Y': track_collections['Validation'][3]['path_sql']},
                 'expected': [(15,  20,  'NameA with Name1',  0.0, 0),
                              (32,  38,  'NameB with Name2',  0.0, 0),
                              (95,  100, 'NameD with Name5',  0.0, 0),
                              (110, 115, 'Name6 with NameD',  0.0, 0),
                              (130, 135, 'Name7 with NameE',  0.0, 0),
                              (140, 145, 'NameF with Name7',  0.0, 0),
                              (185, 190, 'NameG with Name8',  0.0, 0),
                              (185, 195, 'NameG with Name9',  0.0, 0),
                              (210, 215, 'Name10 with NameH', 0.0, 0),
                              (215, 220, 'NameI with Name10', 0.0, 0),
                              (235, 240, 'NameJ with Name11', 0.0, 0),
                              (250, 254, 'Name12 with NameJ', 0.0, 0),
                              (252, 258, 'NameK with Name12', 0.0, 0),
                              (256, 260, 'NameL with Name12', 0.0, 0),
                              (270, 275, 'Name13 with NameL', 0.0, 0)]}
                 ]

        #for t in tests: run_one(self, t)
