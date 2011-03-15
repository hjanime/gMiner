===========
gFeatMiner
===========

gFeatMiner is a Python module and can be seen as a framework for dealing with genomic data using a request based system. Typically the user has in his posession a few files containing genomic data. These files, refered to as tracks, contain genomic interval type information (.bed, .gff) or genomic score type information (.wig). Using the gFeatMiner module, he now can easily compute the answer to questions involving descriptive statistices like:

* What is the length distribution of the features inside the selection I made?

* What is the score distribution of the features inside these three tracks?

* What is the cumulative base coverage of these 2 tracks broken down by chromosome?

As well as access functionality involving genomic manipulations like:

* Provide a new track built by merging two other tracks.

* View the overlapping intervals of two tracks.

* Create a track that is the complement of another track.

Typical usage often looks like this:

    # Import gFeatMiner #
    import gMiner

    # Run a request #
    gMiner.run(track1          = '/tmp/a.sql',
               track1_name     = 'Test track 1',
               operation_type  = 'genomic_manip', 
               manipulation    = 'complement',
               output_location = '/tmp/result.sql')

Full documentation
=========

The full documentation can be found on our wiki page:

http://bbcf.epfl.ch/twiki/bin/view/BBCF/GFeatMiner
