import gMiner
files = gMiner.run(
    track1          = '/scratch/sinclair/Genomic/yeast_data/all_yeast_genes/all_yeast_genes.sql',
    track1_name     = 'S. cer. genes (SGD)',
    operation_type  = 'desc_stat',
    characteristic  = 'number_of_features',
    per_chromosome  = 'True',
    compare_parents = 'False',
    output_location = '/tmp/',
)
