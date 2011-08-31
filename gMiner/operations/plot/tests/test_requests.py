# Built-in modules #
import os

# Internal modules #
from gMiner import run

# Other modules #
from bbcflib.track.track_collection import track_collections, small_chr_file

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class Test(unittest.TestCase):
    def setUp(self):
        import matplotlib
        matplotlib.use('Agg', warn=False)
        import matplotlib.pyplot as pyplot
        if pyplot.get_backend() != 'agg':
            self.skipTest("The backend for matplotlib was not set correctly.")

    def runTest(self):
        outdir = '/tmp/gMiner/'
        if not os.path.exists(outdir): os.mkdir(outdir)

        # Cross-correlation #
        files = run(
           track1          = track_collections['Scores'][1]['path_sql'],
           track1_name     = 'Scores 1',
           track1_chrs     = small_chr_file,
           track2          = track_collections['Scores'][2]['path_sql'],
           track2_name     = 'Scores 2',
           track2_chrs     = small_chr_file,
           operation_type  = 'plot',
           plot            = 'correlation',
           output_location = outdir,
        )

        # Scatter plot #
        files = run(
           track1          = track_collections['Scores'][1]['path_sql'],
           track1_name     = 'Scores 1',
           track1_chrs     = small_chr_file,
           track2          = track_collections['Scores'][1]['path_sql'],
           track2_name     = 'Scores 2',
           track2_chrs     = small_chr_file,
           track3          = track_collections['Validation'][1]['path_sql'],
           track3_name     = 'Features 1',
           track3_chrs     = small_chr_file,
           operation_type  = 'plot',
           plot            = 'scatter',
           output_location = outdir,
        )

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
