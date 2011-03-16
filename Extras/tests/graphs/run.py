'''
This script will genereate almost every possible graph with the desc_stat module. 
'''

# Modules #
import os, sys

# gMiner #
import gMiner
from gMiner.gm_constants import *

# Generate test tracks #
execfile(gm_path + '/../Extras/tracks/generate.py')

# Every collection of data
collections = {
    'Validation': gm_path + '/../Extras/tests/graphs/collections/gm_col_validation.py',
    'Yeast':      gm_path + '/../Extras/tests/graphs/collections/gm_col_yeast.py',
    'Random':     gm_path + '/../Extras/tests/graphs/collections/gm_col_random.py',
}

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

# Where are the files written to ? #
result_path = '/tmp/gMiner/'

# Count how many graphs we will make #
max_count = 2*2*2*2*4
max_count -= max_count/4 
max_count *= len(collections) 
count = 1

# Main loops #
print gm_terminal_colors['bldylw'] + "    Writing graphs in: " + result_path + gm_terminal_colors['end']
for col_name, col_path in collections.items():
    execfile(col_path)
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
                        print gm_terminal_colors['txtylw'] + "Graph " + str(count) + " out of " + str(max_count) + "   (" + name + ")" + gm_terminal_colors['end']
                        count += 1
                        # Making the request #
                        request = {}
                        request['gm_encoding'] = 'image/png'
                        request['operation_type'] = 'desc_stat'
                        request['characteristic'] = chara 
                        if b_many:
                            request['track1'] = track_set['many'][1]['location'] 
                            request['track1_name'] = make_track_name(track_set['many'][1]['name'])
                            request['track2'] = track_set['many'][2]['location'] 
                            request['track2_name'] = make_track_name(track_set['many'][2]['name']) 
                            request['track3'] = track_set['many'][3]['location'] 
                            request['track3_name'] = make_track_name(track_set['many'][3]['name'])
                        else:
                            request['track1'] = track_set['single']['location'] 
                            request['track1_name'] = make_track_name(track_set['single']['name']) 
                        if b_sel:
                            request['selected_regions'] = request_selection_string
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
