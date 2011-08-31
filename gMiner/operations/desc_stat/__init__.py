"""
======================
Descriptive Statistics
======================

One of the primary goals of gFeatMiner is to provide simple graphs that help the user describe and explore his genomic datasets. These graphs are generated quickly and on-the-fly as they are requested. To access this functionality you must specify ``operation_type=desc_stat`` in the job request as seen in this example, in addition to a few other parameters that are detailed below::

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

The ``files`` variable will now contain the path to the file created in PNG format.

Parameters
----------

Here are described all the parameters that can or should be passed to gFeatMiner's run function.

====================== =====
Key                    Value
====================== =====
**track_1**            This specifies the location of the first track file. At least one genomic file must be inputted to compute a statistic. Of course, an undefined number of supplementary tracks can be specified. The order in which they are given may or may not influence the output depending on the operation requested.

**track_1_name**       This field is also required. Without a name, the resulting graph will not have a comprehensive legend associated and the user will get confused. Every track must have a name

**track_1_chrs**       If the track is missing required chromosome meta data, you can specify it here under the form of a chromosome file or an assembly name.

**track_2**            The location of the second track file. This field is optional, for instance, if the operation only requires one genomic file

**track_2_name**       The name of the second track.

**track_2_chrs**       Same as above.

*[More tracks ...]*      Following tracks are specified according to the standard ``track_N`` and ``track_N_name``

**operation_type**     This field must be specified in the request and must take the value of ``desc_stat`` if one wishes to perform descriptive statistic operations on the tracks provided.

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
Several types of characteristics can be used to generate different types of graphs. You can chose which characteristic to plot by specifying ``characteristic=`` followed by one of the values in bold below:

.. automethod:: gmCharacteristic.number_of_features
.. automethod:: gmCharacteristic.base_coverage
.. automethod:: gmCharacteristic.length
.. automethod:: gmCharacteristic.score

Inner workings
--------------

gFeatMiner will produce one of the 8 different bar-graphs depending on the boolean values of the two variables ``compare_parents`` and ``per_chromosome`` as well as depending on the quantity of tracks inputted. The same workflow exists for box-plot based graphs, of course.

.. image:: /images/stat_workflow.png

"""

# Internal modules #
from ...constants import *
from ... import common
from .. import genomic_manip as manip

# Other modules #
from bbcflib.track import load

###########################################################################
class gmSubtrack(object):
    def __init__(self, request, track, selection, parent=None):
        self.request = request
        self.track = track
        self.selection = selection
        self.parent = parent

        # Unique chromosome #
        self.chr = None
        if self.selection['type'] == 'chr': self.chr = selection['chr']
        if self.selection['type'] == 'regions' and self.request['per_chromosome']: self.chr = selection['regions'][0]['chr']
        if self.selection['type'] == 'trackchr': self.chr = selection['chr']

    def __iter__(self):
        if self.selection['type'] == 'chr':
            yield self.track.read(self.selection['chr'], self.fields)
        elif self.selection['type'] == 'all':
            for chr in self.track.chrs: yield self.track.read(chr, self.fields)
        elif self.selection['type'] == 'regions':
            for span in self.selection['regions']: yield self.track.read(span, self.fields)
        elif self.selection['type'] == 'trackchr':
            with load(self.request['selected_regions'], readonly=True) as t:
                for x in self.make_overlap(t, self.selection['chr']): yield x
        elif self.selection['type'] == 'track':
            with load(self.request['selected_regions'], readonly=True) as t:
                for chrom in self.track.chrs:
                    for x in self.make_overlap(t, chrom): yield x

    def make_overlap(self, t, chrom):
        sel_feats  = t.read(chrom, ['start', 'end'])
        orig_feats = self.track.read(chrom, self.fields)
        yield manip.filter()(orig_feats, sel_feats)

###########################################################################
def track_cut_down(request, track):
    regions = request['selected_regions']
    if not regions:
        #--- NO SELECTION ---#
        if not request['per_chromosome']:
           yield gmSubtrack(request, track, {'type': 'all'})
        else:
           for chr in track.chrs: yield gmSubtrack(request, track, {'type': 'chr', 'chr': chr})
    elif type(regions) == list:
        #--- STRING SELECTION ---#
        if not request['per_chromosome']:
            yield gmSubtrack(request, track, {'type': 'regions', 'regions': regions}, False)
            if request['compare_parents']: yield gmSubtrack(request, track, {'type': 'all'}, True)
        else:
            for chr in track.chrs:
                subregions = [subr for subr in regions if subr['chr'] == chr]
                if subregions == []: continue
                yield gmSubtrack(request, track, {'type': 'regions', 'regions': subregions}, False)
                if request['compare_parents']: yield gmSubtrack(request, track, {'type': 'chr', 'chr': chr}, True)
    else:
        #--- TRACK SELECTION ---#
        if not request['per_chromosome']:
            yield gmSubtrack(request, track, {'type': 'track', 'track': request['selected_regions']}, False)
            if request['compare_parents']: yield gmSubtrack(request, track, {'type': 'all'}, True)
        else:
            with load(request['selected_regions'], readonly=True) as t:
                for chr in track.chrs:
                    if chr not in t: continue
                    yield gmSubtrack(request, track, {'type': 'trackchr', 'chr': chr}, False)
                    if request['compare_parents']: yield gmSubtrack(request, track, {'type': 'chr', 'chr': chr}, True)

