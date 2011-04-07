# Modules #
from .. import gm_tracks    as gm_tra
from .. import gm_errors    as gm_err
from ..gm_constants import *

# General Modules #
import os, time

# Constants #
all_fields_possible = ['start', 'end', 'name', 'score', 'strand', 'thick_start', 'thick_end',
                       'item_rgb', 'block_count', 'block_sizes', 'block_starts']

###########################################################################   
class gmFormat(gm_tra.gmTrack):
    def initialize(self):
        self.format   = "bed"
        self.type     = 'qualitative'
        self.data     = {}
        self.all_chrs = []
   
    @classmethod
    def make_new(cls, location, type, name):
        open(location, 'w').close()

    def load(self):
        with open(self.location, 'r') as self.file:
            self.get_chr_meta()
            self.get_meta_data()
            self.get_chr_fields()
            for chr, iterator in self.iter_over_chrs():
                self.data[chr] = list(iterator)
    
    #-----------------------------------------------------------------------------#   
    def get_chr_meta(self):
        if not self.chr_file:
            raise gm_err.gmError("400", "The bed track " + self.name + " does not have a chromosome file associated.")
        if not os.path.exists(self.chr_file):
            raise gm_err.gmError("400", "The file " + self.chr_file + " cannot be found")
        if os.path.isdir(self.chr_file):
            raise gm_err.gmError("400", "The location " + self.chr_file + " is a directory (a file was expected).")
        self.chrmeta = []
        with open(self.chr_file, 'r') as f:
            for line in f:
                line = line.strip('\n')            
                if len(line) == 0:       continue
                if line.startswith("#"): continue
                if '\t' in line: seperator = '\t'
                else:            seperator = ' '
                line = line.split(seperator)
                if len(line) != 2:
                    raise gm_err.gmError("400", "The file " + self.chr_file + " does not seam to be a valid chromosome file.")
                name = line[0]
                try:
                    length = int(line[1])
                except ValueError as err:
                    raise gm_err.gmError("400", "The file " + self.chr_file + " has invalid values.", err)
                self.chrmeta.append(dict([('name', name),('length', length)]))
        if not self.chrmeta:
            raise gm_err.gmError("400", "The file " + self.chr_file + " does not seam to contain any information.", err)
        self.all_chrs = [x['name'] for x in self.chrmeta]
 
    def get_meta_data(self):
        self.file.seek(0)
        self.attributes = {}    
        for line in self.file:
            line = line.strip("\n").lstrip()
            if len(line) == 0:              continue
            if line.startswith("#"):        continue
            if line.startswith("browser "): continue
            if line.startswith("track "):
                import shlex
                try:
                    self.attributes = dict([p.split('=',1) for p in shlex.split(line[6:])])
                except ValueError as err:
                    raise gm_err.gmError("400", "The <track> header line for the file " + self.location + " seams to be invalid", err)
            break

    def get_chr_fields(self):
        self.file.seek(0)    
        while True:
            line = self.file.readline().strip("\n").lstrip()
            if len(line) == 0:              continue
            if line.startswith("#"):        continue
            if line.startswith("track "):   continue
            if line.startswith("browser "): continue
            else:
                if '\t' in line: self.seperator = '\t'
                else:            self.seperator = ' '
                line = line.split(self.seperator)
            self.num_fields = len(line) - 1
            if self.num_fields < 2:
                raise gm_err.gmError("400", "The track " + self.location + " has less than three columns and is hence not a valid BED file.")
            if self.num_fields > len(all_fields_possible):
                raise gm_err.gmError("400", "The track " + self.location + " has too many columns and is hence not a valid BED file.")
            self.fields = all_fields_possible[0:self.num_fields]
            break

    def iter_over_chrs(self):
        global line, chr
        line = ''
        chr  = ''
        seen_chr = []
        def get_next_line():
            global line, chr
            while True:
                line = self.file.next().strip("\n").lstrip()
                if len(line) == 0:              continue
                if line.startswith("#"):        continue
                if line.startswith("track "):
                    if not chr: continue
                    raise gm_err.gmError("400", "The file " + self.location + " contains a second 'track' directive. This is not supported.")
                if line.startswith("browser "):
                    if not chr: continue
                    raise gm_err.gmError("400", "The file " + self.location + " contains a 'browser' directive. This is not supported.")
                line = line.split(self.seperator)
                if len(line) != self.num_fields + 1:
                    raise gm_err.gmError("400", "The track " + self.location + " has a varying number of columns. This is not supported.")
                try:
                    line[1] = int(line[1])
                    line[2] = int(line[2])
                except ValueError:
                    raise gm_err.gmError("400", "The track " + self.location + " has non integers as interval bounds and is hence not valid.")
                if line[2] <= line[1]:
                    raise gm_err.gmError("400", "The track " + self.location + " has negative or null intervals and is hence not valid.")
                break
        def iter_until_different_chr():
            global line
            while True:
                if line[0] != chr: break
                yield line[1:]
                get_next_line()
        self.file.seek(0)
        get_next_line()
        while True:
            if line[0] == chr: break
            chr = line[0]
            if chr in seen_chr:
                raise gm_err.gmError("400", "The track " + self.location + " is not sorted by chromosomes (" + chr + ").")
            seen_chr.append(chr)
            yield chr, iter_until_different_chr()

    def convert_to_sql(self, new_track):
        with open(self.location, 'r') as self.file:
            # Various info #
            self.get_chr_meta()
            self.get_meta_data()
            self.get_chr_fields()
            # Add info #
            self.attributes['converted_by']   = gm_project_name
            self.attributes['converted_from'] = self.location
            self.attributes['converted_at']   = time.asctime()
            # Copy meta data #
            new_track.write_chr_meta(self.chrmeta)
            new_track.write_meta_data(self.attributes)
            # Read the whole file #
            for chr, iterator in self.iter_over_chrs():
                new_track.write_data_qual(chr, iterator, self.fields)

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
        self.fields = ['start', 'end'] 
        for f in all_fields_possible[2:]:
            if f in old_track.fields: self.fields.append(f)
            else: break
        # Wrapper function #
        def stringify(chr, iterator):
            for i in iterator:
                yield chr + '\t' + '\t'.join(str(i)) + '\n' 
        # Write everything #
        with open(self.location, 'w') as self.file:
            self.file.write(line)
            for chr in old_track.all_chrs:
                self.file.writelines(stringify(chr, old_track.get_data_qual({'type':'chr', 'chr':chr}, self.fields)))
