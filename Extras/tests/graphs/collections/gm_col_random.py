# Modules #
from gm_constants import *

# Collections of track sets: RANDOM #
sql_files = [
    sql_path + 'random1.sql', 
    sql_path + 'random2.sql', 
    sql_path + 'random3.sql',
    sql_path + 'random4.sql',
]

# Generate #
chrsuffix = 'Awfully super extra long chromosome denomination string '
if True:
    for file in sql_files:
        if os.path.exists(file): os.remove(file)
    import random
    import gm_random_track as gm_random
    import gm_tracks as gm_tra
    new_format = 'sql'
    new_type = 'qualitative'
    new_name = 'Unitest graphs'
    old_track = gm_random.gmRandomTrack(1000,chrsuffix)
    for num in [1,2,3,4]:
        new_location = sql_path + 'random' + str(num) + '.sql'
        gm_tra.gmTrackConverter.convert(old_track, new_location, new_format, new_type, new_name)

# Final variable #
track_set = {
    'single': sql_path + 'random1.sql',
    'many': {
        1: sql_path + 'random2.sql',
        2: sql_path + 'random3.sql',
        3: sql_path + 'random4.sql',
}}

# Extra variable #
request_selection_regions = ['1:0:50000','2:50000:9999999999999']
request_selection_string =';'.join([chrsuffix + r for r in request_selection_regions])
 
# Make name #
def make_track_name(path): 
    import tempfile
    name_gen = tempfile._RandomNameSequence()
    return ' '.join([name_gen.next() for x in range(10)]) + ' ' + path.split('/')[-1] 
