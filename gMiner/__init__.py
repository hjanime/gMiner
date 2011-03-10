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
def request(**kwargs):
    kwargs['service'] = gm_project_name
    kwargs['version'] = gm_project_version
    request = gmRequest(kwargs, True)
    error, result, type = request.prepare()
    error, result, type = request.run()
    return result

###########################################################################   
class gmRequest(object):
    def __init__(self, request, errors=False):
        self.errors = errors   # Do errors pass sliently or should we raise them ?
        self.request = request # The request is a dictionary of values

    def prepare(self):
        try:
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
            # Fork the execution #
            if not hasattr(op, self.request['operation_type']):
                try:
                    __import__('gMiner.gm_operations.' + self.request['operation_type'])
                except ImportError as err:
                    raise gm_err.gmError(400, "The operation " + self.request['operation_type'] + " is not supported at the moment.", err)
            self.operation = getattr(op, self.request['operation_type']).gmOperation(self.request, self.tracks)
            # Prepare the operation #
            self.operation.prepare()
         
        # Catch errors #  
        except gm_err.gmError as err:
            self.prepare_passed = False
            return self.catch_error(err)
            
        # Report success #
        self.prepare_passed = True
        return 200, 'Method prepare() done', 'text/plain'

    def run(self):
        try:
            # Check that the request was prepared #
            try:
                if not self.prepare_passed:
                    raise gm_err.gmError(400, "You tried to run a request that didn't pass the prepare phase")
            except NameError as err:
                raise gm_err.gmError(400, "You tried to run a request that hasn't yet passed the prepare phase")
           
             # Run it #
            return self.operation.run()

        # Catch errors #  
        except gm_err.gmError as err:
            self.run_passed = False
            return self.catch_error(err)

    def catch_error(self, err):
        if self.errors:
            if err.origin:
                print gm_terminal_colors['bakred'] + str(err) + gm_terminal_colors['end']
                raise err.origin
            else: raise err
        return err.code, err.msg, "text/plain"

###########################################################################
class gmListOptions(object):
    def run(self):
        return_string = ''
        module_list = ['desc_stat', 'genomic_manip']
        for module_name in module_list:
            return_string.append(module_name)
            module = __import__('gm_operations.' + module_name)
            return_string.append(module_name + "\n")
            return_string.append(module.list_options())
            return_string.append("\n\n\n")
        return 200, return_string, "text/plain"
