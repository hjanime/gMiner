from gMiner.gm_constants import *
import gMiner.gm_tracks as gm_tra
import gMiner.gm_errors as gm_err
import random, tempfile

class gmRandomTrack(gm_tra.gmTrack):
    def __init__(self, minsize, chrsuffix):
        self.minsize = minsize
        self.type = 'qualitative'
        self.all_chrs = [chrsuffix + str(x) for x in range(10)]
        self.fields = ['start', 'end', 'name', 'score', 'strand']
        self.name_gen = tempfile._RandomNameSequence()
        self.name = 'Random track'
 
    def get_data_qual(self, selection, fields):
        if fields != self.fields: raise gm_err.RunError(0, 'Non standard random track')
        if selection['type'] != 'chr': raise gm_err.RunError(0, 'Selection on random track')
        start = 0
        for feat in range(int(self.minsize + 4*self.minsize*random.random())):
            start = start + (random.randint(0,100))
            end = start + (random.randint(1,100) )
            score = random.gammavariate(1, 0.1) * 1000  
            strand = map(lambda x: x==1 and '+' or '-', [random.randint(0,1)])[0]
            yield [start, end, self.name_gen.next(), score, strand]
