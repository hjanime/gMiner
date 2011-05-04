'''
This module will genereate almost every possible graph with the desc_stat module. 
'''

# General modules #
import os, sys, tempfile

# Other modules #
from bbcflib.track import Track
from bbcflib.track.test_variables import track_collections

# Internal modules #
import gMiner
from ...constants import *

# A naming convention dictonary #
name_dict = {
    True: {
        True:  {True: 'H', False: 'D'},
        False: {True: 'G', False: 'C'},
    },
    False: {
        True:  {True: 'F', False: 'B'},
        False: {True: 'E', False: 'A'},
    }
}

# An other naming dictionary #
chara_dict = {
    'number_of_features': '_Count',
    'base_coverage': '_Base',
    'length': '_Length',
    'score': '_Score',
}

# An invented chromosome name #
chrsuffix = 'Awfully super extra long chromosome denomination string '
request_selection_regions = ['1:0:50000','2:50000:9999999999999']

# Two name generating functions #
def make_track_name_path(path): 
    return path.split('/')[-1]
def make_track_name_random(path): 
    name_gen = tempfile._RandomNameSequence()
    return ' '.join([name_gen.next() for x in range(10)]) + ' ' + path.split('/')[-1] 

# Every collection of data #
collections = {
    'Validation': {
        'track_set': {
            'single': track_collections['Validation'][1],
            'many': {
                1: track_collections['Validation'][1],
                2: track_collections['Validation'][2],
                3: track_collections['Validation'][3],
        }},
        'request_selection_string': 'chr1:0:30;chr1:122:126',
        'track_name_fn': make_track_name_path
    },
    'Yeast': {
        'track_set': {
            'single': track_collections['Yeast']['All genes'],
            'many': {
                1: track_collections['Yeast']['All genes'],
                2: track_collections['Yeast']['Ribi genes'],
                3: track_collections['Yeast']['RP genes'],
        }},
        'request_selection_string': 'chr1:0:50000;chr1:52000:54000;chr1:56000:58000;chr2:50000:9999999999999',
        'track_name_fn': make_track_name_path
    },
    'Random': {
        'track_set': {
            'single': track_collections['Random'][1],
            'many': {
                1: track_collections['Random'][2],
                2: track_collections['Random'][3],
                3: track_collections['Random'][4],
        }},
        'request_selection_string': ';'.join([chrsuffix + r for r in request_selection_regions]),
        'track_name_fn': make_track_name_random
    },
}

# Main loops #
def run(result_path='/tmp/gMiner/'):
    if not os.path.isdir(result_path):
        raise Exception("The result location specified is not a directory")
    max_count = 2*2*2*2*4
    max_count -= max_count/4 
    max_count *= len(collections) 
    count = 1
    print gm_terminal_colors['bldylw'] + "    Writing graphs in: " + result_path + gm_terminal_colors['end']
    for col_name, col in collections.items():
        for b_many in [True, False]:
            for b_sel in [True, False]:
                for b_comp in [True, False]:
                    for b_chr in [True, False]:
                        for chara in chara_dict.keys():
                            # Preparation #
                            if not b_sel and b_comp: continue
                            name = col_name + '_'
                            name = name + name_dict[b_comp][b_chr][b_many]
                            name = name + chara_dict[chara]
                            if not b_sel: name += '_NoSel'
                            print gm_terminal_colors['txtylw'] + "Graph " + str(count) + " out of " + str(max_count) + \
                            "   " + gm_terminal_colors['txtpur'] + name + gm_terminal_colors['end']
                            count += 1
                            # Making the request #
                            request = {}
                            request['gm_encoding'] = 'image/png'
                            request['operation_type'] = 'desc_stat'
                            request['characteristic'] = chara 
                            if b_many:
                                request['track1'] = col['track_set']['many'][1]['path_sql'] 
                                request['track1_name'] = col['track_name_fn'](col['track_set']['many'][1]['name'])
                                request['track2'] = col['track_set']['many'][2]['path_sql'] 
                                request['track2_name'] = col['track_name_fn'](col['track_set']['many'][2]['name']) 
                                request['track3'] = col['track_set']['many'][3]['path_sql'] 
                                request['track3_name'] = col['track_name_fn'](col['track_set']['many'][3]['name'])
                            else:
                                request['track1'] = col['track_set']['single']['path_sql'] 
                                request['track1_name'] = col['track_name_fn'](col['track_set']['single']['name']) 
                            if b_sel:
                                request['selected_regions'] = col['request_selection_string']
                            if b_chr: 
                                request['per_chromosome'] = 'True' 
                            if b_comp: 
                                request['compare_parents'] = 'True'
                            # Executing the request #
                            result = gMiner.run(**request)
                            # Write the result #
                            result_file = open(result_path + name + '.png', 'w')
                            result_file.write(result)
                            result_file.close()

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
