'''
=====================
Genomic Manipulations
=====================

Another functionality provided by gFeatMiner is the ability to manipulate genomic data and create new tracks from existing ones. To access this functionality you must specify ``operation_type=genomic_manip`` in the job request as seen in this example, in addition to a few other parameters that are detailed below::

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

**track_1_chrs**         If the track is missing required chromosome meta data, you can specify it here under the form of a chromosome file or an assembly name.

**track_2**              The location of the second track file. This field is optional, for instance, if the operation only requires one genomic file

**track_2_name**         The name of the second track.

**track_2_chrs**         Same as above.

*[More tracks ...]*      Following tracks are specified according to the standard ``track_N`` and ``track_N_name``

**operation_type**       This field must be specified in the request and must take the value of ``genomic_manip`` if one wishes to perform genomic manipulation operations on the tracks provided.

**manipulation**         Can take any of the values described in the next section, "Manipulations".

**output_location**      Specifies the location at which the newly created track will be written.

**output_name**          Optionally specifies the name of the file to be created in ``output_location``.

*[Extra parameters ...]* Depending on the manipulation requested, you may need to provide extra parameters like a window size or a threshold value. Refer to the manipulation documentation for more details.
======================== =====

Using the library in 'manual' mode
----------------------------------
Instead of accessing gFeatMiner services via the ``gMiner.run()`` function, you can directly import the wanted manipulation and call it manually with your own queries. Here is a short example where a new track containing the ``mean_score_by_feature`` (computed on two other tracks) is created::

    from bbcflib import track
    from gMiner.operations.genomic_manip.scores import mean_score_by_feature
    manip = mean_score_by_feature()
    with track.load('/scratch/genomic/tracks/pol2.sql') as a:
        with track.load('/scratch/genomic/tracks/ribosome_proteins.sql') as b:
            with track.new('/tmp/manual.sql') as r:
                for chrom in a:
                    r.write(chrom, manip(a.read(chrom), b.read(chrom)))

Now you are only one step away from modifying the input of your manipulation on the fly. You just need to write a function taking a generator object and returning a generator object. In this example our generator will yield several new features for every original feature it receives::

    def create_bins(X, num_of_bins=10):
        for x in X:
            length = (x[1] - x[0]) / num_of_bins
            for i in xrange(num_of_bins):
                yield (x[0]+i*length, x[0]+(i+1)*length, x[2], x[3], x[4])

    from bbcflib import track
    from gMiner.operations.genomic_manip.scores import mean_score_by_feature
    manip = mean_score_by_feature()
    with track.load('/scratch/genomic/tracks/pol2.sql') as a:
        with track.load('/scratch/genomic/tracks/ribosome_proteins.sql') as b:
            with track.new('/tmp/manual.sql') as r:
                for chrom in a:
                    r.write(chrom, manip(a.read(chrom), create_bins(b.read(chrom))))

Of course when you create tracks using this method, the resulting database is missing all its metadata. You probably will want to copy that over at some moment::

    r.chrmeta    = a.chrmeta
    r.attributes = {'datatype': 'qualitative', 'name': 'Mean score per bin', 'created_by': 'Custom feature bin script'}

Manipulations
-------------
Several types of manipulations can be used to generate different types of tracks. You can chose which manipulation to execute by specifying ``manipulation=`` followed by one of the values in bold below:

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
'''

# Internal modules #
from gMiner import common

# Other modules #
from bbcflib import track
from bbcflib.track.track_bundle import TrackBundle

################################################################################
def track_matches_desc(track, info):
    # Datatype #
    if not info['kind'] == 'any' and track.datatype != info['kind']: return False
    # Fields #
    if info['fields'][-1] == '...':
        if set(info['fields'][:-1]) > set(track.fields): return False
    else:
        if set(info['fields'])      > set(track.fields): return False
    # Default case #
    return True

