from distutils.core import setup

setup(
    name             = 'gMiner',
    version          = '0.1.6',
    packages         = ['gMiner','gMiner.gm_formats', 'gMiner.gm_operations'],
    license          = 'Kopimi',
    description      = "Manuiplations and statistics on genomic data.",
    long_description = open('README.txt').read(),
    url              = 'http://bbcf.epfl.ch/view/BBCF/GFeatMiner',
    author           = 'Lucas Sinclair',
    author_email     = 'lucas.sinclair@epfl.ch',
    install_requires = ['python-magic', 'cherrypy', 'matplotlib'],
)
