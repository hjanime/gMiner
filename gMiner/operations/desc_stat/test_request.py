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
           track1          = track_collections['Yeast']['All genes']['path_sql'],
           track1_name     = 'All genes from SGD',
           track2          = track_collections['Yeast']['Ribi genes']['path_sql'],
           track2_name     = 'Ribosome genesis',
           track3          = track_collections['Yeast']['RP genes']['path_sql'],
           track3_name     = 'Ribosome proteins',
           operation_type  = 'desc_stat',
           characteristic  = 'length',
           output_location = outdir,
        )

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#