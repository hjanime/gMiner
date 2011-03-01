# General modules #
import os
import json as jsonparser

# Modules #
from .. import gm_tracks as gm_tra

class gmFormat(gm_tra.gmTrack):
    def initialize(self):
        self.format = "json"
        self.type = 'qualitative'
        self.all_chrs = [os.path.splitext(file)[0] for file in os.listdir(self.location)]
        self.data = {}
        for chr in self.all_chrs: load_chr(chr)

    def load_chr(chr):
        chrfile = open(self.location + '/' + chr + '.' + self.format, 'r')
        raw = jsonparser.load(chrfile)
        self.fields = raw[u'headers']
        self.data[chr] = raw[u'featureNCList'] 
        chrfile.close()
