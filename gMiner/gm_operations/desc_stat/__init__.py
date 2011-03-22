# gMiner Modules #
from ... import gm_common    as gm_com
from ... import gm_parsing   as gm_par
from ... import gm_errors    as gm_err
from ...gm_constants import *

# Submodules #
from .graphs import *

# Functions #
def list_options():
    return '\n'.join([f[0]+':'+f[1].title for f in gmCharacteristic.__dict__.items() if f[0][0] != '_'])

###########################################################################   
class gmOperation(object):
    def __init__(self, request, tracks):
        self.type = 'desc_stat'
        self.request = request
        self.tracks = tracks
    
    def prepare(self):
        # characteristic #
        if not gm_par.exists_in_dict(self.request, 'characteristic'):
            raise gm_err.gmError(400, "There does not seem to be a characteristic specified in the request")
        gm_par.assert_has_method(gmCharacteristic, self.request['characteristic'])
        # per_chromosome #
        gm_par.default_if_none(self.request, 'per_chromosome')
        gm_par.convert_to_bool(self.request, 'per_chromosome')
        gm_par.assert_is_type(self.request['per_chromosome'], bool, 'per_chromosome')
        # compare_parents #
        if not self.request['selected_regions']: self.request['compare_parents'] = False
        gm_par.default_if_none(self.request, 'compare_parents')
        gm_par.convert_to_bool(self.request, 'compare_parents')
        gm_par.assert_is_type(self.request['compare_parents'], bool, 'compare_parents')
        # gm_encoding elf
        gm_par.default_if_none(self.request, 'gm_encoding', 'text/base64')
        gm_par.assert_is_among(self.request['gm_encoding'], ['text/base64','image/png'], 'encoding')
        # Create subtracks #
        self.subtracks = [subtrack for track in self.tracks for subtrack in self.track_cut_down(track)]
        # Create graph #
        self.graph = gmGraph(self.request, self.subtracks, self.tracks)
         
    def track_cut_down(self, track):
        region = self.request['selected_regions']
        if region:
            #--- YES SELECTION ---#    
            if self.request['per_chromosome']:
                for chr in track.chrs:
                    subregion = [subr for subr in region if subr['chr'] == chr]
                    if subregion == []: continue
                    yield gmSubtrack(self.request, track, {'type': 'region', 'region': subregion})
                    if self.request['compare_parents']: yield gmSubtrack(self.request, track, {'type': 'chr', 'chr': chr})
            else:
                yield gmSubtrack(self.request, track, {'type': 'region', 'region': region})
                if self.request['compare_parents']: yield gmSubtrack(self.request, track, {'type': 'all'})
        else:
            #--- NO SELECTION ---#
            if self.request['per_chromosome']:
               for chr in track.chrs: yield gmSubtrack(self.request, track, {'type': 'chr', 'chr': chr})
            else:
                yield gmSubtrack(self.request, track, {'type': 'all'})
        
    def run(self):
        # Compute characterisitcs #
        for track in self.tracks:
            [gm_get_characteristic(subtrack, self.request['characteristic']) for subtrack in self.subtracks if subtrack.track == track]
            track.unload() 
        # Generate the graph #
        r1, r2, r3 = self.graph.generate()
        # Free memory #
        self.graph.cleanup()
        for subtrack in self.subtracks: subtrack.cleanup()
        # Return result #
        return r1, r2, r3

###########################################################################   
class gmSubtrack(object):
    def __init__(self, request, track, selection):
        self.request = request
        self.track = track 
        self.selection = selection
        
        # Unique chromosome #
        self.chr = None
        if self.selection['type'] == 'chr': self.chr = selection['chr']
        if self.selection['type'] == 'region' and self.request['per_chromosome']: self.chr = selection['region'][0]['chr']
    
    def __iter__(self):
        if self.selection['type'] == 'chr':
            yield self.track.get_data_qual(self.selection, self.fields)
        elif self.selection['type'] == 'all':
            for chr in self.track.chrs: yield self.track.get_data_qual({'type': 'chr', 'chr': chr}, self.fields)
        elif self.selection['type'] == 'region': 
            for span in self.selection['region']: yield self.track.get_data_qual({'type': 'span', 'span': span}, self.fields)

    def cleanup(self):
       del self.stat 
 
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
    if storable: stored = subtrack.track.get_stored('desc_stat', chara, subtrack.selection)
    if stored: result = stored
    # Shortcut #
    shortcutable = not result and charafn.shortcutable and (type == 'chr' or type == 'all')
    if shortcutable: shortcut = subtrack.track.stat_shortcut(chara, subtrack.selection)
    if shortcut: result = shortcut
    # Do it #
    subtrack.fields = charafn.fields
    result = getattr(gm_com.gmCollapse, charafn.collapse)([charafn(data) for data in subtrack])
    subtrack.stat = result
    # Store it #
    if storable and not stored: subtrack.track.write_stored('desc_stat', chara, subtrack.selection, result)

#-----------------------------------------------------------------------------#   
class gmCharacteristic(object):

    def num_of_features_options(func):
        func.title = '''Number of features'''
        func.fields = ['strand']
        func.shortcutable = True
        func.storable = True
        func.units = 'Count'
        func.collapse = 'by_adding'
        return func
    @classmethod 
    @num_of_features_options
    def number_of_features(cls, iterable):
        '''Returns the number of features'''
        return sum(1 for _ in iterable)

    def base_coverage_options(func):
        func.title = '''Base coverage'''
        func.fields = ['start','end']
        func.shortcutable = False
        func.storable = True
        func.units = 'Base pairs'
        func.collapse = 'by_adding'
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
        func.title = '''Length distribution'''
        func.fields = ['start','end']
        func.shortcutable = False
        func.storable = False
        func.units = 'Base Pairs'
        func.collapse = 'by_appending'
        return func
    @classmethod
    @length_options
    def length(cls, iterable):
        '''Returns the length distribution'''
        return [x[1]-x[0] for x in iterable]

    def score_options(func):
        func.title = '''Score distribution'''
        func.fields = ['score']
        func.shortcutable = False
        func.storable = False
        func.units = 'Undefined'
        func.collapse = 'by_appending'
        return func
    @classmethod
    @score_options
    def score(cls, iterable):
        '''Returns the score distribution'''
        iterable = list(iterable)
        return [x[0] for x in iterable]

###########################################################################   
