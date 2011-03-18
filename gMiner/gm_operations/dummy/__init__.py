'''
To implement your own operation, copy this file
and write the prepare() and run() classes.

__init__() gets the original request as a dictionary
plus a list of gmTracks objects from which you can
read or write.

run() must return an HTTP error code, some content and
a MIME type.

list() should print the available parameters of this
operation type
''' 

def list_options():
    return "This is a dummy module"

class gmOperation(object):
    def __init__(self, request, tracks):
        self.type = 'dummy'
        self.request = request
        self.tracks = tracks
    
    def prepare(self):
        pass
        
    def run(self):
        return "200", "Hello world", "text/plain"
