# Modules #
import random, tempfile

# gMiner modules #
import gMiner.gm_tracks as gm_tra
import gMiner.gm_common as gm_com

# Special modules #
gm_random = gm_com.import_module('gm_random_track', gm_path + '/../Extras/scripts/')

# Collections of track sets: RANDOM #
sql_files = [
    sql_path + 'random1.sql', 
    sql_path + 'random2.sql', 
    sql_path + 'random3.sql',
    sql_path + 'random4.sql',
]

# Remove #
for file in sql_files:
    if os.path.exists(file): os.remove(file)

# Generate #
new_format = 'sql'
new_type = 'qualitative'
new_name = 'Unitest graphs'
chrsuffix = 'Awfully super extra long chromosome denomination string '
old_track = gm_random.gmRandomTrack(1000,chrsuffix)
for num in [1,2,3,4]:
    new_location = sql_path + 'random' + str(num) + '.sql'
    gm_tra.gmTrackConverter.convert(old_track, new_location, new_format, new_type, new_name)

# Final variable #
track_set = {
    'single': sql_files[0],
    'many': {
        1: sql_files[1],
        2: sql_files[2],
        3: sql_files[3],
}}

# Extra variable #
request_selection_regions = ['1:0:50000','2:50000:9999999999999']
request_selection_string =';'.join([chrsuffix + r for r in request_selection_regions])
 
# Make name #
def make_track_name(path): 
    name_gen = tempfile._RandomNameSequence()
    return ' '.join([name_gen.next() for x in range(10)]) + ' ' + path.split('/')[-1] 
