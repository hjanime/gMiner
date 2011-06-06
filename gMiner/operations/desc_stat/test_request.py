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
        try:
            import Tkinter
            window = Tkinter.Tk()
            window.destroy()
        except Tkinter.TclError:
            self.skipTest("You don't have access to a DISPLAY, skipping appropriate tests")
        
    def runTest(self):
        outdir = '/tmp/gMiner/'

        # Simple boxplot
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

        # Track selection
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

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
