# Modules #
from . import gm_errors    as gm_err
from . import gm_parsing   as gm_par
from . import gm_common    as gm_com
from . import gm_formats   as formats
from .gm_constants import *

# Extra modules #
import os, re, sys


###########################################################################   
class gmTrack(object):
    @classmethod
    def Factory(cls, track_dict, number=None, locked=False, conversion=True):
        name = track_dict['name']
        location = track_dict['location'].rstrip('/')
        location, format = cls.determine_format(location)
        cls.import_format(format)
        track = getattr(formats, 'gm_' + format).gmFormat(name, location, number, locked)
        if conversion: return gm_convert_track(track) 
        else: return track

    @classmethod
    def determine_format(cls, location):
        # Does the file exist ? #
        if not os.path.exists(location):
            raise gm_err.gmError("400", "The file " + location + " cannot be found")
        # Directories #
        if os.path.isdir(location):
            raise gm_err.gmError("400", "The location " + location + " is a directory")
        # Get extension #
        extension = os.path.splitext(location)[1][1:]
        # If no extension then try magic #
        if not extension: extension = cls.determine_format_magic(location)
        # Synonyms #
        if extension == 'db': extension = 'sql'
        # General case #
        return location, extension
    
    @classmethod
    def determine_format_magic(cls, location):
        try:
            import magic
        except ImportError:
            raise gm_err.gmError("400", "The format of the track " + location + " cannot be determined", err)
        if os.path.exists('magic'):
            m = magic.Magic('magic')
        else:
            m = magic.Magic()
        type = m.from_file(location)
        try:
            extension = gm_known_extensions[type]
        except KeyError as err:
            raise gm_err.gmError("400", "The format of the track " + location + " resolves to " + type + " which is not supported at the moment.", err)
        return extension

    @classmethod
    def import_format(cls, format):
        if not hasattr(formats, 'gm_' + format):
            try: __import__('gMiner.gm_formats.gm_' + format)
            except ImportError as err:
                raise gm_err.gmError("400", "The format " + format + " is not supported at the moment", err)

    def __init__(self, name, location, number, locked):
        self.name = name
        self.location = location
        self.locked = locked
        self.number = number
        self.initialize()
        self.check()

    def check(self):
        # Sort chromosomes #
        self.all_chrs.sort(key=gm_com.natural_sort)
        # Test variables #
        gm_par.assert_is_among(self.type, ['quantitative', 'qualitative'], 'track type')

    def write_qual(self, *args):
        if self.locked: raise gm_err.gmError("500", "Attempted to write to a locked track")
        return self.write_data_qual(*args)

    def write_quan(self, *args):
        if self.locked: raise gm_err.gmError("500", "Attempted to write to a locked track")
        return self.write_data_quan(*args)

    @classmethod
    def new(cls, location, format, type, name):
        if os.path.exists(location):
            raise gm_err.gmError("400", "The location " + location + " is already taken")
        cls.import_format(format)
        getattr(formats, 'gm_' + format).gmFormat.make_new(location, type, name)
        return cls.Factory({'location': location, 'name': name}, conversion=False) 

    #-----------------------------------------------------------------------------#   
    @classmethod
    def make_new(*args): pass
    def get_stored(*args): return False
    def write_data_qual(*args): pass
    def write_data_quan(*args): pass
    def write_meta_data(*args): pass
    def write_chr_meta(*args): pass
    def write_stored(*args): pass
    def commit(*args): pass
    def stat_shortcut(*args): return False
    def unload(*args): del self.data

    #---------------------------------------------------------------------------#   
    def get_data_quan(self, *args): return self.get_data_qual(*args)
    def get_data_qual(self, selection, fields):
        def get_chr(chr):
            for feat in self.data[chr]: yield [feat[self.fields.index(field)] for field in fields]
        def get_span(span):
            chr = span['chr']
            for feat in self.data[chr]:
                if feat[self.fields.index('start')] < span['end'] & feat[self.fields.index('end')] > span['start']:
                    yield [feat[self.fields.index(field)] for field in fields]
        if selection['type'] == 'span':
            return get_span(selection['span'])
        if selection['type'] == 'chr':
            return get_chr(selection['chr'])


###########################################################################   
def gm_convert_track(old_track):
    if old_track.format in gm_convert_dict:
        new_format = gm_convert_dict[old_track.format]
        if new_format:
            new_location = old_track.location.rsplit('.',1)[0]+'.'+new_format
            new_type = old_track.type
            new_name = old_track.name
            gmTrackConverter.convert(old_track, new_location, new_format, new_type, new_name)
            return gmTrack.Factory({'location': new_location, 'name': new_name})
    return old_track

class gmTrackConverter(object):
    @classmethod
    def convert(self, old_track, new_location, new_format, new_type, new_name):
        new_track = gmTrack.new(new_location, new_format, new_type, new_name)
        # Copy meta data #
        new_track.write_meta_data(old_track.attributes)
        new_track.write_chr_meta(old_track.chrmeta)
        # Copy raw data #
        for chr in old_track.all_chrs: getattr(new_track, 'write_' + new_track.type[0:4])(chr, getattr(old_track, 'get_data_'+old_track.type[0:4])({'type':'chr', 'chr':chr}, old_track.fields), old_track.fields) 
        # Close it #
        new_track.unload()
