# General modules #
import time, base64, cStringIO

# Change backend #
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as pyplot

# Modules #
from .. import gm_common    as gm_com
from .. import gm_parsing   as gm_par
from .. import gm_errors    as gm_err
from ..gm_constants import *

# Constants #
gm_default_plot_color      = 'magenta'
gm_default_color_selection = 'green'
gm_default_color_parent    = 'blue'

# Functions #
def list_options():
    return '\n'.join([f[0]+':'+f[1].__doc__ for f in gmCharacteristic.__dict__.items() if f[0][0] != '_'])


###########################################################################   
class gmOperation(object):
    def __init__(self, request, tracks):
        self.type = 'desc_stat'
        self.request = request
        self.tracks = tracks
    
    def prepare(self):
        # characteristic #
        if not gm_par.exists_in_dict(self.request, 'characteristic'):
            raise gm_err.gmError(400, "There does not seem to be a characteristic specified in the request")
        gm_par.assert_has_method(gmCharacteristic, self.request['characteristic'])
        # per_chromosome #
        gm_par.default_if_none(self.request, 'per_chromosome')
        gm_par.convert_to_bool(self.request, 'per_chromosome')
        gm_par.assert_is_type(self.request['per_chromosome'], bool, 'per_chromosome')
        # compare_parents #
        if not self.request['selected_regions']: self.request['compare_parents'] = False
        gm_par.default_if_none(self.request, 'compare_parents')
        gm_par.convert_to_bool(self.request, 'compare_parents')
        gm_par.assert_is_type(self.request['compare_parents'], bool, 'compare_parents')
        # gm_encoding #
        gm_par.default_if_none(self.request, 'gm_encoding', 'text/base64')
        gm_par.assert_is_among(self.request['gm_encoding'], ['text/base64','image/png'], 'encoding')
        # Create subtracks #
        self.subtracks = [subtrack for track in self.tracks for subtrack in self.track_cut_down(track)]
        # Create graph #
        self.graph = gmGraph(self.request, self.subtracks, self.tracks)
         
    def track_cut_down(self, track):
        region = self.request['selected_regions']
        if region:
            #--- YES SELECTION ---#    
            if self.request['per_chromosome']:
                for chr in track.chrs:
                    subregion = [subr for subr in region if subr['chr'] == chr]
                    if subregion == []: continue
                    yield gmSubtrack(self.request, track, {'type': 'region', 'region': subregion})
                    if self.request['compare_parents']: yield gmSubtrack(self.request, track, {'type': 'chr', 'chr': chr})
            else:
                yield gmSubtrack(self.request, track, {'type': 'region', 'region': region})
                if self.request['compare_parents']: yield gmSubtrack(self.request, track, {'type': 'all'})
        else:
            #--- NO SELECTION ---#
            if self.request['per_chromosome']:
               for chr in track.chrs: yield gmSubtrack(self.request, track, {'type': 'chr', 'chr': chr})
            else:
                yield gmSubtrack(self.request, track, {'type': 'all'})
        
    def run(self):
        # Compute characterisitcs #
        for track in self.tracks:
            [gm_get_characteristic(subtrack, self.request['characteristic']) for subtrack in self.subtracks if subtrack.track == track]
            track.unload() 
        # Generate the graph #
        r1, r2, r3 = self.graph.generate()
        # Free memory #
        self.graph.cleanup()
        for subtrack in self.subtracks: subtrack.cleanup()
        # Return result #
        return r1, r2, r3

###########################################################################   
class gmSubtrack(object):
    def __init__(self, request, track, selection):
        self.request = request
        self.track = track 
        self.selection = selection
        
        # Unique chromosome #
        self.chr = None
        if self.selection['type'] == 'chr': self.chr = selection['chr']
        if self.selection['type'] == 'region' and self.request['per_chromosome']: self.chr = selection['region'][0]['chr']
    
    def __iter__(self):
        if self.selection['type'] == 'chr':
            yield self.track.get_data_qual(self.selection, self.fields)
        elif self.selection['type'] == 'all':
            for chr in self.track.chrs: yield self.track.get_data_qual({'type': 'chr', 'chr': chr}, self.fields)
        elif self.selection['type'] == 'region': 
            for span in self.selection['region']: yield self.track.get_data_qual({'type': 'span', 'span': span}, self.fields)

    def cleanup(self):
       del self.stat 
 
