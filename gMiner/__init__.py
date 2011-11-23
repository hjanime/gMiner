"""
###################
What is gFeatMiner?
###################

gFeatMiner is a framework written in python for analyzing and manipulating genomic data. Typically the user has in his possession a few files containing genomic data. These files, referred to as tracks, contain genomic interval type information (`.bed`, `.gff`) or genomic score type information (`.wig`). Using the gFeatMiner module, he now can easily compute the answer to questions involving descriptive statistics like:

* What is the length distribution of the features inside the selection I made?
* What is the score distribution of the features inside these three tracks?
* What is the cumulative base coverage of these 2 tracks broken down by chromosome?

As well as access functionality involving genomic manipulations like:

* Provide a new track built by merging two other tracks.
* View the overlapping intervals of two tracks.
* Create a track that is the complement of another track.

#####################
How do I install it ?
#####################

The ``easy_install`` tool is probably already on your machine. If such is the case, you can simply proceed by typing one of the following on your command prompt::

     $ sudo easy_install gMiner

gFeatMiner is now installed on your computer. You can jump to the "How do I use it ?" section.

If you are missing the ``easy_install`` tool just enter one of the following commands::

     $ sudo apt-get install python-setuptools
     $ sudo yum install python-setuptools
     $ sudo port install python-setuptools

Requirements
''''''''''''
gFeatMiner requires Python 2.6 or above to work in addition to the following packages: ``matplotlib, track``. These package dependencies can be automatically resolved if you use the ``easy_install`` command. Be aware that matplotlib only rarely builds without errors. It might be best to install matplotlib using a package manager specific to your system before hand.

Source code
'''''''''''
Downloading the source code is optional but, if you are interested, all of the files and testing material are stored in a git repository on github. You can explore the repository with a web browser here:

https://github.com/bbcf/gMiner

To download a copy of the gFeatMiner code to your computer, simply use the following command::

    $ git clone git://github.com/bbcf/gMiner.git

Manual install
''''''''''''''
If you have downloaded the source code, you can switch to the repository directory and manually install gMiner like so::

    $ cd gMiner
    $ sudo python setup.py install

If you need to install it in a particular directory, use::

    $ sudo python setup.py install --prefix=/prefix/path

#################
How do I use it ?
#################
Once gFeatMiner is installed, you use it in a python script by importing it and running a job, like so::

    import gMiner
    files = gMiner.run(
        track1          = '/scratch/genomic/tracks/all_yeast_genes.sql',
        track1_name     = 'S. cer. genes (SGD)',
        operation       = 'describe',
        characteristic  = 'number_of_features',
        per_chromosome  = 'True',
        compare_parents = 'False',
        output_location = '/tmp/',
    )

The ``files`` varaible now contains a list of file paths. In this case::

    ['/tmp/gminer_number_of_features.png']

Other types of job, for instance, might create new tracks instead of image files. Here is an example that creates a new genomic track in the temporary directory::

    import gMiner
    files = gMiner.run(
       track1          = '/scratch/genomic/tracks/refseq_ucsc.sql',
       track1_name     = 'hg19 refSeq genome-wide from UCSC',
       track2          = '/scratch/genomic/tracks/hiv_bushman.sql',
       track2_name     = 'hg19 HIV integration sites from liftOver',
       operation       = 'manipulate',
       manipulation    = 'overlap',
       output_location = '/tmp/',
    )

The ``files`` varaible now contains a list of file paths. In this case::

    ['/tmp/gminer_overlap.sql']

gFeatMiner is capable of numerous operations on genomic data. Currently, three modules are included:

* :doc:`describe`
* :doc:`manipulate`
* :doc:`plot`

#######
Warning
#######
It is important to note that the general numbering convention of features on a chromosome varies depending on the source of the data. For instance, UCSC and Ensembl differ in this point such that an interval labeled `(start=4,end=8)` will span four base pairs according to UCSC but will span five base pairs according to Ensembl. The representation that the this packages sticks to is explained `here <http://bbcf.epfl.ch/twiki/bin/view/BBCF/NumberingConvention>`_.

##############
Reporting bugs
##############
The github repository provides an issue tracking system. You are welcome to open a new ticket in it if you think you have found a bug in gFeatMiner:

https://github.com/bbcf/gMiner/issues

You will however need to create a github account if you don't already have one to open a new issue, sorry.

##########################
Developement documentation
##########################
A more developer-oriented documentation is available on the  `project's github pages <http://bbcf.github.com/gMiner/>`_.
"""

b'This module needs Python 2.6 or later.'

# Built-in modules #
import os
from contextlib import nested

# Other modules #
import track

# Constants #
project_name = 'gMiner'
project_long_name = 'gFeatMiner'

# Special variables #
__version__ = '1.5.0'
__all__ = ['run']

###########################################################################
def run(**kwargs):
    """Simple entry point where request can be described as
    dictionaries"""
    self_module = sys.modules[__name__]
    # Mandatory 'operation_type' parameter #
    module_name = kwargs['operation']
    if not hasattr(self_module, module_name):
        try:
            __import__('gMiner.' + module_name)
        except ImportError as err:
            raise Exception("The operation '%s' could not be imported because: %s" % (module_name, err))
    run_func = getattr(gMiner, module_name).run
    # Mandatory 'output_location' parameter #
    if not kwargs.get('output_location'):
        raise Exception("There does not seem to be an output location specified in the request.")
    output_dir = kwargs['output_location'].rstrip('/')
    if not os.path.isdir(output_dir):
        raise Exception("The output location '%s' specified is not a directory." % output_dir)
    # Mandatory 'track' parameter #
    if 'track1' not in kwargs:
        raise Exception("No tracks have been specified in the request.")
    number_of_tracks_sent = 1
    while kwargs.has_key("track" + str(number_of_tracks_sent + 1)):
        number_of_tracks_sent += 1
    # Make a list of tracks #
    tracks = []
    for i in xrange(1,number_of_tracks_sent):
        name = "track_%i"%i
        t = track.load(kwargs[name], readonly=True)
        keys = [k for k in kwargs if k.startswith(name)]
        for k in keys: setattr(t, k.split('_')[0], kwargs[k])
        tracks.append(t)
    # Enter them #
    with nested(*tracks) as tracks:
        # Assign numbers #
        for i, t in enumerate(tracks): t.number = i
        # Run it #
        return run_func(kwargs, tracks, output_dir)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
