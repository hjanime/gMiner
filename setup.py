from distutils.core import setup

setup(
    name             = 'gMiner',
    version          = '1.4.0',
    packages         = ['gMiner',
                        'gMiner.operations',
                        'gMiner.operations.desc_stat',
                        'gMiner.operations.genomic_manip'],
    license          = open('LICENSE.txt').read(),
    description      = "Manuiplations and statistics on genomic data.",
    long_description = open('README.md').read(),
    url              = 'http://bbcf.epfl.ch/gMiner',
    author           = 'Lucas Sinclair',
    author_email     = 'lucas.sinclair@epfl.ch',
    install_requires = ['bbcflib', 'matplotlib'],
    classifiers      = ['Topic :: Scientific/Engineering :: Bio-Informatics']
)
