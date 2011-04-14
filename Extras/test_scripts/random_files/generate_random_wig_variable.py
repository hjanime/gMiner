#python Extras/tests/random_files/generate_random_wig_variable.py > Extras/tracks/quan/wig/rap1.wig

# Variables #
number_of_features = 64
size               = 50
range              = 1000
jump               = 10000
orig_start         = 0
chrs               = 16

# Import modules #
import sys, random

# First line #
sys.stdout.write('track type=wiggle_0 name="Rap1 Peaks" description="Chip-Seq" source="Random generator"\n')

# Main loop #
chr = 0
for i in xrange(number_of_features):
    if i % (number_of_features / chrs) == 0:
        chr += 1
        end  = orig_start
        sys.stdout.write('variableStep chrom=chr' + str(chr) + '\n')
    start = end   + (random.randint(0,jump))
    end   = start + (random.randint(1,size))
    multiplier = random.randint(1,range) 
    for x in xrange(start,end):
        sys.stdout.write(str(x) + ' ' + str(multiplier + multiplier * random.random()) + '\n')
