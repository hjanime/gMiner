from distutils.core import setup

setup(
        name             =   'gMiner',
        version          =   '1.5.0',
        description      =   'Manuiplations and statistics on genomic data',
        long_description =   open('README.md').read(),
        license          =   open('LICENSE.txt').read(),
        url              =   'http://bbcf.epfl.ch/gMiner',
        author           =   'EPFL BBCF',
        author_email     =   'webmaster.bbcf@epfl.ch',
        classifiers      =   ['Topic :: Scientific/Engineering :: Bio-Informatics'],
        install_requires =   ['matplotlib', 'track'],
        packages         =   ['gMiner',
                              'gMiner.operations',
                              'gMiner.operations.describe',
                              'gMiner.operations.plot',
                              'gMiner.operations.manipulate',
                              'gMiner.operations.manipulate.all_manips']
    )
