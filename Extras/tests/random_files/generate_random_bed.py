# Variables #
number_of_features = 15000000
size               = 1000
jump               = 1000
orig_start         = 0
chrs               = 20 

# Import modules #
import sys, random, tempfile

# First line #
sys.stdout.write('track type=bed name="Features" description="Intervals" source="Random generator"\n')

# Name generator #
name_gen = tempfile._RandomNameSequence()

# Main loop #
chr = 0
for i in range(number_of_features):
    if i % (number_of_features / chrs) == 0:
        chr += 1
        start = orig_start
    start       =   start + (random.randint(0,jump))
    end         =   start + (random.randint(1,size))
    thick_start =   start + (random.randint(-size*0.25,size*0.25)) 
    thick_end   =   end   + (random.randint(-size*0.25,size*0.25))
    name        = name_gen.next() + name_gen.next()
    strand      = random.random() < 0.5 and '+' or '-'
    score       = random.random()
    line        = ['chr' + str(chr), str(start), str(end), name, score, strand, str(thick_start), str(thick_end)]
    sys.stdout.write('\t'.join(line) + '\n')