###########################################################################   
def gm_get_characteristic(subtrack, chara):
    # Variables #
    result = False
    stored = False
    shortcut = False
    type = subtrack.selection['type']
    charafn = getattr(gmCharacteristic, chara)
    # Stored #
    storable = charafn.storable and (type == 'chr' or type == 'all')
    if storable: stored = subtrack.track.get_stored('desc_stat', chara, subtrack.selection)
    if stored: result = stored
    # Shortcut #
    shortcutable = not result and charafn.shortcutable and (type == 'chr' or type == 'all')
    if shortcutable: shortcut = subtrack.track.stat_shortcut(chara, subtrack.selection)
    if shortcut: result = shortcut
    # Do it #
    subtrack.fields = charafn.fields
    result = getattr(gm_com.gmCollapse, charafn.collapse)([charafn(data) for data in subtrack])
    subtrack.stat = result
    # Store it #
    if storable and not stored: subtrack.track.write_stored('desc_stat', chara, subtrack.selection, result)

#-----------------------------------------------------------------------------#   
class gmCharacteristic(object):

    def num_of_features_options(func):
        func.fields = ['strand']
        func.shortcutable = True
        func.storable = True
        func.units = 'Count'
        func.collapse = 'by_adding'
        return func
    @classmethod 
    @num_of_features_options
    def number_of_features(cls, iterable):
        '''Number of features'''
        return sum(1 for _ in iterable)

    def base_coverage_options(func):
        func.fields = ['start','end']
        func.shortcutable = False
        func.storable = True
        func.units = 'Base pairs'
        func.collapse = 'by_adding'
        return func
    @classmethod 
    @base_coverage_options
    def base_coverage(cls, iterable):
        '''Base coverage'''
        sum = 0 
        position = -1
        for x in iterable:
            if x[1] > position:
                if x[0] < position: sum += x[1] - position
                else: sum += x[1] - x[0]
                position = x[1]
        return sum

    def length_options(func):
        func.fields = ['start','end']
        func.shortcutable = False
        func.storable = False
        func.units = 'Base Pairs'
        func.collapse = 'by_appending'
        return func
    @classmethod
    @length_options
    def length(cls, iterable):
        '''Length distribution'''
        return [x[1]-x[0] for x in iterable]

    def score_options(func):
        func.fields = ['score']
        func.shortcutable = False
        func.storable = False
        func.units = 'Undefined'
        func.collapse = 'by_appending'
        return func
    @classmethod
    @score_options
    def score(cls, iterable):
        '''Score distribution'''
        iterable = list(iterable)
        return [x[0] for x in iterable]

