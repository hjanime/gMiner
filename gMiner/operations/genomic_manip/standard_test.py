# Other modules #
from bbcflib.track import Track
from bbcflib.track.test_variables import track_collections

# Internal modules #
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
                {'fn':     genomic_manip.standard.overlap_track(),
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
                {'fn':     genomic_manip.standard.overlap_pieces(),
                 'input':  {'stop_val': 400},
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
                              (270, 275, 'Name13 with NameL', 0.0, 0)]},
                 ]

        for t in tests:
            for k,v in t['tracks'].items():
                with Track(v) as x: t['tracks'][k] = list(x.read('chr1'))
            dict = t.get('input', {})
            dict.update(t['tracks'])
            self.assertEqual(list(t['fn'](**dict)), t['expected'])

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
