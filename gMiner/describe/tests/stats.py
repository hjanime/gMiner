# Other modules #
from bbcflib import track
from bbcflib.track.track_collection import track_collections

# Internal modules #
from gMiner.operations import desc_stat

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class Test_Stats(unittest.TestCase):
    def runTest(self):
        t = track_collections['Validation'][1]
        with track.load(t['path_sql']) as t['track']:
            t['data'] = list(t['track'].read('chr1'))
        tests  = [
                {'fn':       desc_stat.gmCharacteristic.number_of_features,
                 'input':    t['data'],
                 'expected': 12},

                {'fn':       desc_stat.gmCharacteristic.base_coverage,
                 'input':    t['data'],
                 'expected': 85},

                {'fn':       desc_stat.gmCharacteristic.length,
                 'input':    t['data'],
                 'expected': [10, 6, 10, 5, 5, 10, 10, 10, 10, 20, 10, 10]},

                {'fn':       desc_stat.gmCharacteristic.score,
                 'input':    t['data'],
                 'expected': [10.0, 0.0, 10.0, 0.0, 0.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 5.0]},
                ]

        for case in tests:
            self.assertEqual(case['fn']([[d[track.Track.qualitative_fields.index(f)] for f in case['fn'].fields] for d in case['input']]), case['expected'])

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
