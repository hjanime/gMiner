# gMiner #
from ... import gm_tests

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

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------# 
