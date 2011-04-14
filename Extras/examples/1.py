import gMiner
result = gMiner.run(
    track1          = '/scratch/genomic/tracks/all_yeast_genes.sql',
    track1_name     = 'S. cer. genes (SGD)',
    operation_type  = 'desc_stat',
    characteristic  = 'number_of_features',
    per_chromosome  = 'True',
    compare_parents = 'False',
    gm_encoding     = 'image/png',
)
with open('/tmp/graph.png', 'w') as file: file.write(result)
