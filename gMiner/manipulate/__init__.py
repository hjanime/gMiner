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

    from gMiner.genomic_manip import mean_score_by_feature
    virtual_track = mean_score_by_feature('/scratch/tracks/pol2.sql', '/scratch/tracks/ribosome_proteins.sql')
    virtual_track.export('/tmp/result.sql')

As you can see, manipulations accept path as input, but they can also accept track objects for more fine grained control::

    import track
    from gMiner.genomic_manip import mean_score_by_feature
    with track.load('/scratch/tracks/pol2.sql') as pol2:
        with track.load('/scratch/tracks/ribosome_proteins.sql') as rpgenes:
            virtual_track = mean_score_by_feature(pol2,rpgenes)
            virtual_track.export('/tmp/result.sql')

Chaining manipulations
----------------------
The beautiful thing about this library is that operations can be chained one to an other without having to compute intermediary states. The following also works::

    import track
    from gMiner.genomic_manip import overlap
    with track.load('/scratch/genomic/tracks/pol2.sql') as pol2:
        with track.load('/scratch/genomic/tracks/rap1.sql') as rap1:
            virtual_track = complement(overlap(pol2,rap1))
            virtual_track.export('/tmp/result.sql')

Using the library in "manual" mode
----------------------------------
If you want to modify the input of your manipulation on the fly, you can also use the manipulations as generator functions. To do this, you just need to write a function taking a generator object and returning a generator object. In this example our generator will yield several new features for every original feature it receives::

    def create_bins(X, num_of_bins=10):
        for x in X:
            length = (x[1] - x[0]) / num_of_bins
            for i in xrange(num_of_bins):
                yield (x[0]+i*length, x[0]+(i+1)*length, x[2], x[3], x[4])

    import track
    from gMiner.operations.genomic_manip.scores import mean_score_by_feature
    manip = mean_score_by_feature()
    with track.load('/scratch/tracks/pol2.sql') as pol2:
        with track.load('/scratch/tracks/ribosome_proteins.sql') as rpgenes:
            with track.new('/tmp/result.sql') as r:
                for chrom in pol2:
                    r.write(chrom, mean_score_by_feature(a.read(chrom), create_bins(b.read(chrom))))

Of course when you create tracks using this method, the resulting database is missing all its metadata. You probably will want to copy that over at some point::

    r.chrmeta = a.chrmeta
    r.info    = {'datatype': 'qualitative', 'name': 'Mean score per bin', 'created_by': 'Custom feature bin script'}

Manipulations
-------------
Several types of manipulations can be used to generate different types of tracks. You can chose which manipulation to execute by specifying ``manipulation=`` followed by one of the values in bold below:

   .. autofunction:: mean_score_by_feature
   .. autofunction:: window_smoothing
   .. autofunction:: complement
   .. autofunction:: merge_scores
