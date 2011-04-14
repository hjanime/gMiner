# Modules #
import sys, tempfile

# gMiner #
import gMiner
from gMiner.gm_constants import *

# Parser #
def parse_args(args):
    option = ''
    for arg in args:
        if arg.startswith("--"): option = arg[2:]
        else:
            if not option:
                print "Bad options"
                sys.exit()
            else:
                yield (option, arg)

# Make the request #
request = dict([(x[0], x[1]) for x in parse_args(sys.argv[1:])])

# Run it #
result = gMiner.run(**request)

# Save result #
data_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
data_file.write(result)
print "Result written in:", data_file.name
data_file.close()
