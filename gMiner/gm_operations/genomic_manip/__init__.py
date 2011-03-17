# General modules #
import sys

# Modules #
from ... import gm_parsing   as gm_par
from ... import gm_errors    as gm_err
from ... import gm_tracks    as gm_tra
from ... import gm_common    as gm_com
from ...gm_constants import *

############################################################################################# 
class gmManipulation(object):
    def check(self):
        pass

    def output_chromosomes(self):
        pass

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

#############################################################################################
# Submodules #
from .standard import *
from .scores import *
 
# Main object #
class gmOperation(object):
    def __init__(self, req, trks):
        # Global variables #
        global request, tracks
        # Other variables #
        self.type = 'genomic_manip'
        request = req
        tracks = trks
    
    def prepare(self):
        # Global variables #
        global request, tracks
        # Manipulation specified #
        if not gm_par.exists_in_dict(request, 'manipulation'):
            raise gm_err.gmError(400, "There does not seem to be a manipulation specified in the request")
        # Location specified #
        if not gm_par.exists_in_dict(request, 'output_location'):
            raise gm_err.gmError(400, "There does not seem to be an output location specified in the request")
        # Manipulation is a gmManipulation #
        try:
            if not issubclass(globals()[request['manipulation']], gmManipulation):
                raise gm_err.gmError(400, "The specified manipulation '" + request['manipulation'] + "' is not a manipulation.")
        except KeyError:
            raise gm_err.gmError(400,     "The specified manipulation '" + request['manipulation'] + "' does not exist.")
        except TypeError:
            raise gm_err.gmError(400,     "The specified manipulation '" + request['manipulation'] + "' is a speical object in python.")
        # Get the manipulation #
        self.manip = globals()[request['manipulation']]()
        # Manipulation methods # 
        self.manip.check()
        self.manip.output_chromosomes()
        self.manip.output_metadata()
        self.manip.output_names()
        self.manip.output_fields()
        self.manip.output_tracks()
    
    def run(self):
        # Do it # 
        self.mani_fn.run()
        # Report success # 
        return 200, "Manipulation succeded", "text/plain"
