# Modules #
import sys, httplib, tempfile

# Args #
args = [('track1', '/scratch/tracks/qual/sql/ribosome_genesis.sql'), ('track1_name', 'Fake client track one'), ('track2', '/scratch/tracks/qual/sql/ribosome_proteins.sql'), ('track2_name', 'Fake client track two'), ('operation_type', 'desc_stat'), ('characteristic', 'number_of_features'), ('per_chromosome', 'True'), ('compare_parents', 'False')]

# Make the request #
request = '[gMiner]' + '\n'
request += 'version=0.1.6\n'
request += '\n'.join([x[0] + '=' + x[1] for x in args])

# Send it #
con = httplib.HTTPConnection('www.example.com')
con.request("POST", '/gMiner/', request)
res = con.getresponse()
print res.status, res.reason
data = res.read()

# Write file #
data_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
print "Result written in:", data_file.name
data_file.write(data)
data_file.close()
