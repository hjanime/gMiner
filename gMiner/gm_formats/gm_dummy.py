'''
To implement your own format, make a copy of
this file and implement all the appropriate methods.
'''

# Mother class #
from .. import gm_tracks as gm_tra 

class gmFormat(gm_tra.gmTrack):
    def initialize(self):
        self.format = "dummy"
        self.type = 'qualitative'
        self.all_chrs = ['lorem', 'ipsum']
        self.fields = ['start', 'end', 'cuil_factor']
        self.attributes = {}
        self.chrmeta = []

    @classmethod
    def make_new(cls, location, type, name):
        pass

    def get_data_qual(self, selection, fields):
        pass

    def get_data_quan(self, selection, fields):
        pass

    def get_stored(self, type, subtype, selection):
        pass
    
    def write_data_qual(self, chr, fields, iterable):
        pass

    def write_data_quan(self, chr, iterable):
        pass

    def write_meta_data(self, data):
        pass

    def write_chr_meta(self, data):
        pass
    
    def write_stored(self, type, subtype, selection, result):
        pass

    def commit(self):
        pass

    def unload(self):
        pass
