=================
Introduction
=================

What is gFeatMiner?
-------------------

gFeatMiner is a Python module and can be seen as a framework for dealing with genomic data using a request based system. Typically the user has in his posession a few files containing genomic data. These files, refered to as tracks, contain genomic interval type information (.bed, .gff) or genomic score type information (.wig). Using the gFeatMiner module, he now can easily compute the answer to questions involving descriptive statistices like:

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

gFeatMiner is now installed on your computer. You can jump to the "How do I use it ?" section. If you are missing the ``pip`` utility just enter this on your command prompt::

     $ sudo easy_install pip

Requirements
""""""""""""
gFeatMiner doesn't depend on exotic libraries, but it requires Python 2.6 or above to work in addition to the three following packages: ``matplotlib, cherrypy, python-magic``. These package dependencies will be automatically resolved if you use the ``pip`` command.

Source code
"""""""""""
Downloading the source code is optional, but if you are interested, all of the files and testing material are stored in a git repository on github. You can explore the repository with a web browser here:

https://github.com/bbcf/gMiner

To download a copy of the gFeatMiner code to your computer, simply use the following command::

    $ git clone git://github.com/bbcf/gMiner.git

Developement copy
"""""""""""""""""
Executing the previous command enables you to play with a second copy of gFeatMiner while leaving the one installed with the shared python packages untouched. Any ``import gMiner`` statement will still refer to the shared copy unless you set the current directory the git repository root::

    $ cd gMiner
    $ python -c "import gMiner; print gMiner.__file__"

How do I use it ?
-----------------
Once gFeatMiner is installed, you use it in a python script by importing it and running a job, like so::
     
    import gMiner
    result = gMiner.run(
        track1          = '/scratch/genomic/tracks/ribosome_proteins.sql',
        track1_name     = 'RP genes',
        operation_type  = 'desc_stat',
        characteristic  = 'number_of_features',
        per_chromosome  = 'True',
        compare_parents = 'False',
        gm_encoding     = 'image/png'
    )

The ``result`` varaible now contains the requested graph in PNG format, suitable for displaying or writing to a file like so::

    with open('/tmp/graph.png', 'w') as file: file.write(result)


gFeatMiner is capable, 


Starting a server
"""""""""""""""""
gFeatMiner is also designed to be accessed from other programs via the HTTP protocol. You can launch the gFeatMiner server by typing::

    $ python -c "import gMiner.gm_server as srv; srv.gmServer(port=7520).serve()"

A server is now running locally. The default port is 7520 but this can be changed by specifying another value in the line above. Sending a POST request to ``http://localhost:7520/`` should work. However, extra configuration may be necessary on your server (Apache etc).

To understand how to correctly form and send a POST request, as well as how to recieve the response, you can check out the files in ``Extras/test/webservice/``

Reporting bugs
--------------
The github repository provides an issue tracking system in which you are welcome to open a new ticket if you think you have found a bug in gFeatMiner:

https://github.com/bbcf/gMiner/issues

You will however need to create a github account to create a ticket, sorry.