###########################################################################   
class gmGraph(object):
    def __init__(self, request, subtracks, tracks):
        self.request = request
        self.subtracks = subtracks
        self.tracks = tracks

    def generate(self):
        # Size variables #
        self.graph_width = 12.0
        ideal_height = float(len(self.subtracks))/2.0
        self.graph_height = min([ max([3.0, ideal_height]) , 10.0 ])    
        self.hjump = 0.8
        self.fontsize0 = 7.0
        self.fontsize1 = 9.0
        self.fontsize2 = 14.0

        # Chromosome check #
        self.chrs = list(set([subtrack.chr for subtrack in self.subtracks if subtrack.chr]))
        self.chrs.sort(key=gm_com.natural_sort)
        if self.request['per_chromosome'] and len(self.chrs)==0:
            raise gm_err.gmError(400, "After processing no chromosomes are left to graph")

        # Type of graph #
        self.request['gm_graph_type'] =  map(lambda x: isinstance(x,list) and 'boxplot' or 'barplot', [self.subtracks[0].stat])[0]
 
        # Empty variables #
        self.elements = []
        self.ylabels = []
        self.graph_legend = []
        self.upper_left_text = False
        self.xlabel = ''

        #---------------------------#   
        self.gen_bool_cases()
        self.gen_legend()
        self.gen_graph_title()
        self.gen_upper_left_text()
        self.gen_plot_elements()
        self.gen_ylabels()
        self.gen_xlabel()
        #---------------------------#   
 
        # Interactive mode #
        # if 'gm_interactive' in self.request: pyplot.ion()
        # else: pyplot.ioff()
        
        # Create figure #
        figprops = dict(figsize=(self.graph_width, self.graph_height))
        fig = pyplot.figure(**figprops)
        self.canvas = fig.canvas
        self.request['fig'] = fig

        # Adjust figure size #
        ylabels_extra_space = max([len(l[1].split('\n')[0]) for l in self.ylabels]) * (0.12 / self.graph_width)
        leftspace = max(0.03, min(ylabels_extra_space , 0.5))
        topspace = 1.0 - ((len(self.graph_title.split('\n'))-1.0)*0.6 + 1.0) * (0.4/self.graph_height)
        rightspace = 1.0 - 0.4/self.graph_width
        bottomspace = 0.5/self.graph_height
        adjustprops = dict(left=leftspace, right=rightspace, bottom=bottomspace, top=topspace)
        fig.subplots_adjust(**adjustprops)
        axes = fig.add_subplot(111)
      
        # Draw all we can now #
        if self.graph_legend:
            self.graph_legend.reverse()
            for label in self.graph_legend: axes.plot([-1.0, -1.0], color=label[0], label=label[1])
            axes.legend(prop={'size': self.fontsize2}, fancybox=True, labelspacing=0.3)    
        axes.set_title(self.graph_title)
        for e in self.elements: e.plot(axes)
        axes.set_yticks(zip(*self.ylabels)[0])
        axes.set_yticklabels(zip(*self.ylabels)[1])
        axes.set_xlabel(self.xlabel)
        self.canvas.set_window_title('(' + gm_project_name + ') ' + self.graph_title)

        # Finalize plot #
        self.graph_max_value = e.get_max_value(self.elements)
        for e in self.elements: e.finalize(axes, maxval=self.graph_max_value)

        # Adjust axis size #
        legend_extra_height = 0.8 * sum([len(l[1].split('\n')) for l in self.graph_legend])
        upperleft_extra_height = map(lambda x: x and 1.5 or 0.0, [self.upper_left_text])[0]
        extra_height = max(legend_extra_height, upperleft_extra_height)
        highest_value = self.graph_height + extra_height/(self.graph_height*0.25)
        rightmost_value = float(self.graph_max_value)*1.1
        bottom_value = -0.2*self.major_ystep
        axes.axis([0.0, rightmost_value, bottom_value, highest_value])

        # Corner texts #
        if self.upper_left_text:          
            axes.annotate(self.upper_left_text,xy=(8,-38), xycoords='axes pixels', fontsize=self.fontsize1)
        topleftcorner = 1.0 - 0.2/self.graph_height
        leftcorner = 0.1/self.graph_width
        toprightcorner = 1.0 - 0.17/self.graph_height
        rightcorner = 1.0 - 0.1/self.graph_width
        fig.text(rightcorner, toprightcorner, time.asctime(), horizontalalignment='right', fontsize=self.fontsize0)
        fig.text(leftcorner, topleftcorner, gm_project_name + ' generated graph', horizontalalignment='left', fontsize=self.fontsize0)

        # Return a PNG #
        rawfile = cStringIO.StringIO()
        fig.savefig(rawfile, format='png', transparent=True)
        result = rawfile.getvalue()
        if not 'gm_interactive' in self.request: pyplot.close(fig)
        if self.request['gm_encoding'] == 'text/base64': result = base64.encodestring(result)
        return 200, result, self.request['gm_encoding']

    def gen_bool_cases(self):
        self.b_many = len(self.tracks) > 1
        self.b_chr = self.request['per_chromosome']
        self.b_comp = self.request['compare_parents']
        self.b_sel = bool(self.request['selected_regions'])
        self.b_bar = self.request['gm_graph_type'] == 'barplot'

    def gen_legend(self):
        if self.b_comp and not self.b_bar and (not self.b_chr or not self.b_many):
            self.graph_legend.append([gm_default_color_parent , "Whole track"])
            self.graph_legend.append([gm_default_color_selection , "Selection"])
        if self.b_many and self.b_chr:
            for track in self.tracks:
                self.graph_legend.append([gm_com.number_to_color(track.number) , track.name])
        for l in self.graph_legend: l[1] = gm_com.wrap_string(l[1], 25)
        self.graph_legend = [[l[0], gm_com.wrap_string(l[1], 52)] for l in self.graph_legend]

    def gen_graph_title(self):
        chara_name = getattr(gmCharacteristic, self.request['characteristic']).__doc__
        self.graph_title = chara_name
        if not self.b_many:
            self.graph_title += ' of\n'
            if self.b_sel: self.graph_title += 'selection on '
            self.graph_title += '"' + self.tracks[0].name  + '"'
        else:
            if self.b_sel and not self.b_comp: self.graph_title += '\n of selection on multiple tracks' 

    def gen_upper_left_text(self):
        if self.b_comp:
            self.upper_left_text = "Selection is compared\nagainst whole track"
        if self.b_comp and not self.b_bar and self.b_chr and self.b_many:
            self.upper_left_text = "Selection (below) is compared\nagainst whole track (above)"
        if self.b_comp and not self.b_bar and (not self.b_chr or not self.b_many):
            self.upper_left_text = False

    def gen_plot_elements(self):
        if self.b_chr:#      chr: -----YES-----
            self.major_ystep = self.graph_height / float(len(self.chrs))
            self.minor_ystep = self.major_ystep*self.hjump / float(len(self.tracks))
            for i, chr in enumerate(self.chrs):
                for j, track in enumerate(self.tracks):
                    tmp_subtracks = [s for s in self.subtracks if s.track == track and s.chr == chr]
                    tmp_position = i*self.major_ystep+j*self.minor_ystep
                    tmp_height = self.minor_ystep
                    if self.b_many: tmp_color = gm_com.number_to_color(track.number)
                    else: tmp_color = gm_default_plot_color
                    self.elements += [gmPlotElement.Factory(self.request, tmp_subtracks, tmp_position, self.minor_ystep, tmp_color)]
        else:#                chr: -----NO-----
            self.major_ystep = self.graph_height / float(len(self.tracks))
            for i, track in enumerate(self.tracks):
                if True:
                    tmp_subtracks = [s for s in self.subtracks if s.track == track]
                    tmp_position = i*self.major_ystep
                    tmp_height = self.hjump
                    self.elements += [gmPlotElement.Factory(self.request, tmp_subtracks, tmp_position, tmp_height)]

    def gen_ylabels(self):
        if self.b_chr:
            for i, chr in enumerate(self.chrs):
                self.ylabels.append([i*self.major_ystep + self.minor_ystep*len(self.tracks)*0.5, chr])
        elif self.b_many:
            for i, track in enumerate(self.tracks):
                self.ylabels.append([i*self.major_ystep + self.hjump*0.5, track.name])
        else:
            self.ylabels = [[0.0, '']]
        self.ylabels = [[l[0], gm_com.wrap_string(l[1], 30)] for l in self.ylabels]

    def gen_xlabel(self):
        unit_name = getattr(gmCharacteristic, self.request['characteristic']).units
        self.xlabel = unit_name

    def cleanup(self):
        for element in self.elements: element.cleanup()

