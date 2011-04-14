#python Extras/tests/random_files/generate_random_wig_fixed.py > Extras/tracks/quan/wig/pol2.wig

# Variables #
number_of_features = 32
size               = 100
range              = 1000
jump               = 10000
small_jump         = 200
orig_start         = 0
chrs               = 16

# Import modules #
import sys, random

# First line #
sys.stdout.write('track type=wiggle_0 name="Pol2 Signal" description="Chip-Seq" source="Random generator"\n')

# Main loop #
chr = 0
for i in xrange(number_of_features):
    if i % (number_of_features / chrs) == 0:
        chr += 1
        end  = orig_start
    start = end   + (random.randint(0,jump))
    end   = start + (random.randint(1,size))
    multiplier = random.randint(1,range) 
    sys.stdout.write('fixedStep chrom=chr' + str(chr) + ' start=' + str(start) + ' step=1' + '\n')
    for x in xrange(start, end):
        sys.stdout.write(str(multiplier + multiplier * random.random()) + '\n')
    for x in xrange(start, end):
        sys.stdout.write('0\n')
    start = end   + small_jump + (random.randint(0,jump))
    end   = start +              (random.randint(1,size))
    multiplier = random.randint(1,range) 
    for x in xrange(start,end):
        sys.stdout.write(str(multiplier + multiplier * random.random()) + '\n')
