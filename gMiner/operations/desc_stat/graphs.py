# General modules #
import time

# Change backend #
import matplotlib
matplotlib.use('Agg', warn=False)
# If this continues to cause trouble,
# use the following experimental feature:
# matplotlib.pyplot.switch_backend('Agg')

# Plotting module #
import matplotlib.pyplot as pyplot

# gMiner Modules #
from ...constants import *
from ... import common
from ..desc_stat import gmCharacteristic

# Constants #
gm_default_plot_color      = 'magenta'
gm_default_color_selection = 'green'
gm_default_color_parent    = 'blue'

###########################################################################
class gmGraph(object):
    def __init__(self, request, subtracks, tracks, output_dir):
        self.request = request
        self.subtracks = subtracks
        self.tracks = tracks
        self.output_dir = output_dir

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
        self.chrs.sort(key=common.natural_sort)
        if self.request['per_chromosome'] and len(self.chrs)==0:
            raise Exception("After processing no chromosomes are left to graph")

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
        if self.request.get('output_name'): self.path = self.output_dir + '/' + self.request['output_name'] + '.png'
        else: self.path = self.output_dir + '/gminer_' + self.request['characteristic']           + '.png'
        with open(self.path, 'w') as f:
            fig.savefig(f, format='png', transparent=True)
        if not 'gm_interactive' in self.request: pyplot.close(fig)
        return [self.path]

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
                self.graph_legend.append([common.number_to_color(track.number) , track.name])
        for l in self.graph_legend: l[1] = common.wrap_string(l[1], 25)
        self.graph_legend = [[l[0], common.wrap_string(l[1], 52)] for l in self.graph_legend]

    def gen_graph_title(self):
        self.graph_title = getattr(gmCharacteristic, self.request['characteristic']).title
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
                    if self.b_many: tmp_color = common.number_to_color(track.number)
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
        self.ylabels = [[l[0], common.wrap_string(l[1], 30)] for l in self.ylabels]

    def gen_xlabel(self):
        unit_name = getattr(gmCharacteristic, self.request['characteristic']).units
        self.xlabel = unit_name

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

#-----------------------------------------------------------------------------#
class gmBarElement(gmPlotElement):
    def plot(self, axes):
        if len(self.subtracks) == 0:
            self.rect = None
            self.name = ''
            return 0
        if len(self.subtracks) == 2:
            child_stat = [s for s in self.subtracks if not s.parent][0].stat
            parent_stat = [s for s in self.subtracks if s.parent][0].stat
            if parent_stat == 0: ratio = 0
            else: ratio = 100.0 * child_stat / parent_stat
            big_rect = axes.barh(self.position, 100.0, align='edge', height=self.height, color='gray')
            self.name = str(int(ratio)) + '%'
            self.rect = axes.barh(self.position, ratio, align='edge', height=self.height, color=self.color)[0]
        else:
            self.name = common.split_thousands(self.subtracks[0].stat)
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

#-----------------------------------------------------------------------------#
class gmBoxElement(gmPlotElement):
    def plot(self, axes):
        self.DIQ = 0
        if len(self.subtracks) == 0:
            self.components = None
            return 0
        if len(self.subtracks) == 2:
            stat_selection = [s.stat for s in self.subtracks if not s.parent][0]
            if stat_selection:
                comp_selection = axes.boxplot(stat_selection, vert=0, positions=[self.position+self.height/2.0+0.1])
                box_coord_sel = comp_selection['boxes'][0].get_xdata()
                diq_sel = max(box_coord_sel) - min(box_coord_sel)
                if not self.request['per_chromosome'] or not 'track2' in self.request: self.color = gm_default_color_selection
                for comp in comp_selection.items(): [pyplot.setp(line, color=self.color) for line in comp[1]]
            else:
                diq_sel = 0
            stat_parent = [s.stat for s in self.subtracks if s.parent][0]
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
        if maxvalue == 0:
            all_values = [max(subtrack.stat) for e in elements for subtrack in e.subtracks if subtrack.stat]
            if all_values: return max(all_values)
        return maxvalue

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
