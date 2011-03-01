# Modules #
import gm_convert_tracks as gm_convert

# Collections of track sets: VALIDATION #
bed_files = [
qual_path + 'bed/validation1.bed', 
qual_path + 'bed/validation2.bed', 
qual_path + 'bed/validation3.bed', 
]
sql_files = [
sql_path + 'validation1.sql', 
sql_path + 'validation2.sql', 
sql_path + 'validation3.sql', 
]

if False:
    for file in sql_files:
        if os.path.exists(file): os.remove(file)
    for file in bed_files:
        gm_convert.convert_single_track(file, sql_path)

# Final variable #
track_set = {
    'single': sql_path + 'validation1.sql',
    'many': {
        1: sql_path + 'validation1.sql',
        2: sql_path + 'validation2.sql',
        3: sql_path + 'validation3.sql',
}}

# Extra variable #
request_selection_string = 'chr1:0:30;chr1:122:126'

# Make name #
def make_track_name(path): 
    return path.split('/')[-1] 
