# gMiner #
import gMiner
from gMiner.gm_constants import *

# Track set #
track_set = {
    'single': gm_track_collections['Random']['Test random track 1'],
    'many': {
        1: gm_track_collections['Random']['Test random track 2'],
        2: gm_track_collections['Random']['Test random track 3'],
        3: gm_track_collections['Random']['Test random track 4'],
}}

# Extra variable #
chrsuffix = 'Awfully super extra long chromosome denomination string '
request_selection_regions = ['1:0:50000','2:50000:9999999999999']
request_selection_string =';'.join([chrsuffix + r for r in request_selection_regions])
 
# Make name #
def make_track_name(path): 
    name_gen = tempfile._RandomNameSequence()
    return ' '.join([name_gen.next() for x in range(10)]) + ' ' + path.split('/')[-1] 
