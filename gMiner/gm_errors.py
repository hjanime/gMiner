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
