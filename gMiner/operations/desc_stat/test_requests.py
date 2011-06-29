# General modules #
import os

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
    def setUp(self):
        import matplotlib
        matplotlib.use('Agg', warn=False)
        import matplotlib.pyplot as pyplot
        if pyplot.get_backend() != 'agg':
            self.skipTest("The backend for matplotlib was not set correctly.")

    def runTest(self):
        outdir = '/tmp/gMiner/'
        if not os.path.exists(outdir): os.mkdir(outdir)

        # Simple boxplot #
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

        # Track selection #
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
        # Result should be 120 / 150 or 80%

        # Field test via filter #
        files = gMiner.run(
           track1           = track_collections['Yeast']['All genes']['path_sql'],
           track1_name      = 'S. cer refseq genes',
           track2           = track_collections['Yeast']['RP genes']['path_sql'],
           track2_name      = 'RP genes',
           operation_type   = 'desc_stat',
           characteristic   = 'number_of_features',
           selected_regions = track_collections['Yeast']['Ribi genes']['path_sql'],
           per_chromosome   = True,
           compare_parents  = False,
           output_location  = outdir,
        )

        # Permission test #
        if os.path.exists('/scratch/genomic/tracks/locked.sql'):
            files = gMiner.run(
               track1           = '/scratch/genomic/tracks/locked.sql',
               track1_name      = 'Permission test',
               selected_regions = '/scratch/genomic/tracks/locked.sql',
               operation_type   = 'desc_stat',
               characteristic   = 'number_of_features',
               output_location  = outdir,
            )

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#

