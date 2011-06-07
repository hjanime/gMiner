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
        tests = [{'fn':    genomic_manip.scores.merge_scores(),
                 'input':  {'stop_val': 200,
                            'list_of_tracks': [[],[]]},
                 'expected': []}]

        for t in tests:
            self.assertEqual(list(t['fn'](**t['input'])), t['expected'])
                 
        #--------------------------------------------------------------------------#
        tests = [{'fn':    genomic_manip.scores.merge_scores(),
                 'input':  {'stop_val': 200,
                            'list_of_tracks': [track_collections['Scores'][1]['path_sql'],
                                               track_collections['Scores'][2]['path_sql'],
                                               track_collections['Scores'][3]['path_sql']]},
                 'expected': [(0,    5,    2.0 + 0.6666666666666666),
                            (5,   10,    4.0),
                            (20,  30,   10.0),
                            (30,  40,   30.0),
                            (40,  50,   26.0 + 0.666666666666666),
                            (50,  60,  120.0),
                            (60,  68,  100.0),
                            (68,  70,  200.0),
                            (70,  80,  100.0),
                            (90,  110,   3.0),
                            (120, 130,  10.)]},
                {'fn':    genomic_manip.scores.merge_scores(),
                 'input':  {'stop_val': 200,
                            'geometric': True,
                            'list_of_tracks': [track_collections['Scores'][1]['path_sql'],
                                               track_collections['Scores'][2]['path_sql'],
                                               track_collections['Scores'][3]['path_sql']]},
                 'expected':  [(0,     5, 2.0),
                              (5,    10, 2.2894284851066637),
                              (20,   30, 3.1072325059538586),
                              (30,   40, 4.481404746557164),
                              (40,   50, 4.3088693800637667),
                              (50,   60, 7.1137866089801252),
                              (60,   68, 6.6943295008216941),
                              (68,   70, 8.4343266530174912),
                              (70,   80, 6.6943295008216941),
                              (90,  110, 2.0800838230519041),
                              (120, 130, 3.1072325059538586)]}]

        for t in tests:
            for i,v in enumerate(t['input']['list_of_tracks']):
                with Track(v) as x: t['input']['list_of_tracks'][i] = list(x.read('chr1'))
            self.assertEqual(list(t['fn'](**t['input'])), t['expected'])

        #--------------------------------------------------------------------------#
        tests  = [{'fn':   genomic_manip.scores.mean_score_by_feature(),
                 'tracks': {'X': track_collections['Scores'    ][4]['path_sql'],
                            'Y': track_collections['Validation'][2]['path_sql']},
                 'input':   {},
                 'expected': [(10,  20,  u'Name1',  15.0, 1),
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
                             (290, 300, u'Name14',  0.0, 1)]},
                {'fn':   genomic_manip.scores.threshold(),
                 'tracks': {'X': track_collections['Validation'][1]['path_sql']},
                 'fields': {'X': ['start', 'end', 'score', 'name']},
                 'input':  {'s': 4.0,
                            'in_type' : 'qualitative',
                            'out_type': 'qualitative'},
                 'expected': [( 0,   10,  10.0, u'Validation feature 1'),
                             (20,   30,  10.0, u'Validation feature 3'),
                             (40,   50,  10.0, u'Validation feature 6'),
                             (60,   70,  10.0, u'Validation feature 7'),
                             (70,   80,  10.0, u'Validation feature 8'),
                             (90,  100,  10.0, u'Validation feature 9'),
                             (90,  110,  10.0, u'Validation feature 10'),
                             (120, 130,  10.0, u'Validation feature 11'),
                             (125, 135,   5.0, u'Validation feature 12')]},
                 ]

        for t in tests:
            for k,v in t['tracks'].items():
                if t.get('fields') and t['fields'].get(k):
                    with Track(v) as x: t['tracks'][k] = iter(list(x.read('chr1', fields=t['fields'][k])))
                else:                                      
                    with Track(v) as x: t['tracks'][k] = iter(list(x.read('chr1')))
            t['input'].update(t['tracks'])
            self.assertEqual(list(t['fn'](**t['input'])), t['expected'])

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
