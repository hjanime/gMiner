# gMiner Modules #
from ..  import genomic_manip as gm_manip
from ... import gm_tests

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

################################################################################### 
class Unittest_test(unittest.TestCase):
    def runTest(self):
        tests  = [
                 ]

        for t in tests:
            self.assertEqual(list(t['fn'](**t['input'])), t['output'])
