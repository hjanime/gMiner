"""
=====
Plots
=====

gFeatMiner can generate different kind of plots. To access this functionality you must specify ``operation='plot'`` in the job request as seen in this example, in addition to a few other parameters that are detailed below::

    import gMiner
    files = gMiner.run(
        track1             = '/scratch/genomic/tracks/ribosome_proteins.sql',
        track1_name        = 'RP genes (SGD)',
        track2             = '/scratch/genomic/tracks/rap1.sql',
        track2_name        = 'Rap1 signal',
        track3             = '/scratch/genomic/tracks/pol2.sql',
        track3_name        = 'Pol2 signal',
        operation          = 'plot',
        plot               = 'scatter',
        output_location    = '/tmp/',
    )

The ``files`` variable will now contain the path to the file created in PNG format.

Parameters
----------

Here are described all the parameters that can or should be passed to gFeatMiner's run function.

======================== =====
Key                      Value
======================== =====
**track_1**              This specifies the location of the first track file. At least one genomic file must be inputted to compute a statistic. Of course, an undefined number of supplementary tracks can be specified. The order in which they are given may or may not influence the output depending on the operation requested.

**track_1_name**         This field is also required. Without a name, the resulting graph will not have a comprehensive legend associated and the user will get confused. Every track must have a name

**track_1_assembly**     If the track is missing required chromosome meta data, you can specify it here under the form of an assembly name.

**track_2**              The location of the second track file. This field is optional, for instance, if the operation only requires one genomic file

**track_2_name**         The name of the second track.

**track_2_assembly**     Same as above.

*[More tracks ...]*      Following tracks are specified according to the standard ``track_N`` and ``track_N_name``

**operation**            This field must be specified in the request and must take the value of ``plot`` if one wishes to perform descriptive statistic operations on the tracks provided.

**plot**                 Can take any of the values described in the next section, "Plots".

**output_location**      Specifies the directory in which the newly created track will be written.

**output_name**          Optionally specifies the name of the file to be created in ``output_location``.

*[Extra parameters ...]* Depending on the plot requested, you may need to provide extra parameters. Refer to the plot documentation for more details.
======================== =====

Plots
---------------
Several types of plots can be used to generate different types of graphs. You can chose which graph to plot by specifying ``plot=`` followed by one of the values in bold below:

.. automodule
"""

# Plotting module #
import matplotlib
matplotlib.use('Agg', warn=False)
import matplotlib.pyplot as pyplot

# Built-in modules #
import time

# Internal modules #
from gMiner import project_name

# Other modules #
import track
from track import Track

# Public objects #
__all__ = ['correlation', 'scatter']

################################################################################
class Plot(object):
    """Parent class to all specific plots. It mainly handles argument
       parsing coming from ``gMiner.run`` requests and also direct calls."""

    def generate(self, *args, **kwargs):
        """All child classes must implement
           this method."""
        raise NotImplementedError

    def from_request(self, request, tracks):
        """Put tracks and parameters in the right order.
           To be used when gMiner is called from the
           ``gMiner.run()`` function."""
        # Put the track in the order they came #
        tracks_needed = [(v['position'],k) for (k,v) in self.args.items() if v['kind'] == Track]
        tracks_needed.sort()
        for index,(pos,name) in enumerate(tracks_needed):
            request.update({name:tracks[index]})
        # Call child class #
        return self(**request)

    def __call__(self, *largs, **kwargs):
        """Check that all arguments are present
           and load all tracks that are given as paths
           instead of track objects. To be used
           when a plot is called directly from a script."""
        # Initialization #
        parsed_args = {}
        tracks_to_unload = []
        # Parse arguments #
        for key, arg in self.args.items():
            # The value is either in largs or kwargs#
            if key in kwargs:
                value = kwargs[key]
            elif len(largs) >= arg['position']:
                value = largs[arg['position']-1]
            elif arg.get('optional'):
                continue
            else:
                raise Exception("The argument '" + key + "' is missing" \
                                + " for the plot '" + self.name + "'.")
            # Special conditions  tracks that are paths #
            if arg['kind'] == Track:
                # Check if its a path #
                if isinstance(value, basestring):
                    value = track.load(value)
                    tracks_to_unload.append(value)
                # Check the datatype #
                if arg.get('datatype'):
                    if value.datatype != arg['datatype']:
                        raise Exception("The datatype of track '" + value.path + "' " \
                                        + "isn't '" + arg['datatype'] + "'.")
            # Is the value is not the right type, cast it #
            if not isinstance(value, arg['kind']):
                value = arg['kind'](value)
            # Add it to the dict #
            parsed_args[key] = value
        # Call generate #
        fig = self.generate(**parsed_args)
        # Close tracks #
        for track in tracks_to_unload: track.unload()
        # Return a figure #
        return fig

