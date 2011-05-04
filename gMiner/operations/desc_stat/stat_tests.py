# gMiner Modules #
from ...gm_constants import *
from .. import desc_stat as gm_stat
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
                {'fn':       gm_stat.gmCharacteristic.number_of_features,
                 'input':    gm_tests.gm_track_collections['Validation']['Validation 1']['data']['chr1'],
                 'expected': 12},

                {'fn':       gm_stat.gmCharacteristic.base_coverage,
                 'input':    gm_tests.gm_track_collections['Validation']['Validation 1']['data']['chr1'],
                 'expected': 85},

                {'fn':       gm_stat.gmCharacteristic.length,
                 'input':    gm_tests.gm_track_collections['Validation']['Validation 1']['data']['chr1'],
                 'expected': [10, 6, 10, 5, 5, 10, 10, 10, 10, 20, 10, 10]},

                {'fn':       gm_stat.gmCharacteristic.score,
                 'input':    gm_tests.gm_track_collections['Validation']['Validation 1']['data']['chr1'],
                 'expected': [10.0, 0.0, 10.0, 0.0, 0.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 5.0]},
                ]

        for t in tests:
            self.assertEqual(t['fn']([[d[gm_qualitative_fields.index(f)] for f in t['fn'].fields] for d in t['input']]), t['expected'])

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#