def gm_get_characteristic(subtrack, chara):
    # Variables #
    result = False
    stored = False
    shortcut = False
    type = subtrack.selection['type']
    charafn = getattr(gmCharacteristic, chara)
    # Stored #
    storable = charafn.storable and (type == 'chr' or type == 'all')
    if storable: stored = False # subtrack.track.get_stored('desc_stat', chara, subtrack.selection)
    if stored: result = stored
    # Shortcut #
    shortcutable = not result and charafn.shortcutable and (type == 'chr' or type == 'all')
    if shortcutable: shortcut = False #subtrack.track.stat_shortcut(chara, subtrack.selection)
    if shortcut: result = shortcut
    # Do it #
    subtrack.fields = charafn.fields
    result = getattr(common.collapse, charafn.collapse)([charafn(data) for data in subtrack])
    subtrack.stat = result
    # Store it #
    # if storable and not stored: subtrack.track.write_stored('desc_stat', chara, subtrack.selection, result)

#-------------------------------------------------------------------------#
class gmCharacteristic(object):

    def num_of_features_options(func):
        func.title        = '''Number of features'''
        func.fields       = ['start','end']
        func.shortcutable = True
        func.storable     = True
        func.units        = 'Count'
        func.collapse     = 'by_adding'
        return func
    @classmethod
    @num_of_features_options
    def number_of_features(cls, iterable):
        '''Returns the number of features'''
        sum = 0
        for x in iterable: sum +=1
        return sum

    def base_coverage_options(func):
        func.title        = '''Base coverage'''
        func.fields       = ['start','end']
        func.shortcutable = False
        func.storable     = True
        func.units        = 'Base pairs'
        func.collapse     = 'by_adding'
        return func
    @classmethod
    @base_coverage_options
    def base_coverage(cls, iterable):
        '''Returns the base coverage'''
        sum = 0
        position = -1
        for x in iterable:
            if x[1] > position:
                if x[0] < position: sum += x[1] - position
                else: sum += x[1] - x[0]
                position = x[1]
        return sum

    def length_options(func):
        func.title        = '''Length distribution'''
        func.fields       = ['start','end']
        func.shortcutable = False
        func.storable     = False
        func.units        = 'Base Pairs'
        func.collapse     = 'by_appending'
        return func
    @classmethod
    @length_options
    def length(cls, iterable):
        '''Returns the length distribution'''
        return [x[1]-x[0] for x in iterable]

    def score_options(func):
        func.title        = '''Score distribution'''
        func.fields       = ['start','end','score']
        func.shortcutable = False
        func.storable     = False
        func.units        = 'Undefined'
        func.collapse     = 'by_appending'
        return func
    @classmethod
    @score_options
    def score(cls, iterable):
        '''Returns the score distribution'''
        iterable = list(iterable)
        return [x[2] for x in iterable]

###########################################################################
def run(request, tracks, output_dir):
    # characteristic #
    if not request.get('characteristic'):
        raise Exception("There does not seem to be a characteristic specified in the request")
    if not hasattr(gmCharacteristic, request['characteristic']):
        raise Exception("The '" + object.__name__ + "' object does not seem to have '" + attribute + "'.")
    # per_chromosome #
    request['per_chromosome'] = request.get('per_chromosome', False)
    request['per_chromosome'] = bool(request['per_chromosome'])
    # compare_parents #
    if not request['selected_regions']: request['compare_parents'] = False
    request['compare_parents'] = request.get('compare_parents', False)
    request['compare_parents'] = bool(request['compare_parents'])
    # Create subtracks #
    subtracks = [subtrack for track in tracks for subtrack in track_cut_down(request, track)]
    # Create graph #
    graph = graphs.gmGraph(request, subtracks, tracks, output_dir)
    # Compute characteristics #
    for track in tracks:
        [gm_get_characteristic(subtrack, request['characteristic']) for subtrack in subtracks if subtrack.track == track]
    # Generate the graph #
    return graph.generate()

# Avoid circular imports #
from . import graphs

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
