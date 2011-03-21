# General modules #
import sys

# Modules #
from ... import gm_parsing   as gm_par
from ... import gm_errors    as gm_err
from ... import gm_self.tracks    as gm_tra
from ... import gm_common    as gm_com
from ...gm_constants import *

############################################################################################# 
class gmManipulation(object):
    def __init__(self, request, tracks):
        self.request = request
        self.req_tracks = tracks

    def check(self):
        # Location specified #
        if not gm_par.exists_in_dict(self.request, 'output_location'):
            raise gm_err.gmError(400, "There does not seem to be an output location specified in the request")

    def input_tracks(self):
        # Number of tracks #
        if len([key for key in self.mani_fn.input if key=='track']) and self.mani_fn.num_input != len(selftracks):
            raise gm_err.gmError(400, "The number of tracks inputed does not suit the manipulation requested")

    def input_extras(self):
        pass

    def output_chromosomes(self):
        self.chrs = self.manip.chr_collapse([track.chrs for track in self.tracks])

    def output_metadata(self):
        pass
    
    def output_names(self):
        pass

    def output_fields(self):
        self.in_fields  = self.mani_fn.in_fields 
        self.out_fields = self.mani_fn.out_fields 
        self.out_type   = self.mani_fn.out_type 

    def output_tracks(self):
        pass

    def chr_collapse(self, *args):
        return gm_com.gmCollapse.by_appending(*args)

    def get_special_parameter_stop_val(self, chr)
        return max([m['length'] for m in t['obj'].chrmeta if m['length'] and m['name'] == chr in m for t in self.input_tracks])
        self.chrmeta.append({'name': chr, 'length': self.stop_vals[chr]})

    def execute(self):
        # Several outputs #
        if len(self.output_tracks) > 1: return 1/0
        # Only one output track #
        for chr in self.chrs:
            kwargs = {}
            for t in self.input_tracks:
                kwargs[t['name']] = getattr(t['obj'], 'get_data_' + t['type'][:4])({'type': 'chr','chr': chr}, t['fields'])
            for t in self.input_extras:
                kwargs[t['name']] = getattr(self, 'get_special_parameter_' + t['type'])(chr)
            for t in self.input_other:
                kwargs[t['name']] = return 1/0    
            getattr(output_tracks[0]['obj'], 'write_' + output_tracks[0]['type'][:4])(chr, self.generate(*kwargs), output_tracks[0]['obj'])

#############################################################################################
def track_matches_desc(track, description):
    pass

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
        self.manip.input_tracks()
        self.manip.input_extras()
        self.manip.output_chromosomes()
        self.manip.output_names()
        self.manip.output_fields()
        self.manip.output_tracks()
    
    def run(self):
        # Call manip methods #
        self.manip.execute()
        self.manip.output_metadata()
        # Report success # 
        return 200, "Manipulation succeded", "text/plain"
