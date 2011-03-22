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
                 'output': [(10,  20,  u'Name1',  0.1, u'+'),
                            (30,  40,  u'Name2',  0.2, u'+'),
                            (90,  100, u'Name5',  0.0, u'+'),
                            (110, 120, u'Name6',  0.4, u'+'),
                            (130, 150, u'Name7',  0.4, u'+'),
                            (180, 190, u'Name8',  0.1, u'+'),
                            (180, 200, u'Name9',  0.1, u'+'),
                            (210, 220, u'Name10', 0.2, u'+'),
                            (230, 240, u'Name11', 0.1, u'+'),
                            (250, 260, u'Name12', 0.2, u'+'),
                            (270, 280, u'Name13', 0.0, u'+')]}
                 ]

        for t in tests:
            self.assertEqual(list(t['fn'](**t['input'])), t['output'])
