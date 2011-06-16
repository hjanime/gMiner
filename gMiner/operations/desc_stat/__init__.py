# Other modules #
from bbcflib.track import Track

# Internal modules #
from ...constants import *
from ... import common
from .. import genomic_manip as manip

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
            with Track(self.request['selected_regions'], readonly=True) as t:
                for x in self.make_overlap(t, self.selection['chr']): yield x
        elif self.selection['type'] == 'track':
            with Track(self.request['selected_regions'], readonly=True) as t:
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
            with Track(request['selected_regions'], readonly=True) as t:
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
    # Compute characterisitcs #
    for track in tracks:
        [gm_get_characteristic(subtrack, request['characteristic']) for subtrack in subtracks if subtrack.track == track]
    # Generate the graph #
    return graph.generate()

# Avoid circular imports #
from . import graphs

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
