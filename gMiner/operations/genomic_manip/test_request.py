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
           track1          = track_collections['Scores'][1]['path'],
           track1_name     = 'Validation score track 1',
           track1_chrs     = yeast_chr_file,
           track2          = track_collections['Scores'][2]['path'],
           track2_name     = 'Validation score track 2',
           track2_chrs     = yeast_chr_file,
           track3          = track_collections['Scores'][3]['path'],
           track3_name     = 'Validation score track 3',
           track3_chrs     = yeast_chr_file,
           operation_type  = 'genomic_manip',
           manipulation    = 'merge_scores',
           output_location = outdir,
        )
        
        with Track(files[0], chrfile=yeast_chr_file) as t:
            data = list(t.read('chr1'))
        os.remove(files[0])
        os.removedirs(outdir)

        expected = [(0,    5,    2.0 + 0.6666666666666666),
                    (5,   10,    4.0),
                    (20,  30,   10.0),
                    (30,  40,   30.0),
                    (40,  50,   26.0 + 0.666666666666666),
                    (50,  60,  120.0),
                    (60,  68,  100.0),
                    (68,  70,  200.0),
                    (70,  80,  100.0),
                    (90,  110,   3.0),
                    (120, 130,  10.)]

        self.assertEqual(data, expected)

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
