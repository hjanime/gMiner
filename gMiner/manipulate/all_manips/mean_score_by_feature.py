################################# Description ##################################
label           = 'mean_score_by_feature'
short_name      = 'Mean score by feature'
long_name       = 'Mean score of the signal in every feature'
input_tracks    = [{'key':'X', 'position':1, 'fields':['start','end','...']},
                   {'key':'Y', 'position':2, 'fields':['start','end','score']}]
input_args      = []
input_meta      = []
output_tracks   = [{'position':1, 'fields': ['start','end','score','...']}]
tracks_collapse = None
chroms_collapse = 'union'

################################ Documentation #################################
tooltip = \
"""
    Given a signal track ``X`` and a feature track ``Y``,
the ``mean_score_by_feature`` manipulation computes the mean of scores
of every of ``Y``'s features in ``X``. The output consists of a feature track
similar to ``Y`` but with a new score value property for every feature.
"""

################################## Examples ####################################
numeric_example = \
""""""

visual_example = \
""""""

#################################### Tests #####################################
tests = [
    {'tracks':   [iter(([0,2,10],[2,4,20],[6,8,10]))],
     'args':     {'l':9, 'L':2},
     'expected': [(0,  1,   8.0),
                  (1,  3,  12.0),
                  (3,  5,  10.0),
                  (5,  6,   8.0),
                  (6,  9,   4.0),]}
     ,
    {'tracks':   [iter(([0,2,10],[2,4,20],[6,8,10]))],
     'args':     {'l':12, 'L':2},
     'expected': [(0,  1,   8.0),
                  (1,  3,  12.0),
                  (3,  5,  10.0),
                  (5,  6,   8.0),
                  (6,  9,   4.0),
                  (9,  10,  2.0),]}]

############################### Implementation #################################
def generate(X, Y):
    # Sentinel #
    sentinel = (sys.maxint, sys.maxint, 0.0)
    X = common.sentinelize(X, sentinel)
    # Growing and shrinking list of features in X #
    F = [(-sys.maxint, -sys.maxint, 0.0)]
    # --- Core loop --- #
    for y in Y:
        # Check that we have all the scores necessary #
        xnext = F[-1]
        while xnext[0] < y[1]:
            xnext = X.next()
            if xnext[1] > y[0]: F.append(xnext)
        # Throw away the scores that are not needed anymore #
        n = 0
        while F[n][1] <= y[0]:
            n+=1
        F = F[n:]
        # Compute the average #
        score = 0.0
        for f in F:
            if y[1] <= f[0]: continue
            if f[0] <  y[0]: start = y[0]
            else:            start = f[0]
            if y[1] <  f[1]: end   = y[1]
            else:            end   = f[1]
            score += (end-start) * f[2]
        # Emit a feature #
        yield y[0:3]+(score/(y[1]-y[0]),)+y[4:]
