'''
What is gFeatMiner?
-------------------

gFeatMiner is a Python module that can be seen as a framework for dealing with genomic data using a request based system. Typically the user has in his possession a few files containing genomic data. These files, referred to as tracks, contain genomic interval type information (.bed, .gff) or genomic score type information (.wig). Using the gFeatMiner module, he now can easily compute the answer to questions involving descriptive statistics like:

* What is the length distribution of the features inside the selection I made?
* What is the score distribution of the features inside these three tracks?
* What is the cumulative base coverage of these 2 tracks broken down by chromosome?

As well as access functionality involving genomic manipulations like:

* Provide a new track built by merging two other tracks.
* View the overlapping intervals of two tracks.
* Create a track that is the complement of another track.


How do I install it ?
---------------------

The ``easy_install`` or ``pip`` utilities are most probably already installed on your machine. If such is the case, you can simply proceed by typing one of the following on your command prompt::

     $ sudo easy_install pip
     $ sudo pip install gMiner

gFeatMiner is now installed on your computer. You can jump to the "How do I use it ?" section.

If you are missing the ``easy_install`` utility just enter one of the following commands::

     $ sudo apt-get install python-setuptools
     $ sudo yum install python-setuptools
     $ sudo port install python-setuptools

Requirements
""""""""""""
gFeatMiner doesn't depend on exotic libraries, but it requires Python 2.6 or above to work in addition to the two following packages: ``matplotlib, python-magic, bbcflib``. These package dependencies will automatically be resolved if you use the ``pip`` command.

If you get strange errors when ``pip`` tries to install matplotlib (because of the ft2font extension for instance), just type one of the following commands::

     $ sudo apt-get install python-matplotlib
     $ sudo yum install python-matplotlib
     $ sudo port install python-setuptools

Upgrading
"""""""""
When upgrading to the latest version of gFeatMiner, to avoid also upgrading the dependencies, you can use::

    $ sudo pip install --upgrade --no-deps gMiner

Source code
"""""""""""
Downloading the source code is optional but, if you are interested, all of the files and testing material are stored in a git repository on github. You can explore the repository with a web browser here:

https://github.com/bbcf/gMiner

To download a copy of the gFeatMiner code to your computer, simply use the following command::

    $ git clone git://github.com/bbcf/gMiner.git

Manual install
""""""""""""""
If you have downloaded the source code, you can switch to the git repository root and manually install gMiner like so::

    $ sudo python setup.py install

If you need to install it in a particular directory, use::

    $ sudo python setup.py install --prefix=/prefix/path

How do I use it ?
-----------------
Once gFeatMiner is installed, you use it in a python script by importing it and running a job, like so::

    import gMiner
    files = gMiner.run(
        track1          = '/scratch/genomic/tracks/all_yeast_genes.sql',
        track1_name     = 'S. cer. genes (SGD)',
        operation_type  = 'desc_stat',
        characteristic  = 'number_of_features',
        per_chromosome  = 'True',
        compare_parents = 'False',
        output_location = '/tmp/',
    )

The ``files`` varaible now contains the a list of file paths. In this case::

    ['/tmp/gminer_number_of_features.png']

Other types of job, for instance, might create new tracks instead of image files. Here is an example that creates a new genomic track in the temporary directory::

    import gMiner
    files = gMiner.run(
       track1          = '/scratch/genomic/tracks/refseq_ucsc.sql',
       track1_name     = 'hg19 refSeq genome-wide from UCSC',
       track2          = '/scratch/genomic/tracks/hiv_bushman.sql',
       track2_name     = 'hg19 HIV integration sites from liftOver',
       operation_type  = 'genomic_manip',
       manipulation    = 'overlap',
       output_location = '/tmp/',
    )

gFeatMiner is capable of numerous operations on genomic data. Currently, two modules are included:

* :doc:`desc_stat`
* :doc:`genomic_manip`

Warning
-------
It is important to note that the general numbering convention of features on a chromosome varies depending on the source of the data. For instance, UCSC and Ensembl differ in this point such that an interval labeled `(start=4,end=8)` will span four base pairs according to UCSC but will span five base pairs according to Ensembl. The representation that the this packages sticks to is explained `here <http://bbcf.epfl.ch/twiki/bin/view/BBCF/NumberingConvention>`_.

Reporting bugs
--------------
The github repository provides an issue tracking system. You are welcome to open a new ticket in it if you think you have found a bug in gFeatMiner:

https://github.com/bbcf/gMiner/issues

You will however need to create a github account if you don't already have one to open a new issue, sorry.

How do develop it ?
-------------------
Developement copy
"""""""""""""""""
Executing the ``git clone`` command enables you to play with a second copy of gFeatMiner while leaving the one installed in the shared python packages untouched. Any ``import gMiner`` statement will still refer to the shared copy unless you set the current directory to the git repository root::

    $ cd gMiner
    $ python -c "import gMiner; print gMiner.__file__"

Developement documentation
""""""""""""""""""""""""""
A more developer-oriented documentation is available on the  `project's github pages <http://bbcf.github.com/gMiner/>`_.
'''

