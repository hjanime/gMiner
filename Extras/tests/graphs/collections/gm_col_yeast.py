# Modules #
import gm_convert_tracks as gm_convert

# Collections of track sets: YEAST #
yeast_files = [
qual_path + 'bed/all_yeast_genes.bed', 
qual_path + 'gff/ribosome_genesis.gff', 
qual_path + 'gff/ribosome_proteins.gff',
]
bed_files = [
sql_path + 'all_yeast_genes.sql', 
sql_path + 'ribosome_genesis.sql', 
sql_path + 'ribosome_proteins.sql',
]

if False:
    for file in sql_files:
        if os.path.exists(file): os.remove(file)
    for file in bed_files:
        gm_convert.convert_single_track(file, sql_path)

# Final variable #
track_set = {
    'single': sql_path + 'all_yeast_genes.sql',
    'many': {
        1: sql_path + 'all_yeast_genes.sql',
        2: sql_path + 'ribosome_proteins.sql',
        3: sql_path + 'ribosome_genesis.sql',
}}

# Extra variable #
request_selection_string = 'chr1:0:50000;chr2:50000:9999999999999'

# Make name #
def make_track_name(path): 
    return path.split('/')[-1] 