########################################################################### 
class gmPlotElement(object):
    @classmethod
    def Factory(cls, *args): 
        switch_var = args[0]['gm_graph_type'] 
        switch_dict = {
            'barplot': gmBarElement,
            'boxplot': gmBoxElement,
        }
        try:
            return switch_dict[switch_var](*args)
        except KeyError:
            return cls(*args)

    def __init__(self, request, subtracks, position, height, color=gm_default_plot_color):
        self.request = request
        self.subtracks = subtracks
        self.position = position
        self.height = height
        self.color = color

    def finalize(self, axes, **kwargs):
        pass

    def cleanup(self):
       del self.request
       del self.subtracks
       del self.position
       del self.height
       del self.color 

#-----------------------------------------------------------------------------#   
class gmBarElement(gmPlotElement):
    def plot(self, axes):
        if len(self.subtracks) == 0:
            self.rect = None
            self.name = ''
            return 0
        if len(self.subtracks) == 2:
            ratio = 100.0*[s for s in self.subtracks if s.selection['type'] == 'region'][0].stat / [s for s in self.subtracks if s.selection['type'] != 'region'][0].stat  
            big_rect = axes.barh(self.position, 100.0, align='edge', height=self.height, color='gray') 
            self.name = str(int(ratio)) + '%'
            self.rect = axes.barh(self.position, ratio, align='edge', height=self.height, color=self.color)[0]
        else:
            self.name = gm_com.split_thousands(self.subtracks[0].stat)
            self.rect = axes.barh(self.position, self.subtracks[0].stat, align='edge', height=self.height, color=self.color)[0]

    @classmethod
    def get_max_value(cls, elements):
        if len(elements[0].subtracks) == 2: return 102.0
        else: return max([e.rect.get_width() for e in elements if e.rect])

    def finalize(self, axes, **kwargs):
        graph_max_value = kwargs['maxval']
        if not self.rect: return 0
        cutoff = float(graph_max_value)/20.0
        width = self.rect.get_width()
        good_fontsize = 8 + self.request['fig'].get_figheight() * 0.25
        yloc = self.rect.get_y() + self.rect.get_height() / 2.0
        if width < cutoff:
            xloc = width + graph_max_value/200.0
            colour = 'black'
            align = 'left' 
        else:
            xloc = width - graph_max_value/200.0
            colour = 'white'
            align = 'right'
        axes.text(xloc, yloc, self.name, horizontalalignment=align, verticalalignment='center', color=colour, weight='bold', fontsize=good_fontsize)
        if len(self.subtracks) == 2:
            axes.text(101.0, yloc, "100%", horizontalalignment='left', verticalalignment='center', color='k', weight='bold', fontsize=good_fontsize)

    def cleanup(self):
        del self.name
        del self.rect
        super(gmBarElement, self).cleanup() 
        
