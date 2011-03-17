# Importing #
from . import gmManipulation
from ... import gm_common as gm_com

#-------------------------------------------------------------------------------------------#   
class merge_scores(gmManipulation):
    '''Merges N quantitative tracks using the average fucntion'''
    input              = {'tracks': {'type': 'quantitative', 'fields': ['start', 'end', 'score']}}
    input_constraints  = []
    input_extras       = ['stop_val']
    output             = {'track':  {'type': 'quantitative', 'fields': ['start', 'end', 'score']}}
    output_constraints = []
    def chr_collapse(self, *args): return gm_com.gmCollapse.by_union(*args) 
    
    def run(self, **kwargs):
        '''Merge scores'''
        # Get all iterators #
        sentinel = [sys.maxint, sys.maxint, 0.0]
        tracks = [gm_com.sentinelize(x, sentinel) for x in iterables]
        elements = [x.next() for x in tracks]
        tracks_denom = 1.0/len(tracks)
        # Check empty #
        for i in xrange(len(tracks)-1, -1, -1):
            if elements[i] == sentinel:
                tracks.pop(i)
                elements.pop(i)
        # Core loop #
        while tracks:
            # Find the next boundaries #
            start = min([x[0] for x in elements])
            end = min([x[0] for x in elements if x[0] > start] + [x[1] for x in elements])
            # Scores between boundaries #
            scores = [x[2] for x in elements if x[1] > start and x[0] < end]
            if scores:
                score = sum(scores)*tracks_denom
                if abs(score) > 1e-10: yield (start, end, score)
            # Iterate over elements #
            for i in xrange(len(tracks)-1, -1, -1):
                # Change all starts #
                if elements[i][0] < end:
                    elements[i] = (end, elements[i][1], elements[i][2])
                # Advance the elements that need to be advanced #
                if elements[i][1] <= end:
                    elements[i] = tracks[i].next()
                # Pop sentinels #
                if elements[i] == sentinel:
                    tracks.pop(i)
                    elements.pop(i)