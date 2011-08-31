import gMiner
files = gMiner.run(
    track1          : '/scratch/genomic/tracks/refseq_ucsc.sql',
    track1_name     : 'hg19 refSeq genome-wide from UCSC',
    track2          : '/scratch/genomic/tracks/hiv_bushman.sql',
    track2_name     : 'hg19 HIV integration sites from liftOver',
    operation_type  : 'genomic_manip',
    manipulation    : 'overlap_track',
    output_location : '/tmp/gMiner/',
)
