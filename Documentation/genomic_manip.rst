.. automodule:: gMiner.operations.genomic_manip

=====================
Genomic Manipulations
=====================

Another functionality provided by gFeatMiner is the ability to manipulate genomic data and craete new tracks from existing ones. To access this functionality you must specify ``operation_type=genomic_manip`` in the job request as seen in this exemple, in addition to a few other parameters that are detailed below::

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

After executing these two statements, a new track will be created in the ``/tmp/gMiner/`` directory and its path returned to you.

Parameters
----------

Here are described all the paramaters that can or should be passed to gFeatMiner's run function.

======================== =====
Key                      Value   
======================== =====
**track_1**              This specifies the location of the first track file. At least one genomic file must be inputted to compute a statistic. Of course, an undefined number of supplementary tracks can be specified. The order in which they are given may or may not influence the output depending on the operation requested.

**track_1_name**         This field is also required. Every track must have a name

**track_2**              The location of the second track file. This field is optional, for instance, if the operation only requires one genomic file

**track_2_name**         The name of the second track.

*[More tracks ...]*      Following tracks are specified according to the standard ``track_N`` and ``track_N_name``

**operation_type**       This field must be specified in the request and must take the value of ``genomic_manip`` if one wishes to perform genomic manipulation operations on the tracks provided.

**manipulation**         Can take any of the values described in the next section, "Manipulations".

**output_location**      Specifies the location at which the newly created track will be written.

**output_name**          Optionally specifies the name of the file to be created in ``output_location``.

*[Extra parameters ...]* Depending on the manipulation requested, you may need to provide extra parameters like a window size or a threashold value. Refer to the manipulation documentation for more details.
======================== =====

Manipulations
-------------
Several types of manipulations can be used to generate different types of tracks. You can chose which manipulation to execute by specifiing ``manipulation=`` followed by one of the values in bold below:

Basic
""""""""
.. automodule:: gMiner.operations.genomic_manip.basic
    :members:

Standard
""""""""
.. automodule:: gMiner.operations.genomic_manip.standard
    :members:

Scores
""""""
.. automodule:: gMiner.operations.genomic_manip.scores
   :members:

Boolean
"""""""
.. automodule:: gMiner.operations.genomic_manip.boolean
   :members:


Using the library in 'manual' mode
----------------------------------
Instead of accessing gFeatMiner services via the ``gMiner.run()`` function, you can directly import the wanted manipulation and call it manually with your own queries. Here is a short example where a new track containing the ``mean_score_by_feature`` (computed on two other tracks) is created::

    from bbcflib.track import Track, new
    from gMiner.operations.genomic_manip.scores import mean_score_by_feature
    manip = mean_score_by_feature()
    with Track('a.sql') as a:
        with Track('b.sql') as b:
            with new('r.sql') as r:
                for chrom in a:
                    r.write(chrom, manip(a.read(chrom), b.read(chrom)))

Now you are only one step away from modifying the input of your manipulation on the fly. You just need to write a function taking a generator object and returning a generator object. In this example our generator will yield several new features for every original feature it receives::

    def create_bins(X, num_of_bins=10):
        for x in X:
            length = (x[1] - x[0]) / num_of_bins
            for i in xrange(num_of_bins):
                yield (x[0]+i*length, x[0]+(i+1)*length, x[2], x[3], x[4])

    from bbcflib.track import Track, new
    from gMiner.operations.genomic_manip.scores import mean_score_by_feature
    manip = mean_score_by_feature()
    with Track('a.sql') as a:
        with Track('b.sql') as b:
            with new('r.sql') as r:
                for chrom in a:
                    r.write(chrom, manip(a.read(chrom), create_bins(b.read(chrom))))

Of course when you create tracks using this method, the resulting database is missing all its metadata. You probably will want to copy that over at some moment::

    r.meta_chr   = b.meta_chr
    r.meta_track = {'datatype': 'qualitative', 'name': 'Mean score per bin', 'created_by': 'Custom feature bin script'}
