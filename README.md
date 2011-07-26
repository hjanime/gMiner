gFeatMiner
==========

gFeatMiner is a Python module and can be seen as a framework for dealing with genomic data using a request based system. Typically the user has in his posession a few files containing genomic data. These files, refered to as tracks, contain genomic interval type information (.bed, .gff) or genomic score type information (.wig). Using the gFeatMiner module, he now can easily compute the answer to questions involving descriptive statistices like:

* What is the length distribution of the features inside the selection I made?
* What is the score distribution of the features inside these three tracks?
* What is the cumulative base coverage of these 2 tracks broken down by chromosome?

As well as access functionality involving genomic manipulations like:

* Provide a new track built by merging two other tracks.
* View the overlapping intervals of two tracks.
* Create a track that is the complement of another track.

To install it just type:

    $ pip install gMiner

Typical usage often looks like this:

    import gMiner
    files = gMiner.run(
        track1          = '/scratch/genomic/tracks/ribosome_proteins.sql',
        track1_name     = 'RP genes',
        operation_type  = 'desc_stat',
        characteristic  = 'number_of_features',
        per_chromosome  = 'True',
        compare_parents = 'False',
        gm_encoding     = 'image/png'
    )

Full documentation
==================

The full documentation can be found [on our website](http://bbcf.epfl.ch/gMiner).
