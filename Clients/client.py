# Modules #
import sys, httplib2, tempfile

# Args #
args = [('service', 'gMiner'), ('version','0.1.6'), ('track1', '/scratch/tracks/qual/sql/ribosome_genesis.sql'), ('track1_name', 'Fake client track one'), ('track2', '/scratch/tracks/qual/sql/ribosome_proteins.sql'), ('track2_name', 'Fake client track two'), ('operation_type', 'desc_stat'), ('characteristic', 'number_of_features'), ('per_chromosome', 'True'), ('compare_parents', 'False')]

# Make the request #
request = '&'.join([x[0] + '=' + x[1] for x in args])

# Send it #
h = httplib2.Http()
res, data = h.request("http://www.example.com/gMiner/", "POST", body=request, headers={'content-type':'application/x-www-form-urlencoded'})
print res.status, res.reason

# Write file #
data_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
print "Result written in:", data_file.name
data_file.write(data)
data_file.close()
