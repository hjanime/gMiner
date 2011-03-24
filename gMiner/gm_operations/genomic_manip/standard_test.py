# gMiner Modules #
from ..  import genomic_manip as gm_manip
from ... import gm_tests

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

################################################################################### 
class Unittest_test(unittest.TestCase):
    def runTest(self):
        self.maxDiff = None

        tests  = [
                {'fn':     gm_manip.standard.complement().generate,
                 'input':  {'stop_val': 200,
                            'X': gm_tests.gm_track_collections['Validation']['Validation 1']['data']['chr1']},
                 'output': [(10,  20,  None, None, '.'),
                            (30,  40,  None, None, '.'),
                            (50,  60,  None, None, '.'),
                            (80,  90,  None, None, '.'),
                            (110, 120, None, None, '.'),
                            (135, 200, None, None, '.')]}
                ,
                {'fn':     gm_manip.standard.overlap_track().generate,
                 'input':  {'X': gm_tests.gm_track_collections['Validation']['Validation 2']['data']['chr1'],
                            'Y': gm_tests.gm_track_collections['Validation']['Validation 3']['data']['chr1']},
                 'output': [(10,  20,  'Name1',  0.1, u'+'),
                            (30,  40,  'Name2',  0.2, u'+'),
                            (90,  100, 'Name5',  0.0, u'+'),
                            (110, 120, 'Name6',  0.4, u'+'),
                            (130, 150, 'Name7',  0.4, u'+'),
                            (180, 190, 'Name8',  0.1, u'+'),
                            (180, 200, 'Name9',  0.1, u'+'),
                            (210, 220, 'Name10', 0.2, u'+'),
                            (230, 240, 'Name11', 0.1, u'+'),
                            (250, 260, 'Name12', 0.2, u'+'),
                            (270, 280, 'Name13', 0.0, u'+')]}
                ,
                {'fn':     gm_manip.standard.overlap_pieces().generate,
                 'input':  {'stop_val': 400,
                            'X': gm_tests.gm_track_collections['Validation']['Validation 2']['data']['chr1'],
                            'Y': gm_tests.gm_track_collections['Validation']['Validation 3']['data']['chr1']},
                 'output': [(15,  20,  'NameA with Name1',  0.0, '.'),
                            (32,  38,  'NameB with Name2',  0.0, '.'),
                            (95,  100, 'NameD with Name5',  0.0, '.'),
                            (110, 115, 'Name6 with NameD',  0.0, '.'),
                            (130, 135, 'Name7 with NameE',  0.0, '.'),
                            (140, 145, 'NameF with Name7',  0.0, '.'),
                            (185, 190, 'NameG with Name8',  0.0, '.'),
                            (185, 195, 'NameG with Name9',  0.0, '.'),
                            (210, 215, 'Name10 with NameH', 0.0, '.'),
                            (215, 220, 'NameI with Name10', 0.0, '.'),
                            (235, 240, 'NameJ with Name11', 0.0, '.'),
                            (250, 254, 'Name12 with NameJ', 0.0, '.'),
                            (252, 258, 'NameK with Name12', 0.0, '.'),
                            (256, 260, 'NameL with Name12', 0.0, '.'),
                            (270, 275, 'Name13 with NameL', 0.0, '.')]},
                 ]

        for t in tests:
            self.assertEqual(list(t['fn'](**t['input'])), t['output'])
