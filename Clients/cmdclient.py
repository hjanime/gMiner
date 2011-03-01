# Modules #
import sys, gMiner

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
request = '[gMiner]' + '\n'
request += 'version=' + str(gm_project_version) + '\n'
request += '\n'.join([x[0] + '=' + x[1] for x in parse_args(sys.argv[1:])]

# Run it #
req = gMiner.gmRequest(request, True)
error, result, type = req.prepare()
error, result, type = req.run()

# Show result #
print result
