"""
=================
Script: gm_server
=================

Implementation of a web server around the functionality of gFeatMiner.

The servers listens for requests. When it gets one, it formats them. Then, sends the request off to the gMiner library. Formats the result obtained and sends that off in a HTTP POST to an URL specified in the original request. This can be useful if GDV wants to send requests to an instance of gm_server and receive answers.

#########################   REQUEST   ##########################
A typical job arriving to the server would be (HTML FORM ENCODED):
 - output_location = /tmp/ (path where you want the output)
 - callback_url = http://server.org/gfeatminer (URL to post back the response)
 - data = u'' (the data from the web form specifying the request, it is JSON formatted)
 - job_id : 1 (the identifier of the job)

This is the detailled description of 'data' parameter:
 - operation_type : 'desc_stat' (self-explanatory)
 - characteristic : 'base_coverage' (self-explanatory)
 - compare_parents :[] (a boolean)
 - per_chromosome : ['per_chromosome'] (idem)
 - filter:[{path:'/data/gdv_dev/files/115d5da7db0c588ae95bb91a5710ba2147be3df0.db',name:'foo'}] (path to a file that take the role of a filter, a selection)
 - ntracks:[{path:'/data/gdv_dev/files/d08aa4569c17aa79abc57c3b44da6abab927fa2.db',name:'bar'},{...},...] (path to the file(s) to process. It can be ordered)

Example:
    {'job_id': u'208', 'output_location': u'/data/gdv_dev/gFeatMiner/208', 'data': u'{"compare_parents":["compare_parents"],"per_chromosome":["per_chromosome"],"characteristic":"base_coverage","operation_type":"desc_stat","ntracks":[{"name":"RNAPol_fwd.sql","path":"/data/gdv_dev/files/6cb8a2f895e2cf829912bdbd244a6092289fe82f.db"}],"filter":[{"name":"chr(2839500,2909000)_chr(3023000,3070000)_.db","path":"/data/gdv_dev/files/952f788e0e0c5b43ec854515c9ebbad6a5c5e771.db"}]}', 'callback_url': u'http://svitsrv25.epfl.ch/gdv_dev/post', 'output_name': u'gfeatminer_output'}

#########################  RESPONSE  ###########################
A typical answer from the server would be (HTML FORM ENCODED):
 - id = 'job' (static)
 - action = 'gfeatresponse' (static)
 - job_id = the job identifier
 - data = u'' (the result, JSON formatted)

This is the detailled description of 'data' parameter:
 - files : [] a list of result files in JSON
 -  ...  path : path to the file
 -  ...  type : type of the file

Example with a track:
    {'id':'job','action':'gfeatresponse','job_id':'1','datatype':'new_track','data':'''{"files":[{"path":"/tmp/genes.sql","type":"sql"},{"path":"/tmp/regions.sql","type":"sql"}]}'''}

Example with a picture:
    {'id':'job','action':'gfeatresponse','job_id':'2','datatype':'new_image','data':'''{"files":[{"path":"/tmp/stat.png","type":"png"},{"path":"/tmp/distribution.png","type":"png"}]}'''}

If an error is found, the answer could be:
    {'id':'job','action':'gfeatresponse','job_id':'3','datatype':'unknown','data':'''{"type":"error","msg":"Text about error","html":"<html>Displayable version for user</html>"'''}
"""

# General modules #
import sys, os, cherrypy, httplib2, urllib, json, cgitb, traceback, warnings, time

# Other modules #
import gMiner

# Specific variables #
from gMiner.constants import gm_project_name, gm_project_version

# Job list #
global jobs
jobs = []

