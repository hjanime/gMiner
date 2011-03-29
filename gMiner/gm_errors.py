class gmError(Exception):
    '''Exception raised when gMiner encounters a problem.

    Attributes:
        code   -- HTTP error code (e.g. 400 or 500)
        msg    -- A message describing the problem
        origin -- The original exception if applicable
    '''

    def __init__(self, code, msg, origin=None):
        self.code = code
        self.msg = msg
        self.origin = origin

    def __str__(self):
        return self.msg + " - HTTP " + str(self.code)

###########################################################################
def catch_errors(fn):
    def wrapper(*args, **kwargs):
        try: 
            return fn(*args, **kwargs)
        except gm_err.gmError as err:
            return err.code, err.msg, "text/plain"
    return wrapper
