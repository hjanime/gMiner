# Other modules #
from bbcflib.track import Track

# Internal modules #
from ...constants import *
from ... import common
from ..genomic_manip import standard as manip

###########################################################################
class gmOperation(object):
    def prepare(self):
        # characteristic #
        if not self.request.get('characteristic'):
            raise Exception("There does not seem to be a characteristic specified in the request")
        if not hasattr(gmCharacteristic, self.request['characteristic']):
            raise Exception("The '" + object.__name__ + "' object does not seem to have '" + attribute + "'.")
        # per_chromosome #
        self.request['per_chromosome'] = self.request.get('per_chromosome', False)
        self.request['per_chromosome'] = bool(self.request['per_chromosome'])
        # compare_parents #
        if not self.request['selected_regions']: self.request['compare_parents'] = False
        self.request['compare_parents'] = self.request.get('compare_parents', False)
        self.request['compare_parents'] = bool(self.request['compare_parents'])
        # Create subtracks #
        self.subtracks = [subtrack for track in self.tracks for subtrack in self.track_cut_down(track)]
        # Create graph #
        self.graph = graphs.gmGraph(self.request, self.subtracks, self.tracks, self.output_dir)
         
    def track_cut_down(self, track):
        regions = self.request['selected_regions']
        if not regions:
            #--- NO SELECTION ---#
            if not self.request['per_chromosome']:
               yield gmSubtrack(self.request, track, {'type': 'all'})
            else:
               for chr in track.chrs: yield gmSubtrack(self.request, track, {'type': 'chr', 'chr': chr})
        elif type(regions) == list:
            #--- STRING SELECTION ---#
            if not self.request['per_chromosome']:
                yield gmSubtrack(self.request, track, {'type': 'regions', 'regions': regions}, False)
                if self.request['compare_parents']: yield gmSubtrack(self.request, track, {'type': 'all'}, True)
            else:
                for chr in track.chrs:
                    subregions = [subr for subr in regions if subr['chr'] == chr]
                    if subregions == []: continue
                    yield gmSubtrack(self.request, track, {'type': 'regions', 'regions': subregions}, False)
                    if self.request['compare_parents']: yield gmSubtrack(self.request, track, {'type': 'chr', 'chr': chr}, True)
        else:
            #--- TRACK SELECTION ---#
            if not self.request['per_chromosome']:
                yield gmSubtrack(self.request, track, {'type': 'track', 'track': self.request['selected_regions']}, False)
                if self.request['compare_parents']: yield gmSubtrack(self.request, track, {'type': 'all'}, True)
            else:
                with Track(self.request['selected_regions']) as t:
                    for chr in track.chrs:
                        if chr not in t: continue
                        yield gmSubtrack(self.request, track, {'type': 'trackchr', 'chr': chr}, False)
                        if self.request['compare_parents']: yield gmSubtrack(self.request, track, {'type': 'chr', 'chr': chr}, True)
        
    def run(self):
        # Compute characterisitcs #
        for track in self.tracks:
            [gm_get_characteristic(subtrack, self.request['characteristic']) for subtrack in self.subtracks if subtrack.track == track]
        # Generate the graph #
        return self.graph.generate()

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
            with Track(self.request['selected_regions']) as t:
                for x in self.make_overlap(t, self.selection['chr']): yield x
        elif self.selection['type'] == 'track':
            with Track(self.request['selected_regions']) as t:
                for chrom in self.track.chrs:
                    for x in self.make_overlap(t, chrom): yield x
 
    def make_overlap(self, t, chrom):
        sel_feats  = t.read(chrom, ['start', 'end'])
        orig_feats = self.track.read(chrom, self.fields)
        yield manip.overlap_track()(orig_feats, sel_feats)
        
###########################################################################
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
        func.fields       = ['start']
        func.shortcutable = True
        func.storable     = True
        func.units        = 'Count'
        func.collapse     = 'by_adding'
        return func
    @classmethod 
    @num_of_features_options
    def number_of_features(cls, iterable):
        '''Returns the number of features'''
        return sum(1 for _ in iterable)

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
        func.fields       = ['score']
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
        return [x[0] for x in iterable]

# Avoid circular imports #
from . import graphs

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