################################################################################
class gmServer(object):
    def __init__(self, port):
        self.port = port

    def serve(self):
        # Change the server name #
        serverTag = gm_project_name + "/" + str(gm_project_version)
        cherrypy.config.update({'tools.response_headers.on':      True,
                                'tools.response_headers.headers': [('Server', serverTag)]})
        # Change the port #
        cherrypy.server.socket_port = self.port
        # Add post processing #
        cherrypy.tools.post_process = cherrypy.Tool('on_end_request', post_process)
        # Start Server #
        cherrypy.quickstart(CherryRoot(), config={'/':
            {'request.dispatch':      cherrypy.dispatch.MethodDispatcher(),
             'tools.post_process.on': True}})

class CherryRoot(object):
    exposed = True
    def GET(self, **kwargs):  return pre_process(**kwargs)
    def POST(self, **kwargs): return pre_process(**kwargs)

################################################################################
def pre_process(**kwargs):
    global jobs
    jobs.append(kwargs)
    return 'Job "' + kwargs.get('job_id', -1) + '" added to queue'

def post_process(**kwargs):
    try:
        # Get a job from the list #
        global jobs
        job = jobs.pop(0)
        # Prepare the body dictonary #
        body_dict = {'id': 'job', 'action': 'gfeatresponse'}
        # Add the job id #
        job_id = job.get('job_id', -1)
        body_dict.update(job_id=job_id)
        # Prepare the standard output #
        stamp = '\033[1;33m[id ' + str(job_id) + ']\033[0m \033[4;33m' +  time.asctime() + '\033[0m %s\033[0m'
        # Load the form data #
        request = json.loads(job['data'])
        # Get the output location #
        request['output_location'] = job.pop('output_location')
        # Format the request #
        if request.has_key('compare_parents' ): request['compare_parents' ] = bool(request['compare_parents'  ])
        if request.has_key('per_chromosome'  ): request['per_chromosome'  ] = bool(request['per_chromosome'   ])
        if request.get('filter'):
            request['selected_regions'] = request['filter'][0]['path']
            request.pop('filter')
        if request.get('ntracks'):
            request.update(dict([('track' + str(i+1), v['path'])                         for i,v in enumerate(request['ntracks'])]))
            request.update(dict([('track' + str(i+1) + '_name', v.get('name', 'Unamed')) for i,v in enumerate(request['ntracks'])]))
            request.pop('ntracks')
        # Unicode filtering #
        request = dict([(k.encode('ascii'),v) for k,v in request.items()])
        # Run the request #
        files = gMiner.run(**request)
        # Determine the datatype #
        datatype = {'.png':'new_image', '.sql':'new_track'}.get(os.path.splitext(files[0])[-1], 'unknown')
        body_dict.update(datatype=datatype)
        # Format the output #
        return_data = {'files': [dict([('path',p),('type',p.split('.')[-1])]) for p in files]}
        body_dict.update(data=json.dumps(return_data))
        # Report success #
        print stamp % ('\033[42m' + files[0])
        # Print the response #
        print '\n\033[1;36mResponse: \033[0;36m' + str(body_dict) + '\033[0m\n'
    except Exception as err:
        # Report failure #
        print stamp % ('\033[41m' + str(err))
        # Print the request #
        print '\n\033[1;35mRequest: \033[0;35m' + str(request) + '\033[0m'
        # Print the traceback #
        print >>sys.stdout, '\033[0;31m'
        traceback.print_exc()
        print >>sys.stdout,'\033[0m'
        # Generate some html that can be displayed to the user #
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return_data = {'type':'error', 'html':cgitb.html(sys.exc_info()), 'msg': str(err)}
            body_dict.update(data=json.dumps(return_data))
    finally:
        url     = job['callback_url']
        method  = 'POST'
        body    = urllib.urlencode(body_dict)
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        httplib2.Http().request(url, method, body, headers)

#------------------------------------------------------------------------------#
if __name__ == '__main__': gmServer(port=7522).serve()

#-----------------------------------#
# This code was written by the BBCF #
# http://bbcf.epfl.ch/              #
# webmaster.bbcf@epfl.ch            #
#-----------------------------------#
