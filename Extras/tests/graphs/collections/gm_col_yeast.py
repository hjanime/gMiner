track_set = {
    'single': gm_track_collections['Yeast']['All S. cer. genes (UCSC)'],
    'many': {
        1: gm_track_collections['Yeast']['All S. cer. genes (UCSC)'],
        2: gm_track_collections['Yeast']['Ribi genes'],
        3: gm_track_collections['Yeast']['RP genes'],
}}

# Extra variable #
request_selection_string = 'chr1:0:50000;chr1:52000:54000;chr1:56000:58000;chr2:50000:9999999999999'

# Make name #
def make_track_name(path): 
    return path.split('/')[-1] 
