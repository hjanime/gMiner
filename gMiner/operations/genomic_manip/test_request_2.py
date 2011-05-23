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
        self.maxDiff = None
        files = gMiner.run(
           track1          = track_collections['Validation'][1]['path_sql'],
           track1_name     = 'Validation feature track 1',
           operation_type  = 'genomic_manip',
           manipulation    = 'neighborhood',
           before_start    = -2,
           after_end       = 2,
           output_location = '/tmp/gMiner',
        )
        with Track(files[0]) as t:
            data = list(t.read('chr1'))
        os.remove(files[0])

        expected = [( 0,   10,  u'Validation feature 2',   0.0),
                    ( 0,   12,  u'Validation feature 1',  10.0),
                    (18,   32,  u'Validation feature 3',  10.0),
                    (23,   32,  u'Validation feature 4',   0.0),
                    (38,   47,  u'Validation feature 5',   0.0),
                    (38,   52,  u'Validation feature 6',  10.0),
                    (58,   72,  u'Validation feature 7',  10.0),
                    (68,   82,  u'Validation feature 8',  10.0),
                    (88,  102,  u'Validation feature 9',  10.0),
                    (88,  112,  u'Validation feature 10', 10.0),
                    (118, 132,  u'Validation feature 11', 10.0),
                    (123, 137,  u'Validation feature 12',  5.0)]
        self.assertEqual(data, expected)
        #---------------------------------------------------------------------------------------#

        files = gMiner.run(
           track1          = track_collections['Scores'][3]['path_sql'],
           track1_name     = 'Validation score track 3',
           track1_chrs     = yeast_chr_file,
           operation_type  = 'genomic_manip',
           manipulation    = 'neighborhood',
           before_start    = 2,
           after_end       = 2,
           output_location = '/tmp/gMiner',
        )
        with Track(files[0], chrfile=yeast_chr_file) as t:
            data = list(t.read('chr1'))
        os.remove(files[0])

        expected = [( 22,  52,  20.0),
                    ( 52,  82, 300.0)]
        self.assertEqual(data, expected)

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
