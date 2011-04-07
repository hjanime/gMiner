# Modules #
from .. import gm_tracks    as gm_tra
from .. import gm_errors    as gm_err
from ..gm_constants import *

# General Modules #
import os, time

###########################################################################   
class gmFormat(gm_tra.gmTrack):
    def initialize(self):
        self.format   = "bed"
        self.type     = 'qualitative'
        self.fields   = gm_quantitative_fields
        self.data     = {}
        self.all_chrs = []
   
    @classmethod
    def make_new(cls, location, type, name):
        open(location, 'w').close()

    def load(self):
        pass

#-----------------------------------------------------------------------------#
    def iter_over_chrs(self):
        global line, prv_chr, cur_chr, seen_chr
        line = ''
        prv_chr  = ''
        cur_chr  = ''
        seen_chr = []
        def get_next_line():
            global line, prv_chr, cur_chr
            while True:
                line = self.file.next().strip("\n").lstrip()
                if len(line) == 0:              continue
                if line.startswith("#"):        continue
                if line.startswith("track "):
                    if not cur_chr: continue
                    raise gm_err.gmError("400", "The file " + self.location + " contains a second 'track' directive. This is not supported.")
                if line.startswith("browser "):
                    if not cur_chr: continue
                    raise gm_err.gmError("400", "The file " + self.location + " contains a 'browser' directive. This is not supported.")
                line = line.split()
                if len(line) != self.num_fields + 1:
                    raise gm_err.gmError("400", "The track " + self.location + " has a varying number of columns. This is not supported.")
                try:
                    line[1] = int(line[1])
                    line[2] = int(line[2])
                except ValueError:
                    raise gm_err.gmError("400", "The track " + self.location + " has non integers as interval bounds and is hence not valid.")
                if line[2] <= line[1]:
                    raise gm_err.gmError("400", "The track " + self.location + " has negative or null intervals and is hence not valid.")
                if len(line) > 3:
                    if line[4] == '.': line[4] = 0.0
                    try:
                        line[4] = float(line[4])
                    except ValueError:
                        raise gm_err.gmError("400", "The track " + self.location + " has non floats as score values and is hence not valid.")
                break
        def iter_until_different_chr():
            global line
            while True:
                if cur_chr != prv_chr: break
                yield line
                get_next_line()
        self.file.seek(0)
        get_next_line()
        while True:
            if cur_chr == prv_chr: break
            if cur_chr in seen_chr:
                raise gm_err.gmError("400", "The track " + self.location + " is not sorted by chromosomes (" + cur_chr + ").")
            seen_chr.append(cur_chr)
            yield cur_chr, iter_until_different_chr()

    def convert_to_sql(self, new_track):
        with open(self.location, 'r') as self.file:
            # Various info #
            self.get_chr_meta()
            self.get_meta_data()
            # Add info #
            self.attributes['converted_by']   = gm_project_name
            self.attributes['converted_from'] = self.location
            self.attributes['converted_at']   = time.asctime()
            new_track.write_meta_data(self.attributes)
            # Read the whole file #
            for chr, iterator in self.iter_over_chrs():
                new_track.write_data_quan(chr, iterator, self.fields)
            # Copy meta data #
            global seen_chr
            new_track.write_chr_meta([chr for chr in self.chrmeta if chr['name'] in seen_chr])

    #-----------------------------------------------------------------------------#
    def convert_from_sql(self, old_track):
        # Add info #
        self.attributes = old_track.attributes
        self.attributes['name']           = old_track.name
        self.attributes['type']           = 'bed'
        self.attributes['converted_by']   = gm_project_name
        self.attributes['converted_from'] = old_track.location
        self.attributes['converted_at']   = time.asctime()        
        # Make first line #
        line = "track " + ' '.join([key + '="' + value + '"' for key, value in self.attributes.items()]) + '\n'
        # Get fields #
        pass
        # Wrapper function #
        def stringify(chr, iterator):
            for line in iterator:
                yield chr + '\t' + '\t'.join([str(f) for f in line]) + '\n' 
        # Write everything #
        with open(self.location, 'w') as self.file:
            self.file.write(line)
            for chr in old_track.all_chrs:
                self.file.writelines(stringify(chr, old_track.get_data_quan({'type':'chr', 'chr':chr}, self.fields)))
 
