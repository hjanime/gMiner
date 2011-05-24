# Other modules #
from bbcflib.track import new

# Internal modules #
from ... import common

#############################################################################################
class TrackCollection(object):
    def __init__(self, tracks):
        self.tracks = tracks
        self.name = 'Collection of ' + str(len(tracks)) + ' track' + ((len(tracks) > 1) and 's' or '')
        self.chrs = common.collapse.by_intersection([t.chrs for t in tracks])
        self.meta_chr = []
        for chrom in self.chrs: self.meta_chr.append({'name': chrom, 'length': max([m['length'] for n in tracks for m in n.meta_chr if m['length'] and m['name'] == chrom])})
    def read(self, selection, fields): return [t.read(selection, fields) for t in self.tracks]

############################################################################################# 
class gmManipulation(object):
    def make_input_tracks(self):
        # Number of tracks #
        if not 'list of tracks' in [t['type'] for t in self.input_tracks]:
            if len(self.input_tracks) != len(self.req_tracks):
                raise Exception("The number of tracks inputed does not suit the manipulation requested")
        # Find tracks #
        print 'req_tracks', [t.name for t in self.req_tracks]
        print 'input_tracks 1', self.input_tracks
        for t in self.input_tracks:
            if t['type'] == 'list of tracks':
                tracks = []
                for i in xrange(len(self.req_tracks) - 1, -1, -1):
                    if track_matches_desc(self.req_tracks[i], t):
                        tracks.append(self.req_tracks[i])
                        self.req_tracks.pop(i)
                if tracks: t['obj'] = TrackCollection(tracks)
            else: 
                for req_t in self.req_tracks:
                    if track_matches_desc(req_t, t):
                        t['obj'] = req_t
                        self.req_tracks.remove(req_t)
                        break
            if not t.has_key('obj'): raise Exception("A required track for the manipulation '" + self.request['manipulation'] + "' is missing." + " You should include a " + t['kind'] + " track with at least the following fields: " + str(t['fields']))
        # Check all used #
        if not self.req_tracks == []: raise Exception("You provided too many tracks for the manipulation '" + self.request['manipulation'] + "'. The track '" + self.req_tracks[0].name + "' was not used.")
        print 'input_tracks 2', self.input_tracks

    def make_input_fields(self):
        for t in self.input_tracks:
            if t['fields'][-1] == '...': t['fields'] = t['fields'][:-1] + [f for f in t['obj'].fields if not f in t['fields']]             

    def make_input_other(self):
        for t in self.input_other:
            if self.request.has_key(t['key']):
                try:
                    t['value'] = t['type'](self.request[t['key']])
                except ValueError as err:
                    raise Exception("The '" + t['key'] + "' parameter is not of type: " + t['type'].__name__, err)
            else:
                if t.has_key('default'):
                    t['value'] = t['default']
                else:
                    raise Exception("A required parameter for the manipulation " + self.request['manipulation'] + " is missing." + " You should include a '" + t['key'] + "' paramater that must be of type: " + t['type'].__name__)

    def make_output_chromosomes(self):
        self.chrs = self.chr_collapse([t['obj'].chrs for t in self.input_tracks])

    def make_output_tracks(self):
        for t in self.output_tracks:
            t['name']     = self.name + ' on ' + common.andify_strings([track['obj'].name for track in self.input_tracks])
            t['location'] = self.output_dir + '/gminer_' + self.__class__.__name__  + '.sql'
            t['obj']      = new(t['location'], 'sql', t['kind'], t['name'])

    def make_output_meta_track(self):
        for t in self.output_tracks:
            t['obj'].meta_track = {'datatype': t['kind'], 'name': t['name'], 'created_by': __package__}

    def make_output_meta_chr(self):
        self.chrmeta = []
        for chrom in self.chrs: self.chrmeta.append({'name': chrom, 'length': max([m['length'] for n in self.input_tracks for m in n['obj'].meta_chr if m['length'] and m['name'] == chrom])})
        for t in self.output_tracks: t['obj'].meta_chr = self.chrmeta

    def make_output_fields(self):
        for t in self.output_tracks:
            if type(t['fields']) == dict:
                if t['fields'].has_key('same'): t['fields'] = self.input_tracks[t['fields']['same']]['obj'].fields

        self.chrmeta = []
        for chrom in self.chrs: self.chrmeta.append({'name': chrom, 'length': max([m['length'] for n in self.input_tracks for m in n['obj'].meta_chr if m['length'] and m['name'] == chrom])})
        for t in self.output_tracks: t['obj'].meta_chr = self.chrmeta

    def get_special_parameter_stop_val(self, chr_name):
        for chrom in self.chrmeta:
            if chrom['name'] == chr_name: return chrom['length']

    def get_special_parameter_datatype(self, chr_name):
        return self.input_tracks[0]['obj'].datatype

    #-------------------------------------------------------------------------------------------#
    def __call__(self, datatype='qualitative', **kwargs):
        if datatype == 'qualitative':
            for x in self.qual(**kwargs): yield x
        if datatype == 'quantitative':
            for x in self.quan(**kwargs): yield x

    #-------------------------------------------------------------------------------------------#
    def run(self):
        # Prepare stuff #
        self.make_input_tracks()
        self.make_input_fields()
        self.make_input_other()
        self.make_output_chromosomes()
        self.make_output_tracks()
        self.make_output_meta_track()
        self.make_output_meta_chr()
        self.make_output_fields()
        # Several outputs #
        if len(self.output_tracks) > 1: raise NotImplementedError
        # Only one output track #
        T = self.output_tracks[0] 
        for chrom in self.chrs:
            kwargs = {}
            for t in self.input_extras:
                kwargs[t['name']] = getattr(self, 'get_special_parameter_' + t['type'])(chrom)
            for t in self.input_other:
                kwargs[t['name']] = t['value']
            for t in self.input_tracks:
                kwargs[t['name']] = t['obj'].read(chrom, t['fields'])
            T['obj'].write(chrom, self(**kwargs), T['fields'])
        self.output_tracks[0]['obj'].unload()

#############################################################################################
# Submodules #
from .standard import *
from .scores import *
 
def track_matches_desc(track, info):
    # Datatype #
    if not info['kind'] == 'any' and track.datatype != info['kind']: return False
    # Fields #
    if track.fields[-1] == '...':
        if set(track.fields[:-1]) < set(info['fields']): return False
    else:
        if set(track.fields)      < set(info['fields']): return False
    # Default case #
    return True

def run(request, tracks, output_dir):
    # Manipulation specified #
    if not request.get('manipulation'):
        raise Exception("There does not seem to be a manipulation specified in the request")
    # Manipulation exists #
    try:
        if not issubclass(globals()[request['manipulation']], gmManipulation):
            raise Exception("The specified manipulation '" + request['manipulation'] + "' is not a manipulation.")
    except KeyError:
        raise Exception("The specified manipulation '" + request['manipulation'] + "' does not exist.")
    except TypeError:
        raise Exception("The specified manipulation '" + request['manipulation'] + "' is a special object in python.")
    # Get the manipulation #
    manip = globals()[request['manipulation']]()
    # Copy vars #
    manip.request = request
    manip.req_tracks = tracks
    manip.output_dir = output_dir        
    # Run it #
    manip.run()
    # Report success # 
    return [t['location'] for t in manip.output_tracks]

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
