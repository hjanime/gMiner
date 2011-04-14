import gMiner
result = gMiner.run(
    track1             = '/scratch/genomic/tracks/ribosome_proteins.sql',
    track1_name        = 'RP genes (SGD)',
    track2             = '/scratch/genomic/tracks/ribosome_genesis.sql',
    track2_name        = 'Ribi genes (SGD)',
    operation_type     = 'desc_stat',
    characteristic     = 'base_coverage',
    selected_regions   = 'chr2:0:300000;chr5:0:200000',
    compare_parents    = 'False',
    per_chromosome     = 'True',
    wanted_chromosomes = 'chr1;chr2;chr5;chr6;chr7;chr8;chr9;chr10;chr11;chr12;' + \
                         'chr13;chr14;chr15;chr16;chr17;chr18;chr19;chr20;chr21;' + \
                         'chr22;chrX;chrY',
    gm_encoding        = 'image/png',
)
with open('/tmp/graph.png', 'w') as file: file.write(result)
