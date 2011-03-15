# gMiner modules #
import gMiner.gm_common as gm_com

# Special modules #
gm_convert = gm_com.import_module('gm_convert_tracks', gm_path + '/../Extras/scripts/')

# Collections of track sets: YEAST #
bed_files = [
    tracks_path + 'qual/bed/all_yeast_genes.bed', 
    tracks_path + 'qual/gff/ribosome_genesis.gff', 
    tracks_path + 'qual/gff/ribosome_proteins.gff',
]
sql_files = [
    sql_path + 'all_yeast_genes.sql', 
    sql_path + 'ribosome_genesis.sql', 
    sql_path + 'ribosome_proteins.sql',
]

# Recreate the SQL files from the BED ones #
if False:
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
request_selection_string = 'chr1:0:50000;chr2:50000:9999999999999'

# Make name #
def make_track_name(path): 
    return path.split('/')[-1] 
