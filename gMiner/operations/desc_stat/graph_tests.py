'''
This module will genereate almost every possible graph with the desc_stat module. 
'''

# Modules #
import os, sys

# gMiner #
import gMiner
from ... import gm_errors as gm_err
from ...gm_constants import *

# Every collection of data #
collections = {
    'Validation': 'gMiner.gm_tests.gm_graphs.gm_graph_validation',
    'Yeast':      'gMiner.gm_tests.gm_graphs.gm_graph_yeast',
    'Random':     'gMiner.gm_tests.gm_graphs.gm_graph_random',
}

for col in collections:
    __import__(collections[col]) 
    collections[col] = sys.modules[collections[col]]

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

# Main loops #
def generate_graphs(result_path='/tmp/gMiner/'):
    if not os.path.isdir(result_path):
        raise gm_err.gmError(400, "The result location specified is not a directory")
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
                            print gm_terminal_colors['txtylw'] + "Graph " + str(count) + " out of " + str(max_count) + "   (" + name + ")" + gm_terminal_colors['end']
                            count += 1
                            # Making the request #
                            request = {}
                            request['gm_encoding'] = 'image/png'
                            request['operation_type'] = 'desc_stat'
                            request['characteristic'] = chara 
                            if b_many:
                                request['track1'] = col.track_set['many'][1]['location'] 
                                request['track1_name'] = col.make_track_name(col.track_set['many'][1]['name'])
                                request['track2'] = col.track_set['many'][2]['location'] 
                                request['track2_name'] = col.make_track_name(col.track_set['many'][2]['name']) 
                                request['track3'] = col.track_set['many'][3]['location'] 
                                request['track3_name'] = col.make_track_name(col.track_set['many'][3]['name'])
                            else:
                                request['track1'] = col.track_set['single']['location'] 
                                request['track1_name'] = col.make_track_name(col.track_set['single']['name']) 
                            if b_sel:
                                request['selected_regions'] = col.request_selection_string
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

#TODO
########################################################################### 
# Track set #
track_set = {
    'single': gm_tests.gm_track_collections['Random']['Test random track 1'],
    'many': {
        1: gm_tests.gm_track_collections['Random']['Test random track 2'],
        2: gm_tests.gm_track_collections['Random']['Test random track 3'],
        3: gm_tests.gm_track_collections['Random']['Test random track 4'],
}}

# Extra variable #
chrsuffix = 'Awfully super extra long chromosome denomination string '
request_selection_regions = ['1:0:50000','2:50000:9999999999999']
request_selection_string =';'.join([chrsuffix + r for r in request_selection_regions])
 
# Make name #
def make_track_name(path): 
    name_gen = tempfile._RandomNameSequence()
    return ' '.join([name_gen.next() for x in range(10)]) + ' ' + path.split('/')[-1] 

########################################################################### 
# Track set #
track_set = {
    'single': gm_tests.gm_track_collections['Validation']['Validation 1'],
    'many': {
        1: gm_tests.gm_track_collections['Validation']['Validation 1'],
        2: gm_tests.gm_track_collections['Validation']['Validation 2'],
        3: gm_tests.gm_track_collections['Validation']['Validation 3'],
}}

# Extra variable #
request_selection_string = 'chr1:0:30;chr1:122:126'

# Make name #
def make_track_name(path): 
    return path.split('/')[-1]

########################################################################### 
# Track set #
track_set = {
    'single': gm_tests.gm_track_collections['Yeast']['All genes'],
    'many': {
        1: gm_tests.gm_track_collections['Yeast']['All genes'],
        2: gm_tests.gm_track_collections['Yeast']['Ribi genes'],
        3: gm_tests.gm_track_collections['Yeast']['RP genes'],
}}

# Extra variable #
request_selection_string = 'chr1:0:50000;chr1:52000:54000;chr1:56000:58000;chr2:50000:9999999999999'

# Make name #
def make_track_name(path): 
    return path.split('/')[-1]

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
