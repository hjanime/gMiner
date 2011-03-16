# gMiner #
import gMiner
from gMiner.gm_constants import *
import gMiner.gm_operations.desc_stat     as gm_stat
import gMiner.gm_operations.genomic_manip as gm_manip

###########################################################################
class Unittest_gMinerModule(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate test tracks #
        execfile(gm_path + '/../Extras/tracks/generate.py')

    def runTest(self):
        self.maxDiff = None
        #-----------------------------------------------------------------------------#   
        fields = ['start', 'end', 'name', 'score', 'strand']
        tests  = [
                {'fn':     gm_stat.gmCharacteristic.number_of_features,
                 'input':  gMiner.gm_constants.gm_track_collections['Validation']['Validation 1']['data']['chr1'],
                 'output': 12},

                {'fn':     gm_stat.gmCharacteristic.base_coverage,
                 'input':  gMiner.gm_constants.gm_track_collections['Validation']['Validation 1']['data']['chr1'],
                 'output': 85},

                {'fn':     gm_stat.gmCharacteristic.length,
                 'input':  gMiner.gm_constants.gm_track_collections['Validation']['Validation 1']['data']['chr1'],
                 'output': [10, 6, 10, 5, 5, 10, 10, 10, 10, 20, 10, 10]},

                {'fn':     gm_stat.gmCharacteristic.score,
                 'input':  gMiner.gm_constants.gm_track_collections['Validation']['Validation 1']['data']['chr1'],
                 'output': [10.0, 0.0, 10.0, 0.0, 0.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 5.0]},

                ]
        for test in tests:
            self.assertEqual(test['fn']([[d[fields.index(f)] for f in test['fn'].fields] for d in test['input']]), test['output'])

        #-----------------------------------------------------------------------------#   
        fields = ['start', 'end', 'name', 'score', 'strand']
        tests  = [
                {'fn':     gm_manip.gmManipulation.complement,
                 'input':  (200,
                            gMiner.gm_constants.gm_track_collections['Validation']['Validation 1']['data']['chr1']),
                 'output': [(10, 20, None, None, '.'),
                           (30, 40, None, None, '.'),
                           (50, 60, None, None, '.'),
                           (80, 90, None, None, '.'),
                           (110, 120, None, None, '.'),
                           (135, 200, None, None, '.')]},

                {'fn':     gm_manip.gmManipulation.overlap_track,
                 'input':  (400,
                            gMiner.gm_constants.gm_track_collections['Validation']['Validation 2']['data']['chr1'],
                            gMiner.gm_constants.gm_track_collections['Validation']['Validation 3']['data']['chr1']),
                 'output': [(10, 20, u'Name1', 0.10000000000000001, u'+'),
                           (30, 40, u'Name2', 0.20000000000000001, u'+'),
                           (90, 100, u'Name5', 0.0, u'+'),
                           (110, 120, u'Name6', 0.40000000000000002, u'+'),
                           (130, 150, u'Name7', 0.40000000000000002, u'+'),
                           (180, 190, u'Name8', 0.10000000000000001, u'+'),
                           (180, 200, u'Name9', 0.10000000000000001, u'+'),
                           (210, 220, u'Name10', 0.20000000000000001, u'+'),
                           (230, 240, u'Name11', 0.10000000000000001, u'+'),
                           (250, 260, u'Name12', 0.20000000000000001, u'+')]},

                {'fn':     gm_manip.gmManipulation.overlap_pieces,
                 'input':  (400,
                            gMiner.gm_constants.gm_track_collections['Validation']['Validation 2']['data']['chr1'],
                            gMiner.gm_constants.gm_track_collections['Validation']['Validation 3']['data']['chr1']),
                 'output': [(15, 20, u'NameA with Name1', 0.0, '.'),
                           (32, 38, u'NameB with Name2', 0.0, '.'),
                           (95, 100, u'NameD with Name5', 0.0, '.'),
                           (110, 115, u'Name6 with NameD', 0.0, '.'),
                           (130, 135, u'Name7 with NameE', 0.0, '.'),
                           (140, 145, u'NameF with Name7', 0.0, '.'),
                           (185, 190, u'NameG with Name8', 0.0, '.'),
                           (185, 195, u'NameG with Name9', 0.0, '.'),
                           (210, 215, u'Name10 with NameH', 0.0, '.'),
                           (215, 220, u'NameI with Name10', 0.0, '.'),
                           (235, 240, u'NameJ with Name11', 0.0, '.'),
                           (250, 254, u'Name12 with NameJ', 0.0, '.'),
                           (252, 258, u'NameK with Name12', 0.0, '.'),
                           (256, 260, u'NameL with Name12', 0.0, '.'),
                           (270, 275, u'Name13 with NameL', 0.0, '.')]},

                ]
        for test in tests:
            self.assertEqual(list(test['fn'](*test['input'])), test['output'])

if __name__ == '__main__':
    suite.addTest(Unittest_gMinerModule())
