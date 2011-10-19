# Other modules #
from bbcflib.track.track_collection import track_collections

# Internal modules #
from gMiner.operations import genomic_manip
from gMiner.operations.genomic_manip.tests import run_one

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

################################################################################
class Test(unittest.TestCase):
    def runTest(self):
        self.maxDiff = None
        my_test = {
                 'fn':     genomic_manip.association.find_closest_features(),
                 'tracks': {'X': track_collections['Validation'][1]['path_sql'],
                            'Y': track_collections['Validation'][2]['path_sql']},
                 'input':  {'max_length':0, 'utr_cutoff':0, 'prom_cutoff': 45},
                 'expected': [0]
                 }
        run_one(self, my_test)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
