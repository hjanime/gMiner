###########################################################################
##############################  GRAPHS  ###################################
###########################################################################
# Modules #
import os, sys, cStringIO
import gm_request as gm_req

# Tracks should better be local #
tracks_path = gm_path + '/../Extras/tracks/'
qual_path = tracks_path + 'qual/'
sql_path = tracks_path + 'qual/sql/'

# Chose a collection of tracks #
execfile(gm_path + '/../Extras/tests/graphs/collections/gm_col_yeast.py')
#execfile(gm_path + '/../Extras/tests/graphs/collections/gm_col_random.py')
#execfile(gm_path + '/../Extras/tests/graphs/collections/gm_col_validation.py')

# A name dictonary #
name_dict = {
    True: {
        True:  {True: 'H', False: 'D'},
        False: {True: 'G', False: 'C'},
    },
    False: {
        True:  {True: 'F', False: 'B'},
        False: {True: 'E', False: 'A'},
    }
}

# Other #
chara_dict = {
    'number_of_features': '_Count',
    'base_coverage': '_Base',
    'length': '_Length',
    'score': '_Score',
}
result_path = '/tmp/gMiner/'

# Main loops #
count = 1
max_count = 2*2*2*2*4
max_count -= max_count/4 
for b_many in [True, False]:
    for b_sel in [True, False]:
        for b_comp in [True, False]:
            for b_chr in [True, False]:
                for chara in chara_dict.keys():
                    if not b_sel and b_comp: continue
                    name = name_dict[b_comp][b_chr][b_many]
                    name = name + chara_dict[chara]
                    if not b_sel: name += '_NoSel'
                    print "Graph " + str(count) + " out of " + str(max_count) + "   (" + name + ")"
                    count += 1
                    request = '[gMiner]'
                    request += '\n' + 'version=0.1.5'
                    request += '\n' + 'gm_encoding=image/png'
                    request += '\n' + 'operation_type=desc_stat'
                    request += '\n' + 'characteristic=' + chara 
                    if b_many:
                        request += '\n' + 'track1=' + track_set['many'][1] 
                        request += '\n' + 'track1_name=' + make_track_name(track_set['many'][1])
                        request += '\n' + 'track2=' + track_set['many'][2] 
                        request += '\n' + 'track2_name=' + make_track_name(track_set['many'][2]) 
                        request += '\n' + 'track3=' + track_set['many'][3] 
                        request += '\n' + 'track3_name=' + make_track_name(track_set['many'][3])
                    else:
                        request += '\n' + 'track1=' + track_set['single'] 
                        request += '\n' + 'track1_name=' + make_track_name(track_set['single']) 
                    if b_sel:
                        request += '\n' + 'selected_regions=' + request_selection_string
                    if b_chr: 
                        request += '\n' + 'per_chromosome=True' 
                    if b_comp: 
                        request += '\n' + 'compare_parents=True' 
                    request_file = cStringIO.StringIO()
                    request_file.write(request)
                    request_file.seek(0)
                    req = gm_req.gmRequest(request_file)
                    error, result, type = req.prepare()
                    if error != 200:
                        print error, result
                        sys.exit()
                    else:
                        error, result, type = req.run()
                    if error != 200:
                        print error, result
                        sys.exit()
                    result_file = open(result_path + name + '.png', 'w')
                    result_file.write(result)
                    result_file.close()