#---------------------------------------------------------------------------------#
class correlation(Plot):
    """Plots the cross-correlation between all chromosomes of
       two tracks using the numeric vectors of scores at every
       position of the genome::

           correlation(Q1, Q2)

       Contrary to most code in this library, in order to
       use scipy's functionality, it loads all the data in
       memory. Be careful when using on large genomes.

        ``correlation`` returns a matplotlib figure object.
    """

    def __init__(self):
        self.name = 'Cross correlation'
        self.args = {'X': {'position':1, 'kind':Track},
                     'Y': {'position':2, 'kind':Track}}

    def generate(self, X, Y):
        # Module #
        import scipy
        # Get the long numeric vectors (fills memory) #
        x = [score for chrom in X for score in X.score_vector(chrom)]
        y = [score for chrom in Y for score in Y.score_vector(chrom)]
        # Corr will contain the numeric vector #
        self.corr = scipy.correlate(x, y, mode='full')
        # Graph it #
        fig, axes = make_default_figure()
        axes.set_title('Correlation of "' + X.name + '" and "' + Y.name + '"')
        axes.set_xlabel('Shift [base pairs]')
        axes.set_ylabel('Correlation [no units]')
        axes.plot(self.corr)
        widen_axis(axes)
        # Return a figure #
        return fig

#---------------------------------------------------------------------------------#
class scatter(Plot):
    """Draws a scatter plot of 2 scores tracks in one or many
       list of regions::

           scatterplot(Q1, Q2, R1, log_scale=True)

       will make a scatterplot of the average of Q1 against
       the average of Q2 in every feature of R1.

       ``scatter`` returns a matplotlib figure object.
    """

    def __init__(self):
        self.name = 'Cross correlation'
        self.args = {'Q1': {'position':1, 'kind':Track, 'datatype':'quantitative'},
                     'Q2': {'position':2, 'kind':Track, 'datatype':'quantitative'},
                     'R1': {'position':3, 'kind':Track, 'datatype':'qualitative'},
                     'log_scale': {'position':4, 'kind':bool, 'optional':True}}

    def generate(self, Q1, Q2, R1, log_scale=False):
        # Module #
        from gMiner.operations.genomic_manip.scores import mean_score_by_feature
        # Get all the values (fills memory) #
        manip = mean_score_by_feature()
        x = [feature[3] for chrom in R1 for feature in manip(Q1.read(chrom), R1.read(chrom))]
        y = [feature[3] for chrom in R1 for feature in manip(Q2.read(chrom), R1.read(chrom))]
        # Graph it #
        fig, axes = make_default_figure()
        axes.set_title('Scatter plot of "' + Q1.name + '" against "' + Q2.name + '"' + \
                       ' in "' + R1.name + '"')
        axes.set_xlabel('Score of "' + Q1.name + '" [unspecified units]')
        axes.set_ylabel('Score of "' + Q2.name + '" [unspecified units]')
        axes.plot(x,y,'.')
        # Logarithmic scale option #
        if log_scale:
            axes.set_xscale('log')
            axes.set_yscale('log')
        widen_axis(axes)
        # Return a figure #
        return fig

################################################################################
def run(request, tracks, output_dir):
    """This function is called when running gMiner through
       the ``gMiner.run()`` fashion."""
    # Mandatory 'plot' parameter #
    plot_type = request.get('plot')
    if not plot_type:
        raise Exception("There does not seem to be a plot type specified in the request")
    if not plot_type in __all__:
        raise Exception("The specified plot '" + plot_type + "' does not exist.")
    try:
        plot_class = globals()[plot_type]
    except KeyError:
        raise Exception("The specified plot '" + plot_type + "' is not implemented yet.")
    except TypeError:
        raise Exception("The specified plot '" + plot_type + "' is a special object in python.")
    plot = plot_class()
    # Run it #
    figure = plot.from_request(request, tracks)
    # Save it #
    if request.get('output_name'): path = output_dir + '/' + request['output_name'] + '.png'
    else:                          path = output_dir + '/gminer_' + plot_type + '.png'
    with open(path, 'w') as file:  figure.savefig(file, format='png', transparent=True)
    # Return a list of paths #
    return [path]

#---------------------------------------------------------------------------------#
def make_default_figure():
    """Create a simple figure with axes."""
    fig = pyplot.figure()
    fig.text(0.96, 0.96, time.asctime(), horizontalalignment='right')
    fig.text(0.04, 0.96, project_name + ' generated graph', horizontalalignment='left')
    axes = fig.add_subplot(111)
    return fig, axes

def widen_axis(axes, factor=0.1):
    """Increase coordinates of a figure by 10%."""
    left, right, bottom, top = axes.axis()
    width  = (right - left) * factor
    height = (top - bottom) * factor
    axes.axis((left-width, right+width, bottom-height, top+height))

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
