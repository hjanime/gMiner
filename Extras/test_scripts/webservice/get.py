# Modules #
import cherrypy, tempfile, base64 

# Cherrypy server #
class CherryRoot(object):
    exposed = True
    def POST(self, **kwargs):
        print "Callback status:", kwargs['status']
        # Temporary file #
        data_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        # Decode result #
        if kwargs.has_key('type') and kwargs['type'] == 'text/base64':
            result = base64.decodestring(kwargs['result'])
        else:
            result = kwargs['result']
        # Write result #
        data_file.write(result)
        print "Result written in:", data_file.name
        data_file.close()

# Prepare to recieve the response #
cherrypy.server.socket_port = 9999
cherrypy.quickstart(CherryRoot(), config={'/': {'request.dispatch': cherrypy.dispatch.MethodDispatcher()}})