################################################################################
class Manipulation(object):
    def __call__(self, in_type=None, out_type=None, **kwargs):
        for x in {('qualitative'  , None):           self.qual,
                  ('quantitative' , None):           self.quan,
                  (None           , 'quantitative'): self.qual,
                  (None           , 'qualitative' ): self.quan,
                  ('qualitative'  , 'qualitative' ): self.qual_to_qual,
                  ('qualitative'  , 'quantitative'): self.qual_to_quan,
                  ('quantitative' , 'qualitative' ): self.quan_to_qual,
                  ('quantitative' , 'quantitative'): self.quan_to_quan,
                 }[(in_type, out_type)](**kwargs): yield x

    def qual(self):         raise NotImplementedError
    def quan(self):         raise NotImplementedError
    def qual_to_quan(self): raise NotImplementedError
    def qual_to_qual(self): raise NotImplementedError
    def quan_to_qual(self): raise NotImplementedError
    def quan_to_quan(self): raise NotImplementedError

    #--------------------------------------------------------------------------#
    def get_parameter_stop_val(self, chr_name):
        return self.output_tracks[0]['obj'].chrmeta[chr_name]['length']

    #-------------------------------------------------------------------------------------------#
    def auto_prepare(self):
        ##### Input tracks #####
        # Number of tracks #
        if not 'list of tracks' in [t['type'] for t in self.input_tracks]:
            if len(self.input_tracks) != len(self.req_tracks):
                raise Exception("The number of tracks inputed does not suit the manipulation requested")
        # Find tracks #
        for t in self.input_tracks:
            if not self.req_tracks:
                raise Exception("A required track for the manipulation '" + self.request['manipulation'] + "' is missing." + " You should include a " + t['kind'] + " track with at least the following fields: " + str(t['fields']))
            if t['type'] == 'list of tracks':
                tracks = []
                for i in xrange(len(self.req_tracks) - 1, -1, -1):
                    if track_matches_desc(self.req_tracks[i], t):
                        tracks.append(self.req_tracks[i])
                        self.req_tracks.pop(i)
                if tracks: t['obj'] = TrackBundle(tracks)
            else:
                for req_t in self.req_tracks:
                    if track_matches_desc(req_t, t):
                        t['obj'] = req_t
                        self.req_tracks.remove(req_t)
                        break
                if not t.has_key('obj'):
                    t['obj'] = self.req_tracks.pop()
                    if t['obj'].datatype == 'quantitative' and t['kind'] == 'qualitative':
                        t['convert'] = quan_to_qual()
        # Check all used #
        if not self.req_tracks == []: raise Exception("You provided too many tracks for the manipulation '" + self.request['manipulation'] + "'. The track '" + self.req_tracks[0].name + "' was not used.")
        ##### Input fields #####
        for t in self.input_tracks:
            if t['fields'][-1] == '...':
                t['fields'] = t['fields'][:-1]
                t['fields'] += [f for f in track.Track.qualitative_fields if f in t['obj'].fields and not f in t['fields']]
                t['fields'] += [f for f in t['obj'].fields if not f in t['fields']]
        ##### Input request #####
        base_kwargs = {}
        for t in self.input_request:
            if self.request.has_key(t['key']):
                try:
                    base_kwargs[t['name']] = t['type'](self.request[t['key']])
                except ValueError as err:
                    raise Exception("The '" + t['key'] + "' parameter is not of type: " + t['type'].__name__, err)
            else:
                if t.has_key('default'):
                    base_kwargs[t['name']] = t['default']
                else:
                    raise Exception("A required parameter for the manipulation " + self.request['manipulation'] + " is missing." + " You should include a '" + t['key'] + "' paramater that must be of type: " + t['type'].__name__)
        ##### Input special #####
        for i in self.input_special:
            if i['type'] == 'in_datatype':  base_kwargs[i['name']] = self.input_tracks[0]['obj'].datatype
            if i['type'] == 'out_datatype':
                if self.request.has_key(i['type']): datatype = self.request[i['type']]
                else:                               datatype = self.input_tracks[0]['obj'].datatype
                base_kwargs[i['name']]                 = datatype
                for t in self.output_tracks: t['kind'] = datatype
                if datatype == 'quantitative': t['fields'] = track.Track.quantitative_fields
                if datatype == 'qualitative':  t['fields'] = {'same': 0}
        ##### Output chromosomes #####
        self.chrs = self.chr_collapse([t['obj'].chrs for t in self.input_tracks])
        ##### Output tracks #####
        for t in self.output_tracks:
            if t['kind'] == 'various':
                t['kind'] = ''
            t['name']     = self.name + ' on ' + common.andify_strings([i['obj'].name for i in self.input_tracks])
            if self.request.get('output_name'): t['location'] = self.output_dir + '/' + self.request['output_name'] + '.sql'
            else: t['location'] = self.output_dir + '/gminer_' + self.__class__.__name__  + '.sql'
            t['obj']      = track.new(t['location'], 'sql', t['name'])
        ##### Output attributes #####
        for t in self.output_tracks:
            t['obj'].attributes = {'datatype': t['kind'], 'name': t['name'], 'created_by': __package__}
        ##### Output chrmeta #####
        for i in self.output_tracks:
            i['obj'].chrmeta = self.input_tracks[0]['obj'].chrmeta
            for j in self.input_tracks: i['obj'].chrmeta.choose_max(j['obj'].chrmeta)
        ##### Output fields #####
        for t in self.output_tracks:
            if type(t['fields']) == dict:
                if t['fields'].has_key('same'): t['fields'] = self.input_tracks[t['fields']['same']]['fields']
        ##### Run it #####
        # Several outputs #
        if len(self.output_tracks) > 1: raise NotImplementedError
        # Maybe convert stream #
        def read_and_convert(t, chrom, fields, cursor, func=None):
            if not func: return      t.read(chrom, fields, cursor=cursor)
            else:        return func(t.read(chrom,         cursor=cursor))
        # Only one output track #
        T = self.output_tracks[0]
        for chrom in self.chrs:
            kwargs = base_kwargs.copy()
            for t in self.input_by_chrom:
                kwargs[t['name']] = getattr(self, 'get_parameter_' + t['type'])(chrom)
            for t in self.input_tracks:
                if type(t['name']) != list:
                    kwargs[t['name']] = read_and_convert(t['obj'], chrom, t['fields'], cursor=True, func=t.get('convert', None))
                else:
                    for n in t['name']: kwargs[n] = read_and_convert(t['obj'], chrom, t['fields'], cursor=True, func=t.get('convert', None))
            T['obj'].write(chrom, self(**kwargs), T['fields'])
        self.output_tracks[0]['obj'].unload()
        return [t['location'] for t in self.output_tracks]

################################################################################
# Submodules #
from .basic import *
from .standard import *
from .scores import *
from .boolean import *
from .association import *

def run(request, tracks, output_dir):
    # Manipulation specified #
    if not request.get('manipulation'):
        raise Exception("There does not seem to be a manipulation specified in the request")
    # Manipulation exists #
    try:
        if not issubclass(globals()[request['manipulation']], Manipulation):
            raise Exception("The specified manipulation '" + request['manipulation'] + "' is not a manipulation.")
    except KeyError:
        raise Exception("The specified manipulation '" + request['manipulation'] + "' does not exist.")
    except TypeError:
        raise Exception("The specified manipulation '" + request['manipulation'] + "' is a special object in python.")
    # Get the manipulation #
    manip = globals()[request['manipulation']]()
    # Automatically run it #
    manip.request    = request
    manip.req_tracks = tracks
    manip.output_dir = output_dir
    return manip.auto_prepare()

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
