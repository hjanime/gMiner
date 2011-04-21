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
        # Conversion #
        if os.path.exists(track['location']): os.remove(track['location'])
        gm_tra.gmTrackConverter.convert(track['old_track'], track['location'], 'sql', 'qualitative', name)
        track['track'] = gm_tra.gmTrack.Factory({'location': track['location'], 'name': name})
        # Final file #
        temp_file = tempfile.NamedTemporaryFile(suffix='.bed', delete=False)
        bed_path = temp_file.name
        temp_file.close()
        os.remove(bed_path)
        # Conversion again #
        gm_tra.gmTrackConverter.convert(track['track'], bed_path, 'bed', 'qualitative', name)
        # Comparison #
        a = open(track['orig_path'], 'r')
        b = open(bed_path,           'r')
        a.next()
        b.next()
        for A,B in zip(a,b): self.assertEqual(A.split(), B.split())
        # Clean up #
        os.remove(bed_path)
