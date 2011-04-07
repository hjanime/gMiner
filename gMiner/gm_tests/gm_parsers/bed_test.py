# gMiner Modules #
from ... import gm_tests
from ... import gm_tracks as gm_tra

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# General modules #
import os, tempfile

################################################################################### 
class Unittest_test(unittest.TestCase):
    def runTest(self):
        # Chose track to test #
        name = 'All genes'
        track = gm_tests.gm_track_collections['Yeast'][name]
        # Intermediate file #
        temp_file = tempfile.NamedTemporaryFile(suffix='.sql', delete=False)
        sql_path = temp_file.name
        temp_file.close()
        os.remove(sql_path)
        # Conversion #
        gm_tra.gmTrackConverter.convert(track['track'], sql_path, 'sql', 'qualitative', name)
        # Open it #
        sql_track = gm_tra.gmTrack.Factory({'location': sql_path, 'name': name})
        # Final file #
        temp_file = tempfile.NamedTemporaryFile(suffix='.bed', delete=False)
        bed_path = temp_file.name
        temp_file.close()
        os.remove(bed_path)
        # Conversion again #
        gm_tra.gmTrackConverter.convert(sql_track, bed_path, 'bed', 'qualitative', name)
        # Comparison #
        a = open(track['orig_path'], 'r')
        b = open(bed_path,           'r')
        a.next()
        b.next()
        while True: self.assertEqual(a.next(), b.next())
        # Clean up #
        os.remove(sql_path)
        os.remove(bed_path)

Unittest_test().runTest() 
