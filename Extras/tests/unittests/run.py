'''
This script will run all the unittests we have. 
'''

# Modules #
import sys, os, doctest

# gMiner #
import gMiner
from gMiner.gm_constants import *

# Check version of unittest #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Prepare unittest execution #
suite = unittest.TestSuite()
runner = unittest.TextTestRunner(verbosity=1)

# Add other tests #
execfile(gm_path + '/../Extras/tests/unittests/module_test.py')

# Run every unittest #
runner.run(suite)
