'''
This script will run all the unittests we have. 
'''

# Modules #
import gMiner, nose

# Doctest #
nose.run(module=gMiner, argv=['nosetests', '--with-doctest', '-w', 'Extras/tests/nose'])
