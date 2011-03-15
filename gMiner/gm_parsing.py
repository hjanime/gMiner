# Sub modules #
from . import gm_errors as gm_err
from . import gm_constants
from .gm_constants import *

###########################################################################
def parse_request(request_file): 
    import ConfigParser
    config = ConfigParser.ConfigParser()

    # Try to read it #
    try:
        config.readfp(request_file)
    except ConfigParser.MissingSectionHeaderError as err:
        raise gm_err.gmError(400, "The request file does not seem to be valid. It does not start with a proper header.", err)

    # Check for prog name #
    if not config.has_section(gm_project_name):
        raise gm_err.gmError(400, "The request file does not seem to be valid. It does not start with [" + gm_project_name + "].")
    
    # Check for version number #
    for i, num in enumerate(config.get(gm_project_name, "version").split('.')):
        if num > gm_project_version.split('.')[i]:
            raise gm_err.gmError(400, "The request file has a version number higher than this current installation of " + gm_project_name + ".")
        if num < gm_project_version.split('.')[i]:
            break

    # Return everything #
    return dict(config.items(gm_project_name))


def parse_tracks(request_dict):
    '''
    >>> parse_tracks({'track1': 'aa', 'track1_name': 'ff'})
    [{'location': 'aa', 'name': 'ff'}]
    '''

    # Number of tracks #
    if 'track1' not in request_dict:
        raise gm_err.gmError(400, "No tracks have been specified in the request")
    number_of_tracks_sent = 1
    while request_dict.has_key("track" + str(number_of_tracks_sent + 1)):
        number_of_tracks_sent += 1

    # Make a dictionary #
    try:
        return [dict([['location',request_dict['track'+str(num)]],['name',request_dict['track'+str(num)+'_name']]]) for num in range(1,number_of_tracks_sent+1)]
    except KeyError as err: 
        raise gm_err.gmError(400, "Every track specified must have a name associated", err)

###########################################################################
def parse_regions(request):
    '''
    >>> d = {'selected_regions': 'chr1:0:9;chr2:333:55555'}
    >>> parse_regions(d)
    >>> d
    {'selected_regions': [{'start': 0, 'chr': 'chr1', 'end': 9}, {'start': 333, 'chr': 'chr2', 'end': 55555}]}
    '''
    default_if_none(request, 'selected_regions')
    if request['selected_regions']:
        try: 
            request['selected_regions'] = [dict([['chr',p[0]],['start',int(p[1])],['end',int(p[2])]]) for p in [r.split(':') for r in request['selected_regions'].split(';')]]
        except ValueError as err:
            raise gm_err.gmError(400, "The selected regions are not properly formated.", err)
        except IndexError as err:
            raise gm_err.gmError(400, "The selected regions are not properly formated.", err)
        
def parse_chrlist(request):
    '''
    >>> d = {'wanted_chromosomes': 'chr1;chr2;chr9'}
    >>> parse_chrlist(d)
    >>> d
    {'wanted_chromosomes': ['chr1', 'chr2', 'chr9']}
    '''
    default_if_none(request, 'wanted_chromosomes')    
    if request['wanted_chromosomes']:
        request['wanted_chromosomes'] = [c for c in request['wanted_chromosomes'].split(';')]

def default_if_none(dict, key, default=False):
    if not (dict.has_key(key) and dict[key] != ''): dict[key] = default

def convert_to_bool(dict, key):
    dict[key] = dict[key] in [True, 'True', 'true', '1', 'y', 'yes', 'on']

def exists_in_dict(dict, key):
    if dict.has_key(key):
        if dict[key] != '': return True
    return False

def assert_is_type(var, type, name):
    if not isinstance(var, type):
        raise gm_err.gmError(400, "The '" + name + "' variable does not seem to be of type '" + type.__name__ + "'.") 

def assert_has_method(object, attribute):
    if not hasattr(object, attribute):
        raise gm_err.gmError(400, "The '" + object.__name__ + "' object does not seem to have '" + attribute + "'.")

def assert_is_among(var, list, name):
    if var not in list:
        raise gm_err.gmError(400, "The '" + name + "' variable does not seem to be any of the following possibilites: " + str(list) + ".")
        

