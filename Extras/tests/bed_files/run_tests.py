# The modules #
import os, tempfile, re
from inspect import getfile, currentframe

# Tested modules #
from gMiner import gm_tracks as gm_tra

# This directory #
current_path = getfile(currentframe())
this_dir = '/'.join(os.path.abspath(current_path).split('/')[:-1])

# Tests #
tests = []
tests += [(this_dir+'/should_pass/'+bed, True)  for bed in os.listdir(this_dir+'/should_pass') if bed.endswith(".bed")]
tests += [(this_dir+'/should_fail/'+bed, False) for bed in os.listdir(this_dir+'/should_fail') if bed.endswith(".bed")]

# Output #
def message(path, name, status, expected, extra=None):
    if extra: extra = re.sub(path + ' ', '', extra)
    if extra: extra = re.sub(' - HTTP 400', '', extra)
    s = name.ljust(26)
    if status==expected:
        s += '\033[0;37m\033[42m passed the test \033[0m'
    else:
        s += '\033[1;37m\033[41m\033[5;37m failed the test \033[0m'
    if extra:
        s += '  (' + extra + ')' 
    print s

# The tests #
chr_file = '/'.join(this_dir.split('/')[:-2]) + '/tracks/chr/yeast.chr'
for bed, expected in tests:
    name = bed.split('/')[-1]
    if name == 'challange.bed': continue
    temp_file = tempfile.NamedTemporaryFile(suffix='.sql', delete=False)
    sql_path = temp_file.name
    temp_file.close()
    os.remove(sql_path)
    try:
        track = gm_tra.gmTrack.Factory({'name': name, 'location': bed, 'chrs': chr_file}, conversion=False)
        gm_tra.gmTrackConverter.convert(track, sql_path, 'sql', 'qualitative', name)
    except Exception as err:
        message(bed, name, False, expected, str(err))
        continue
    finally:
        os.remove(sql_path)
    message(bed, name, True, expected)
