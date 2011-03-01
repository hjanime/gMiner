# General modules #
import sys

# Modules #
from .. import gm_parsing   as gm_par
from .. import gm_errors    as gm_err
from .. import gm_tracks    as gm_tra
from .. import gm_common    as gm_com
from ..gm_constants import *

# Functions #
def list_options():
    return '\n'.join([f[0]+':'+f[1].__doc__ for f in gmManipulation.__dict__.items() if f[0][0] != '_'])

class gmOperation(object):
    def __init__(self, request, tracks):
        self.type = 'genomic_manip'
        self.request = request
        self.tracks = tracks
    
    def prepare(self):
        # Manipulation specified #
        if not gm_par.exists_in_dict(self.request, 'manipulation'):
            raise gm_err.gmError(400, "There does not seem to be a manipulation specified in the request")
        # Manipulation exists #        
        gm_par.assert_has_method(gmManipulation, self.request['manipulation'])
        self.mani_fn = getattr(gmManipulation, self.request['manipulation'])
        # Manipulation valid # 
        if self.mani_fn.num_input != 'n' and self.mani_fn.num_input != len(self.tracks):
            raise gm_err.gmError(400, "The number of tracks inputed does not suit the manipulation requested")
        # Output specified #
        if not gm_par.exists_in_dict(self.request, 'output_location'):
            raise gm_err.gmError(400, "There does not seem to be an output location specified in the request")
        # Determine chromosomes #
        self.chrs = self.mani_fn.chr_fn([track.chrs for track in self.tracks])
        # Determine chr metadata #
        self.stop_vals = {}
        self.chrmeta = []
        for chr in self.chrs:
            self.stop_vals[chr] = max([m['length'] for m in track.chrmeta if m['name'] == chr and 'length' in m for track in self.tracks])
            self.chrmeta.append({'name':chr, 'length':self.stop_vals[chr]})
        # Determine name #
        self.out_name = self.mani_fn.__doc__ + ' on ' + ', '.join([track.name for track in self.tracks])
        comma_index = self.out_name.rfind(',')
        if comma_index > -1: self.out_name = self.out_name[:comma_index] + ' and' + self.out_name[comma_index+1:]
        # Determine fields #
        self.in_fields = self.mani_fn.in_fields 
        self.out_fields = self.mani_fn.out_fields 
        self.out_type = self.mani_fn.out_type 
        # Create output track #
        self.out = gm_tra.gmTrack.new(self.request['output_location'], 'sql', self.out_type, self.out_name)
        self.out.write_chr_meta(self.chrmeta)
        self.out.write_meta_data({'name': self.out_name})

    def run(self):
        for chr in self.chrs: self.out.write_qual(chr, self.mani_fn(self.stop_vals[chr],*[t.get_data_qual({'type':'chr','chr':chr},self.in_fields) for t in self.tracks]), self.out_fields)
        return 200, "Manipulation succeded", "text/plain"


