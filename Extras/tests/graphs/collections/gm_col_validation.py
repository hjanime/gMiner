#gMiner modules #
import gMiner.gm_common as gm_com

# Special modules #
gm_convert = gm_com.import_module('gm_convert_tracks', gm_path + '/../Extras/scripts/')

# Collections of track sets: VALIDATION #
bed_files = [
    tracks_path + 'qual/bed/validation1.bed', 
    tracks_path + 'qual/bed/validation2.bed', 
    tracks_path + 'qual/bed/validation3.bed', 
]
sql_files = [
    sql_path + 'validation1.sql', 
    sql_path + 'validation2.sql', 
    sql_path + 'validation3.sql', 
]

# Recreate the SQL files from the BED ones #
for file in sql_files:
    if os.path.exists(file): os.remove(file)
for file in bed_files:
    gm_convert.convert_single_track(file, sql_path)

# Final variable #
track_set = {
    'single': sql_files[0],
    'many': {
        1: sql_files[0],
        2: sql_files[1],
        3: sql_files[2],
}}

# Extra variable #
request_selection_string = 'chr1:0:30;chr1:122:126'

# Make name #
def make_track_name(path): 
    return path.split('/')[-1] 
