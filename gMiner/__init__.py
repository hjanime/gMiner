b'This module needs Python 2.6 or later.'

# General modules #
import os
from contextlib import nested

# Other modules #
from bbcflib.track import Track

# Internal modules #
from constants import *
from . import operations

# Current version #
__version__ = gm_project_version

# Current path #
try:
    gm_path = __path__[0]
except NameError:
    gm_path = 'gMiner'

###########################################################################
def run(**request):
    # Import the correct operation #
    if not hasattr(operations, request['operation_type']):
        try:
            __import__('gMiner.operations.' + request['operation_type'])
        except ImportError:
            raise Exception("The operation " + request['operation_type'] + " is not supported.")
    run_op = getattr(operations, request['operation_type']).run
    # Mandatory request variables #
    if not request.get('output_location'):
        raise Exception("There does not seem to be an output location specified in the request")
    output_dir = request['output_location'].rstrip('/')
    if not os.path.isdir(output_dir):
        raise Exception("The output location specified is not a directory")
    # Optional request variables #
    request['selected_regions']   = request.get('selected_regions', '')
    parse_regions(request)
    request['wanted_chromosomes'] = request.get('wanted_chromosomes', '')
    parse_chrlist(request)
    # Prepare the tracks #
    track_dicts = parse_tracks(request)
    contexts = [Track(t['path'], name=t['name'], chrmeta=t.get('chrs'), readonly=True) for t in track_dicts]
    with nested(*contexts) as tracks:
        # Assign numbers #
        for i, t in enumerate(tracks): t.number = i
        # Determine final chromosome list #
        if request['wanted_chromosomes']:
            for track in tracks: track.chrs = (set(track.all_chrs) & set(request['wanted_chromosomes']))
        else:
            for track in tracks: track.chrs = track.all_chrs
        # Run it #
        return run_op(request, tracks, output_dir)

###########################################################################
def parse_tracks(request_dict):
    '''
    >>> parse_tracks({'track1': 'aa', 'track1_name': 'ff', 'track1_chrs': 'bb'})
    [{'path': 'aa', 'chrs': 'bb', 'name': 'ff'}]
    '''

    # Number of tracks #
    if 'track1' not in request_dict:
        raise Exception("No tracks have been specified in the request")
    number_of_tracks_sent = 1
    while request_dict.has_key("track" + str(number_of_tracks_sent + 1)):
        number_of_tracks_sent += 1
    # Make a list of dictionaries #
    try:
        tracks = [dict([['path',request_dict['track'+str(num)]],['name',request_dict['track'+str(num)+'_name']]]) for num in range(1,number_of_tracks_sent+1)]
    except KeyError:
        raise Exception("Every track specified must have a name associated")
    # Chromosome info #
    for i, track in enumerate(tracks):
        if request_dict.has_key("track" + str(i+1) + '_chrs'):
            track['chrs'] = request_dict["track" + str(i+1) + '_chrs']
    return tracks

def parse_regions(request):
    '''
    >>> d = {'selected_regions': 'chr1:0:9;chr2:333:55555'}
    >>> parse_regions(d)
    >>> d
    {'selected_regions': [{'start': 0, 'chr': 'chr1', 'end': 9}, {'start': 333, 'chr': 'chr2', 'end': 55555}]}
    '''
    if os.path.exists(request['selected_regions']): return
    if request['selected_regions']:
        try:
            request['selected_regions'] = [dict([['chr',p[0]],['start',int(p[1])],['end',int(p[2])]]) for p in [r.split(':') for r in request['selected_regions'].split(';')]]
        except ValueError, IndexError:
            raise Exception("The selected regions are not properly formated.")

def parse_chrlist(request):
    '''
    >>> d = {'wanted_chromosomes': 'chr1;chr2;chr9'}
    >>> parse_chrlist(d)
    >>> d
    {'wanted_chromosomes': ['chr1', 'chr2', 'chr9']}
    '''
    if request['wanted_chromosomes']:
        request['wanted_chromosomes'] = [c for c in request['wanted_chromosomes'].split(';')]

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
