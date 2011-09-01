# Built-in modules #
import os

# Internal modules #
from gMiner.operations import plot
from gMiner.common import named_temporary_path

# Other modules #
from bbcflib.track import new

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class Test_Scatter(unittest.TestCase):
    def runTest(self):
        outdir = '/tmp/gMiner/'
        if not os.path.exists(outdir): os.mkdir(outdir)
        Q1, Q2, R1 = [named_temporary_path('.sql') for x in range(3)]
        with new(Q1, datatype='quantitative', name='Q1') as q1:
            q1.write('chr1', ((0, 10, 1.0), (10, 20, 2.0), (20, 30, 1.0), (30, 40, 9.0)))
        with new(Q2, datatype='quantitative', name='Q2') as q2:
            q2.write('chr1', ((0, 10, 1.0), (10, 20, 1.0), (20, 26, 2.0), (26, 30, 5.0)))
        with new(R1, name='R1') as r1:
            r1.write('chr1', ((2, 8, 'A', 0, 0), (14, 16, 'B', 0, 0), (22, 28, 'C', 0 ,0)))
        fig = plot.scatter()(Q1, Q2, R1)
        fig.savefig(outdir + ('scatter_test.png'))
        for path in (Q1, Q2, R1): os.remove(path)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
