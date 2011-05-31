def create_bins(X, num_of_bins=10):
    for x in X:
        length = (x[1] - x[0]) / num_of_bins
        for i in xrange(num_of_bins):
            yield (x[0]+i*length, x[0]+(i+1)*length, x[2], x[3], x[4])

from bbcflib.track import Track, new
from gMiner.operations.genomic_manip.scores import mean_score_by_feature
manip = mean_score_by_feature()
with Track('/scratch/genomic/tracks/rap1.sql') as a:
    with Track('/scratch/genomic/tracks/ribosome_proteins.sql') as b:
        with new('/tmp/manual.sql') as r:
            for chrom in a:
                r.write(chrom, manip(a.read(chrom), create_bins(b.read(chrom))))
            r.meta_chr   = a.meta_chr
            r.meta_track = {'datatype': 'qualitative', 'name': 'Mean score per bin', 'created_by': 'gMiner example script'}