"""

# Built-in modules #
import sys, types, pkgutil, sqlite3

# Internal modules #
from gMiner.common import import_module, temporary_path, collapse, andify_strings, make_file_names
from gMiner.manipulate import all_manips

# Other modules #
import track
from track.extras import TrackCollection, VirtualTrack

# Constants #
base_attributes = ['label', 'short_name', 'long_name', 'input_tracks', 'input_args',
                   'input_meta', 'output_tracks', 'tracks_collapse', 'chroms_collapse',
                   'tooltip', 'numeric_example', 'visual_example', 'tests']
base_functions = ['generate']

################################################################################
class Manipulation(object):
    def __init__(self, *args):
        """Taking the module object of a standard manipulation file
            will build a callable instance satisfying the three
            access methods:

                1) overlap('tracks/pol2.sql', 'rap1.sql') # returns a virtual track
                2) overlap(pol2,rap1) # returns a virtual track
                3) overlap(pol2.read(chrom), rap1.read(chrom)) # returns a generator

            Other special cases:

                1) window_smoothing(pol2,rap1,L=100)
                2) merge_scores([pol2,rap1,ifhl,fhl1])
                3) overlap(pol2,rap1,ifhl,fhl1)
                4) complement(pol2.read(chrom), l=pol2.chrmeta[chrom]['length'])
        """
        # Only one argument #
        module = args[0]
        # Module attributes become instance attributes #
        for attr in base_attributes + base_functions: setattr(self, attr, getattr(module,attr))
        # Update the documentation #
        self.__doc__ = self.documentation

    @property
    def documentation(self):
        """Generate the sphinx docstring from the attributes of the manipulation."""
        # The long title #
        msg = self.long_name + "."
        # The tool tip #
        msg += "\n\n" + self.tooltip.replace('\n',' ') + '\n'
        # The input tracks #
        for t in self.input_tracks:
            if t.get('kind') == 'many':
                sub_msg = "\n:param %s: An arbitrary number of tracks or paths to tracks." \
                          " Eventually, generators yielding features."
            else:
                sub_msg = "\n:param %s: A track or the path to a track. Eventually, a generator yielding features."
            sub_msg = sub_msg % t['key']
            if 'fields' in t:
                if t.get('kind')=='many': sub_msg += " The minimum fields required for these tracks are: ``%s``"
                else:                     sub_msg += " The minimum fields required for this track are: ``%s``"
                sub_msg = sub_msg % t['fields']
                if '...' in t['fields']: sub_msg += ", extra fields can be used."
                else:                    sub_msg += ", extra fields cannot be used."
            msg += sub_msg + '\n'
            if t.get('kind') == 'many': msg += ":type %s: list\n" % t['key']
        # The arguments #
        for p in self.input_args:
            msg += ":param %s:" % p['key']
            if 'doc' in p: msg += " " + p['doc']
            if 'default' in p: msg += " By default ``%s``." % p['default']
            if 'type' in p: msg += "\n:type %s: %s" % (p['key'], p['type'].__name__)
            msg += '\n'
        # The special parameter #
        for p in self.input_meta:
            msg += "\n:param %s:" % p['key']
            if 'kind' in p and p['kind'] == 'chrom_len':
                msg += " The length of the current chromosome " \
                       "(only necessary when calling the manipulation with generators).\n" \
                       ":type %s: int" % p['key']
            msg += '\n'
        # The output #
        for t in self.output_tracks:
            if 'fields' in t: msg += ":returns: A track with the following fields: ``%s``." % t['fields']
            else:             msg += ":returns: A track."
            msg += '\n'
        # The numeric example #
        if self.numeric_example:
            msg += '\nA numerical example::\n %s\n' % self.numeric_example.replace('\n','\n     ')
        # The viusal example #
        if self.visual_example:
            msg += '\nA visual example::\n %s\n' % self.visual_example.replace('\n','\n    ')
        # Chromosomes collapse #
        if self.chroms_collapse: msg += "\n"\
        "If the list of chromosomes contained in the various tracks differ," \
        " the conflict will be resolved by applying the '%s' principle." \
        % self.chroms_collapse
        # Tracks collapse #
        if self.tracks_collapse: msg += "\n"\
        "If the list of tracks supplied is more than the two authorized," \
        " the conflict will be resolved by applying the '%s' principle." \
        % self.tracks_collapse
        # Return the message #
        return msg

    def test(self):
        """Run all the unittests"""
        pass

    def from_request(self, request, tracks, output_dir):
        """To be used when gMiner is called from the
           ``gMiner.run()`` function."""
        # Put the track in the order they came #
        tracks_needed = [(v['position'],k) for (k,v) in self.input_tracks]
        tracks_needed.sort()
        for index,(pos,name) in enumerate(tracks_needed):
            request.update({name:tracks[index]})
        # Call the manipulation #
        virtual_tracks = self(*tracks, **request)
        # Filename generator #
        if 'output_dir' in request:
            folder = request['output_dir']
            if 'output_name' in kwargs: file_names = make_file_names(folder + '/' + request['output_name'] + '.sql')
            else:                       file_names = make_file_names(folder + '/' + self.short_name + '.sql')
        else:
            file_names = make_file_names(temporary_path('.sql'))

    def __call__(self, *args, **kwargs):
        """Check that all arguments are present
           and load all tracks that are given as paths
           instead of track objects. Also checks for
           direct calls with generators."""
        # Initialization #
        found_args = {}
        found_tracks = []
        tracks_to_unload = []
        virtual_tracks = []
        generator_call = False
        # Parse tracks #
        for t in self.input_tracks:
            if t['key'] in kwargs: value = kwargs[t['key']]
            elif len(args) >= t['position']: value = args[t['position']-1]
            elif t.get('default'): value = t['default']
            elif t.get('optional'): continue
            else: raise Exception("The argument '%s' is missing for the manipulation '%s'." \
                                  % (t['key'], self.short_name))
            # Check is path #
            if isinstance(value, basestring):
                value = track.load(value, readonly=True)
                tracks_to_unload.append(value)
            # Check is generator #
            is_gen  = lambda x: isinstance(x, sqlite3.Cursor) or \
                                isinstance(x, track.FeatureStrem) or \
                                isinstance(x, types.GeneratorType)
            is_list = lambda x: isinstance(x, tuple) or \
                                isinstance(x, list)
            # Track collection case#
            if t.get('kind') == 'many':
                if not is_list(value): raise Exception("The track collection '%s' for the manipulation '%s'" \
                                                       " is not a list or a tuple: %s" \
                                                       % (t['key'], self.short_name, value))
                if is_gen(value[0]): generator_call = True
                else: value = track.TrackCollection(value)
            # Only one track case #
            else:
                if is_gen(value): generator_call = True
            # Add it to the dict #
            found_args[t['key']] = value
            # Add it another list #
            found_tracks.append(value)
        # Parse arguments #
        for p in self.input_args:
            if p['key'] in kwargs: value = kwargs[p['key']]
            elif len(args) >= p['position']: value = args[p['position']-1]
            elif p.get('default'): value = p['default']
            elif p.get('optional'): continue
            else: raise Exception("The argument '%s' is missing for the manipulation '%s'." \
                                  % (p['key'], self.short_name))
            # Cast it if it's not the right type #
            if not isinstance(value, p['type']): value = p['type'](value)
            # Add it to the dict #
            found_args[p['key']] = value
        # Check for generator case #
        if generator_call: return self.from_generator(found_args, args, kwargs)
        # Collapse chromosomes #
        if not self.chroms_collapse: chromosomes = found_tracks[0].chromosomes
        else: chromosomes = collapse(self.chroms_collapse, [t.chromosomes for t in found_tracks])
        # Output tracks #
        for t in self.output_tracks:
            # Get the output path #
            out_path = file_names.next()
            # Create a new track #
            out_track = track.new(out_path)
            # Iterate on chromosomes #
            for chrom in chromosomes:
                # Get special input arguments #
                # Call generate #
                self.generate(**found_args)
            # Output name #
            name = self.long_name + ' on ' + andify_strings([i['obj'].name for i in self.input_tracks])
            # Output chromosome metadata #

            # Output attributes #

            # Add it #
            virtual_tracks.append()
        # Close tracks #
        for t in tracks_to_unload: t.unload()
        # Return a list of paths #
        return [out_path]

    def from_generator(self, found_args, args, kwargs):
        """To be used when the manipulation is accessed
        directly with generators"""
        # Parse special input arguments #
        for p in self.input_meta:
            if p['key'] in kwargs: value = kwargs[p['key']]
            elif len(args) >= p['position']: value = args[p['position']-1]
            elif p.get('default'): value = p['default']
            elif p.get('optional'): continue
            else: raise Exception("The special argument '%s' is missing for the generator '%s'." \
                                  % (p['kind'], self.short_name))
            # Cast it if it's not the right type #
            if not isinstance(value, p['type']): value = p['type'](value)
            # Add it to the dict #
            found_args[p['key']] = value
        # Call the generator #
        return self.generate(**found_args)

################################################################################
def run(request, tracks, output_dir):
    """This function is called when running gMiner through
       the ``gMiner.run()`` fashion."""
    # Mandatory 'manipulation' parameter #
    if not request.get('manipulation'):
        raise Exception("There does not seem to be a manipulation specified in the request")
    try:
        manipulation = getattr(self_module, request['manipulation'])
    except KeyError:
        raise Exception("The specified manipulation '%s' does not exist." % request['manipulation'])
    except TypeError:
        raise Exception("The specified manipulation '%s' is a special object in python."  % request['manipulation'])
    if not issubclass(manipulation, Manipulation):
        raise Exception("The specified manipulation '%s' is not a manipulation." % request['manipulation'])
    # Run it and return a list of paths #
    return manipulation.from_request(request, tracks, output_dir)

################################################################################
# This module #
self_module = sys.modules[__name__]
# Where are the all the manipulations #
manips_directory = all_manips.__path__[0]
# A list containing their names #
list_of_manip_names = [name for loader, name, ispkg in pkgutil.iter_modules([manips_directory])]
# For every one make a callable function #
for manip_name in list_of_manip_names:
    manip_module = import_module('gMiner.manipulate.all_manips.' + manip_name)
    setattr(self_module, manip_name, Manipulation(manip_module))

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
