# Modules #
import sys, httplib2, urllib

# All parameters #
args = {
       'service'         : 'gMiner',
       'version'         : '1.0.2',
       'track1'          : '/scratch/sinclair/Tracks/qual/sql/ribosome_genesis.sql',
       'track1_name'     : 'Fake client track one',
       'track2'          : '/scratch/sinclair/Tracks/qual/sql/ribosome_proteins.sql',
       'track2_name'     : 'Fake client track two',
       'operation_type'  : 'desc_stat',
       'characteristic'  : 'number_of_features',
       'per_chromosome'  : 'True',
       'compare_parents' : 'False',
       'callback_url'    : 'http://localhost:9999/',
       }

# Make the request #
connection = httplib2.Http()
body = urllib.urlencode(args)
headers = {'content-type':'application/x-www-form-urlencoded'}
address = "http://localhost:7520/"

# Send it #
response, content = connection.request(address, "POST", body=body, headers=headers)
print "gMiner status:",  res.status
print "gMiner reason:",  res.reason
print "gMiner content:", content
