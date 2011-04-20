from distutils.core import setup

setup(
    name             = 'gMiner',
    version          = '1.1.0',
    packages         = ['gMiner','gMiner.gm_formats', 
                        'gMiner.gm_tests',
                        'gMiner.gm_tests.gm_graphs', 'gMiner.gm_tests.gm_parsers',
                        'gMiner.gm_operations',
                        'gMiner.gm_operations.dummy', 'gMiner.gm_operations.desc_stat', 'gMiner.gm_operations.genomic_manip'],
    license          = open('LICENSE.txt').read(),
    description      = "Manuiplations and statistics on genomic data.",
    long_description = open('README.md').read(),
    url              = 'http://bbcf.epfl.ch/gMiner',
    author           = 'Lucas Sinclair',
    author_email     = 'lucas.sinclair@epfl.ch',
    install_requires = ['python-magic', 'cherrypy', 'matplotlib'],
    classifiers      = ['Topic :: Scientific/Engineering :: Bio-Informatics']
)