#-----------------------------------------------------------------------------#   
class gmBoxElement(gmPlotElement):
    def plot(self, axes):
        self.DIQ = 0
        if len(self.subtracks) == 0:
            self.components = None
            return 0
        if len(self.subtracks) == 2:
            stat_selection =[s.stat for s in self.subtracks if s.selection['type'] == 'region'][0]
            if stat_selection:
                comp_selection = axes.boxplot(stat_selection, vert=0, positions=[self.position+self.height/2.0+0.1])
                box_coord_sel = comp_selection['boxes'][0].get_xdata()
                diq_sel = max(box_coord_sel) - min(box_coord_sel)
                if not self.request['per_chromosome'] or not 'track2' in self.request: self.color = gm_default_color_selection 
                for comp in comp_selection.items(): [pyplot.setp(line, color=self.color) for line in comp[1]]
            else:
                diq_sel = 0
            stat_parent = [s.stat for s in self.subtracks if s.selection['type'] != 'region'][0]
            if stat_parent:
                comp_parent = axes.boxplot(stat_parent, vert=0, positions=[self.position+self.height/2.0-0.1])
                box_coord_parent = comp_parent['boxes'][0].get_xdata()
                diq_parent = max(box_coord_parent) - min(box_coord_parent)
                if not self.request['per_chromosome'] or not 'track2' in self.request: self.color = gm_default_color_parent 
                for comp in comp_parent.items(): [pyplot.setp(line, color=self.color) for line in comp[1]]
            else:
                diq_parent = 0
            self.DIQ = max([diq_parent, diq_sel])
        else:
            stat = self.subtracks[0].stat
            if stat:
                components = axes.boxplot(stat, vert=0, positions=[self.position+self.height/2.0])
                main_box_coord = components['boxes'][0].get_xdata()
                self.DIQ = max(main_box_coord) - min(main_box_coord)
                for comp in components.items(): [pyplot.setp(line, color=self.color) for line in comp[1]]
   
    def get_max_value(self, elements):
        maxvalue = 3.0 * max([e.DIQ for e in elements])
        if maxvalue == 0: return max([max(subtrack.stat) for e in elements for subtrack in e.subtracks if subtrack.stat])
        else: return maxvalue

    def cleanup(self):
        del self.DIQ
        super(gmBoxElement, self).cleanup()
 
########################################################################### 

