# Variables #
number_of_features = 64
size               = 100
jump               = 10000
orig_start         = 0
chrs               = 16

# Import modules #
import sys, random

# First line #
sys.stdout.write('track type=wiggle_0 name="Rap1 Peaks" description="Chip-Seq" source="Random generator"\n')

# Main loop #
chr = 0
for i in range(number_of_features):
    if i % (number_of_features / chrs) == 0:
        chr += 1
        start = orig_start
        sys.stdout.write('variableStep chrom=chr' + str(chr) + '\n')
    start = start + (random.randint(0,jump))
    end   = start + (random.randint(1,size))
    for x in xrange(start,end):
        sys.stdout.write(str(x) + ' ' + str(random.random()) + '\n')
