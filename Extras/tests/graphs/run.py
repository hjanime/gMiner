'''
This script will genereate almost every possible graph. 
'''

# Modules #
import os, sys

# gMiner #
import gMiner
from gMiner.gm_constants import *

# Tracks should better be local #
tracks_path = gm_path + '/../Extras/tracks/'
sql_path = tracks_path + 'qual/sql/'

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


# Every collection of data
collections = {
    'Yeast':      gm_path + '/../Extras/tests/graphs/collections/gm_col_yeast.py',
    'Validation': gm_path + '/../Extras/tests/graphs/collections/gm_col_validation.py',
    'Random':     gm_path + '/../Extras/tests/graphs/collections/gm_col_random.py',
}

# Count how many graphs we will make #
max_count = 2*2*2*2*4
max_count -= max_count/4 
max_count *= len(collections) 
count = 1

# Main loops #
for col_name, col_path in collections.items():
    print "Starting collection: " + col_name
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
                        print "Graph " + str(count) + " out of " + str(max_count) + "   (" + name + ")"
                        count += 1
                        # Making the request #
                        request = '[gMiner]'
                        request += '\n' + 'version=0.1.5'
                        request += '\n' + 'gm_encoding=image/png'
                        request += '\n' + 'operation_type=desc_stat'
                        request += '\n' + 'characteristic=' + chara 
                        if b_many:
                            request += '\n' + 'track1=' + track_set['many'][1] 
                            request += '\n' + 'track1_name=' + make_track_name(track_set['many'][1])
                            request += '\n' + 'track2=' + track_set['many'][2] 
                            request += '\n' + 'track2_name=' + make_track_name(track_set['many'][2]) 
                            request += '\n' + 'track3=' + track_set['many'][3] 
                            request += '\n' + 'track3_name=' + make_track_name(track_set['many'][3])
                        else:
                            request += '\n' + 'track1=' + track_set['single'] 
                            request += '\n' + 'track1_name=' + make_track_name(track_set['single']) 
                        if b_sel:
                            request += '\n' + 'selected_regions=' + request_selection_string
                        if b_chr: 
                            request += '\n' + 'per_chromosome=True' 
                        if b_comp: 
                            request += '\n' + 'compare_parents=True'
                        # Executing the request #
                        req = gMiner.gmRequest(request, True)
                        error, result, type = req.prepare()
                        error, result, type = req.run()
                        # Write the result #
                        result_file = open(result_path + name + '.png', 'w')
                        result_file.write(result)
                        result_file.close()
