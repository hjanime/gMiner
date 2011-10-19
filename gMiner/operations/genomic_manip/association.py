"""
Assocation manipulation
"""

# Built-in modules #
import sys

# Internal modules #
from gMiner.operations.genomic_manip import Manipulation as Manip
from gMiner import common

################################################################################
class find_closest_features(Manip):
    '''Blah blah.'''

    def __init__(self):
        self.name               = 'Find closest features'
        self.input_tracks       = [{'type':'track', 'name':'X', 'kind':'qualitative', 'fields':['start','end','name','score','strand']},
                                   {'type':'track', 'name':'Y', 'kind':'qualitative', 'fields':['start','end','name','score','strand']}]
        self.input_constraints  = []
        self.input_request      = [{'type': int, 'key': 'max_length',    'name': 'max_length',    'default': 1000},
                                   {'type': int, 'key': 'utr_cutoff',    'name': 'utr_cutoff',    'default': 2000},
                                   {'type': int, 'key': 'prom_cutoff',   'name': 'prom_cutoff',   'default': 3000}]
        self.input_special      = []
        self.input_by_chrom     = []
        self.output_tracks      = [{'type': 'track', 'kind': 'any', 'fields': ['start','end','name','strand','id','type','location']}]
        self.output_constraints = []
        self.output_other       = []

    def chr_collapse(self, *args): return common.collapse.by_union(*args)

    def __call__(self, X, Y, max_length, utr_cutoff, prom_cutoff):
        x = X.next()
        y = Y.next()
        print x,y
        yield 0

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
