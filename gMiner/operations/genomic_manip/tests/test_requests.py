# Built-in modules #
import os, tempfile

# Internal modules #
from ..tests import run_request
from .... import run

# Other modules #
from bbcflib.track.track_collection import track_collections, yeast_chr_file
from bbcflib.track import load

# Unittesting #
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Nosetest flag #
__test__ = True

###################################################################################
class Test_Request(unittest.TestCase):
    def runTest(self):
        outdir = tempfile.mkdtemp(prefix='gMiner')
        tests = [{'kwargs': {'track1'          : track_collections['Scores'][1]['path'],
                             'track1_name'     : 'Validation score track 1',
                             'track1_chrs'     : yeast_chr_file,
                             'track2'          : track_collections['Scores'][2]['path'],
                             'track2_name'     : 'Validation score track 2',
                             'track2_chrs'     : yeast_chr_file,
                             'track3'          : track_collections['Scores'][3]['path'],
                             'track3_name'     : 'Validation score track 3',
                             'track3_chrs'     : yeast_chr_file,
                             'operation_type'  : 'genomic_manip',
                             'manipulation'    : 'merge_scores',
                             'output_location' : outdir},
                   'expected':  [(0,    5,    2.0 + 0.6666666666666666),
                                 (5,   10,    4.0),
                                 (20,  30,   10.0),
                                 (30,  40,   30.0),
                                 (40,  50,   26.0 + 0.666666666666666),
                                 (50,  60,  120.0),
                                 (60,  68,  100.0),
                                 (68,  70,  200.0),
                                 (70,  80,  100.0),
                                 (90,  110,   3.0),
                                 (120, 130,  10.)]}
                 ,
                 {'kwargs': {'track1'          : track_collections['Validation'][1]['path'],
                             'track1_name'     : 'Validation feature track 1',
                             'track1_chrs'     : yeast_chr_file,
                             'operation_type'  : 'genomic_manip',
                             'manipulation'    : 'neighborhood',
                             'before_start'    : -2,
                             'after_end'       : 2,
                             'output_location' : outdir},
                   'expected':  [( 0,   10,  u'Validation feature 2',   0.0, 0),
                                 ( 0,   12,  u'Validation feature 1',  10.0, 0),
                                 (18,   32,  u'Validation feature 3',  10.0, 0),
                                 (23,   32,  u'Validation feature 4',   0.0, 0),
                                 (38,   47,  u'Validation feature 5',   0.0, 0),
                                 (38,   52,  u'Validation feature 6',  10.0, 0),
                                 (58,   72,  u'Validation feature 7',  10.0, 0),
                                 (68,   82,  u'Validation feature 8',  10.0, 0),
                                 (88,  102,  u'Validation feature 9',  10.0, 0),
                                 (88,  112,  u'Validation feature 10', 10.0, 0),
                                 (118, 132,  u'Validation feature 11', 10.0, 0),
                                 (123, 137,  u'Validation feature 12',  5.0, 0)]}
                 ,
                 {'kwargs': {'track1'          : track_collections['Scores'][3]['path'],
                             'track1_name'     : 'Validation score track 3',
                             'track1_chrs'     : yeast_chr_file,
                             'operation_type'  : 'genomic_manip',
                             'manipulation'    : 'neighborhood',
                             'before_start'    : 2,
                             'after_end'       : 2,
                             'output_location' : outdir},
                   'expected':  [( 22,  52,  20.0),
                                 ( 52,  82, 300.0)]}
                 ,
                 {'kwargs': {'track1'          : track_collections['Scores'][3]['path'],
                             'track1_name'     : 'Validation score track 3',
                             'track1_chrs'     : yeast_chr_file,
                             'operation_type'  : 'genomic_manip',
                             'manipulation'    : 'threshold',
                             'threshold'       : 2,
                             'out_datatype'    : 'qualitative',
                             'output_location' : outdir},
                   'expected':  [(20, 80, 160.0)]}
                 ,
                 {'kwargs': {'track1'          : track_collections['Signals']['A']['path'],
                             'track1_name'     : 'Validation signal track 3',
                             'track1_chrs'     : yeast_chr_file,
                             'track2'          : track_collections['Signals']['B']['path'],
                             'track2_name'     : 'Validation signal track 2',
                             'track2_chrs'     : yeast_chr_file,
                             'operation_type'  : 'genomic_manip',
                             'manipulation'    : 'bool_and',
                             'output_location' : outdir},
                   'expected':  [(5, 10, u'Unnamed + Unnamed', 0.0, 0), (25, 30, u'Unnamed + Unnamed', 0.0, 0)]}
                ]
        for t in tests: run_request(self, t)
        os.removedirs(outdir)

#------------------------------------------------------------------------------#
class Test_No_Chrmeta(unittest.TestCase):
    def runTest(self):
        path = track_collections['Validation'][1]['path']
        files = run(
           track1           = path,
           track1_name      = 'Validation track one',
           operation_type   = 'genomic_manip',
           manipulation     = 'merge',
           output_location  = tempfile.gettempdir(),
        )
        os.remove(files[0])

#------------------------------------------------------------------------------#
class Test_Copy_Chrmeta(unittest.TestCase):
    def runTest(self):
        sql_path = track_collections['Validation'][2]['path_sql']
        bed_path = track_collections['Validation'][2]['path']
        files = run(
           track1           = bed_path,
           track1_name      = 'Validation track two',
           track1_chrs      = yeast_chr_file,
           operation_type   = 'genomic_manip',
           manipulation     = 'bool_not',
           output_location  = tempfile.gettempdir(),
        )
        with load(sql_path, chrmeta=yeast_chr_file, readonly=True) as sql:
            with load(files[0]) as bed:
                self.assertEqual(sql.chrmeta, bed.chrmeta)
        os.remove(files[0])

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
