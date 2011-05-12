# General modules #
import os, tempfile

# Other modules #
from bbcflib.track import Track
from bbcflib.track.test_variables import track_collections, yeast_chr_file

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
        outdir = tempfile.mkdtemp(prefix='gMiner')
        files = gMiner.run(
           track1          = track_collections['Yeast']['All genes']['path_sql'],
           track1_name     = 'All genes from SGD',
           track2          = track_collections['Yeast']['Ribi genes']['path_sql'],
           track2_name     = 'Ribosome genesis',
           track3          = track_collections['Yeast']['RP genes']['path_sql'],
           track3_name     = 'Ribosome proteins',
           operation_type  = 'desc_stat',
           characteristic  = 'base_coverage',
           per_chromosome  = True,
           output_location = outdir,
        )
        
        os.remove(files[0])
        os.removedirs(outdir)

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