########################################################################### 
class gmManipulation(object):
    def complement_options(func):
        '''The result consists of all spaces that were not
        covered by a feature in the original track'''
        func.num_input = 1
        func.chr_fn = gm_com.gmCollapse.by_appending
        func.in_fields = ['start', 'end']
        func.out_fields = ['start', 'end', 'name', 'score', 'strand']
        func.out_type = 'qualitative'
        return func
    @classmethod 
    @complement_options
    def complement(cls, stop_val, iterable):
        '''Complement'''
        last_end = 0
        for x in iterable:
            if x[0] > last_end:
                yield (last_end, x[0], None, None, '.')
                last_end = x[1]
            else:
                last_end = max(x[1], last_end)
        if last_end < stop_val:
            yield (last_end, stop_val, None, None, '.')

    #-----------------------------------------------------------------------------#  
    def internal_merge_options(func):
        '''Merges features that are adjacent or overlapping in one track'''
        func.num_input = 1
        func.chr_fn = gm_com.gmCollapse.by_appending
        func.in_fields = ['start', 'end', 'name', 'score', 'strand']
        func.out_fields = ['start', 'end', 'name', 'score', 'strand']
        func.out_type = 'qualitative'
        return func
    @classmethod
    @internal_merge_options
    def internal_merge(cls, stop_val, iterable):
        '''Internal merge'''
        sentinel = (sys.maxint, sys.maxint)
        X = gm_com.sentinelize(iterable, sentinel)
        x = X.next()
        if x != sentinel:
            while True:
                x_next = X.next()
                if x_next == sentinel:
                    yield tuple(x)
                    break
                if (x_next[0] <= x[1]):
                    x = list(x)
                    x[1] = max(x[1], x_next[1])
                    x[2] = x[2] + ' + ' + x_next[2]
                    x[3] = x[3] + x_next[3]
                    x[4] = x[4] == x_next[4] and x[4] or '.' 
                else:
                    yield tuple(x) 
                    x = x_next

    #-----------------------------------------------------------------------------#   
    def overlap_track_options(func):
        '''Computes the overlap of the first track against the second track
           returning only complete features from the first track'''
        func.num_input = 2
        func.chr_fn = gm_com.gmCollapse.by_intersection
        func.in_fields = ['start', 'end', 'name', 'score', 'strand']
        func.out_fields = ['start', 'end', 'name', 'score', 'strand']
        func.out_type = 'qualitative'
        return func
    @classmethod 
    @overlap_track_options
    def overlap_track(cls, stop_val, X, Y):
        '''Overlap by track'''
        sentinel = [sys.maxint, sys.maxint]
        X = gm_com.sentinelize(X, sentinel)
        Y = gm_com.sentinelize(Y, sentinel)
        x = X.next()
        y = Y.next()
        if x == sentinel or y == sentinel: continue_loop = False
        else: continue_loop = True
        while continue_loop:
            open_window = y[0]
            close_window = y[1]
            # Extend the y window as long as possible #
            while True:
                if y == sentinel: break
                y = Y.next()
                if y[0] > close_window: break
                if y[1] > close_window: close_window = y[1]
            # Read features from X until overshooting the y window #
            while True:
                if x[0] >= close_window: break
                if x[1] > open_window: yield x
                x = X.next()
                if x == sentinel:
                    continue_loop = False
                    break        

    #-----------------------------------------------------------------------------#   
    def overlap_pieces_options(func):
        '''Computes the overlap between both tracks returning
           new features that exacly match the overlaping zones'''
        func.num_input = 2
        func.chr_fn = gm_com.gmCollapse.by_intersection
        func.in_fields = ['start', 'end', 'name', 'score', 'strand']
        func.out_fields = ['start', 'end', 'name', 'score', 'strand']
        func.out_type = 'qualitative'
        return func
    @classmethod 
    @overlap_pieces_options
    def overlap_pieces(cls, stop_val, X, Y):
        '''Overlap by pieces'''
        def scan(f, Wf, g, Wg, lastPick):
            g_index = 0
            while g_index < len(Wg):
                g_current = Wg[g_index]
                if left_of(g_current, f):
                    Wg.pop(g_index)
                else:
                    g_index += 1
                    if overlaps(g_current, f):
                        yield (max(f[0],g_current[0]), min(f[1],g_current[1]), f[2] + " with " + g_current[2], 0.0, ".")
            if not left_of(f, g):
                Wf.append(f)
        def left_of(a, b):
            return (a[1] < b[0])
        def overlaps(a, b):
            return min(a[1],b[1]) - max(a[0],b[0]) > 0
        # This is the fjoin algorithm #
        sentinel = [sys.maxint, sys.maxint]
        X = gm_com.sentinelize(X, sentinel)
        Y = gm_com.sentinelize(Y, sentinel)
        x = X.next()
        y = Y.next()
        Wx = []
        Wy = []
        while x[0] != sentinel or y[0] != sentinel:
            if x[0] < y[0]:
                for z in scan(x, Wx, y, Wy, 0): yield z
                x = X.next()
            else:
                for z in scan(y, Wy, x, Wx, 1): yield z 
                y = Y.next()      

    #-----------------------------------------------------------------------------#   
    def merge_tracks_options(func):
        '''Merges all the features of several tracks together'''
        func.num_input = 'n'
        func.chr_fn = gm_com.gmCollapse.by_union
        func.in_fields = ['start', 'end']
        func.out_fields = ['start', 'end', 'name', 'score', 'strand']
        func.out_type = 'qualitative'
        return func
    @classmethod 
    @merge_tracks_options
    def merge_tracks(cls, stop_val, *iterables):
        '''Merge tracks'''
        pass

    #-----------------------------------------------------------------------------#   
    def merge_scores_options(func):
        '''Merges N quantitative tracks using the average fucntion'''
        func.num_input = 'n'
        func.chr_fn = gm_com.gmCollapse.by_union
        func.in_fields = ['start', 'end', 'score']
        func.out_fields = ['start', 'end', 'score']
        func.out_type = 'quantitative'
        return func
    @classmethod 
    @merge_scores_options
    def merge_scores(cls, stop_val, *iterables):
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
                if abs(score) > 1e-10: yield (start, end, score); print start, end, score
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
