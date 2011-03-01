# General Modules #
import cherrypy

# Modules #
from . import gmRequest
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
        
        # Start Server #
        cherrypy.quickstart(CherryRoot(), config={'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}})


###########################################################################
class CherryRoot(object):
    exposed = True

    def POST(self):
        request = gmRequest(cherrypy.request.body)
        error, result, type = request.prepare()
        if error == 200: error, result, type = request.run()
        cherrypy.response.headers['Content-Type'] = type
        cherrypy.response.status = error
        del request
        return result

    def GET(self):
        cherrypy.response.status = 301
        cherrypy.response.headers['Location'] = gm_doc_url
        return 'Redirecting to documentation'
