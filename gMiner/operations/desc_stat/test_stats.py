# Other modules #
from bbcflib.track import Track
from bbcflib.track.test_variables import track_collections

# Internal modules #
from .. import desc_stat

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

################################################################################### 
class Test_Stats(unittest.TestCase):
    def runTest(self):
        track = track_collections['Validation'][1]
        with Track(track['path_sql']) as track['track']:
            track['data'] = list(track['track'].read('chr1'))
        tests  = [
                {'fn':       desc_stat.gmCharacteristic.number_of_features,
                 'input':    track['data'],
                 'expected': 12},

                {'fn':       desc_stat.gmCharacteristic.base_coverage,
                 'input':    track['data'],
                 'expected': 85},

                {'fn':       desc_stat.gmCharacteristic.length,
                 'input':    track['data'],
                 'expected': [10, 6, 10, 5, 5, 10, 10, 10, 10, 20, 10, 10]},

                {'fn':       desc_stat.gmCharacteristic.score,
                 'input':    track['data'],
                 'expected': [10.0, 0.0, 10.0, 0.0, 0.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 5.0]},
                ]

        for t in tests:
            self.assertEqual(t['fn']([[d[Track.qualitative_fields.index(f)] for f in t['fn'].fields] for d in t['input']]), t['expected'])

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
