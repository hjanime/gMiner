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

# Add doc tests #
modules_base = [m[:-3] for m in os.listdir(gm_path) if m.endswith('.py')]
modules_base.append('gm_operations')
modules_operation = ['gm_operations.' + m[:-3] for m in os.listdir(gm_path + '/gm_operations/') if m.endswith('.py')]
modules_base.append('gm_formats')
modules_formats = ['gm_formats.' + m[:-3] for m in os.listdir(gm_path + '/gm_formats/') if m.endswith('.py')]
for m in modules_base + modules_operation + modules_formats:
    try:
        suite.addTest(doctest.DocTestSuite("gMiner." + m))
    except ValueError as err:
        err_message = m + ' ' + err[1]

# Add other tests #
execfile(gm_path + '/../Extras/tests/unittests/goodrequests.py')
execfile(gm_path + '/../Extras/tests/unittests/badrequests.py')

# Run every unittest #
runner.run(suite)
