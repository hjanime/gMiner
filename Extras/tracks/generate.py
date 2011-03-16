'''
This script will generate a few collections of tracks usefull for testing and validation. 
'''

# Modules #
import os, sys, random, tempfile

# gMiner #
import gMiner
import gMiner.gm_tracks as gm_tra
import gMiner.gm_common as gm_com
from gMiner.gm_constants import *

# Tracks should better be local for speed #
if os.environ.has_key('GMINER_TRACKS'): gm_tracks_path = os.environ['GMINER_TRACKS'] 
else:                                   gm_tracks_path = gm_path + '/../Extras/tracks/'

# Various variables #
fields1 = ['start', 'end', 'name', 'score', 'strand']
fields2 = ['start', 'end', 'score']

# Every collection of tracks #
gm_track_collections = {
    'Validation': {
        'Validation 1':             {'orig_path': gm_tracks_path + 'qual/bed/validation1.bed', 'type': 'qualitative', 'fields': fields1},
        'Validation 2':             {'orig_path': gm_tracks_path + 'qual/bed/validation2.bed', 'type': 'qualitative', 'fields': fields1},
        'Validation 3':             {'orig_path': gm_tracks_path + 'qual/bed/validation3.bed', 'type': 'qualitative', 'fields': fields1},
    },
    'Yeast': {
        'All S. cer. genes (UCSC)': {'orig_path': gm_tracks_path + 'qual/bed/all_yeast_genes.bed',   'type': 'qualitative', 'fields': fields1},
        'Ribi genes':               {'orig_path': gm_tracks_path + 'qual/gff/ribosome_genesis.gff',  'type': 'qualitative', 'fields': fields1},
        'RP genes':                 {'orig_path': gm_tracks_path + 'qual/gff/ribosome_proteins.gff', 'type': 'qualitative', 'fields': fields1},
    },
    'Scores': {
        'Scores 1':                 {'orig_path': gm_tracks_path + 'quan/wig/scores1.wig', 'type': 'qualitative', 'fields': fields2},
        'Scores 2':                 {'orig_path': gm_tracks_path + 'quan/wig/scores2.wig', 'type': 'qualitative', 'fields': fields2},
        'Scores 3':                 {'orig_path': gm_tracks_path + 'quan/wig/scores3.wig', 'type': 'qualitative', 'fields': fields2},
    },
}

# Conversion #
print gm_terminal_colors['bldylw'] + "    Starting test tracks creation:" + gm_terminal_colors['end']
for _, collection in sorted(gm_track_collections.items()):
    for track, __ in sorted(collection.items()):
        print gm_terminal_colors['txtylw'] + "Creating track '" + track + "'" + gm_terminal_colors['end']
        # New path #
        old_path = collection[track]['orig_path']
        old_name = old_path.split('/')[-1]
        new_dir  = '/'.join(old_path.split('/')[:-2]) + '/' + 'sql' + '/'
        new_name = '.'.join(old_name.split('.')[:-1]  + ['sql'])
        new_path = new_dir + new_name
        collection[track]['location'] = new_path        
        if os.path.exists(new_path): os.remove(new_path)
        # Conversion #
        old_track  = gm_tra.gmTrack.Factory({'location': old_path, 'name': track})
        new_format = 'sql'
        new_name   = track
        new_type   = collection[track]['type']
        gm_tra.gmTrackConverter.convert(old_track, new_path, new_format, new_type, new_name)
        # Loading #
        fields = collection[track]['fields']
        track_obj = gm_tra.gmTrack.Factory({'location': new_path, 'name': track}, 0, True) 
        collection[track]['track'] = track_obj
        data = list(getattr(track_obj, 'get_data_' + new_type[0:4])({'type':'chr', 'chr':'chr1'}, fields))
        collection[track]['data'] = data
        # Name #
        collection[track]['name'] = track

# Extra collections #
gm_track_collections['Random'] = {}
gm_random  = gm_com.import_module('gm_random_track', gm_path + '/../Extras/scripts/')
for num in [1,2,3,4]:
    new_format = 'sql'
    new_type = 'qualitative'
    new_name = 'Test random track ' + str(num)
    print gm_terminal_colors['txtylw'] + "Creating track '" + new_name + "'" + gm_terminal_colors['end']
    chrsuffix = 'Awfully super extra long chromosome denomination string '
    old_track = gm_random.gmRandomTrack(1000.0*(float(num)/2.0), chrsuffix)
    new_path = gm_tracks_path + 'qual/sql/' + 'random' + str(num) + '.sql'
    if os.path.exists(new_path): os.remove(new_path)
    # Variables #
    gm_track_collections['Random'][new_name] = {}
    gm_track_collections['Random'][new_name]['location'] = new_path
    gm_track_collections['Random'][new_name]['type']     = new_type 
    gm_track_collections['Random'][new_name]['fields']   = fields1 
    # Conversion #
    gm_tra.gmTrackConverter.convert(old_track, new_path, new_format, new_type, new_name)
    # Name #
    gm_track_collections['Random'][new_name]['name'] = new_name
