# Other modules #
from bbcflib.track.test_variables import track_collections

# Internal modules #
import gMiner

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

################################################################################### 
class Test(unittest.TestCase):
    def runTest(self):
        outdir = '/tmp/gMiner/'
        files = gMiner.run(
           track1           = track_collections['Validation'][2]['path_sql'],
           track1_name      = 'Validation track two',
           operation_type   = 'desc_stat',
           characteristic   = 'base_coverage',
           selected_regions = track_collections['Validation'][3]['path_sql'],
           per_chromosome   = True,
           compare_parents  = True,
           output_location  = outdir,
        )
        
        # Result should be 120 / 150

Test().runTest()

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
