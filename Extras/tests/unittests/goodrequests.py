# General modules #
import os

# Modules #
from   gMiner.gm_constants import *
import gMiner.gm_operations.desc_stat     as gm_stat
import gMiner.gm_operations.genomic_manip as gm_manip
import gMiner.gm_tracks                   as gm_tra

# Special test modules #
import gm_convert_tracks as gm_convert


###########################################################################
class Unittest_DescStat(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Paths #         
        tracks_path = gm_path + '/../Extras/tracks/'
        qual_path = tracks_path + 'qual/'
        quan_path = tracks_path + 'quant/'
        sql_qual = qual_path + 'sql/'
        sql_quan = quan_path + 'sql/'

        print sql_quan 
        # Lists #
        normal_files = [
            (qual_path + 'bed/validation1.bed', ['start', 'end', 'name', 'score', 'strand'], 'qualitative'),
            (qual_path + 'bed/validation2.bed', ['start', 'end', 'name', 'score', 'strand'], 'qualitative'),
            (qual_path + 'bed/validation3.bed', ['start', 'end', 'name', 'score', 'strand'], 'qualitative'),
            (quan_path + 'wig/scores1.wig', ['start', 'end', 'score'], 'quantitative'),
            (quan_path + 'wig/scores2.wig', ['start', 'end', 'score'], 'quantitative'),
            (quan_path + 'wig/scores3.wig', ['start', 'end', 'score'], 'quantitative'),
        ]
        sql_files = [
            sql_qual + 'validation1.sql', 
            sql_qual + 'validation2.sql', 
            sql_qual + 'validation3.sql', 
            sql_quan + 'scores1.sql', 
            sql_quan + 'scores2.sql', 
            sql_quan + 'scores3.sql', 
        ]

        # Conversion #
        global data
        data = []
        if True:
            for file in sql_files:
                if os.path.exists(file): os.remove(file)
            for i, file in enumerate(normal_files):
                gm_convert.convert_single_track(file[0], '/'.join(sql_files[i].split('/')[:-1])+'/', file[2])

        # Loading #
        for i, file in enumerate(sql_files):
            val_track = gm_tra.gmTrack.Factory({'name':'Validation track', 'location': file})
            data.append(list(getattr(val_track, 'get_data_' + normal_files[i][2][0:4])({'type':'chr', 'chr':'chr1'}, normal_files[i][1])))

    def runTest(self):
        global data

        # Desc stat #
        fields = ['start', 'end', 'name', 'score', 'strand']
        tests = [
            (gm_stat.gmCharacteristic.number_of_features,12),
            (gm_stat.gmCharacteristic.base_coverage,85),
            (gm_stat.gmCharacteristic.length,[10, 6, 10, 5, 5, 10, 10, 10, 10, 20, 10, 10]),
            (gm_stat.gmCharacteristic.score,[10.0, 0.0, 10.0, 0.0, 0.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 5.0]),
        ]
        for test in tests:
            self.assertEqual(test[0]([[d[fields.index(f)] for f in test[0].fields] for d in data[0]]) , test[1])

        # Manipulations #
        self.maxDiff = None
        operations = [
            list(gm_manip.gmManipulation.complement(200, data[0])),
            list(gm_manip.gmManipulation.overlap_track(400, data[1], data[2])),
            list(gm_manip.gmManipulation.overlap_pieces(400, data[1], data[2])),
        ]
        results = [
           [(10, 20, None, None, '.'),
            (30, 40, None, None, '.'),
            (50, 60, None, None, '.'),
            (80, 90, None, None, '.'),
            (110, 120, None, None, '.'),
            (135, 200, None, None, '.')],
           [(10, 20, u'Name1', 0.10000000000000001, u'+'),
            (30, 40, u'Name2', 0.20000000000000001, u'+'),
            (90, 100, u'Name5', 0.0, u'+'),
            (110, 120, u'Name6', 0.40000000000000002, u'+'),
            (130, 150, u'Name7', 0.40000000000000002, u'+'),
            (180, 190, u'Name8', 0.10000000000000001, u'+'),
            (180, 200, u'Name9', 0.10000000000000001, u'+'),
            (210, 220, u'Name10', 0.20000000000000001, u'+'),
            (230, 240, u'Name11', 0.10000000000000001, u'+'),
            (250, 260, u'Name12', 0.20000000000000001, u'+'),
            (270, 280, u'Name13', 0.0, u'+')],
           [(15, 20, u'NameA with Name1', 0.0, '.'),
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
            (270, 275, u'Name13 with NameL', 0.0, '.')]
        ]
        for i in range(len(operations)):
            self.assertEqual(operations[i], results[i])

        # Quant manipulations #
        operations = [
            list(gm_manip.gmManipulation.merge_scores(200, data[3], data[4], data[5])),
        ]
        results = [
            [(0, 5, 2.6666666666666665),
            (5, 10, 4.0),
            (20, 30, 10.0),
            (30, 40, 30.0),
            (40, 50, 26.666666666666664),
            (50, 60, 120.0),
            (60, 68, 100.0),
            (68, 70, 200.0),
            (70, 80, 100.0),
            (90, 110, 3.0),
            (120, 130, 10.0)]
        ]
        for i in range(len(operations)):
            self.assertEqual(operations[i], results[i])


# Add it #
if __name__ == '__main__':
    suite.addTest(Unittest_DescStat())
