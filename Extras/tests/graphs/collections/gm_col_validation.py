# gMiner #
import gMiner
from gMiner.gm_constants import *

# Track set #
track_set = {
    'single': gm_track_collections['Validation']['Validation 1'],
    'many': {
        1: gm_track_collections['Validation']['Validation 1'],
        2: gm_track_collections['Validation']['Validation 2'],
        3: gm_track_collections['Validation']['Validation 3'],
}}

# Extra variable #
request_selection_string = 'chr1:0:30;chr1:122:126'

# Make name #
def make_track_name(path): 
    return path.split('/')[-1] 
