# Modules #
import os, sys, random, tempfile

# gMiner Modules #
from .. import gm_common as gm_com
from .. import gm_tracks as gm_tra
from ..gm_constants import *
import gm_random_track as gm_random

# Tracks should better be local for speed #
if os.environ.has_key('GMINER_TRACKS'): gm_tracks_path = os.environ['GMINER_TRACKS'] 
else:                                   gm_tracks_path = gm_path + '/../Extras/tracks/'

# Every collection of tracks #
gm_track_collections = {
    'Validation': {
        'Validation 1': {'orig_path': gm_tracks_path + 'qual/bed/validation1.bed', 'type': 'qualitative', 'fields': gm_qualitative_fields[:4]},
        'Validation 2': {'orig_path': gm_tracks_path + 'qual/bed/validation2.bed', 'type': 'qualitative', 'fields': gm_qualitative_fields},
        'Validation 3': {'orig_path': gm_tracks_path + 'qual/bed/validation3.bed', 'type': 'qualitative', 'fields': gm_qualitative_fields},
    },
    'Yeast': {
        'All genes':  {'orig_path': gm_tracks_path + 'qual/bed/all_yeast_genes.bed',   'type': 'qualitative', 'fields': gm_qualitative_fields},
        'Ribi genes': {'orig_path': gm_tracks_path + 'qual/bed/ribosome_genesis.bed',  'type': 'qualitative', 'fields': gm_qualitative_fields},
        'RP genes':   {'orig_path': gm_tracks_path + 'qual/bed/ribosome_proteins.bed', 'type': 'qualitative', 'fields': gm_qualitative_fields},
    },
    'Scores': {
        'Scores 1': {'orig_path': gm_tracks_path + 'quan/wig/scores1.wig', 'type': 'quantitative', 'fields': gm_quantitative_fields},
        'Scores 2': {'orig_path': gm_tracks_path + 'quan/wig/scores2.wig', 'type': 'quantitative', 'fields': gm_quantitative_fields},
        'Scores 3': {'orig_path': gm_tracks_path + 'quan/wig/scores3.wig', 'type': 'quantitative', 'fields': gm_quantitative_fields},
        'Scores 4': {'orig_path': gm_tracks_path + 'quan/wig/scores4.wig', 'type': 'quantitative', 'fields': gm_quantitative_fields},
    },
}

# The chromosome length info #
yeast_chr_file = gm_tracks_path + 'chr/yeast.chr'
 
# The parser test files #
gm_parser_tests  = [(path + b, True)  for path in [gm_tracks_path + 'qual/bed/should_pass/'] for b in os.listdir(path) if b.endswith(".bed")]
gm_parser_tests += [(path + b, False) for path in [gm_tracks_path + 'qual/bed/should_fail/'] for b in os.listdir(path) if b.endswith(".bed")]
gm_parser_tests += [(path + w, True)  for path in [gm_tracks_path + 'quan/wig/should_pass/'] for w in os.listdir(path) if w.endswith(".wig")]
gm_parser_tests += [(path + w, False) for path in [gm_tracks_path + 'quan/wig/should_fail/'] for w in os.listdir(path) if w.endswith(".wig")]


#############################################################################################
def generate_tracks(rebuild=True):
    '''
    This function will generate a few collections of tracks usefull for testing and validation. 
    '''

    # Conversion #
    if rebuild: print gm_terminal_colors['bldylw'] + "    Starting test tracks creation in " + gm_tracks_path + gm_terminal_colors['end']
    for _, collection in sorted(gm_track_collections.items()):
        for track, __ in sorted(collection.items()):
            if rebuild: print gm_terminal_colors['txtylw'] + "Creating track '" + track + "'" + gm_terminal_colors['end']
            # New path #
            old_path = collection[track]['orig_path']
            old_name = old_path.split('/')[-1]
            new_dir  = '/'.join(old_path.split('/')[:-2]) + '/' + 'sql' + '/'
            new_name = '.'.join(old_name.split('.')[:-1]  + ['sql'])
            new_path = new_dir + new_name
            collection[track]['location'] = new_path        
            if rebuild and os.path.exists(new_path): os.remove(new_path)
            # Old track #
            old_track  = gm_tra.gmTrack.Factory({'location': old_path, 'name': track, 'chrs': yeast_chr_file}, conversion=False)
            collection[track]['old_track'] = old_track
            # Conversion #
            new_format = 'sql'
            new_name   = track
            new_type   = collection[track]['type']
            fields     = collection[track]['fields']
            if rebuild: gm_tra.gmTrackConverter.convert(old_track, new_path, new_format, new_type, new_name)
            # Loading #
            track_obj = gm_tra.gmTrack.Factory({'location': new_path, 'name': track}, 0, True) 
            collection[track]['track'] = track_obj
            # Data #
            collection[track]['data'] = {}
            for chr in track_obj.all_chrs:
                collection[track]['data'][chr] = list(getattr(track_obj, 'get_data_' + new_type[0:4])({'type':'chr', 'chr':chr}, fields))
            # Name #
            collection[track]['name'] = track

#############################################################################################
def generate_random_tracks(rebuild=True):
    # Extra collections #
    gm_track_collections['Random'] = {}
    #gm_random  = gm_com.import_module('gm_random_track', gm_path + '/../Extras/scripts/')
    for num in [1,2,3,4]:
        new_format = 'sql'
        new_type = 'qualitative'
        new_name = 'Test random track ' + str(num)
        if rebuild: print gm_terminal_colors['txtylw'] + "Creating track '" + new_name + "'" + gm_terminal_colors['end']
        chrsuffix = 'Awfully super extra long chromosome denomination string '
        old_track = gm_random.gmRandomTrack(1000.0*(float(num)/2.0), chrsuffix)
        new_path = gm_tracks_path + 'qual/sql/' + 'random' + str(num) + '.sql'
        if rebuild and os.path.exists(new_path): os.remove(new_path)
        # Variables #
        gm_track_collections['Random'][new_name] = {}
        gm_track_collections['Random'][new_name]['location'] = new_path
        gm_track_collections['Random'][new_name]['type']     = new_type 
        gm_track_collections['Random'][new_name]['fields']   = gm_qualitative_fields 
        # Conversion #
        if rebuild: gm_tra.gmTrackConverter.convert(old_track, new_path, new_format, new_type, new_name)
        # Name #
        gm_track_collections['Random'][new_name]['name'] = new_name

#############################################################################################
#generate_tracks()
generate_tracks(rebuild=False)
