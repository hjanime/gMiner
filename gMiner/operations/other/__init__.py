# General modules #
import scipy

# Other modules #
from bbcflib.track import Track

# Internal modules #
from ..genomic_manip.basic import flatten
from ..genomic_manip.basic import qual_to_quan

#############################################################################################
def get_signal(T, chrom):
    with Track(T) as t:
        manip = flatten()
        if t.datatype == 'quantitative':
            s = list(manip(t.read(chrom)))
        else:
            if 'score' in t.fields:
                s = list(manip(qual_to_quan()(t.read('chr1',['start','end','score']))))
            else:
                s = list(manip(qual_to_quan()(t.read('chr1',['start','end']))))
        return s, t.name

def correlate(X, Y, chrom):
    import matplotlib.pyplot as p
    x, x_name = get_signal(X, chrom)
    y, y_name = get_signal(Y, chrom)
    print x
    print y
    corr = scipy.correlate(x, y, mode='full')
    p.plot(corr)
    p.xlabel('Shift [base pairs]')
    p.ylabel('Correlation [no units]')
    p.title('Correlation of "' + x_name + '" and "' + y_name + '"')
    p.show()
    return corr

#-----------------------------------------#
# This code was written by Lucas Sinclair #
# Kopimi                                  #
#-----------------------------------------#
