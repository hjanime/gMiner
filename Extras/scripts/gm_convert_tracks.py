import gMiner.gm_tracks as gm_tra

def convert_single_track(file, sql_dir, new_type='qualitative'):
    old_track = gm_tra.gmTrack.Factory({'location': file, 'name': 'Unitest graphs'})
    new_location = sql_dir + '.'.join(file.split('/')[-1].split('.')[:-1]) + '.sql'
    new_format = 'sql'
    new_name = 'Converted track'
    gm_tra.gmTrackConverter.convert(old_track, new_location, new_format, new_type, new_name)
