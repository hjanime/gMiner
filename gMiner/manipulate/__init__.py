"""
=====================
Genomic Manipulations
=====================

Another functionality provided by gFeatMiner is the ability to manipulate genomic data and create new tracks from existing ones. To access this functionality you must specify ``operation='manipulate'`` in the job request as seen in this example, in addition to a few other parameters that are detailed below::

    import gMiner
    files = gMiner.run(
        track1          = '/scratch/genomic/tracks/refseq_ucsc.sql',
        track1_name     = 'hg19 refSeq genome-wide from UCSC',
        track2          = '/scratch/genomic/tracks/hiv_bushman.sql',
        track2_name     = 'hg19 HIV integration sites from liftOver',
        operation       = 'manipulate',
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

**track_1_assembly**     If the track is missing required chromosome meta data, you can specify it here under the form of an assembly name.

**track_2**              The location of the second track file. This field is optional, for instance, if the operation only requires one genomic file

**track_2_name**         The name of the second track.

**track_2_assembly**     Same as above.

*[More tracks ...]*      Following tracks are specified according to the standard ``track_N`` and ``track_N_name``

**operation**            This field must be specified in the request and must take the value of ``manipulate`` if one wishes to perform genomic manipulation operations on the tracks provided.

**manipulation**         Can take any of the values described in the next section, "Manipulations".

**output_location**      Specifies the directory in which the newly created track will be written.

**output_name**          Optionally specifies the name of the file to be created in ``output_location``.

*[Extra parameters ...]* Depending on the manipulation requested, you may need to provide extra parameters like a window size or a threshold value. Refer to the manipulation documentation for more details.
======================== =====

Using the library in a script
-----------------------------
Instead of accessing gFeatMiner services via the ``gMiner.run()`` function, you can directly import the wanted manipulation and call it manually with your own queries. Here is a short example where a new track is created containing the ``mean_score_by_feature`` computed on two other tracks::

    import track
    from gMiner.genomic_manip import mean_score_by_feature
    with track.load('/scratch/genomic/tracks/pol2.sql') as pol2:
        with track.load('/scratch/genomic/tracks/ribosome_proteins.sql') as rpgenes:
            virtual_track = mean_score_by_feature(pol2,rpgenes)
            virtual_track.export('/tmp/result.sql')

Chaining manipulations
----------------------
The beautiful thing about this library is that operations can be chained one to an other without having to compute intermediary states. The following works::

    import track
    from gMiner.genomic_manip import overlap
    with track.load('/scratch/genomic/tracks/pol2.sql') as pol2:
        with track.load('/scratch/genomic/tracks/rap1.sql') as rap1:
            virtual_track = complement(overlap(pol2,rap1))
            virtual_track.export('/tmp/result.sql')

Using the library in "manual" mode
----------------------------------
If you want to modify the input of your manipulation on the fly, you can dig in to the generator functions as is explained here. You just need to write a function taking a generator object and returning a generator object. In this example our generator will yield several new features for every original feature it receives::

    def create_bins(X, num_of_bins=10):
        for x in X:
            length = (x[1] - x[0]) / num_of_bins
            for i in xrange(num_of_bins):
                yield (x[0]+i*length, x[0]+(i+1)*length, x[2], x[3], x[4])

    import track
    from gMiner.operations.genomic_manip.scores import mean_score_by_feature
    manip = mean_score_by_feature()
    with track.load('/scratch/genomic/tracks/pol2.sql') as pol2:
        with track.load('/scratch/genomic/tracks/ribosome_proteins.sql') as rpgenes:
            with track.new('/tmp/result.sql') as r:
                for chrom in pol2:
                    r.write(chrom, mean_score_by_feature(a.read(chrom), create_bins(b.read(chrom))))

Of course when you create tracks using this method, the resulting database is missing all its metadata. You probably will want to copy that over at some point::

    r.chrmeta = a.chrmeta
    r.info    = {'datatype': 'qualitative', 'name': 'Mean score per bin', 'created_by': 'Custom feature bin script'}

Manipulations
-------------
Several types of manipulations can be used to generate different types of tracks. You can chose which manipulation to execute by specifying ``manipulation=`` followed by one of the values in bold below:

.. automodule:: gMiner.manipulate
    :members:
"""

# Built-in modules #
import sys, pkgutil

# Internal modules #
from gMiner.manipulate import all_manips

# Other modules #
import track

################################################################################
class Manipulation(object):
    '''Parent class to all specific manipulations. It mainly handles argument
       parsing coming from ``gMiner.run`` requests and also from direct calls.'''

    def generate(self, *args, **kwargs):
        '''All child classes must implement
           this method.'''
        raise NotImplementedError

    def from_request(self, request, tracks):
        '''Put tracks and parameters in the right order.
           To be used when gMiner is called from the
           ``gMiner.run()`` function.'''
        # Put the track in the order they came #
        tracks_needed = [(v['position'],k) for (k,v) in self.args.items() if v['kind'] == Track]
        tracks_needed.sort()
        for index,(pos,name) in enumerate(tracks_needed):
            request.update({name:tracks[index]})
        # Call child class #
        return self(**request)

    def __call__(self, *largs, **kwargs):
        '''Check that all arguments are present
           and load all tracks that are given as paths
           instead of track objects. To be used
           when a plot is called directly from a script.'''
        # Initialization #
        parsed_args = {}
        tracks_to_unload = []
        # Parse arguments #
        for key, arg in self.args.items():
            # The value is either in largs or kwargs#
            if key in kwargs:
                value = kwargs[key]
            elif len(largs) >= arg['position']:
                value = largs[arg['position']-1]
            elif arg.get('optional'):
                continue
            else:
                raise Exception("The argument '" + key + "' is missing" \
                                + " for the plot '" + self.name + "'.")
            # Special conditions  tracks that are paths #
            if arg['kind'] == Track:
                # Check if its a path #
                if isinstance(value, basestring):
                    value = track.load(value)
                    tracks_to_unload.append(value)
                # Check the datatype #
                if arg.get('datatype'):
                    if value.datatype != arg['datatype']:
                        raise Exception("The datatype of track '" + value.path + "' " \
                                        + "isn't '" + arg['datatype'] + "'.")
            # Is the value is not the right type, cast it #
            if not isinstance(value, arg['kind']):
                value = arg['kind'](value)
            # Add it to the dict #
            parsed_args[key] = value
        # Call generate #
        fig = self.generate(**parsed_args)
        # Close tracks #
        for track in tracks_to_unload: track.unload()
        # Return a figure #
        return fig

################################################################################
def run(request, tracks, output_dir):
    # Mandatory 'manipulation' parameter #
    if not request.get('manipulation'):
        raise Exception("There does not seem to be a manipulation specified in the request")
    try:
        manipulation = globals()[request['manipulation']]
    except KeyError:
        raise Exception("The specified manipulation '%s' does not exist." % request['manipulation'])
    except TypeError:
        raise Exception("The specified manipulation '%s' is a special object in python."  % request['manipulation'])
    if not issubclass(manipulation, Manipulation):
        raise Exception("The specified manipulation '%s' is not a manipulation." % request['manipulation'])
    manip = manipulation()
    # Run it #
    manip.request    = request
    manip.req_tracks = tracks
    manip.output_dir = output_dir
    return manip.auto_prepare()

################################################################################
def build_manip_fn(request, tracks, output_dir):
    pass

################################################################################
self = sys.modules[__name__]
list_of_manips = [name for _, name, _ in pkgutil.iter_modules(all_manips.__path__)]
for manip in list_of_manips:
    print manip
    #func = build_manip_fn(manip)
    #setattr(self, manip, func)

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
