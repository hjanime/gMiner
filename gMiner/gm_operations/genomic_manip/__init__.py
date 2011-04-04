# General modules #
import sys, os

# Modules #
from ... import gm_parsing   as gm_par
from ... import gm_errors    as gm_err
from ... import gm_tracks    as gm_tra
from ... import gm_common    as gm_com
from ...gm_constants import *

############################################################################################# 
class gmManipulation(object):
    def __init__(self, request=None, tracks=None):
        self.request = request
        self.req_tracks = tracks

    def check(self):
        # Location specified #
        if len(self.output_tracks) > 0:
            if not gm_par.exists_in_dict(self.request, 'output_location'):
                raise gm_err.gmError(400, "There does not seem to be an output location specified in the request")
        # Location is a directory #
        self.output_dir = self.request['output_location'].rstrip('/')
        if not os.path.isdir(self.output_dir):
            raise gm_err.gmError(400, "The output location specified is not a directory")

    def make_input_tracks(self):
        # Number of tracks #
        if not 'list of tracks' in [t['type'] for t in self.input_tracks]:
            if len(self.input_tracks) != len(self.req_tracks):
                raise gm_err.gmError(400, "The number of tracks inputed does not suit the manipulation requested")
        # Find tracks #
        for t in self.input_tracks:
            if t['type'] == 'list of tracks':
                tracks = []
                for i in xrange(len(self.req_tracks) - 1, -1, -1):
                    if track_matches_desc(self.req_tracks[i], t):
                        tracks.append(self.req_tracks[i])
                        self.req_tracks.pop(i)
                if tracks: t['obj'] = gm_tra.gmTrackCollection(tracks)
            else: 
                for req_t in self.req_tracks:
                    if track_matches_desc(req_t, t):
                        t['obj'] = req_t
                        self.req_tracks.remove(req_t)
                        break
            if not t.has_key('obj'): raise gm_err.gmError(400, "A required track for the manipulation " + self.request['manipulation'] + " is missing." + " You should include a " + t['kind'] + " track with at least the following fields: " + str(t['fields']))
        # Check all used #
        if not self.req_tracks == []: raise gm_err.gmError(400, "You provided too many tracks for the manipulation " + self.request['manipulation'] + ". The track '" + self.req_tracks[0].name + "' was not used.")

    def make_input_other(self):
        for t in self.input_other:
            if not gm_par.exists_in_dict(self.request, t['key']):
                raise gm_err.gmError(400, "A required parameter for the manipulation " + self.request['manipulation'] + " is missing." + " You should include a '" + t['key'] + "' paramater that must be of type: " + t['type'].__name__)
            try:
                t['value'] = t['type'](self.request[t['key']])
            except ValueError as err:
                raise gm_err.gmError(400, "The '" + t['key'] + "' parameter is not of type: " + t['type'].__name__, err)

    def make_output_chromosomes(self):
        self.chrs = self.chr_collapse([t['obj'].chrs for t in self.input_tracks])

    def make_output_tracks(self):
        for t in self.output_tracks:
            t['name']     = self.__doc__ + ' on ' + gm_com.andify_strings([track['obj'].name for track in self.input_tracks])
            t['location'] = self.output_dir + '/gminer_' + self.__class__.__name__  + '.sql' 
            t['obj']      = gm_tra.gmTrack.new(t['location'], 'sql', t['kind'], t['name'])
            t['obj'].write_meta_data({'name': t['name']})

    def make_output_metadata(self):
        self.chrmeta = []
        for chr in self.chrs: self.chrmeta.append({'name': chr, 'length': max([m['length'] for n in self.input_tracks for m in n['obj'].chrmeta if m['length'] and m['name'] == chr])})
        for t in self.output_tracks: t['obj'].write_chr_meta(self.chrmeta)

    def get_special_parameter_stop_val(self, chr_name):
        for chr in self.chrmeta:
            if chr['name'] == chr_name: return chr['length']

    def execute(self):
        # Several outputs #
        if len(self.output_tracks) > 1: raise NotImplementedError
        # Only one output track #
        T = self.output_tracks[0] 
        for chr in self.chrs:
            kwargs = {}
            for t in self.input_tracks:
                kwargs[t['name']] = getattr(t['obj'], 'get_data_' + t['kind'][:4])({'type': 'chr','chr': chr}, t['fields'])
            for t in self.input_extras:
                kwargs[t['name']] = getattr(self, 'get_special_parameter_' + t['type'])(chr)
            for t in self.input_other:
                kwargs[t['name']] = t['value']
            getattr(T['obj'], 'write_' + T['kind'][:4])(chr, self.generate(**kwargs), T['fields'])

    def finalize(self):
        self.output_tracks[0]['obj'].unload()

    def chr_collapse(self, *args):
        return gm_com.gmCollapse.by_appending(*args)

#-------------------------------------------------------------------------------------------#   
def track_matches_desc(track, dict):
    if track.type        != dict['kind']:       return False
    if set(track.fields) < set(dict['fields']): return False
    return True

#############################################################################################
# Submodules #
from .standard import *
from .scores import *
 
# Main object #
class gmOperation(object):
    def __init__(self, request, tracks):
        # Other variables #
        self.type = 'genomic_manip'
        self.request = request
        self.tracks = tracks
    
    def prepare(self):
        # Manipulation specified #
        if not gm_par.exists_in_dict(self.request, 'manipulation'):
            raise gm_err.gmError(400, "There does not seem to be a manipulation specified in the request")
        # Manipulation is a gmManipulation #
        try:
            if not issubclass(globals()[self.request['manipulation']], gmManipulation):
                raise gm_err.gmError(400, "The specified manipulation '" + self.request['manipulation'] + "' is not a manipulation.")
        except KeyError:
            raise gm_err.gmError(400,     "The specified manipulation '" + self.request['manipulation'] + "' does not exist.")
        except TypeError:
            raise gm_err.gmError(400,     "The specified manipulation '" + self.request['manipulation'] + "' is a speical object in python.")
        # Get the manipulation #
        self.manip = globals()[self.request['manipulation']](self.request, self.tracks)
        # Call manip methods #
        self.manip.check()
        self.manip.make_input_tracks()
        self.manip.make_input_other()
        self.manip.make_output_chromosomes()
        self.manip.make_output_tracks()
        self.manip.make_output_metadata()
    
    def run(self):
        # Call manip methods #
        self.manip.execute()
        self.manip.finalize()
        # Report success # 
        return 200, [t['location'] for t in self.manip.output_tracks] , "text/plain"
