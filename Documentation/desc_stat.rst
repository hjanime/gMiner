.. automodule:: gMiner.operations.desc_stat

======================
Descriptive Statistics
======================

One of the primary goals of gFeatMiner is to provide simple graphs that help the user describe and explore his genomic datasets. These graphs are generated quickly and on-the-fly as they are requested. To access this functionality you must specify ``operation_type=desc_stat`` in the job request as seen in this exemple, in addition to a few other parameters that are detailed below::

    import gMiner
    files = gMiner.run(
        track1             = '/scratch/genomic/tracks/ribosome_proteins.sql',
        track1_name        = 'RP genes (SGD)',
        track2             = '/scratch/genomic/tracks/ribosome_genesis.sql',
        track2_name        = 'Ribi genes (SGD)',
        operation_type     = 'desc_stat',
        characteristic     = 'base_coverage',
        selected_regions   = 'chr2:0:300000;chr5:0:200000',
        compare_parents    = 'False',
        per_chromosome     = 'True',
        wanted_chromosomes = 'chr1;chr2;chr5;chr6;chr7;chr8;chr9;chr10;chr11;chr12;' + \
                             'chr13;chr14;chr15;chr16;chr17;chr18;chr19;chr20;chr21;' + \
                             'chr22;chrX;chrY',
        output_location    = '/tmp/',
    )

The ``files`` varaible will now contain the path to the file created in PNG format.
 
Parameters
----------

Here are described all the paramaters that can or should be passed to gFeatMiner's run function.
    
====================== =====
Key                    Value   
====================== =====
**track_1**            This specifies the location of the first track file. At least one genomic file must be inputted to compute a statistic. Of course, an undefined number of supplementary tracks can be specified. The order in which they are given may or may not influence the output depending on the operation requested.

**track_1_name**       This field is also required. Without a name, the resulting graph will not have a comprehensive legend associated and the user will get confused. Every track must have a name

**track_2**            The location of the second track file. This field is optional, for instance, if the operation only requires one genomic file

**track_2_name**       The name of the second track.

*[More tracks ...]*      Following tracks are specified according to the standard ``track_N`` and ``track_N_name``

**operation_type**     This field must be specified in the request and must take the value of ``desc_stat`` if one wishes to perform descrtiptive statistic operations on the tracks provided.

**characteristic**     Can take any of the values described in the next section, "Characteristics".

**selected_regions**   Can be empty if no selection was made. Otherwise a list of locations and chromosomes is expected using colons and semicolons as separators. In such a case, the statistic will then only be computed on the selection which may be discontinuous and span several chromosomes.

**compare_parents**    This option can take the following values: ``True`` or ``False``. However, it is ignored if no selection was specified. In the case a selection was made and this option is enabled, gFeatMiner will compute the statistic on the selection as well as on the mother track as a whole and compare both statistics.

**per_chromosome**     Can take the following values: ``True`` or ``False``. It will default to false if not specified. When enabled, this option will break down every chromosome inside a selection or a track and treat them as separate data.

**wanted_chromosomes** An optional list of chromosomes present in the inputed tracks. If such a list is provided, the resulting graph will only contain the specified chromosomes and will ignore those not in the list.

**output_location**    Specifies the location at which the newly created image will be written.

**output_name**          Optionally specifies the name of the file to be created in ``output_location``.
====================== =====

Characteristics
---------------
Several types of characterisitcs can be used to generate different types of graphs. You can chose which charaterisitc to plot by specifiing ``characteristic=`` followed by one of the values in bold below:

.. automethod:: gmCharacteristic.number_of_features
.. automethod:: gmCharacteristic.base_coverage
.. automethod:: gmCharacteristic.length
.. automethod:: gmCharacteristic.score

Inner workings
--------------

gFeatMiner will produce one of the 8 different bar-graphs depending on the boolean values of the two variables ``compare_parents`` and ``per_chromosome`` as well as depending on the quantity of tracks inputted. The same workflow exists for box-plot based graphs, of course.

.. image:: /images/stat_workflow.png
