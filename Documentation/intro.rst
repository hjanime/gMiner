=================
Introduction
=================

What is gFeatMiner?
-------------------

gFeatMiner is a Python module that can be seen as a framework for dealing with genomic data using a request based system. Typically the user has in his posession a few files containing genomic data. These files, refered to as tracks, contain genomic interval type information (.bed, .gff) or genomic score type information (.wig). Using the gFeatMiner module, he now can easily compute the answer to questions involving descriptive statistices like:

* What is the length distribution of the features inside the selection I made?
* What is the score distribution of the features inside these three tracks?
* What is the cumulative base coverage of these 2 tracks broken down by chromosome?

As well as access functionality involving genomic manipulations like:

* Provide a new track built by merging two other tracks.
* View the overlapping intervals of two tracks.
* Create a track that is the complement of another track.

How do I install it ?
---------------------

The ``pip`` utility is most probably already installed on your machine. If such is the case, you can simply proceed by typing the following on your command prompt::

     $ sudo pip install gMiner

gFeatMiner is now installed on your computer. You can jump to the "How do I use it ?" section.

If you are missing the ``pip`` utility just enter this on your command prompt::

     $ sudo easy_install pip

If you are missing the ``easy_install`` utility just enter one of the following commands::

     $ sudo apt-get install python-setuptools
     $ sudo yum install python-setuptools

Requirements
""""""""""""
gFeatMiner doesn't depend on exotic libraries, but it requires Python 2.6 or above to work in addition to the three following packages: ``matplotlib, cherrypy, python-magic``. These package dependencies will automatically be resolved if you use the ``pip`` command.

If you get strange errors when ``pip`` tries to install matplotlib (because of the ft2font extension for instance), just type one of the following commands::

     $ sudo apt-get install python-matplotlib
     $ sudo yum install python-matplotlib

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

Developement copy
"""""""""""""""""
Executing the previous command enables you to play with a second copy of gFeatMiner while leaving the one installed in the shared python packages untouched. Any ``import gMiner`` statement will still refer to the shared copy unless you set the current directory the git repository root::

    $ cd gMiner
    $ python -c "import gMiner; print gMiner.__file__"

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

Other types of job, for instance, might create new tracks instead of image files. Here is an exemple that creates a new genomic track in the temporary directory::

    import gMiner
    files = gMiner.run(
       track1          = '/scratch/genomic/tracks/refseq_ucsc.sql',
       track1_name     = 'hg19 refSeq genome-wide from UCSC',
       track2          = '/scratch/genomic/tracks/hiv_bushman.sql',
       track2_name     = 'hg19 HIV integration sites from liftOver',
       operation_type  = 'genomic_manip',
       manipulation    = 'overlap_track',
       output_location = '/tmp/',
    )

gFeatMiner is capable of numerous operations on genomic data. Currently, two modules are included:

* :doc:`desc_stat`
* :doc:`genomic_manip`

Reporting bugs
""""""""""""""
The github repository provides an issue tracking system. You are welcome to open a new ticket in it if you think you have found a bug in gFeatMiner:

https://github.com/bbcf/gMiner/issues

You will however need to create a github account if you don't already have one to open a new issue, sorry.

.. image:: /images/kopimi_small.png
   :width: 1px
