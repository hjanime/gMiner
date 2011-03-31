# General Modules #
import cherrypy
import httplib2
import urllib

# Modules #
from . import gmJob
from .gm_constants import *

###########################################################################
class gmServer(object):
    def __init__(self, port=7520):
        self.HTTP_PORT = port

    def serve(self):
        # Change the server name #
        serverTag = gm_project_name + "/" + str(gm_project_version)
        cherrypy.config.update({'tools.response_headers.on': True, 'tools.response_headers.headers': [('Server', serverTag)]})
        # Change the port #
        cherrypy.server.socket_port = self.HTTP_PORT
        # Add post processing #
        cherrypy.tools.post_process = cherrypy.Tool('on_end_request', post_process)
        # Start Server #
        cherrypy.quickstart(CherryRoot(), config={'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                                                        'tools.post_process.on': True}})

###########################################################################
class CherryRoot(object):
    exposed = True

    def POST(self, **kwargs):
        # Run the request #
        global job
        job = gmJob(kwargs)
        error, result, type = job.prepare_catch_errors()
        # Check if callback or errors #
        if error != 200:
            del job
        else:
            if not job.request.has_key('callback_url'):
                error, result, type = job.run_catch_errors()
                del job
        # Return result #
        cherrypy.response.headers['Content-Type'] = type
        cherrypy.response.status = error
        return result

    def GET(self):
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = gm_doc_url
        return 'Redirecting to documentation'

###########################################################################
def post_process(**kwargs):
    # Run the job #
    global job
    if not job: return
    if not job.request.has_key('callback_url'): return
    # Run the job #
    error, result, type = job.run_catch_errors()
    # Get the id #
    if job.request.has_key('id'):
        id = job.request['id']
        body = urllib.urlencode({'id': id, 'status': error, 'result': str(result), 'type': type})
    else:
        body = urllib.urlencode({          'status': error, 'result': str(result), 'type': type})
    # Make an HTTP POST #
    connection = httplib2.Http()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    address = job.request['callback_url']
    # Send it #
    response, content = connection.request(address, "POST", body=body, headers=headers)