b'This module needs Python 2.6 or later.'

# Built-in modules #
import os
from contextlib import nested

# Internal modules #
from constants import *
from . import operations

# Other modules #
from bbcflib import track

# Current version #
__version__ = gm_project_version

# Current path #
try:
    gm_path = __path__[0]
except NameError:
    gm_path = 'gMiner'

###########################################################################
def run(**request):
    # Import the correct operation #
    if not hasattr(operations, request['operation_type']):
        try:
            __import__('gMiner.operations.' + request['operation_type'])
        except ImportError:
            raise Exception("The operation " + request['operation_type'] + " is not supported.")
    run_op = getattr(operations, request['operation_type']).run
    # Mandatory request variables #
    if not request.get('output_location'):
        raise Exception("There does not seem to be an output location specified in the request.")
    output_dir = request['output_location'].rstrip('/')
    if not os.path.isdir(output_dir):
        raise Exception("The output location '" + output_dir + "' specified is not a directory.")
    # Optional request variables #
    request['selected_regions']   = request.get('selected_regions', '')
    parse_regions(request)
    request['wanted_chromosomes'] = request.get('wanted_chromosomes', '')
    parse_chrlist(request)
    # Prepare the tracks #
    track_dicts = parse_tracks(request)
    contexts = [track.load(t['path'], name=t['name'], chrmeta=t.get('chrs'), readonly=True) for t in track_dicts]
    with nested(*contexts) as tracks:
        # Assign numbers #
        for i, t in enumerate(tracks): t.number = i
        # Determine final chromosome list #
        if request['wanted_chromosomes']:
            for t in tracks: t.chrs = (set(t.all_chrs) & set(request['wanted_chromosomes']))
        else:
            for t in tracks: t.chrs = t.all_chrs
        # Run it #
        return run_op(request, tracks, output_dir)

###########################################################################
def parse_tracks(request_dict):
    '''
    >>> parse_tracks({'track1': 'aa', 'track1_name': 'ff', 'track1_chrs': 'bb'})
    [{'path': 'aa', 'chrs': 'bb', 'name': 'ff'}]
    '''

    # Number of tracks #
    if 'track1' not in request_dict:
        raise Exception("No tracks have been specified in the request.")
    number_of_tracks_sent = 1
    while request_dict.has_key("track" + str(number_of_tracks_sent + 1)):
        number_of_tracks_sent += 1
    # Make a list of dictionaries #
    try:
        tracks = [dict([['path',request_dict['track'+str(num)]],['name',request_dict['track'+str(num)+'_name']]]) for num in range(1,number_of_tracks_sent+1)]
    except KeyError:
        raise Exception("Every track specified must have a name associated.")
    # Chromosome info #
    for i, t in enumerate(tracks):
        if request_dict.has_key("track" + str(i+1) + '_chrs'):
            t['chrs'] = request_dict["track" + str(i+1) + '_chrs']
    return tracks

def parse_regions(request):
    '''
    >>> d = {'selected_regions': 'chr1:0:9;chr2:333:55555'}
    >>> parse_regions(d)
    >>> d
    {'selected_regions': [{'start': 0, 'chr': 'chr1', 'end': 9}, {'start': 333, 'chr': 'chr2', 'end': 55555}]}
    '''
    if os.path.exists(request['selected_regions']): return
    if request['selected_regions']:
        try:
            request['selected_regions'] = [dict([['chr',p[0]],['start',int(p[1])],['end',int(p[2])]]) for p in [r.split(':') for r in request['selected_regions'].split(';')]]
        except (ValueError, IndexError):
            raise Exception("The selected regions are not properly formated or the file doesn't exist: '" + request['selected_regions'] + "'")

def parse_chrlist(request):
    '''
    >>> d = {'wanted_chromosomes': 'chr1;chr2;chr9'}
    >>> parse_chrlist(d)
    >>> d
    {'wanted_chromosomes': ['chr1', 'chr2', 'chr9']}
    '''
    if request['wanted_chromosomes']:
        request['wanted_chromosomes'] = [c for c in request['wanted_chromosomes'].split(';')]

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
