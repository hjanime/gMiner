# Other modules #
from bbcflib.track import Track, new

# Internal modules #
from ... import common

#############################################################################################
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

    #-------------------------------------------------------------------------------------------#
    def get_parameter_stop_val(self, chr_name):
        for chrom in self.chrmeta:
            if chrom['name'] == chr_name: return chrom['length']

    #-------------------------------------------------------------------------------------------#
    def auto_prepare(self):
        ##### Input tracks #####
        # Number of tracks #
        if not 'list of tracks' in [t['type'] for t in self.input_tracks]:
            if len(self.input_tracks) != len(self.req_tracks):
                raise Exception("The number of tracks inputed does not suit the manipulation requested")
        # Find tracks #
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
        ##### Input fields #####
        for t in self.input_tracks:
            if t['fields'][-1] == '...':
                t['fields'] = t['fields'][:-1]
                t['fields'] += [f for f in Track.qualitative_fields if f in t['obj'].fields and not f in t['fields']]
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
                if datatype == 'quantitative': t['fields'] = Track.quantitative_fields
                if datatype == 'qualitative':  t['fields'] = {'same': 0}
        ##### Output chromosomes #####
        self.chrs = self.chr_collapse([t['obj'].chrs for t in self.input_tracks])
        ##### Output tracks #####
        for t in self.output_tracks:
            if t['kind'] == 'various':
                t['kind'] = ''
            t['name']     = self.name + ' on ' + common.andify_strings([track['obj'].name for track in self.input_tracks])
            if self.request.get('output_name'): t['location'] = self.output_dir + '/' + self.request['output_name'] + '.sql'
            else: t['location'] = self.output_dir + '/gminer_' + self.__class__.__name__  + '.sql'
            t['obj']      = new(t['location'], 'sql', t['kind'], t['name'])
        ##### Output meta track #####
        for t in self.output_tracks:
            t['obj'].meta_track = {'datatype': t['kind'], 'name': t['name'], 'created_by': __package__}
        ##### Output meta chr #####
        self.chrmeta = []
        for chrom in self.chrs: self.chrmeta.append({'name': chrom, 'length': max([m['length'] for n in self.input_tracks for m in n['obj'].meta_chr if m['length'] and m['name'] == chrom])})
        for t in self.output_tracks: t['obj'].meta_chr = self.chrmeta
        ##### Output fields #####
        for t in self.output_tracks:
            if type(t['fields']) == dict:
                if t['fields'].has_key('same'): t['fields'] = self.input_tracks[t['fields']['same']]['fields']
        self.chrmeta = []
        for chrom in self.chrs: self.chrmeta.append({'name': chrom, 'length': max([m['length'] for n in self.input_tracks for m in n['obj'].meta_chr if m['length'] and m['name'] == chrom])})
        for t in self.output_tracks: t['obj'].meta_chr = self.chrmeta
        ##### Run it #####
        # Several outputs #
        if len(self.output_tracks) > 1: raise NotImplementedError
        # Only one output track #
        T = self.output_tracks[0]
        for chrom in self.chrs:
            kwargs = base_kwargs.copy()
            for t in self.input_by_chrom:
                kwargs[t['name']] = getattr(self, 'get_parameter_' + t['type'])(chrom)
            for t in self.input_tracks:
                if type(t['name']) != list:
                    kwargs[t['name']] = t['obj'].read(chrom, t['fields'])
                else:
                    for n in t['name']: kwargs[n] = t['obj'].read(chrom, t['fields'], cursor=True)
            T['obj'].write(chrom, self(**kwargs), T['fields'])
        self.output_tracks[0]['obj'].unload()
        return [t['location'] for t in self.output_tracks]

#############################################################################################
# Submodules #
from .basic import *
from .standard import *
from .scores import *
from .boolean import *

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

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
