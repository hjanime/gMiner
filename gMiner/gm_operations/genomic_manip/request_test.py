# gMiner Modules #
import gMiner
from ... import gm_tests
from ... import gm_tracks as gm_tra

# Other modules #
import os, tempfile

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

################################################################################### 
class Unittest_test(unittest.TestCase):
    def runTest(self):
        outdir = tempfile.mkdtemp(prefix='gMiner')
        files = gMiner.run(
           track1          = gm_tests.gm_track_collections['Scores']['Scores 1']['location'],
           track1_name     = 'Validation score track 1',
           track2          = gm_tests.gm_track_collections['Scores']['Scores 1']['location'],
           track2_name     = 'Validation score track 1',
           track3          = gm_tests.gm_track_collections['Scores']['Scores 1']['location'],
           track3_name     = 'Validation score track 1',
           operation_type  = 'genomic_manip',
           manipulation    = 'merge_scores',
           output_location = outdir,
        )
        
        outfile = files[0]
        outtrack = gm_tra.gmTrack.Factory({'name':'Validation merge scores', 'location':outfile})
        outdata = list(outtrack.get_data_quan({'type':'chr','chr':'chr1'}))
        outtrack.unload()
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

        self.assertEqual(outdata, expected)
