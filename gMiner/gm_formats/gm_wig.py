# General modules #
import sys

# Modules #
from .. import gm_tracks    as gm_tra
from .. import gm_common    as gm_com
from .. import gm_errors    as gm_err
from ..gm_constants import *


class gmFormat(gm_tra.gmTrack):
    def initialize(self):
        self.format = "wig"
        self.type = 'quantitative'
        self.attributes = {}
        self.parse()
        self.invent_chrmeta()

    def invent_chrmeta(self):
        self.chrmeta = [dict([['name',chr],['length',sys.maxint]]) for chr in self.all_chrs]

    def parse(self):
        self.fields = ['start', 'end', 'score']
        self.data = {}
        all_features = []
       
        # Read #
        with open(self.location) as wig_file:
            for line in wig_file:
                feature = {}
                # Comment lines #
                if (line[0] == '#') or (line == '\n'): continue
                # Tab split #
                line = line.strip("\n").split('\t')
                # Custom wig #
                if (line[0][0:6] == 'custom'):
                    current_chromosome = line[0].split(' ')[1].split('=')[1]
                    continue
                # Check format #
                if len(line) < 3:
                    raise gm_err.ParsingError("400", "The wig track " + self.name + " cannot be read by this simple parser")
                # Features #
                feature['chr'] = current_chromosome
                feature['start'] = line[0]
                feature['end'] = line[1]
                feature['score'] = line[2]
                # Append feature #
                all_features.append(feature)
       












 
        # Convert #
        for feature in all_features:
            try:
                feature['start'] = int(feature['start'])
                feature['end'] = int(feature['end'])
                feature['score'] = float(feature['score'])
            except:
                raise gm_err.ParsingError("400", "The wig track " + self.name + " has non-numbers")











        # Check #
        for feature in all_features:
            if feature['start'] >= feature['end']:
                raise gm_err.ParsingError("400", "The wig track " + self.name + " seams to contain negative or null intervals")

        # Store #
        self.all_chrs = list(set([feature['chr'] for feature in all_features]))
        for chr in self.all_chrs:
            self.data[chr] = [[feature[f] for f in self.fields] for feature in all_features if feature['chr'] == chr]
            self.data[chr].sort()
