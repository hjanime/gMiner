# Modules #
from .. import gm_tracks    as gm_tra
from .. import gm_errors    as gm_err
from .. import gm_common    as gm_com
from ..gm_constants import *

# General Modules #
import sys, os, time

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
        global chr, entry, seen_chr 
        chr      = ''
        seen_chr = []

        def all_features():
            params = {}
            for line in self.file:
                line = line.strip("\n").lstrip()
                if len(line) == 0:              continue
                if line.startswith("#"):        continue
                if line.startswith("track "):   continue
                if line.startswith("browser "): continue
                if line.startswith("variableStep ") or line.startswith("fixedStep "):
                    params = dict([p.split('=',1) for p in shlex.split('mode=' + line)])
                    if not 'chrom' in params:
                        raise gm_err.gmError("400", "The track " + self.location + " does not specify a chromosome and is hence not valid.")
                    params['span'] = params.get('span',1)
                    if line.startswith("fixedStep "):
                        if not 'start' in params:
                            raise gm_err.gmError("400", "The track " + self.location + " has a fixedStep directive without a start.")
                        params['step'] = params.get('step',1)
                        if params['span'] > params['step']:
                            raise gm_err.gmError("400", "The track " + self.location + " has a span bigger than its step.")
                    continue
                if not params:
                    raise gm_err.gmError("400", "The track " + self.location + " is missing a fixedStep or variableStep directive.")
                if params['mode'] == 'fixedStep':
                    try:
                        line = float(line)
                    except ValueError:
                        raise gm_err.gmError("400", "The track " + self.location + " has non floats as score values and is hence not valid.")
                    yield (params['chrom'], params['start'], params['start'] + params['step'], line)
                if params['mode'] == 'variableStep':
                    line = line.split()
                    try:
                        line[0] = float(int[0])
                        line[1] = float(line[1])
                    except ValueError:
                        raise gm_err.gmError("400", "The track " + self.location + " has invalid values.")
                    yield (params['chrom'], line[0], line[0] + params['step'], line[1])
        def all_entries():
            sentinel = ('', sys.maxint, sys.maxint, 0.0)
            X = gm_com.sentinelize(all_features(), sentinel)
            x = X.next()
            if x == sentinel:
                yield x
                return 
            while True:
                x_next = X.next()
                if x_next == sentinel:
                    yield x
                    break
                if x_next[1] < x[2]:
                    raise gm_err.gmError("400", "The track " + self.location + " has a span larger than its variable step size.") 
                if x[0] == x_next[0] and x[2] != x[1] and x[3] == x[3]:
                    x[2] = x_next[2]
                    continue
                yield x
                x = x_next 

        def get_next_entry():
            global entry, generator
            entry = generator.next()    
        def iter_until_different_chr():
            global chr, entry, generator, seen_chr 
            while True:
                if entry[0] != chr: break
                yield entry[1:]
                get_next_entry()
        entry     = ['', '', '', '']
        generator = all_entries()
        get_next_entry()
        while True:
            if entry[0] == chr: break
            chr = entry[0]
            if chr in seen_chr:
                raise gm_err.gmError("400", "The track " + self.location + " is not sorted by chromosomes (" + chr + ").")
            seen_chr.append(chr)
            yield chr, iter_until_different_chr()

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
            self.file.seek(0)
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
 
