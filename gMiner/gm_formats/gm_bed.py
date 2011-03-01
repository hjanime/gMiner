# General modules #
import sys

# Modules #
from .. import gm_tracks    as gm_tra
from .. import gm_common    as gm_com
from .. import gm_errors    as gm_err
from ..gm_constants import *


class gmFormat(gm_tra.gmTrack):
    def initialize(self):
        self.format = "bed"
        self.type = 'qualitative'
        self.attributes = {}
        self.parse()
        self.invent_chrmeta()

    def invent_chrmeta(self):
        self.chrmeta = [dict([['name',chr],['length',sys.maxint]]) for chr in self.all_chrs]

    def parse(self):
        self.fields = ['start', 'end', 'name', 'score', 'strand']
        self.data = {}
        all_features = []
        
        # Read #
        with open(self.location) as bed_file:
            for line in bed_file:
                feature = {}
                # Comment lines #
                if (line[0] == '#') or (line == '\n'): continue
                # Tab split #
                line = line.strip("\n").split('\t')
                # Check format #
                if len(line) < 3:
                    raise gm_err.ParsingError("400", "The bed track " + self.name + " does not seam to be a valid interval file")
                # Chromosome #
                feature['chr'] = line[0]
                # Start and end #
                feature['start'] = line[1]
                feature['end'] = line[2]
                # Optional name #                
                try:
                    feature['name'] = line[3]
                except:
                    feature['name'] = 'Unamed'
                # Optional strand #    
                try:    
                    feature['strand'] = line[5]
                except:
                    feature['strand'] = '.'
                # Optional score #
                try:
                    current_score = line[4]
                    score_as_float = float(current_score)
                except:
                    score_as_float = 0.0
                feature['score'] = score_as_float
                # Append feature #
                all_features.append(feature)
        
        # Convert #
        for feature in all_features:
            try:
                feature['start'] = int(feature['start'])
                feature['end'] = int(feature['end'])
            except:
                raise gm_err.ParsingError("400", "The bed track " + self.name + " has non-integers as positions")

        # Transform #
        for feature in all_features:
            if feature['chr'] in gm_chromosome_name_dictionary:
                feature['chr'] = 'chr' + gm_chromosome_name_dictionary[feature['chr']]
            else:
                if feature['chr'].startswith('chr'): feature['chr'] = feature['chr'][3:]
                if feature['chr'][0] not in '0123456789':
                    feature['chr'] = 'chr' + str(gm_com.roman_to_integer(feature['chr']))
                else:
                    feature['chr'] = 'chr' + feature['chr']

        # Check #
        for feature in all_features:
            if feature['start'] >= feature['end']:
                raise gm_err.ParsingError("400", "The bed track " + self.name + " seams to contain negative or null intervals")

        # Store #
        self.all_chrs = list(set([feature['chr'] for feature in all_features]))
        for chr in self.all_chrs:
            self.data[chr] = [[feature[f] for f in self.fields] for feature in all_features if feature['chr'] == chr]
            self.data[chr].sort()
