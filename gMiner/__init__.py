b'This module needs Python 2.6 or later.'

# Modules #
from . import gm_parsing    as gm_par
from . import gm_errors     as gm_err
from . import gm_tracks     as gm_tra
from . import gm_operations as op
from . import gm_constants
from gm_constants import *

# Current version #
__version__ = gm_project_version

# Current path #
try:
    gm_constants.gm_path = __path__[0]
except NameError:
    gm_constants.gm_path = 'gMiner'

###########################################################################   
def run(**kwargs):
    kwargs['service'] = gm_project_name
    kwargs['version'] = gm_project_version
    job = gmJob(kwargs)
    error, result, type = job.prepare_with_errors()
    error, result, type = job.run_with_errors()
    return result

###########################################################################   
class gmJob(object):
    def __init__(self, kwargs):
        self.request = kwargs
    
    @gm_err.catch_errors
    def prepare_catch_errors(self): return self.prepare()
    def prepare_with_errors(self):  return self.prepare() 
    def prepare(self):
        # Check the request file #
        gm_par.check_request(self.request)
        # Check for listing #
        if self.request['operation_type'] == 'list':
            self.operation = gmListOptions() 
            return 200, 'Listing', 'text/plain'
        # Parse the track list # 
        self.track_dict = gm_par.parse_tracks(self.request)
        # Make track objects #
        self.tracks = [gm_tra.gmTrack.Factory(track, i, True) for i, track in enumerate(self.track_dict)]
        # Standard request variables #
        gm_par.default_if_none(self.request, 'selected_regions', '')
        gm_par.parse_regions(self.request)
        gm_par.default_if_none(self.request, 'wanted_chromosomes', '')
        gm_par.parse_chrlist(self.request)
        # Determine final chromosome list #
        if self.request['wanted_chromosomes']:
            for track in self.tracks: track.chrs = (set(track.all_chrs) & set(self.request['wanted_chromosomes']))
        else:
            for track in self.tracks: track.chrs = track.all_chrs
        # Import the correct operation #
        if not hasattr(op, self.request['operation_type']):
            try:
                __import__('gMiner.gm_operations.' + self.request['operation_type'])
            except ImportError as err:
                raise gm_err.gmError(400, "The operation " + self.request['operation_type'] + " is not supported at the moment.", err)
        # Find the gmOperation object #
        self.operation = getattr(op, self.request['operation_type']).gmOperation(self.request, self.tracks)
        # Prepare the operation #
        self.operation.prepare()
        # Report success #
        return 200, 'Method prepare() done', 'text/plain'

    @gm_err.catch_errors
    def run_catch_errors(self): return self.operation.run()
    def run_with_errors(self):  return self.operation.run()
